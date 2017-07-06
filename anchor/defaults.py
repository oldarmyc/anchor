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

from flask_cloudadmin.defaults import check_and_initialize
from config import config


def application_initialize(db, app):
    settings = db.settings.find_one()
    if settings is None:
        # Initialize admin first then setup application
        settings = check_and_initialize(app, db)

    if settings.get('application_set') is None:
        app.logger.debug(
            'Application settings are empty...initializing'
        )
        db.settings.update(
            {'_id': settings.get('_id')},
            {
                '$set': {
                    'application_set': True,
                    'app_title': 'Anchor',
                    'app_well': (
                        '<p class="lead">Anchor - Server Host Distribution</p>'
                        '<div>For improvements or suggestions '
                        'please go to GitHub and submit an '
                        '<a href="https://github.com/oldarmyc/'
                        'anchor/issues/new" class="tooltip-title" target="'
                        '_blank" title="Submit a GitHub issue">issue</a>'
                        '</div><div id="issue_feedback"></div>'
                    ),
                    'app_footer': (
                        'This site is not officially supported by Rackspace. '
                        'Source is available on <a href="https://github.com/'
                        'oldarmyc/anchor/" class="tooltip-title" '
                        'target="_blank" title="Anchor Repository">github</a>'
                    ),
                    'admins': [
                        {
                            'username': config.ADMIN_USERNAME,
                            'active': True,
                            'name': config.ADMIN_NAME,
                            'email': config.ADMIN_EMAIL
                        }
                    ],
                    'menu': [
                        {
                            'active': True,
                            'name': 'Server Breakdown',
                            'divider': False,
                            'db_name': 'breakdown',
                            'order': 1,
                            'parent': '',
                            'parent_order': 1,
                            'url': '/lookup',
                            'permissions': 'logged_in'
                        }, {
                            'active': True,
                            'name': 'Manage Admins',
                            'db_name': 'manage_admins',
                            'parent': 'system',
                            'url': '/admin/users/admins',
                            'parent_order': 2,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Data Centers',
                            'divider': False,
                            'db_name': 'manage_dcs',
                            'order': 3,
                            'parent': 'system',
                            'parent_order': 2,
                            'url': '/manage/regions',
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'General Settings',
                            'db_name': 'general_settings',
                            'parent': 'administrators',
                            'url': '/admin/general/',
                            'parent_order': 3,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Menu Settings',
                            'db_name': 'menu_settings',
                            'parent': 'administrators',
                            'url': '/admin/menu/',
                            'parent_order': 3,
                            'order': 2,
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Manage Roles',
                            'db_name': 'manage_roles',
                            'parent': 'administrators',
                            'url': '/admin/roles/',
                            'parent_order': 3,
                            'order': 3,
                            'permissions': 'administrators'
                        }
                    ],
                    'parent_menu': [
                        {
                            'slug': 'server_breakdown',
                            'name': 'Server Breakdown',
                            'order': 1
                        }, {
                            'slug': 'system',
                            'order': 2,
                            'name': 'System'
                        }, {
                            'slug': 'administrators',
                            'order': 3,
                            'name': 'Administrators'
                        }
                    ],
                    'roles': [
                        {
                            'active': True,
                            'name': 'Administrators',
                            'slug': 'administrators',
                            'perms': []
                        }, {
                            'active': True,
                            'name': 'Logged In',
                            'slug': 'logged_in',
                            'perms': [
                                '/lookup/servers/<task_id>',
                                '/lookup/servers/<task_id>/<lookup_type>/csv',
                                '/admin/logout/',
                                '/lookup/',
                                '/lookup/servers',
                                '/',
                            ]
                        }, {
                            'active': True,
                            'name': 'All',
                            'slug': 'all',
                            'perms': [
                                '/admin/login',
                                '/',
                            ]
                        }
                    ],
                    'regions': [
                        {
                            'abbreviation': 'DFW',
                            'active': True,
                            'name': 'Dallas'
                        }, {
                            'abbreviation': 'ORD',
                            'active': True,
                            'name': 'Chicago'
                        }, {
                            'abbreviation': 'IAD',
                            'active': True,
                            'name': 'Virginia'
                        }, {
                            'abbreviation': 'LON',
                            'active': True,
                            'name': 'London'
                        }, {
                            'abbreviation': 'HKG',
                            'active': True,
                            'name': 'Hong Kong'
                        }, {
                            'abbreviation': 'SYD',
                            'active': True,
                            'name': 'Sydney'
                        }
                    ]
                }
            }
        )
