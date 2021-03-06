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

from anchor import setup_application
from datetime import datetime
from dateutil.relativedelta import relativedelta
from uuid import uuid4


import unittest
import anchor
import urlparse
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

    def setup_useable_account(self):
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
                    'public_zone': (
                        'bf8a1d259e0fdec48a44140b7f5f'
                        'fc3acdcd8e0a76ea57b0c84edbd3'
                    ),
                    'flavor': 'general1-1',
                    'id': '00000000-1111-2222-3333-444444444444',
                    'reboot_window': (
                        '2014-01-28T00:00:00Z;2014-01-28T03:00:00Z'
                    ),
                    'addresses': {
                        'private': ['10.10.10.10'],
                        'public': [
                            '162.162.162.162',
                            '2001:2001:2001:102:2001:2001:2001:2001'
                        ],
                        'custom': ['192.168.1.1']
                    }
                }, {
                    'state': 'active',
                    'name': 'test-server2',
                    'created': '2015-02-04T14:11:09Z',
                    'host_id': (
                        'f0ab54576022b02c128b9516ef23a99'
                        '47c73a8564ca79c7d1debb015'
                    ),
                    'public_zone': (
                        'bf8a1d259e0fdec48a44140b7f5f'
                        'fc3acdcd8e0a76ea57b0c84edbd3'
                    ),
                    'flavor': 'general1-1',
                    'id': '11111111-2222-3333-4444-55566667777',
                    'reboot_window': (
                        '2014-01-28T00:00:00Z;2014-01-28T03:00:00Z'
                    ),
                    'addresses': {
                        'private': [
                            '11.11.11.11'
                        ],
                        'public': [
                            '163.163.163.163',
                            '2002:2002:2002:102:2002:2002:2002:2002'
                        ],
                        'custom': [
                            '192.168.2.1'
                        ]
                    }
                }
            ],
            'token': 'd6ffb5c691a644a4b527f8ddc64c180f',
            'lookup_type': 'host_server',
            'account_number': '123456'
        }
        self.db.accounts.insert(data)

    def setup_useable_cbs_account(self):
        data = {
            'host_servers': None,
            'region': 'iad',
            'public_zones': None,
            'servers': None,
            'account_number': '123456',
            'volumes': [
                {
                    'status': 'available',
                    'host': '4a61be11-f557-40ea-a286-d01edaf72336',
                    'display_name': 'test_cbs',
                    'created': '2015-12-17T12:29:15.000000',
                    'bootable': True,
                    'availability_zone': 'nova',
                    'id': '910cd151-799f-4203-9cc0-9ee60518c60d',
                    'volume_type': 'SATA',
                    'size': 100
                }, {
                    'status': 'available',
                    'host': '4a61be11-f557-40ea-a286-d01edaf72336',
                    'display_name': 'test_cbs_2',
                    'created': '2015-12-17T12:26:46.000000',
                    'bootable': True,
                    'availability_zone': 'nova',
                    'id': '497d4575-2e0a-4375-88db-f6f6dfb8726c',
                    'volume_type': 'SATA',
                    'size': 100
                }
            ],
            'cbs_hosts': [
                '4a61be11-f557-40ea-a286-d01edaf72336'
            ],
            'lookup_type': 'cbs_host'
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

    """ Basic tests """

    def test_ui_lookup_admin(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/lookup/')

        self.assertEqual(
            response._status_code,
            200,
            'Invalid response code %s' % response._status_code
        )

    def test_ui_lookup_user(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/lookup/')

        self.assertEqual(
            response._status_code,
            200,
            'Invalid response code %s' % response._status_code
        )

    def test_ui_lookup_post(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'data_center': 'iad'}
            response = c.post(
                '/lookup/servers',
                data=json.dumps(data),
                content_type='application/json'
            )

        result = json.loads(response.data)
        assert result.get('task_id'), 'Task ID was not found'

    def test_ui_lookup_pending_status(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'PENDING'
                response = c.get(
                    '/lookup/servers/%s' % uuid4().hex
                )

        check = json.loads(response.data)
        assert check.get('state') == 'PENDING', 'Incorrect state found'
        assert check.get('code') == 204, 'Incorrect code found on return'

    def test_ui_lookup_bad_status(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'BAD'
                response = c.get(
                    '/lookup/servers/%s' % uuid4().hex
                )

        check = json.loads(response.data)
        assert check.get('state') == 'BAD', 'Incorrect state found'
        assert check.get('code') == 500, 'Incorrect code found on return'

    def test_ui_lookup_success_with_data(self):
        self.setup_useable_account()
        account = self.db.accounts.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'SUCCESS'
                with mock.patch('anchor.tasks.get_task_results') as data:
                    data.return_value = str(account.get('_id'))
                    response = c.get(
                        '/lookup/servers/%s' % uuid4().hex
                    )

        self.assertIn(
            account.get('servers')[0].get('id'),
            response.data,
            'Could not find the test UUID for server in response'
        )
        self.assertIn(
            account.get('host_servers')[0],
            response.data,
            'Could not find the host ID in response'
        )
        self.assertIn(
            account.get('region').upper(),
            response.data,
            'Could not find the region in the response'
        )

    def test_ui_lookup_success_with_cbs_data(self):
        self.setup_useable_cbs_account()
        account = self.db.accounts.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'SUCCESS'
                with mock.patch('anchor.tasks.get_task_results') as data:
                    data.return_value = str(account.get('_id'))
                    response = c.get(
                        '/lookup/servers/%s' % uuid4().hex
                    )

        self.assertIn(
            account.get('volumes')[0].get('id'),
            response.data,
            'Could not find the test UUID for server in response'
        )
        self.assertIn(
            account.get('cbs_hosts')[0],
            response.data,
            'Could not find the host ID in response'
        )
        self.assertIn(
            account.get('region').upper(),
            response.data,
            'Could not find the region in the response'
        )

    def test_ui_csv_pending_status(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as data:
                data.return_value = 'PENDING'
                response = c.get(
                    '/lookup/servers/%s/host_server/csv' % uuid4().hex
                )

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = urlparse.urlparse(response.headers.get('Location'))
        self.assertEqual(
            location.path,
            '/',
            'Invalid redirect location %s, expected "/"' % location.path
        )

    def test_ui_csv_generate(self):
        self.setup_useable_account()
        account = self.db.accounts.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as state:
                state.return_value = 'SUCCESS'
                with mock.patch('anchor.tasks.get_task_results') as data:
                    data.return_value = str(account.get('_id'))
                    response = c.get(
                        '/lookup/servers/%s/host_server/csv' % uuid4().hex
                    )

        self.assertIn(
            (
                'Zone ID,Host ID,Server ID,Name,State,Flavor,Public IPs'
                ',Private IPs,Custom IPs,Reboot Window'
            ),
            response.data,
            'Incorrect headers found in response'
        )
        self.assertIn(
            (
                '"bf8a1d259e0fdec48a44140b7f5ffc3acdcd8e0a76ea57b0c84edbd3",'
                '"f0ab54576022b02c128b9516ef23a9947c73a8564ca79c7d1debb015",'
                '"11111111-2222-3333-4444-55566667777","test-server2","active"'
                ',"general1-1","163.163.163.163;2002:2002:2002:102:2002:2002:'
                '2002:2002","11.11.11.11","192.168.2.1","01-28-2014 @ 12:00:00'
                ' AM UTC - 01-28-2014 @ 03:00:00 AM UTC"'
            ),
            response.data,
            'Incorrect data returned for CSV'
        )

    def test_ui_csv_generate_cbs(self):
        self.setup_useable_cbs_account()
        account = self.db.accounts.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('anchor.tasks.check_task_state') as state:
                state.return_value = 'SUCCESS'
                with mock.patch('anchor.tasks.get_task_results') as data:
                    data.return_value = str(account.get('_id'))
                    response = c.get(
                        '/lookup/servers/%s/cbs_host/csv' % uuid4().hex
                    )

        self.assertIn(
            (
                'Host ID,Volume ID,Name,Status,Type,Size,Bootable,'
                'Attached To,Attached As,Availability Zone'
            ),
            response.data,
            'Incorrect headers found in response'
        )
        self.assertIn(
            (
                '"4a61be11-f557-40ea-a286-d01edaf72336","910cd151-799f-4203-'
                '9cc0-9ee60518c60d","test_cbs","available","SATA","100","True'
                '","","","nova"'
            ),
            response.data,
            'Incorrect data returned for CSV'
        )
