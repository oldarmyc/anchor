Public API
=========================

Anchor provides a basic API to allow you to programmatically determine if your
new server you just built shares a host with another cloud server on your account.
Thus increasing visibility into shared resources in your environment, and showing
the impact if a host goes down.


API Headers
-------------

All calls will utilize the same header information as shown below, where CLOUD-AUTH-TOKEN
is the token that is given to you after authenticating through Rackspace Identity/

.. code-block:: javascript

    {
      "X-Auth-Token": "CLOUD-AUTH-TOKEN",
      "Content-Type": "application/json"
    }


Initialize
----
.. http:method:: POST /account/{account_id}/{region}

    :arg account_id: Rackspace cloud account number or DDI
    :arg region: Rackspace region - DFW, ORD, IAD, LON, HKG, SYD

.. http:response:: Initialize retrieval of current servers with all details on the account for the specified region

   .. sourcecode:: js

      {
          "task_id": "e3449d1399e946738eb91a339ffa1297"
      }

   :data integer task_id: Task identifier for server retrieval


Check initialization status
----
.. http:method:: GET /task/{task_id}

    :arg task_id: Task ID given in the response of the initialization POST

.. http:response:: Check status of initialization

   .. sourcecode:: js

      {
          "task_status": "SUCCESS"
      }

   :data string task_status: Rackspace cloud account number or DDI


Get all server info
----
.. http:method:: GET /account/{account_id}/{region}

    :arg account_id: Rackspace cloud account number or DDI
    :arg region: Rackspace region - DFW, ORD, IAD, LON, HKG, SYD

.. http:response:: Get all of the servers for the account in the specified region

   .. sourcecode:: js

    {
        'data': {
            'servers': [
                {
                    'created': '2015-01-01T19:52:34Z',
                    'flavor': 'performance1-2',
                    'host_id': 'a0b2a91a8dd332d3b461e30d598057135d1e34ea073b81bf63438e21',
                    'id': '00000000-aaaa-1111-bbbb-22222222222',
                    'name': 'server_name',
                    'private': [
                        '10.10.10.10'
                    ],
                    'public': [
                        '4444:3333:2222:111:dd44:cc33:bb11:aaaa',
                        '100.100.1.3'
                    ],
                    'state': 'active'
                }
            ]
        }
    }

   :data string created: Date server created in UTC
   :data string flavor: Flavor ID for the server
   :data string host_id: Host UUID tha the server resides on
   :data string id: UUID of the server
   :data string name: Server name
   :data string private: List of all private interfaces on the server
   :data string public: List of all public interfaces on the server
   :data string state: State of the server


Delete account server cache
----
.. http:method:: DELETE /account/{account_id}/{region}

    :arg account_id: Rackspace cloud account number or DDI
    :arg region: Rackspace region - DFW, ORD, IAD, LON, HKG, SYD

.. http:response:: Remove cache entry for the account in the specified region


Check status and cache a newly built server
----
.. http:method:: PUT /account/{account_id}/{region}/server/{server_id}

    :arg account_id: Rackspace cloud account number or DDI
    :arg region: Rackspace region - DFW, ORD, IAD, LON, HKG, SYD
    :arg server_id: Server ID of the server you want to check

.. http:response:: Status of whether the server is sharing a host with another server on the account

   .. sourcecode:: js

      {
          "duplicate": false
      }

   :data boolean duplicate: Is the server sharing the host with another resource on the account


Check status of an existing server
----
.. http:method:: GET /account/{account_id}/{region}/server/{server_id}

    :arg account_id: Rackspace cloud account number or DDI
    :arg region: Rackspace region - DFW, ORD, IAD, LON, HKG, SYD
    :arg server_id: Server ID of the server you want to check

.. http:response:: Status of whether the server is sharing a host with another server on the account

   .. sourcecode:: js

    {
        "duplicate": false,
        "host_data": {
            "server": {
                "id": "aaaa11111-00000-2222-3333-73ecc5266dcb",
                "name": "server-name"
            }
        }
    }

   :data boolean duplicate: Is the server sharing the host with another resource on the account
   :data list host_data: All servers on that share a host with the specified server
   :data string id: UUID of server
   :data string name: Server name
