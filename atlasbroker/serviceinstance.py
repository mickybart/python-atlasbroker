"""
Copyright (c) 2018 Yellow Pages Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from openbrokerapi.errors import ErrInstanceAlreadyExists
from openbrokerapi.service_broker import ProvisionedServiceSpec, ProvisionState, DeprovisionServiceSpec
from .errors import ErrClusterNotFound
    
class AtlasServiceInstance():
    """ Service Catalog : Atlas Service Instance """
    
    def __init__(self, backend):
        """ Constructor
        
        Args:
            backend (AtlasBrokerBackend): Atlas Broker Backend
        
        """
        self.backend = backend
    
    def find(self, instance_id):
        """ find an instance
        
        Create a new instance and populate it with data stored if it exists.
        
        Args:
            instance_id (string): UUID of the instance
            
        Returns:
            AtlasServiceInstance
        
        """
        instance = AtlasServiceInstance.Instance(instance_id)
        self.backend.storage.populate(instance)
        return instance
    
    def create(self, instance, parameters, existing):
        """ Create the instance
        
        Args:
            instance (AtlasServiceInstance): Existing or New instance
            parameters (dict): Parameters for the instance
            existing (bool): Create an instance on an existing Atlas cluster
        
        Returns:
            ProvisionedServiceSpec.
            
        Raises:
            ErrInstanceAlreadyExists: If instance exists but with different parameters
            ErrClusterNotFound: Cluster does not exist
        
        """
        
        # Review parameters to add the database name if needed.
        # For now the database is set with the name of the namespace that is mandatory
        if not parameters.get(self.backend.config.PARAMETER_DATABASE):
            parameters[self.backend.config.PARAMETER_DATABASE] = self.backend.config.generate_instance_dbname(parameters)
        
        if not instance.isProvisioned():
            # Provisionning
            instance.parameters = parameters
            
            # Existing cluster
            if existing and not self.backend.atlas.Clusters.is_existing_cluster(parameters[self.backend.config.PARAMETER_CLUSTER]):
                # We need to use an existing cluster that is not available !
                raise ErrClusterNotFound(self.backend.config.PARAMETER_CLUSTER)
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
        """ Delete the instance
        
        Args:
            instance (AtlasServiceInstance): an existing instance
            
        """
        
        self.backend.storage.remove(instance)
        
        #TODO: Really drop the database based on a policy set in instance parameters if nobody else is using it
        #      policy-on-delete : retain|drop
        
        return DeprovisionServiceSpec(False, "done")
    
    class Instance:
        """ Instance """
        
        def __init__(self, instance_id, parameters=None):
            """ Constructor
            
            Args:
                instance_id (string): UUID of the instance
            
            Kwargs:
                parameters (dict): Parameters for the instance
            
            """
            self.instance_id = instance_id
            self.parameters = parameters
            self.provisioned = True
        
        def isProvisioned(self):
            """ is already stored on the storage
            
            Returns:
            
                True -- We populate the content of the instance with stored information 
                False -- The instance is new
                
            """
            return self.provisioned
            
        def __eq__(self, other):
            return type(other) is AtlasServiceInstance.Instance and self.instance_id == other.instance_id and self.parameters == other.parameters
        
        def get_dbname(self):
            return self.parameters[self.backend.config.PARAMETER_DATABASE]
        
        def get_cluster(self):
            return self.parameters[self.backend.config.PARAMETER_CLUSTER]
        
