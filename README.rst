Atlas Broker
============

Atlas Broker for Kubernetes Service Catalog

`Code documentation (sphinx) <https://mickybart.github.io/python-atlasbroker/>`__

Docker
------

The docker folder provides everything to create an image that will serve Service Catalog requests in Kubernetes.

Atlasbroker module
------------------

Installation
^^^^^^^^^^^^

This package is available for Python 3.5+.

.. code:: bash

    pip3 install atlasbroker

Or install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/mickybart/python-atlasbroker.git

Prerequisite
^^^^^^^^^^^^

Examples in this README are using the secret.json file to inject Atlas and Mongo credentials.
Of course you can use any other solution provided by your infrastructure.

.. code:: python
    
    # Secrets structure
    #
    secrets = {
        "mongo" : {
            "uri": "",
            "db": "",
            "timeoutms": 5000,
            "collection" : ""
        },
        "atlas" : {
            "user": "",
            "password" : "",
            "group" : ""
        }
    }

Quick start
^^^^^^^^^^^

.. code:: python

    from atlasbroker.broker import Broker
    from atlasbroker.config import Config
    
    secrets = Config.load_json("secret.json")
    
    config = Config(secrets["atlas"], secrets["mongo"])
    
    Broker(config).run()

Custom Config
^^^^^^^^^^^^^

The class Config is the main way to customize the broker. All important functions like 
generate credentials, database name, permissions of the database user, UUID, etc are exposed on this class.

Please read the Code documentation for more details.

.. code:: python

    from atlasbroker.broker import Broker
    from atlasbroker.config import Config
    
    secrets = Config.load_json("secret.json")
    
    class CustomConfig(Config):
        PARAMETER_NAMESPACE="ns"
        
        def generate_binding_username(self, binding):
            return binding.binding_id + '-rw'

        def generate_instance_dbname(self, instance):
            return instance.parameters[self.PARAMETER_NAMESPACE]

    config = CustomConfig(secrets["atlas"], secrets["mongo"])
    
    Broker(config).run()

Error Types
-----------

Exceptions
^^^^^^^^^^

- ErrClusterNotFound
    Cluster not found
- ErrClusterConfig
    Cluster configuration not found
- ErrStorageMongoConnection
    The storage is not able to communicate with MongoDB
- ErrStorageTypeUnsupported
    Type unsupported
- ErrStorageRemoveInstance
    Failed to remove the instance
- ErrStorageRemoveBinding
    Failed to remove the binding
- ErrStorageStore
    Failed to store the instance or binding
- ErrStorageFindInstance
    Failed to find the instance
- ErrPlanUnsupported
    Plan not supported

Internal Notes
--------------

`Code documentation (sphinx) <https://mickybart.github.io/python-atlasbroker/>`__

Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/mickybart/python-atlasbroker/issues>`__
