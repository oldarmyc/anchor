[![Build Status](https://travis-ci.org/oldarmyc/anchor.svg?branch=master)](https://travis-ci.org/oldarmyc/anchor)
[![Documentation Status](https://readthedocs.org/projects/anchor/badge/?version=latest)](http://anchor.readthedocs.org/?badge=latest)

Anchor
========

Anchor provides an easy way to quickly view your Rackspace cloud server or block storage distribution between host servers by Data Center.

In addition you can utilize an API to ask whether the new server that has just been built shares a host with another server in your account. This provides insight into which of your server(s) would be affected if a specific host server has an issue causing downtime.

To view the API documentation you can visit [https://anchor.readthedocs.org](https://anchor.readthedocs.org)

View the public version at [https://anchor.cloudapi.co](https://anchor.cloudapi.co "Anchor Application")

#### Authentication

To use the application just login with your username and Cloud Account API key. The application does not store the API key and keeps no record of it. It only uses the API key to make the authentication call so that the application can generate the token. The token is then used in subsequent API calls, and is kept as long as there is a session. A logout will clear the session of any data, or when the token expires whichever comes first.

[View Authentication Call details](https://developer.rackspace.com/docs/cloud-identity/v2/developer-guide/#authenticate-as-user-with-password-or-api-key)

___

#### Want to run it locally?
All you need is docker installed along with docker-compose

[View Docker Installation Docs](https://docs.docker.com/engine/installation/ 'Install Docker')

##### Setup working directory
```
mkdir anchor
git clone https://github.com/oldarmyc/anchor.git
cd anchor
```

#### Setup config files

##### Copy over sample configs
````
cp anchor/config/config.example.py anchor/config/config.py
cp anchor/config/celery.example.py anchor/config/celery.py
````

##### Edit the config.py file
```
vim anchor/config/config.py
```

##### Add import at top of file
```python
import os
```

##### Change MONGO_HOST from localhost to the following:
```python
MONGO_HOST = os.environ['ANCHOR_DB_1_PORT_27017_TCP_ADDR']
```

##### Edit the celery.py file
```
vim anchor/config/celery.py
```

##### Add import at top of file
```python
import os
```

##### Change BROKER_URL and MONGO_HOST from localhost to the following:
```python
BROKER_URL = 'amqp://{}'.format(
    os.environ['ANCHOR_RABBITMQ_1_PORT_5672_TCP_ADDR']
)
MONGO_HOST = os.environ['ANCHOR_DB_1_PORT_27017_TCP_ADDR']
```

#### Build the docker images

##### Start the build
```
docker-compose build
```

##### Bring the containers up and run in the background
```
docker-compose up -d
```

##### Verify that everything is running
```
docker ps
```

You should see four containers running named anchor_app, anchor_celery, mongo, and rabbitmq:3. If all four are running then you can browse to http://localhost:5000 to view the running application, and use it like the public version.

If you want to view the container logs in-line just omit the -d flag and it will run in the current terminal window. To stop it in this mode just use CTRL-C. If running in detached mode you can use the command `docker logs CONTAINER_ID` to view the specific container log files.

If in detached mode you can use the following command to stop the containers.
```
docker-compose stop
```
