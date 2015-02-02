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

from flask import g, current_app


def check_and_initialize():
    settings = g.db.settings.find_one()
    forms = g.db.forms.find_one()
    if settings is None:
        current_app.logger.debug('Settings are empty...initializing')
        g.db.settings.insert(
            {
                'application_title': current_app.config.get(
                    'APP_NAME', 'Anchor'
                ),
                'application_email': current_app.config.get('APP_EMAIL'),
                'application_well': (
                    '<p class="lead">Anchor - Server Host Distribution</p>'
                    '<div>For improvements or suggestions '
                    'please go to GitHub and submit an '
                    '<a href="https://github.com/rackerlabs/'
                    'anchor/issues/new" class="tooltip-title" '
                    'target="_blank" title="Submit a GitHub issue">issue</a>'
                    '</div><div id="issue_feedback"></div>'
                ),
                'application_footer': (
                    'This site is not officially supported by Rackspace. '
                    'Source is available on <a href="https://github.com/'
                    'rackerlabs/anchor/" class="tooltip-title" '
                    'target="_blank" title="Anchor Repository">github</a>'
                ),
                'administrators': [
                    {
                        'admin': current_app.config.get(
                            'ADMIN', 'oldarmyc'
                        ),
                        'admin_name': current_app.config.get(
                            'ADMIN_NAME', 'Dave Kludt'
                        )
                    }
                ],
                'menu': [
                    {
                        'active': True,
                        'display_name': 'Server Breakdown',
                        'divider': False,
                        'name': 'breakdown',
                        'order': 1,
                        'parent': '',
                        'parent_order': 1,
                        'url': '/lookup',
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Manage Admins',
                        'name': 'manage_admins',
                        'parent': 'system',
                        'url': '/admin/settings/admins',
                        'parent_order': 2,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/engine/setup',
                        'display_name': 'Manage Engine',
                        'name': 'engine_setup',
                        'parent': 'system',
                        'active': True,
                        'parent_order': 2,
                        'divider': True,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Data Centers',
                        'divider': False,
                        'name': 'manage_dcs',
                        'order': 3,
                        'parent': 'system',
                        'parent_order': 2,
                        'url': '/manage/regions',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'General Settings',
                        'name': 'general_settings',
                        'parent': 'administrators',
                        'url': '/admin/settings/general',
                        'parent_order': 3,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Menu Settings',
                        'name': 'menu_settings',
                        'parent': 'administrators',
                        'url': '/admin/settings/menu',
                        'parent_order': 3,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Roles',
                        'name': 'manage_roles',
                        'parent': 'administrators',
                        'url': '/admin/settings/roles',
                        'parent_order': 3,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/forms',
                        'display_name': 'Manage Forms',
                        'name': 'manage_forms',
                        'parent': 'administrators',
                        'active': True,
                        'parent_order': 3,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }
                ],
                'top_level_menu': [
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
                        'display_name': 'Administrators',
                        'name': 'administrators',
                        'perms': []
                    }, {
                        'active': True,
                        'display_name': 'Logged In',
                        'name': 'logged_in',
                        'perms': [
                            '/lookup/servers/<task_id>',
                            '/admin/logout/',
                            '/lookup/',
                            '/lookup/servers',
                            '/',
                        ]
                    }, {
                        'active': True,
                        'display_name': 'All',
                        'name': 'all',
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
        )
        settings = g.db.settings.find_one({}, {'_id': 0})

    if forms is None:
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Login Form',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Username:',
                        'name': 'username',
                        'order': 1,
                        'required': True
                    }, {
                        'default_value': '',
                        'field_type': 'PasswordField',
                        'field_choices': '',
                        'name': 'password',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 2,
                        'label': 'API Key:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Submit'
                    }
                ],
                'name': 'login_form',
                'submission_url': '/admin/login',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Manage Administrators',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'administrator',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 1,
                        'label': 'Username:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'full_name',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 2,
                        'label': 'Full Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'admin',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Add Admin'
                    }
                ],
                'name': 'add_administrator',
                'submission_url': '/admin/settings/admins',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Manage Roles',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'display_name',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 1,
                        'label': 'Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'status',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 2,
                        'label': 'Active?:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Submit'
                    }
                ],
                'name': 'manage_roles',
                'submission_url': '/admin/settings/roles',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Suggestions',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'suggestion',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 1,
                        'label': 'Suggestion:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 2,
                        'label': 'Send'
                    }
                ],
                'name': 'suggestion_form',
                'submission_url': '/admin/submit_feedback',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'General Settings',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Application Title:',
                        'name': 'application_title',
                        'order': 1,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Application Email:',
                        'name': 'application_email',
                        'order': 2,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextAreaField',
                        'label': 'Application Intro:',
                        'name': 'application_well',
                        'order': 3,
                        'required': False,
                        'style_id': ''
                    }, {
                        'default_value': '',
                        'field_type': 'TextAreaField',
                        'field_choices': '',
                        'name': 'application_footer',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 4,
                        'label': 'Application Footer:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'settings',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 5,
                        'label': 'Apply Settings'
                    }
                ],
                'name': 'application_settings',
                'submission_url': '/admin/settings/general',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Menu Items',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'SelectField',
                        'label': 'Parent Menu:',
                        'name': 'parent_menu',
                        'order': 1,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'New Parent:',
                        'name': 'new_parent',
                        'order': 2,
                        'required': False,
                        'style_id': ''
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'db_name',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 3,
                        'label': 'DB Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'menu_display_name',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 4,
                        'label': 'Display Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'menu_item_url',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 5,
                        'label': 'URL:'
                    }, {
                        'default_value': '',
                        'field_type': 'SelectField',
                        'field_choices': '',
                        'name': 'menu_permissions',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 6,
                        'label': 'Permissions:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'menu_item_status',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 7,
                        'label': 'Active?:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'menu_item_divider',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 8,
                        'label': 'Add Divider?:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'menu',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 9,
                        'label': 'Submit'
                    }
                ],
                'name': 'menu_items_form',
                'submission_url': '/admin/settings/menu',
                'system_form': True
            }
        )

    return settings
