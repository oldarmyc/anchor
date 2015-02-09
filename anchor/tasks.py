# Copyright 2014 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from celery import Celery
from models import Account
from happymongo import HapPyMongo
from celery.utils.log import get_task_logger


import config.celery as config
import requests
import json


celery_app = Celery('anchor')
logger = get_task_logger(__name__)
celery_app.config_from_object(config)
mongo, db = HapPyMongo(config)


def generate_server_list(account_number, token, region):
    response, exit, all_servers, limit, marker = None, False, [], 100, None
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    while exit is False:
        if marker is None:
            url = (
                'https://%s.servers.api.rackspacecloud.com/v2/%s/'
                'servers/detail?limit=%d' % (
                    region.lower(),
                    account_number,
                    limit
                )
            )
        else:
            url = marker

        try:
            response = requests.get(url, headers=headers)
            content = json.loads(response.content)
        except Exception as e:
            logger.error(
                'An error occured retrieving the servers: %s - %s' % (
                    response,
                    e
                )
            )
            break

        servers = content.get('servers')
        if len(servers) < limit:
            exit = True
        else:
            links = content.get('servers_links')[0]
            marker = links.get('href')

        all_servers += servers

    return all_servers


def get_server_details(token, region, account_number, server_id):
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    url = 'https://%s.servers.api.rackspacecloud.com/v2/%s/servers/%s' % (
        region.lower(),
        account_number,
        server_id
    )
    try:
        response = requests.get(url, headers=headers)
        content = json.loads(response.content)
    except Exception as e:
        logger.error(
            'An error occured retrieving the server details: %s - %s' % (
                response,
                e
            )
        )
        return None

    return content.get('server')


def generate_host_and_server_data(all_servers):
    hosts, servers = [], []
    for server in all_servers:
        host_id = server.get('hostId')
        data = process_server_details(server)
        servers.append(data)
        if host_id not in hosts:
            hosts.append(host_id)

    return servers, hosts


def process_server_details(server):
    data, public, private = {}, [], []
    if server.get('addresses').get('public'):
        for item in server.get('addresses').get('public'):
            public.append(item.get('addr'))

    if server.get('addresses').get('private'):
        for item in server.get('addresses').get('private'):
            private.append(item.get('addr'))

    host_id = server.get('hostId')
    data = {
        'state': server.get('OS-EXT-STS:vm_state'),
        'id': server.get('id'),
        'host_id': host_id,
        'name': server.get('name'),
        'created': server.get('created'),
        'flavor': server.get('flavor').get('id'),
        'public': public,
        'private': private
    }
    return data


@celery_app.task
def generate_account_server_list(account_number, token, region, web=None):
    all_servers = generate_server_list(account_number, token, region)
    servers, hosts = generate_host_and_server_data(all_servers)
    data = {
        'account_number': account_number,
        'region': region,
        'token': token,
        'host_servers': hosts,
        'servers': servers
    }
    store_account = Account(data)
    db.accounts.update(
        {
            'account_number': store_account.account_number,
            'region': region
        },
        store_account.__dict__,
        upsert=True
    )
    if web:
        account_data = db.accounts.find_one(
            {
                'account_number': store_account.account_number,
                'region': region
            }
        )
        return str(account_data.get('_id'))
    return


@celery_app.task
def check_add_server_to_cache(
    token,
    region,
    account_number,
    server_id,
    account_data
):
    server_details = get_server_details(
        token,
        region,
        account_number,
        server_id
    )
    if server_details:
        server_data = process_server_details(server_details)
        check_duplicate = db.accounts.find_one(
            {
                'account_number': account_number,
                'region': region,
                'servers.host_id': server_details.get('host_id')
            }
        )
        db.accounts.update(
            {
                '_id': account_data.get('_id')
            }, {
                '$push': {
                    'servers': server_data
                }
            }
        )
        return bool(check_duplicate)
    return None


@celery_app.task
def get_task_results(task_id):
    result = celery_app.AsyncResult(task_id)
    return result.get()


@celery_app.task
def check_task_state(task_id):
    return celery_app.AsyncResult(task_id).state
