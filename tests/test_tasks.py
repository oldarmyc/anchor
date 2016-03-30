# Copyright 2014 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from anchor import setup_application
from datetime import datetime
from dateutil.relativedelta import relativedelta
from uuid import uuid4


import unittest
import anchor
import uuid
import json
import re
import mock


class AnchorCeleryTests(unittest.TestCase):
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
        sess['ddi'] = '654846'
        sess['cloud_token'] = uuid4().hex

    def setup_admin_login(self, sess):
        sess['username'] = 'oldarmyc'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'administrators'
        sess['_permanent'] = True
        sess['ddi'] = '654846'
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
                    'RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId': (
                        'bf8a1d259e0fdec48a44140b7f5f'
                        'fc3acdcd8e0a76ea57b0c84edbd3'
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
                },
            ],
            'token': 'd6ffb5c691a644a4b527f8ddc64c180f',
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

    def setup_cloud_server_details_single_return(self):
        return {
            'server': {
                'OS-EXT-STS:task_state': None,
                'addresses': {
                    'public': [
                        {
                            'version': 4,
                            'addr': '104.104.104.104'
                        }, {
                            'version': 6,
                            'addr': '2001:2001:2001:104:2001:2001:2001:2001'
                        }
                    ],
                    'private': [
                        {
                            'version': 4,
                            'addr': '10.10.10.10'
                        }
                    ]
                },
                'links': [
                    {
                        'href': (
                            'https://iad.servers.api.rackspacecloud.com/v2/123'
                            '456/servers/11111111-2222-3333-4444-55555555555'
                        ),
                        'rel': 'self'
                    }, {
                        'href': (
                            'https://iad.servers.api.rackspacecloud.com/123'
                            '456/servers/11111111-2222-3333-4444-55555555555'
                        ),
                        'rel': 'bookmark'
                    }
                ],
                'image': {
                    'id': '99999999-8888-7777-6666-555555555555',
                    'links': [
                        {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.com/12'
                                '3456/images/99999999-8888-7777-6666-'
                                '555555555555'
                            ),
                            'rel': 'bookmark'
                        }
                    ]
                },
                'OS-EXT-STS:vm_state': 'active',
                'flavor': {
                    'id': 'performance1-2',
                    'links': [
                        {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.com/'
                                '123456/flavors/performance1-2'
                            ),
                            'rel': 'bookmark'
                        }
                    ]
                },
                'id': '11111111-2222-3333-4444-55555555555',
                'user_id': '284275',
                'OS-DCF:diskConfig': 'MANUAL',
                'accessIPv4': '104.104.104.104',
                'accessIPv6': '2001:2001:2001:104:2001:2001:2001:2001',
                'progress': 100,
                'OS-EXT-STS:power_state': 1,
                'config_drive': '',
                'status': 'ACTIVE',
                'updated': '2014-12-04T16:49:37Z',
                'hostId': (
                    '16cde3191df1e6c9fa4dad65eacd4dc7c90d60bca3589ac48f55aae8'
                ),
                'RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId': (
                    'bf8a1d259e0fdec48a44140b7f5f'
                    'fc3acdcd8e0a76ea57b0c84edbd3'
                ),
                'name': 'test_server_awesome',
                'created': '2015-01-01T16:06:05Z',
                'tenant_id': '123456',
            }
        }

    def setup_servers_details_return(self):
        return {
            'servers': [
                {
                    'OS-EXT-STS:task_state': None,
                    'addresses': {
                        'public': [
                            {
                                'version': 4,
                                'addr': '104.104.104.104'
                            }, {
                                'version': 4,
                                'addr': '11.11.11.11'
                            }, {
                                'version': 6,
                                'addr': (
                                    '2001:2001:2001:104:2001:2001:2001:2001'
                                )
                            }
                        ],
                        'private': [
                            {
                                'version': 4,
                                'addr': '10.10.10.10'
                            }
                        ]
                    },
                    'links': [
                        {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.com'
                                '/v2/123456/servers/11111111-2222-3333-4444'
                                '-55555555555'
                            ),
                            'rel': 'self'
                        }, {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.'
                                'com/123456/servers/11111111-2222-3333-4444-'
                                '55555555555'
                            ),
                            'rel': 'bookmark'
                        }
                    ],
                    'image': {
                        'id': '99999999-8888-7777-6666-555555555555',
                        'links': [
                            {
                                'href': (
                                    'https://iad.servers.api.rackspacecloud.'
                                    'com/123456/images/99999999-8888-7777-6666'
                                    '-555555555555'
                                ),
                                'rel': 'bookmark'
                            }
                        ]
                    },
                    'OS-EXT-STS:vm_state': 'active',
                    'flavor': {
                        'id': 'performance1-2',
                        'links': [
                            {
                                'href': (
                                    'https://iad.servers.api.rackspacecloud.'
                                    'com/123456/flavors/performance1-2'
                                ),
                                'rel': 'bookmark'
                            }
                        ]
                    },
                    'id': '11111111-2222-3333-4444-55555555555',
                    'user_id': '284275',
                    'OS-DCF:diskConfig': 'MANUAL',
                    'accessIPv4': '104.130.6.172',
                    'accessIPv6': '2001:4802:7802:104:c573:b34f:8ae3:abd0',
                    'progress': 100,
                    'OS-EXT-STS:power_state': 1,
                    'config_drive': '',
                    'status': 'ACTIVE',
                    'updated': '2014-12-04T16:49:37Z',
                    'hostId': (
                        '16cde3191df1e6c9fa4dad65eacd4dc7'
                        'c90d60bca3589ac48f55aae8'
                    ),
                    'RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId': (
                        'bf8a1d259e0fdec48a44140b7f5f'
                        'fc3acdcd8e0a76ea57b0c84edbd3'
                    ),
                    'name': 'test_server_awesome',
                    'created': '2015-01-01T16:06:05Z',
                    'tenant_id': '123456',
                }, {
                    'OS-EXT-STS:task_state': None,
                    'addresses': {
                        'public': [
                            {
                                'version': 4,
                                'addr': '104.104.104.104'
                            }, {
                                'version': 6,
                                'addr': (
                                    '2020:2020:2020:104:2020:2020:2020:2020'
                                )
                            }
                        ],
                        'private': [
                            {
                                'version': 4,
                                'addr': '10.11.11.11'
                            }
                        ]
                    },
                    'links': [
                        {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.com'
                                '/v2/123456/servers/11111111-2222-3333-4444'
                                '-55555555555'
                            ),
                            'rel': 'self'
                        }, {
                            'href': (
                                'https://iad.servers.api.rackspacecloud.'
                                'com/123456/servers/11111111-2222-3333-4444-'
                                '55555555555'
                            ),
                            'rel': 'bookmark'
                        }
                    ],
                    'image': {
                        'id': '99999999-8888-7777-6666-555555555555',
                        'links': [
                            {
                                'href': (
                                    'https://iad.servers.api.rackspacecloud.'
                                    'com/123456/images/99999999-8888-7777-6666'
                                    '-555555555555'
                                ),
                                'rel': 'bookmark'
                            }
                        ]
                    },
                    'OS-EXT-STS:vm_state': 'active',
                    'flavor': {
                        'id': 'performance1-2',
                        'links': [
                            {
                                'href': (
                                    'https://iad.servers.api.rackspacecloud.'
                                    'com/123456/flavors/performance1-2'
                                ),
                                'rel': 'bookmark'
                            }
                        ]
                    },
                    'id': '22222222-3333-4444-5555-66666666666',
                    'user_id': '284275',
                    'OS-DCF:diskConfig': 'MANUAL',
                    'accessIPv4': '104.130.130.130',
                    'accessIPv6': '2020:2020:2020:104:2020:2020:2020:2020',
                    'progress': 100,
                    'OS-EXT-STS:power_state': 1,
                    'config_drive': '',
                    'status': 'ACTIVE',
                    'updated': '2014-12-04T16:49:37Z',
                    'hostId': (
                        'b4631f368e35d06bef81053b66e5'
                        '40c95836fc0eb796176dc624a2cd'
                    ),
                    'RAX-PUBLIC-IP-ZONE-ID:publicIPZoneId': (
                        'bf8a1d259e0fdec48a44140b7f5f'
                        'fc3acdcd8e0a76ea57b0c84edbd3'
                    ),
                    'name': 'test_server',
                    'created': '2015-01-01T16:06:05Z',
                    'tenant_id': '123456',
                }

            ]
        }

    def setup_cbs_details_return(self):
        return {
            "volumes": [
                {
                    "status": "in-use",
                    "display_name": "mc.backup",
                    "availability_zone": "nova",
                    "bootable": True,
                    "encrypted": False,
                    "created_at": "2015-12-17T12:29:15.000000",
                    "multiattach": False,
                    "display_description": None,
                    "volume_type": "SATA",
                    "snapshot_id": None,
                    "size": 80,
                    "id": "910cd151-799f-4203-9cc0-9ee60518c60d",
                    "attachments": [
                        {
                            "server_id": (
                                "161e2453-a5ba-49d8-a461-ce0e51bdcf52"
                            ),
                            "volume_id": (
                                "910cd151-799f-4203-9cc0-9ee60518c60d"
                            ),
                            "device": "/dev/xvda",
                            "id": "910cd151-799f-4203-9cc0-9ee60518c60d"
                        }
                    ],
                    "metadata": {
                        "storage-node": "497d4575-2e0a-4375-88db-f6f6dfb8726c"
                    }
                }, {
                    "status": "available",
                    "display_name": "drone.backup",
                    "attachments": [],
                    "availability_zone": "nova",
                    "bootable": True,
                    "encrypted": False,
                    "created_at": "2015-12-17T12:26:46.000000",
                    "multiattach": False,
                    "display_description": None,
                    "volume_type": "SATA",
                    "snapshot_id": None,
                    "size": 75,
                    "id": "e7408004-5991-4899-941a-8d2970d77551",
                    "metadata": {
                        "storage-node": "497d4575-2e0a-4375-88db-f6f6dfb8726c"
                    }
                }
            ]
        }

    def setup_fg_servers_details_return(self):
        return {
            'servers': [
                {
                    'status': 'ACTIVE',
                    'hostId': 'caf8f03bb31dbd2d6367615709e853cf',
                    'name': 'test-server',
                    'metadata': {},
                    'imageId': 122,
                    'progress': 100,
                    'flavorId': 1,
                    'id': 12345678,
                    'addresses': {
                        'public': [
                            '111.111.111.111'
                        ],
                        'private': [
                            '11.11.11.11'
                        ]
                    }
                }
            ]
        }

    """ Tests """

    def test_celery_add_server_to_cache(self):
        self.setup_useable_account()
        account_data = self.db.accounts.find_one()
        cloud_return = self.setup_cloud_server_details_single_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(cloud_return)
                    task = self.tasks.check_add_server_to_cache(
                        uuid.uuid4().hex,
                        'iad',
                        '123456',
                        '11111111-2222-3333-4444-55555555555',
                        account_data
                    )
                    assert not task, (
                        'Expecting false to be returned, but got true instead'
                    )

        updated_account = self.db.accounts.find_one()
        self.assertEquals(
            len(updated_account.get('servers')),
            len(account_data.get('servers')) + 1,
            'Expected an additional server added to the cache'
        )

    def test_celery_add_server_to_cache_bad_uuid(self):
        self.setup_useable_account()
        account_data = self.db.accounts.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = None
                    task = self.tasks.check_add_server_to_cache(
                        uuid.uuid4().hex,
                        'iad',
                        '123456',
                        '11111111-2222-3333-4444-55555555555',
                        account_data
                    )
                    assert task is None, (
                        'Expecting task to return None instead of a value'
                    )

        updated_account = self.db.accounts.find_one()
        self.assertEquals(
            account_data,
            updated_account,
            'Data was changed and should not have been from the original data'
        )

    def test_celery_generate_data_host(self):
        cloud_return = self.setup_servers_details_return()
        fg_return = self.setup_fg_servers_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_server_list') as ng:
                    ng.return_value = cloud_return.get('servers')
                    with mock.patch(
                        'anchor.tasks.generate_first_gen_server_list'
                    ) as fg:
                        fg.return_value = fg_return.get('servers')
                        task = self.tasks.generate_account_object_list(
                            '123456',
                            uuid.uuid4().hex,
                            'iad',
                            'host_server'
                        )

        assert task is None, 'Data returned when it should have been stored'
        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('host_servers')),
            3,
            'Host servers should have three IDs'
        )
        self.assertEquals(
            len(account.get('servers')),
            3,
            'Servers should have three stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'

    def test_celery_generate_data_zone(self):
        cloud_return = self.setup_servers_details_return()
        fg_return = self.setup_fg_servers_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_server_list') as ng:
                    ng.return_value = cloud_return.get('servers')
                    with mock.patch(
                        'anchor.tasks.generate_first_gen_server_list'
                    ) as fg:
                        fg.return_value = fg_return.get('servers')
                        task = self.tasks.generate_account_object_list(
                            '123456',
                            uuid.uuid4().hex,
                            'iad',
                            'public_ip_zone'
                        )

        assert task is None, 'Data returned when it should have been stored'
        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('public_zones')),
            1,
            'Zones should have one ID'
        )
        self.assertEquals(
            len(account.get('servers')),
            2,
            'Servers should have two stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'

    def test_celery_generate_data_for_web(self):
        cloud_return = self.setup_servers_details_return()
        fg_return = self.setup_fg_servers_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_server_list') as ng:
                    ng.return_value = cloud_return.get('servers')
                    with mock.patch(
                        'anchor.tasks.generate_first_gen_server_list'
                    ) as fg:
                        fg.return_value = fg_return.get('servers')
                        task = self.tasks.generate_account_object_list(
                            '123456',
                            uuid.uuid4().hex,
                            'iad',
                            'host_server',
                            True
                        )

        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('host_servers')),
            3,
            'Host servers should have three IDs'
        )
        self.assertEquals(
            len(account.get('servers')),
            3,
            'Servers should have three stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'
        assert str(account.get('_id')) == task, (
            'ID returned was not correct for the entry found'
        )

    def test_celery_generate_data_for_web_zones(self):
        cloud_return = self.setup_servers_details_return()
        fg_return = self.setup_fg_servers_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_server_list') as ng:
                    ng.return_value = cloud_return.get('servers')
                    with mock.patch(
                        'anchor.tasks.generate_first_gen_server_list'
                    ) as fg:
                        fg.return_value = fg_return.get('servers')
                        task = self.tasks.generate_account_object_list(
                            '123456',
                            uuid.uuid4().hex,
                            'iad',
                            'public_ip_zone',
                            True
                        )

        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('public_zones')),
            1,
            'Host servers should have three IDs'
        )
        self.assertEquals(
            len(account.get('servers')),
            2,
            'Servers should have three stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'
        assert str(account.get('_id')) == task, (
            'ID returned was not correct for the entry found'
        )

    def test_celery_generate_data_requests_exception(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    error = patched_get.side_effect = ValueError
                    patched_get.return_value = error
                    self.tasks.generate_account_object_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad',
                        'host_server'
                    )

        account = self.db.accounts.find_one()
        assert account, (
            'Account data was not found when it should have been'
        )
        assert len(account.get('host_servers')) == 0, (
            'Host servers listed when there should not have been'
        )
        assert len(account.get('servers')) == 0, (
            'Host servers listed when there should not have been'
        )

    def test_celery_check_token(self):
        cloud_return = {
            'users': [
                {
                    'RAX-AUTH:domainId': '123456',
                    'username': 'bob.richards',
                    'enabled': True,
                    'email': 'bob.richards@rackspace.com',
                    'RAX-AUTH:defaultRegion': 'ORD',
                    'RAX-AUTH:multiFactorEnabled': False,
                    'id': '11111111'
                }
            ]
        }
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(cloud_return)
                    patched_get.return_value._status_code = 200
                    task = self.tasks.check_auth_token(
                        '123456',
                        uuid.uuid4().hex,
                    )

        assert task is True, 'Incorrect status returned with check'

    def test_celery_check_token_error(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    error = patched_get.side_effect = ValueError
                    patched_get.return_value = error
                    task = self.tasks.check_auth_token(
                        '123456',
                        uuid.uuid4().hex,
                    )

        assert task is False, 'Incorrect status returned with check'

    def test_celery_generate_data_no_servers(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        {'servers': []}
                    )
                    self.tasks.generate_account_object_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad',
                        'host_server'
                    )

        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('host_servers')),
            0,
            'Host servers should have 0 IDs'
        )
        self.assertEquals(
            len(account.get('servers')),
            0,
            'Servers should have 0 stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'

    """ CBS """

    def test_celery_generate_cbs_data_for_web(self):
        cloud_return = self.setup_cbs_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_volume_list') as cbs:
                    cbs.return_value = cloud_return.get('volumes')
                    task = self.tasks.generate_account_object_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad',
                        'cbs_host',
                        True
                    )

        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('cbs_hosts')),
            1,
            'CBS Hosts should have one ID'
        )
        self.assertEquals(
            len(account.get('volumes')),
            2,
            'Volumes should have two stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'
        assert str(account.get('_id')) == task, (
            'ID returned was not correct for the entry found'
        )

    def test_celery_generate_data_cbs_host(self):
        cloud_return = self.setup_cbs_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('anchor.tasks.generate_volume_list') as cbs:
                    cbs.return_value = cloud_return.get('volumes')
                    task = self.tasks.generate_account_object_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad',
                        'cbs_host'
                    )

        assert task is None, 'Data returned when it should have been stored'
        account = self.db.accounts.find_one()
        self.assertEquals(
            len(account.get('cbs_hosts')),
            1,
            'CBS Hosts should have one ID'
        )
        self.assertEquals(
            len(account.get('volumes')),
            2,
            'Volumes should have two stored in the data'
        )
        assert account.get('region') == 'iad', 'Incorrect region stored'

    def test_celery_generate_volume_list(self):
        cloud_return = self.setup_cbs_details_return()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(cloud_return)
                    task = self.tasks.generate_volume_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad'
                    )

        self.assertEquals(
            len(task),
            2,
            'Did not get expected return of two volumes'
        )

    def test_celery_generate_volume_list_no_return(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'anchor.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = None
                    task = self.tasks.generate_volume_list(
                        '123456',
                        uuid.uuid4().hex,
                        'iad'
                    )

        assert task == [], 'Got unexpected values on bad data return'
