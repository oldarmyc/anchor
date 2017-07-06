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

"""
    The values are set to run the application either on localhost or
    within docker using docker-compose. If you would like to run it
    a different waay fell free to change the appropriate values.
"""

import os


try:
    MONGO_HOST = os.environ['ANCHOR_DB_1_PORT_27017_TCP_ADDR']
except:
    MONGO_HOST = 'localhost'

MONGO_PORT = 27017
MONGO_KWARGS = {'tz_aware': True}
MONGO_DATABASE = 'anchor'


ADMIN_USERNAME = 'cloud_username'
ADMIN_NAME = 'Admin Full Name'
ADMIN_EMAIL = 'Admin email'


SECRET_KEY = 'secret_key_for_cookie'
