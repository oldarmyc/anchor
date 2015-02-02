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

from flask import Flask, g
from inspect import getmembers, isfunction
from happymongo import HapPyMongo
from flask.ext import restful
from config import config
from adminbp import bp as admin_bp


import context_functions
import template_filters
import views
import re


def create_app(testing=None):
    app = Flask(__name__)
    if testing:
        config.TESTING = True
        m = re.search('_test', config.MONGO_DATABASE)
        if not m:
            config.MONGO_DATABASE = '%s_test' % config.MONGO_DATABASE

        config.ADMIN = 'rusty.shackelford'

    app.config.from_object(config)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    mongo, db = HapPyMongo(config)
    api = restful.Api(app)
    custom_filters = {
        name: function for name, function in getmembers(template_filters)
        if isfunction(function)
    }
    app.jinja_env.filters.update(custom_filters)
    app.context_processor(context_functions.utility_processor)

    @app.before_request
    def before_request():
        g.db = db

    views.BaseView.register(app)
    views.LookupView.register(app)
    views.ManagementView.register(app)

    api.add_resource(
        views.AccountAPI,
        '/account/<int:account_id>',
        endpoint='account'
    )
    api.add_resource(
        views.ServerAPI,
        '/account/<int:account_id>/server/<server_id>',
        endpoint='server'
    )
    return app, db
