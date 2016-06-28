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
    If you are running the application within docker using the provided
    Dockerfile and docker-compose then you will need to change the BROKER_URL
    and the MONGO_HOST option to the following:

    import os

    BROKER_URL = 'amqp://{}'.format(
        os.environ['ANCHOR_RABBITMQ_1_PORT_5672_TCP_ADDR']
    )
    MONGO_HOST = os.environ['ANCHOR_DB_1_PORT_27017_TCP_ADDR']

"""

BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp'
CELERY_TASK_RESULT_EXPIRES = 300
CELERY_RESULT_PERSISTENT = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = None
MONGO_PASS = None
MONGO_DATABASE = 'anchor'
MONGO_KWARGS = {'tz_aware': True}
