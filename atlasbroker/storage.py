# Copyright (c) 2018 Yellow Pages Inc.
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

"""Storage module"""

import pymongo
from .servicebinding import AtlasServiceBinding
from .serviceinstance import AtlasServiceInstance
from .errors import (
    ErrStorageMongoConnection,
    ErrStorageTypeUnsupported,
    ErrStorageRemoveInstance,
    ErrStorageRemoveBinding,
    ErrStorageStore,
    ErrStorageFindInstance
    )

class AtlasBrokerStorage:
    """ Storage
    
    Permit to store ServiceInstance and ServiceBinding into a MongoDB.
    
    This is used for caching and to trace what is done by the broker.
    This is internally used to don't create same instances/bindings and to return appropriate code like AlreadyExists
    That reducing the number of call to Atlas APIs too.
    
    Constructor
    
    Args:
        uri (str): MongoDB connection string
        timeoutms (int): MongoDB requests timeout in ms
        db (str): The DB name
        collection (str): The collection name
        
    Raises:
        ErrStorageMongoConnection: Error during MongoDB communication.
    """
    def __init__(self, uri, timeoutms, db, collection):
        self.mongo_client = None
        
        # Connect to Mongo
        try:
            print("connection to mongo...")
            # Init Mongo and create DB and collections objects
            self.mongo_client = pymongo.MongoClient(uri, timeoutms)
            self.db = self.mongo_client[db]
            self.broker = self.db.get_collection(collection)
            
            if len(self.broker.index_information()) == 0:
                # collection does not exist
                # create it and create indexes
                self.db.create_collection(collection)
                self.broker.create_index( "instance_id" )
                self.broker.create_index( "binding_id" )

            print("mongo: connected")
        except Exception as e:
            print("mongo: " + str(e))
            self.mongo_client = None
            raise ErrStorageMongoConnection("Initialization")
    
    def populate(self, obj):
        """ Populate
        
        Query mongo to get information about the obj if it exists
        
        Args:
            obj (AtlasServiceBinding.Binding or AtlasServiceInstance.Instance): instance or binding
        
        Raises:
            ErrStorageTypeUnsupported: Type unsupported.
            ErrStorageMongoConnection: Error during MongoDB communication.
        """
        
        # query
        if type(obj) is AtlasServiceInstance.Instance:
            query = { "instance_id" : obj.instance_id, "binding_id" : { "$exists" : False } }
        elif type(obj) is AtlasServiceBinding.Binding:
            query = { "binding_id" : obj.binding_id, "instance_id" : obj.instance.instance_id }
        else:
            raise ErrStorageTypeUnsupported(type(obj))
        
        # find
        try:
            result = self.broker.find_one(query)
        except:
            raise ErrStorageMongoConnection("Populate Instance or Binding")
        
        if result is not None:
            obj.parameters = result["parameters"]
            
            # Flags the obj to provisioned
            obj.provisioned = True
        else:
            # New
            obj.provisioned = False
    
    def store(self, obj):
        """ Store 
        
        Store an object into the MongoDB storage for caching
        
        Args:
            obj (AtlasServiceBinding.Binding or AtlasServiceInstance.Instance): instance or binding
            
        Returns:
            ObjectId: MongoDB _id
        
        Raises:
            ErrStorageMongoConnection: Error during MongoDB communication.
            ErrStorageTypeUnsupported: Type unsupported.
            ErrStorageStore : Failed to store the binding or instance.
        """
        
        # query
        if type(obj) is AtlasServiceInstance.Instance:
            query = { "instance_id" : obj.instance_id, "database" : obj.get_dbname(), "cluster": obj.get_cluster(), "parameters" : obj.parameters }
        elif type(obj) is AtlasServiceBinding.Binding:
            query = { "binding_id" : obj.binding_id, "parameters" : obj.parameters, "instance_id": obj.instance.instance_id }
        else:
            raise ErrStorageTypeUnsupported(type(obj))
        
        # insert
        try:
            result = self.broker.insert_one(query)
        except:
            raise ErrStorageMongoConnection("Store Instance or Binding")
        
        if result is not None:
            # Flags the obj to provisioned
            obj.provisioned = True
            return result.inserted_id
        
        raise ErrStorageStore()
    
    def remove(self, obj):
        """ Remove 
        
        Remove an object from the MongoDB storage for caching
        
        Args:
            obj (AtlasServiceBinding.Binding or AtlasServiceInstance.Instance): instance or binding
            
        Raises:
            ErrStorageTypeUnsupported: Type unsupported.
        """
        if type(obj) is AtlasServiceInstance.Instance:
            self.remove_instance(obj)
        elif type(obj) is AtlasServiceBinding.Binding:
            self.remove_binding(obj)
        else:
            raise ErrStorageTypeUnsupported(type(obj))

    def remove_instance(self, instance):
        """ Remove an instance
        
        Remove an object from the MongoDB storage for caching
        
        Args:
            instance (AtlasServiceInstance.Instance): instance
        
        Raises:
            ErrStorageMongoConnection: Error during MongoDB communication.
            ErrStorageRemoveInstance: Failed to remove the instance.
        """
        
        # query
        query = { "instance_id" : instance.instance_id, "binding_id" : { "$exists" : False } }
        
        # delete the instance
        try:
            result = self.broker.delete_one(query)
        except:
            raise ErrStorageMongoConnection("Remove Instance")
        
        # return the result
        if result is not None and result.deleted_count == 1:
            instance.provisioned = False
        else:
            raise ErrStorageRemoveInstance(instance.instance_id)
    
    def remove_binding(self, binding):
        """ Remove a binding
        
        Remove an object from the MongoDB storage for caching
        
        Args:
            binding (AtlasServiceBinding.Binding): binding
            
        Raises:
            ErrStorageMongoConnection: Error during MongoDB communication.
            ErrStorageRemoveBinding: Failed to remove the binding
        """
        
        # query
        query = { "binding_id" : binding.binding_id, "instance_id" : binding.instance.instance_id }
        
        # delete the binding
        try:
            result = self.broker.delete_one(query)
        except:
            raise ErrStorageMongoConnection("Remove Binding")

        # return the result
        if result is not None and result.deleted_count == 1:
            binding.provisioned = False
        else:
            raise ErrStorageRemoveBinding(binding.binding_id)
