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

"""serviceinstance module

Used to manage instance requests
"""

from openbrokerapi.errors import ErrInstanceAlreadyExists
from openbrokerapi.service_broker import ProvisionedServiceSpec, ProvisionState, DeprovisionServiceSpec
from .errors import ErrClusterNotFound
    
class AtlasServiceInstance():
    """Service Catalog : Atlas Service Instance
    
    Constructor
    
    Args:
        backend (AtlasBrokerBackend): Atlas Broker Backend
    """
    def __init__(self, backend):
        self.backend = backend
    
    def find(self, instance_id):
        """ find an instance
        
        Create a new instance and populate it with data stored if it exists.
        
        Args:
            instance_id (str): UUID of the instance
        
        Returns:
            AtlasServiceInstance.Instance: An instance
        """
        instance = AtlasServiceInstance.Instance(instance_id, self.backend)
        self.backend.storage.populate(instance)
        return instance
    
    def create(self, instance, parameters, existing):
        """ Create the instance
        
        Args:
            instance (AtlasServiceInstance.Instance): Existing or New instance
            parameters (dict): Parameters for the instance
            existing (bool): Create an instance on an existing Atlas cluster
        
        Returns:
            ProvisionedServiceSpec: Status
            
        Raises:
            ErrInstanceAlreadyExists: If instance exists but with different parameters
            ErrClusterNotFound: Cluster does not exist
        """
        
        if not instance.isProvisioned():
            # Set parameters
            instance.parameters = parameters
            
            # Existing cluster
            if existing and not self.backend.atlas.Clusters.is_existing_cluster(instance.parameters[self.backend.config.PARAMETER_CLUSTER]):
                # We need to use an existing cluster that is not available !
                raise ErrClusterNotFound(instance.parameters[self.backend.config.PARAMETER_CLUSTER])
            elif not existing:
                # We need to create a new cluster
                # We should not reach this code because the AtlasBroker.provision should
                # raise an ErrPlanUnsupported before.
                raise NotImplementedError()
            
            result = self.backend.storage.store(instance)
            
            # Provision done
            return ProvisionedServiceSpec(ProvisionState.SUCCESSFUL_CREATED,
                                      "",
                                      str(result))
        
        elif instance.parameters == parameters:
            # Identical so nothing to do
            return ProvisionedServiceSpec(ProvisionState.IDENTICAL_ALREADY_EXISTS,
                                        "",
                                        "duplicate")
        
        else:
            # Different parameters ...
            raise ErrInstanceAlreadyExists()
    
    def delete(self, instance):
        """Delete the instance
        
        Args:
            instance (AtlasServiceInstance.Instance): an existing instance
            
        Returns:
            DeprovisionServiceSpec: Status
        """
        
        #TODO: Really drop the database based on a policy set in `instance.parameters`.
        #
        #      We need :
        #      - Set a policy in parameters of the instance (eg: policy-on-delete : retain|drop    => default to retain)
        #      - to check that the database name `instance.get_dbname()` is not in use by another instance (shared database)
        #      - credential on the Atlas cluster `instance.get_cluster()` to drop the database
        #
        
        self.backend.storage.remove(instance)
        
        return DeprovisionServiceSpec(False, "done")
    
    class Instance:
        """Instance
        
        Constructor
        
        Args:
            instance_id (str): UUID of the instance
            backend (AtlasBrokerBackend): Atlas Broker Backend
        
        Keyword Arguments:
            parameters (dict): Parameters for the instance
        """
        def __init__(self, instance_id, backend, parameters=None):
            self.instance_id = instance_id
            self.backend = backend
            self.parameters = parameters
            self.provisioned = True
        
        def isProvisioned(self):
            """was it populated from the storage ?
            
            Returns:
                bool: True (populate from stored information), False (This is a new instance)
            """
            return self.provisioned
            
        def __eq__(self, other):
            return type(other) is AtlasServiceInstance.Instance and self.instance_id == other.instance_id and self.parameters == other.parameters
        
        def get_dbname(self):
            """Get the database name
            
            Returns:
                str: The database name
            """
            static_name = self.parameters.get(self.backend.config.PARAMETER_DATABASE, None)
            if static_name:
                return static_name
            
            return self.backend.config.generate_instance_dbname(self)

        def get_cluster(self):
            """Get the Atlas cluster
            
            Returns:
                str: The Atlas cluster name
            """
            return self.parameters[self.backend.config.PARAMETER_CLUSTER]
        
