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
from datetime import datetime
from dateutil import tz


UTC = tz.tzutc()


class Region:
    def __init__(self, data):
        self.name = data.get('name').title()
        self.abbreviation = data.get('abbreviation').upper()
        self.active = bool(data.get('active'))


class Account:
    def __init__(self, data):
        self.account_number = data.get('account_number')
        self.cache_expiration = self.set_expiration()
        self.host_servers = data.get('host_servers')
        self.public_zones = data.get('public_zones')
        self.region = data.get('region').lower()
        self.servers = data.get('servers')
        self.volumes = data.get('volumes')
        self.cbs_hosts = data.get('cbs_hosts')
        self.lookup_type = data.get('lookup_type')

    def set_expiration(self):
        return datetime.now(UTC) + relativedelta(days=1)
