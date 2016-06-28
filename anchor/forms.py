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

from wtforms import fields, validators
from flask_wtf import Form
from flask import g


class DynamicSelectField(fields.SelectField):
    def pre_validate(self, form):
        """
        Overrides pre validation since all choices are static
        Adding elements dynamically requires this

        """
        pass


class RegionSet(Form):
    name = fields.TextField('Name:', validators=[validators.required()])
    abbreviation = fields.TextField(
        'Abbreviation:',
        validators=[validators.required()]
    )
    active = fields.BooleanField(default=True)
    submit = fields.SubmitField()

    def validate_name(self, field):
        found_region = g.db.settings.find_one(
            {'regions.name': field.data.title()},
            {'regions.$': 1}
        )
        if found_region:
            raise validators.ValidationError('Duplicate region name')

    def validate_abbreviation(self, field):
        found_region = g.db.settings.find_one(
            {'regions.abbreviation': field.data.upper()},
            {'regions.$': 1}
        )
        if found_region:
            raise validators.ValidationError('Duplicate abbreviation')


class DCSelect(Form):
    data_center = DynamicSelectField('Select Data Center:', choices=[('', '')])
    lookup_type = fields.SelectField(
        'Breakdown:',
        choices=[
            ('host_server', 'Compute Hosts'),
            ('public_ip_zone', 'Compute Zones'),
            ('cbs_host', 'CBS Hosts'),
        ],
        default='host_server'
    )
