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

from flask import (
    g, render_template, request, redirect, url_for, flash, jsonify, session,
    make_response
)
from flask_cloudadmin.decorators import check_perms
from flask_classy import FlaskView, route
from flask_restful import Resource
from bson.objectid import ObjectId
from models import Region


import forms
import tasks
import helper


class BaseView(FlaskView):
    route_base = '/'

    def index(self):
        if session and session.get('token'):
            return redirect('/lookup/')

        return render_template('index.html')


class LookupView(FlaskView):
    route_base = '/lookup'
    decorators = [check_perms(request)]

    def index(self):
        form = forms.DCSelect()
        form.data_center.choices = helper.gather_dc_choices()
        return render_template('lookup.html', form=form)

    @route('/servers', methods=['POST'])
    @route('/servers/<task_id>')
    def gather_servers(self, task_id=None):
        if request.method == 'POST':
            task = tasks.generate_account_object_list.delay(
                session.get('ddi'),
                session.get('token'),
                request.json.get('data_center'),
                request.json.get('lookup_type'),
                True
            )
            return jsonify(task_id=task.task_id)
        else:
            status = tasks.check_task_state(task_id)
            if status == 'PENDING':
                return jsonify(state=status, code=204)
            elif status == 'SUCCESS':
                account_id = tasks.get_task_results(task_id)
                account_data = g.db.accounts.find_one(
                    {'_id': ObjectId(account_id)}
                )
                mismatch = False
                if account_data.get('lookup_type') == 'host_server':
                    if (
                        len(account_data.get('servers')) !=
                        len(account_data.get('host_servers'))
                    ):
                        mismatch = True

                elif account_data.get('lookup_type') == 'cbs_host':
                    if (
                        len(account_data.get('volumes')) !=
                        len(account_data.get('cbs_hosts'))
                    ):
                        mismatch = True

                return render_template(
                    '_breakdown.html',
                    data=account_data,
                    mismatch=mismatch,
                    task_id=task_id
                )

            return jsonify(state=status, code=500)

    @route('/servers/<task_id>/<lookup_type>/csv')
    def generate_server_csv(self, task_id, lookup_type):
        status = tasks.check_task_state(task_id)
        if status == 'SUCCESS':
            account_id = tasks.get_task_results(task_id)
            account_data = g.db.accounts.find_one(
                {'_id': ObjectId(account_id)}
            )
            if lookup_type == 'cbs_host':
                use_template = 'cbs.csv'
            else:
                use_template = 'servers.csv'

            template = render_template(
                use_template,
                lookup_type=lookup_type,
                data=account_data
            )
            response = make_response(template)
            response.headers['Content-Type'] = 'application/csv'
            response.headers['Content-Disposition'] = (
                'attachment; filename="%s"' % use_template
            )
            return response
        else:
            flash(
                'Task has not completed yet, so no CSV can be generated',
                'warning'
            )
            return redirect(url_for('BaseView:index'))


class ManagementView(FlaskView):
    route_base = '/manage'
    decorators = [check_perms(request)]

    @route('/regions', methods=['GET', 'POST'])
    def define_available_regions(self):
        settings = g.db.settings.find_one()
        form = forms.RegionSet()
        if request.method == 'POST' and form.validate_on_submit():
            region = Region(request.form)
            if region:
                action, data = '$push', region.__dict__
                if not settings.get('regions'):
                    action, data = '$set', [data]

                g.db.settings.update(
                    {
                        '_id': settings.get('_id')
                    }, {
                        action: {
                            'regions': data
                        }
                    }
                )
                flash('Region successfully added to system', 'success')
                return redirect(
                    url_for(
                        'ManagementView:define_available_regions'
                    )
                )
        else:
            if request.method == 'POST':
                flash(
                    'There was a form validation error, please '
                    'check the required values and try again.',
                    'error'
                )

        return render_template(
            'manage/manage_regions.html',
            form=form,
            settings=settings
        )

    @route('/<key>/<action>/<value>')
    def managed_data_actions(self, key, action, value):
        actions = ['activate', 'deactivate', 'remove']
        maps = {
            'regions': {
                'search': 'regions.abbreviation',
                'status': 'regions.$.active',
                'redirect': '/manage/regions',
                'flash_title': value.upper()
            }
        }
        if maps.get(key):
            options = maps.get(key)
            if action in actions:
                found = g.db.settings.find_one(
                    {
                        options.get('search'): value
                    }
                )
                if found:
                    if action == 'remove':
                        keys = options.get('search').split('.')
                        change = {'$pull': {keys[0]: {keys[1]: value}}}
                    else:
                        if action == 'activate':
                            change = {'$set': {options.get('status'): True}}
                        elif action == 'deactivate':
                            change = {'$set': {options.get('status'): False}}

                    g.db.settings.update(
                        {options.get('search'): value},
                        change
                    )
                    flash(
                        '%s was %sd successfully' % (
                            options.get('flash_title'),
                            action
                        ),
                        'success'
                    )
                else:
                    flash(
                        '%s was not found so no action taken' % value.title(),
                        'error'
                    )
            else:
                flash('Invalid action given so no action taken', 'error')
            return redirect(options.get('redirect'))
        else:
            flash('Invalid data key given so no action taken', 'error')
            return redirect('/')


""" API Classes """


class TaskAPI(Resource):
    def get(self, task_id):
        return jsonify(task_status=tasks.check_task_state(task_id))


class AccountAPI(Resource):
    def get(self, account_id, region):
        token = tasks.check_auth_token(
            account_id,
            helper.check_for_token(request)
        )
        if not token:
            return helper.generate_error(
                'No authentication token provided, '
                'or authentication was unsuccessful',
                401
            )

        account_data = g.db.accounts.find_one(
            {
                'account_number': account_id,
                'region': region,
                'cache_expiration': {
                    '$gte': helper.get_timestamp()
                }
            }, {
                '_id': 0,
                'servers': 1
            }
        )
        return jsonify(data=account_data)

    def post(self, account_id, region):
        token = tasks.check_auth_token(
            account_id,
            helper.check_for_token(request)
        )
        if not token:
            return helper.generate_error(
                'No authentication token provided, '
                'or authentication was unsuccessful',
                401
            )

        task_id = tasks.generate_account_object_list.delay(
            account_id,
            token,
            region,
            'host_server'
        )
        return jsonify(task_id=str(task_id))

    def delete(self, account_id, region):
        try:
            g.db.accounts.remove(
                {
                    'account_number': account_id,
                    'region': region
                }
            )
            return 'Request was successful', 204
        except:
            return helper.generate_error(
                'An error occured that prevented the delete to complete',
                500
            )


class ServerAPI(Resource):
    def put(self, account_id, region, server_id):
        """
            Update the account data with the new server, and return True
            or False as to whether the server is by itself on the hypervisor
            Save the data into cache as either way it will still reside on a
            host that has another server or by itself. The answer will be
            correct either way
        """
        token = tasks.check_auth_token(
            account_id,
            helper.check_for_token(request)
        )
        if not token:
            return helper.generate_error(
                'No authentication token provided, '
                'or authentication was unsuccessful',
                401
            )

        account_data = g.db.accounts.find_one(
            {
                'account_number': account_id,
                'region': region,
                'cache_expiration': {'$gte': helper.get_timestamp()}
            }
        )
        if not account_data:
            return helper.generate_error(
                'You must initialize before checking a server',
                400
            )

        check_server = g.db.accounts.find_one({'servers.id': server_id})
        if check_server:
            return helper.generate_error(
                'Server has been catalogued already',
                400
            )

        response = tasks.check_add_server_to_cache(
            token,
            region,
            account_id,
            server_id,
            account_data
        )
        return jsonify(duplicate=response)

    def get(self, account_id, region, server_id):
        token = tasks.check_auth_token(
            account_id,
            helper.check_for_token(request)
        )
        if not token:
            return helper.generate_error(
                'No authentication token provided, '
                'or authentication was unsuccessful',
                401
            )

        server_data = g.db.accounts.find_one(
            {
                'account_number': account_id,
                'region': region,
                'servers.id': server_id
            }, {
                'servers.$': 1
            }
        )
        if not server_data:
            return helper.generate_error(
                'Server was not found',
                404
            )

        check_host = server_data.get('servers')[0].get('host_id')
        host_servers = helper.generate_servers_on_same_host(
            account_id,
            region,
            check_host
        )
        duplicate = False
        if host_servers is not None and len(host_servers) > 1:
            duplicate = True

        return jsonify(duplicate=duplicate, host_servers=host_servers)
