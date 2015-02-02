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

from flask import jsonify, g
from dateutil import tz


import datetime


UTC = tz.tzutc()


def get_timestamp():
    return datetime.datetime.now(UTC)


def check_for_token(request):
    try:
        return request.headers['X-Auth-Token']
    except:
        return None


def generate_error(message, code):
    response = jsonify({'message': message})
    response.status_code = code
    return response


def gather_dc_choices():
    choices = [('', '')]
    settings = g.db.settings.find_one()
    if settings.get('regions') and len(settings.get('regions')) > 0:
        choices = [
            (
                dc.get('abbreviation'), dc.get('abbreviation')
            ) for dc in settings.get('regions') if dc.get('active')
        ]
    return choices


def format_server_list_for_web(data):
    send_data = {}
    for server in data.get('servers'):
        try:
            send_data[server.get('host_id')].append(server)
        except:
            send_data[server.get('host_id')] = [server]

    return send_data
