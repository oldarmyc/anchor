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

from dateutil.relativedelta import relativedelta
from anchor import setup_application
from datetime import datetime
from uuid import uuid4


import unittest
import anchor
import uuid
import json
import re
import mock


class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.app, self.db = setup_application.create_app('True')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.client.get('/')

        self.tasks = anchor.tasks
        if not re.search('_test', self.tasks.config.MONGO_DATABASE):
            self.tasks.config.MONGO_DATABASE = (
                '%s_test' % self.tasks.config.MONGO_DATABASE
            )

        self.tasks.config.BROKER_URL = 'memory://'
        self.tasks.config.CELERY_RESULT_BACKEND = 'cache'
        self.tasks.config.CELERY_CACHE_BACKEND = 'memory'
        self.tasks.db = self.db

    def tearDown(self):
        self.db.sessions.remove()
        self.db.settings.remove()
        self.db.accounts.remove()
        self.db.forms.remove()

    def setup_user_login(self, sess):
        sess['username'] = 'test'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'logged_in'
        sess['_permanent'] = True
        sess['ddi'] = '123456'
        sess['cloud_token'] = uuid4().hex

    def setup_admin_login(self, sess):
        sess['username'] = 'oldarmyc'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'administrators'
        sess['_permanent'] = True
        sess['ddi'] = '123456'
        sess['cloud_token'] = uuid4().hex

    def setup_useable_admin(self):
        self.db.settings.update(
            {}, {
                '$push': {
                    'administrators': {
                        'admin': 'test1234',
                        'admin_name': 'Test Admin'
                    }
                }
            }
        )

    def setup_useable_account(self, expired=None):
        data = {
            'host_servers': [
                'f0ab54576022b02c128b9516ef23a9947c73a8564ca79c7d1debb015',
            ],
            'region': 'iad',
            'servers': [
                {
                    'state': 'active',
                    'name': 'test-server',
                    'created': '2015-02-04T14:11:09Z',
                    'host_id': (
                        'f0ab54576022b02c128b9516ef23a99'
                        '47c73a8564ca79c7d1debb015'
                    ),
                    'flavor': 'general1-1',
                    'id': '00000000-1111-2222-3333-444444444444',
                    'private': [
                        '10.10.10.10'
                    ],
                    'public': [
                        '162.162.162.162',
                        '2001:2001:2001:102:2001:2001:2001:2001'
                    ]
                }
            ],
            'token': 'd6ffb5c691a644a4b527f8ddc64c180f',
            'account_number': '123456'
        }
        if expired:
            data['cache_expiration'] = datetime.now() + relativedelta(days=-1)
        else:
            data['cache_expiration'] = datetime.now() + relativedelta(days=1)

        self.db.accounts.insert(data)

    def setup_useable_duplicate_servers_for_account(self):
        data = {
            'host_servers': [
                'f0ab54576022b02c128b9516ef23a9947c73a8564ca79c7d1debb015',
            ],
            'region': 'iad',
            'cache_expiration': datetime.now() + relativedelta(days=1),
            'servers': [
                {
                    'state': 'active',
                    'name': 'test-server',
                    'created': '2015-02-04T14:11:09Z',
                    'host_id': (
                        'f0ab54576022b02c128b9516ef23a99'
                        '47c73a8564ca79c7d1debb015'
                    ),
                    'flavor': 'general1-1',
                    'id': '00000000-1111-2222-3333-444444444444',
                    'private': [
                        '10.10.10.10'
                    ],
                    'public': [
                        '162.162.162.162',
                        '2001:2001:2001:102:2001:2001:2001:2001'
                    ]
                }, {
                    'state': 'active',
                    'name': 'test-server2',
                    'created': '2015-02-04T14:11:09Z',
                    'host_id': (
                        'f0ab54576022b02c128b9516ef23a99'
                        '47c73a8564ca79c7d1debb015'
                    ),
                    'flavor': 'general1-1',
                    'id': '11111111-2222-3333-4444-55566667777',
                    'private': [
                        '10.10.10.10'
                    ],
                    'public': [
                        '163.163.163.163',
                        '2002:2002:2002:102:2002:2002:2002:2002'
                    ]
                },
            ],
            'token': 'd6ffb5c691a644a4b527f8ddc64c180f',
            'account_number': '123456'
        }
        self.db.accounts.insert(data)

    def retrieve_csrf_token(self, data, variable=None):
        temp = re.search('id="csrf_token"(.+?)>', data)
        token = None
        if temp:
            temp_token = re.search('value="(.+?)"', temp.group(1))
            if temp_token:
                token = temp_token.group(1)

        if variable:
            var_temp = re.search('id="variable_0-csrf_token"(.+?)>', data)
            if var_temp:
                var_token = re.search('value="(.+?)"', var_temp.group(1))
                if var_token:
                    return token, var_token.group(1)
                else:
                    return token, None
            else:
                return token, None
        else:
            return token

    """ Tasks """

    def test_api_status(self):
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'PENDING'
                response = c.get('/task/%s' % uuid4().hex)

        check = json.loads(response.data)
        assert check.get('task_status') == 'PENDING', 'Incorrect state found'

    """ Accounts """

    def test_api_get_account(self):
        self.setup_useable_account()
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        check_data = {
            'servers': [
                {
                    'state': 'active',
                    'name': 'test-server',
                    'created': '2015-02-04T14:11:09Z',
                    'host_id': (
                        'f0ab54576022b02c128b9516ef23a99'
                        '47c73a8564ca79c7d1debb015'
                    ),
                    'flavor': 'general1-1',
                    'id': '00000000-1111-2222-3333-444444444444',
                    'private': [
                        '10.10.10.10'
                    ],
                    'public': [
                        '162.162.162.162',
                        '2001:2001:2001:102:2001:2001:2001:2001'
                    ]
                }
            ]
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.get(
                    '/account/123456/iad',
                    headers=headers
                )

        check = json.loads(response.data)
        assert check_data == check.get('data'), (
            'Incorrect data returned on account get'
        )

    def test_api_get_account_no_data(self):
        self.setup_useable_account(True)
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.get(
                    '/account/123456/iad',
                    headers=headers
                )

        check = json.loads(response.data)
        print check
        assert check.get('data') is None, (
            'Data returned when there should not have been any'
        )

    def test_api_delete_account(self):
        self.setup_useable_account()
        with self.app.test_client() as c:
            response = c.delete('/account/123456/iad')

        assert response._status_code == 204, 'Incorrect status code recieved'
        found = self.db.accounts.find_one(
            {'account_number': '123456', 'region': 'iad'}
        )
        assert found is None, (
            'Found account data when it should have been deleted'
        )

    def test_api_delete_account_error(self):
        self.setup_useable_account()
        with self.app.test_client() as c:
            with mock.patch('anchor.views.g') as patched_g:
                patched_g.db = None
                response = c.delete('/account/123456/iad')

        assert response._status_code == 500, (
            'Incorrect status code received on exception'
        )
        account = self.db.accounts.find_one(
            {'account_number': '123456', 'region': 'iad'}
        )
        assert account, 'Did not find account when exception was raised'

    def test_api_post_account_no_token(self):
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = False
                response = c.post('/account/123456/iad')

        assert response._status_code == 401, (
            'Incorrect status code recieved on post with no token'
        )
        check_data = json.loads(response.data)
        self.assertEquals(
            check_data.get('message'),
            'No authentication token provided, or '
            'authentication was unsuccessful',
            'Incorrect message received'
        )
        accounts = self.db.accounts.count()
        assert accounts == 0, 'Incorrect account count'

    def test_api_post_account(self):
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.post(
                    '/account/123456/iad',
                    headers=headers
                )

        check_data = json.loads(response.data)
        assert check_data.get('task_id'), (
            'No task ID returned on post'
        )

    """ Servers """

    def test_api_get_server(self):
        self.setup_useable_account()
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        check_server = {
            'id': '00000000-1111-2222-3333-444444444444',
            'name': 'test-server'
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.get(
                    '/account/123456/iad/server/'
                    '00000000-1111-2222-3333-444444444444',
                    headers=headers
                )

        check_data = json.loads(response.data)
        assert check_data.get('duplicate') is False, (
            'Incorrect duplicate value'
        )
        assert check_data is not None, 'Data is none and should not be'
        assert len(check_data.get('host_servers')) == 1, (
            'Incorrect number of servers returned for host'
        )
        server_data = check_data.get('host_servers')[0].get('server')
        assert server_data == check_server, 'Incorrect server data returned'

    def test_api_get_server_not_found(self):
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.get(
                    '/account/123456/iad/server/'
                    '00000000-1111-2222-3333-444444444444',
                    headers=headers
                )

        assert response._status_code == 404, 'Invalid status code received'

    def test_api_get_server_duplicate(self):
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        self.setup_useable_duplicate_servers_for_account()
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.get(
                    '/account/123456/iad/server/'
                    '00000000-1111-2222-3333-444444444444',
                    headers=headers
                )

        check_data = json.loads(response.data)
        assert check_data.get('duplicate') is True, (
            'Incorrect duplicate value'
        )
        assert len(check_data.get('host_servers')) == 2, (
            'Incorrect number of servers returned for host'
        )

    def test_api_get_server_no_token(self):
        self.setup_useable_account()
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = False
                response = c.get(
                    '/account/123456/iad/server/'
                    '00000000-1111-2222-3333-444444444444',
                )

        assert response._status_code == 401, (
            'Incorrect status code recieved on put with no token'
        )
        check_data = json.loads(response.data)
        self.assertEquals(
            check_data.get('message'),
            'No authentication token provided, or '
            'authentication was unsuccessful',
            'Incorrect message received'
        )

    def test_api_put_server(self):
        self.setup_useable_account()
        use_uuid = uuid.uuid4().hex
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                with mock.patch(
                    'anchor.tasks.check_add_server_to_cache'
                ) as cache:
                    cache.return_value = False
                    response = c.put(
                        '/account/123456/iad/server/%s' % use_uuid,
                        headers=headers
                    )

        check_data = json.loads(response.data)
        assert check_data.get('duplicate') is False, 'Incorrect return value'

    def test_api_put_server_duplicate(self):
        self.setup_useable_account()
        use_uuid = '00000000-1111-2222-3333-444444444444'
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.put(
                    '/account/123456/iad/server/%s' % use_uuid,
                    headers=headers
                )

        assert response._status_code == 400, (
            'Incorrect status code recieved on put no initialization'
        )
        check_data = json.loads(response.data)
        self.assertEquals(
            check_data.get('message'),
            'Server has been catalogued already',
            'Incorrect message received'
        )
        accounts = self.db.accounts.find_one()
        assert len(accounts.get('servers')) == 1, 'Incorrect server count'

    def test_api_put_server_not_initialized(self):
        use_uuid = uuid.uuid4().hex
        headers = {
            "X-Auth-Token": uuid.uuid4().hex
        }
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = True
                response = c.put(
                    '/account/123456/iad/server/%s' % use_uuid,
                    headers=headers
                )

        assert response._status_code == 400, (
            'Incorrect status code recieved on put no initialization'
        )
        check_data = json.loads(response.data)
        self.assertEquals(
            check_data.get('message'),
            'You must initialize before checking a server',
            'Incorrect message received'
        )
        accounts = self.db.accounts.count()
        assert accounts == 0, 'Incorrect account count'

    def test_api_put_server_no_token(self):
        use_uuid = uuid.uuid4().hex
        self.setup_useable_account()
        with self.app.test_client() as c:
            with mock.patch('anchor.tasks.check_auth_token') as ctoken:
                ctoken.return_value = False
                response = c.put(
                    '/account/123456/iad/server/%s' % use_uuid
                )

        assert response._status_code == 401, (
            'Incorrect status code recieved on put with no token'
        )
        check_data = json.loads(response.data)
        self.assertEquals(
            check_data.get('message'),
            'No authentication token provided, or '
            'authentication was unsuccessful',
            'Incorrect message received'
        )
        accounts = self.db.accounts.find_one()
        assert len(accounts.get('servers')) == 1, 'Incorrect server count'
