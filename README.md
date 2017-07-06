[![Build Status](https://travis-ci.org/oldarmyc/anchor.svg?branch=master)](https://travis-ci.org/oldarmyc/anchor)
[![Documentation Status](https://readthedocs.org/projects/anchor/badge/?version=latest)](http://anchor.readthedocs.org/?badge=latest)

Anchor
========

Anchor provides an easy way to quickly view your Rackspace cloud server or block storage distribution between host servers by Data Center.

In addition you can utilize an API to ask whether the new server that has just been built shares a host with another server in your account. This provides insight into which of your server(s) would be affected if a specific host server has an issue causing downtime.

To view the API documentation you can visit [https://anchor.readthedocs.org](https://anchor.readthedocs.org)

#### Authentication

To use the application just login with your username and Cloud Account API key. The application does not store the API key and keeps no record of it. It only uses the API key to make the authentication call so that the application can generate the token. The token is then used in subsequent API calls, and is kept as long as there is a session. A logout will clear the session of any data, or when the token expires whichever comes first.

[View Authentication Call details](https://developer.rackspace.com/docs/cloud-identity/v2/developer-guide/#authenticate-as-user-with-password-or-api-key)

___

#### Running it in docker?
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

Change the appropriate values in each of the config files. Currently the sample configs are setup for running everything in Docker or localhost but can be changed depending on the environment.

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

You should see four containers running named anchor_app, anchor_celery, mongo, and rabbitmq:3. If all four are running then you can browse to `http://localhost:5000` to view the running application.

If you want to view the container logs in-line just omit the -d flag and it will run in the current terminal window. To stop it in this mode just use CTRL-C. If running in detached mode you can use the command `docker logs CONTAINER_ID` to view the specific container log files.

If in detached mode you can use the following command to stop the containers.
```
docker-compose stop
```
___

#### Running it locally?

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

Change the appropriate values in each of the config files. You will need a rabbitmq server and a mongo server to run locally. These can both be run in docker without issues to avoid having to install both services, but will need to be accessible from localhost.

RabbitMQ docker example run command
```
docker run --name rabbit-dev -p "15672:15672" -p "5672:5672" -p "4369:4369" -p "5671:5671" -p "25672:25672" -d rabbitmq
```

MongoDB docker example run command
```
docker run --name mongo-dev -p "27017:27017" -d mongo
```

##### Install packages
Install base packages needed for the application
```
pip install -r requirements.txt
```

##### Starting the application
```
python runapp.py
```

___

#### Running Tests

##### Ensure you have the testing requirements installed
```
pip install -r dev-requirements.txt
```

##### Running tests with coverage report
```
nosetests --with-coverage --cover-erase --cover-package anchor
```
