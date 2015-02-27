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

from dateutil.parser import parse


import helper
import re


def utility_processor():
    def unslug(string):
        return re.sub('_', ' ', string)

    def display_date(data):
        if data:
            temp = parse(data)
            return temp.strftime('%m-%d-%Y @ %R %Z')
        return

    def generate_server_age(data):
        duration = '-'
        create = parse(data)
        diff = helper.get_timestamp() - create
        if diff.days > 0:
            diff_str = re.sub('\sdays?,\s', ':', str(diff))
        else:
            diff_str = '0:%s' % str(diff)

        elapsed_str = re.split('\W', diff_str)
        if len(elapsed_str) > 0:
            duration = '%s days %s hours %s minutes %s seconds' % (
                elapsed_str[0],
                elapsed_str[1],
                elapsed_str[2],
                elapsed_str[3]
            )
        return duration

    def get_formatted_server_list(data):
        return helper.format_server_list_for_web(data)

    def process_reboot_data(data):
        if data:
            temp = data.split(';')
            dates = [
                parse(x).strftime(
                    '%m-%d-%Y @ %r %Z'
                ) for x in temp if x is not None
            ]
            return ' - '.join(dates)
        return '-'

    return dict(
        unslug=unslug,
        display_date=display_date,
        get_formatted_server_list=get_formatted_server_list,
        generate_server_age=generate_server_age,
        process_reboot_data=process_reboot_data
    )
