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
from uuid import uuid4


import unittest
import urlparse
import re


class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.app, self.db = setup_application.create_app('True')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.client.get('/')

    def tearDown(self):
        self.db.sessions.remove()
        self.db.settings.remove()
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

    """ Datacenters Management - Perms Test """

    def test_item_manage_dcs_admin_perms(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Regions',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_item_manage_dcs_user_perms(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/regions')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )

    """ Functional Tests """

    def test_item_manage_dcs_add(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = self.db.settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'

    def test_item_manage_dcs_add_no_dcs(self):
        self.db.settings.update({}, {'$unset': {'regions': 1}})
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = self.db.settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'

    def test_item_manage_dcs_add_dupe(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Dallas',
                'abbreviation': 'DFW'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Duplicate region name',
            response.data,
            'Incorrect error message after add duplicate'
        )
        settings = self.db.settings.find_one()
        dcs = settings.get('regions')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after dupe add found %d instead of 1' % count
        )

    def test_item_manage_dcs_add_bad_data(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            data = {
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'There was a form validation error, please check '
                'the required values and try again.'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )

    def test_item_manage_dcs_remove(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/remove/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'DFW was removed successfully',
            response.data,
            'Incorrect flash message after remove'
        )
        settings = self.db.settings.find_one()
        dcs = settings.get('regions')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'DFW':
                count += 1

        self.assertEquals(
            count,
            0,
            'Incorrect count after remove, found %d instead of 0' % count
        )

    def test_item_verbs_deactivate(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/deactivate/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'DFW was deactivated successfully',
            response.data,
            'Incorrect flash message after deactivate'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        deactivated = False
        for region in regions:
            if region.get('abbreviation') == 'DFW':
                if not region.get('active'):
                    deactivated = True

        assert deactivated, 'Region was not deactivated'

    def test_item_verbs_activate(self):
        deactivate = 'DFW'
        self.db.settings.update(
            {
                'regions.abbreviation': deactivate
            }, {
                '$set': {
                    'regions.$.active': False
                }
            }
        )
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/activate/%s' % deactivate,
                follow_redirects=True
            )

        self.assertIn(
            'DFW was activated successfully',
            response.data,
            'Incorrect flash message after activate'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        activated = False
        for region in regions:
            if region.get('abbreviation') == deactivate:
                if region.get('active'):
                    activated = True

        assert activated, 'Region was not activated'

    def test_item_bad_key_for_actions(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/BAD_KEY/delete/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid data key given so no action taken',
            response.data,
            'Incorrect flash message after bad key'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('abbreviation') == 'DFW':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_item_bad_action_for_actions(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/BAD_ACTION/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid action given so no action taken',
            response.data,
            'Incorrect flash message after bad action'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('abbreviation') == 'DFW':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_item_bad_data_element_for_actions(self):
        before_settings = self.db.settings.find_one()
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/remove/BAD_DATA',
                follow_redirects=True
            )

        self.assertIn(
            'Bad_Data was not found so no action taken',
            response.data,
            'Incorrect flash message after bad data'
        )
        settings = self.db.settings.find_one()
        assert settings.get('regions') == before_settings.get('regions'), (
            'Incorrect number of regions found after bad delete'
        )
