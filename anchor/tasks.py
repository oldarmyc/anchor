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
import re


# Disable requests warnings from urllib3
requests.packages.urllib3.disable_warnings()


celery_app = Celery('anchor')
logger = get_task_logger(__name__)
celery_app.config_from_object(config)
mongo, db = HapPyMongo(config)


def process_api_request(url, verb, data, headers, status=None):
    try:
        """
        Commenting out as data may be needed so leaving it here
        if data:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                data=json.dumps(data),
                verify=False
            )
        else:
        """
        response = getattr(requests, verb.lower())(
            url,
            headers=headers,
            verify=False
        )
    except Exception as e:
        logger.error('An error occured executing the API call: %s' % e)

    try:
        if status:
            return response._status_code

        return json.loads(response.content)
    except Exception as e:
        logger.error('An error occured loading the content: %s' % e)
        return None


def generate_server_list(account_number, token, region):
    exit, all_servers, limit, marker = False, [], 100, None
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

        content = process_api_request(url, 'get', None, headers)
        if not content:
            break

        servers = content.get('servers')
        if len(servers) < limit:
            exit = True
        else:
            links = content.get('servers_links')[0]
            marker = links.get('href')

        all_servers += servers

    return all_servers


def generate_first_gen_server_list(account_number, token, region):
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    url = (
        'https://servers.api.rackspacecloud.com/v1.0/%s/'
        'servers/detail' % account_number
    )
    if region.lower() == 'lon':
        url = re.sub('servers.api', 'lon.servers.api', url)

    content = process_api_request(url, 'get', None, headers)
    if not content:
        return []

    servers = content.get('servers')
    return servers


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
    content = process_api_request(url, 'get', None, headers)
    if not content:
        return None

    return content.get('server')


def check_authorized(account_number, token):
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    url = 'https://identity.api.rackspacecloud.com/v2.0/users'
    status_code = process_api_request(url, 'get', None, headers, True)
    if status_code == 200:
        return True

    return False


def generate_host_and_server_data(ng_servers, fg_servers):
    hosts, servers = [], []
    for server in ng_servers:
        host_id = server.get('hostId')
        data = process_server_details(server)
        servers.append(data)
        if host_id not in hosts:
            hosts.append(host_id)

    for server in fg_servers:
        host_id = server.get('hostId')
        data = process_fg_server_details(server)
        servers.append(data)
        if host_id not in hosts:
            hosts.append(host_id)

    return servers, hosts


def generate_zone_and_server_data(ng_servers):
    public_zones, servers = [], []
    for server in ng_servers:
        public_zone = server.get('RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId')
        data = process_server_details(server)
        servers.append(data)
        if public_zone not in public_zones:
            public_zones.append(public_zone)

    return servers, public_zones


def process_server_details(server):
    data, addresses, found_public = {}, {}, False
    for key, value in server.get('addresses').iteritems():
        if key not in ['public', 'private']:
            key = 'custom'

        if key == 'public':
            found_public = True

        if len(value) > 0:
            for item in value:
                server_address = item.get('addr')
                if key == 'public' and item.get('version') == 4:
                    if server_address != server.get('accessIPv4'):
                        server_address = server.get('accessIPv4')

                try:
                    addresses[key].append(server_address)
                except:
                    addresses[key] = [server_address]

    if not found_public and server.get('accessIPv4'):
        addresses['public'] = [server.get('accessIPv4')]

    host_id = server.get('hostId')
    metadata = server.get('metadata', {})
    data = {
        'state': server.get('OS-EXT-STS:vm_state'),
        'id': server.get('id'),
        'host_id': host_id,
        'public_zone': server.get('RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId'),
        'name': server.get('name'),
        'created': server.get('created'),
        'flavor': server.get('flavor').get('id'),
        'addresses': addresses,
        'reboot_window': metadata.get('rax:reboot_window')
    }
    return data


def process_fg_server_details(server):
    data = {}
    host_id = server.get('hostId')
    metadata = server.get('metadata', {})
    data = {
        'type': 'fg',
        'state': server.get('status'),
        'id': server.get('id'),
        'host_id': host_id,
        'name': server.get('name'),
        'flavor': server.get('flavorId'),
        'addresses': server.get('addresses'),
        'reboot_window': metadata.get('rax:reboot_window')
    }
    return data


@celery_app.task
def generate_account_server_list(
    account_number,
    token,
    region,
    lookup_type,
    web=None
):
    ng_servers = generate_server_list(account_number, token, region)
    fg_servers = generate_first_gen_server_list(account_number, token, region)
    servers = []
    data = {
        'account_number': account_number,
        'region': region,
        'token': token
    }
    if lookup_type == 'host_server':
        servers, hosts = generate_host_and_server_data(ng_servers, fg_servers)
        data['host_servers'] = hosts

    elif lookup_type == 'public_ip_zone':
        servers, public_zones = generate_zone_and_server_data(ng_servers)
        data['public_zones'] = public_zones

    data['servers'] = servers
    data['lookup_type'] = lookup_type
    store_account = Account(data)
    db.accounts.update(
        {
            'account_number': store_account.account_number,
            'region': region,
            'lookup_type': lookup_type
        },
        store_account.__dict__,
        upsert=True
    )
    if web:
        account_data = db.accounts.find_one(
            {
                'account_number': store_account.account_number,
                'region': region,
                'lookup_type': lookup_type
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
def check_auth_token(account_number, token):
    return check_authorized(account_number, token)


@celery_app.task
def get_task_results(task_id):
    result = celery_app.AsyncResult(task_id)
    return result.get()


@celery_app.task
def check_task_state(task_id):
    return celery_app.AsyncResult(task_id).state
