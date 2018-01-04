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

from openbrokerapi.errors import ErrBindingAlreadyExists
from openbrokerapi.service_broker import Binding, BindState
from atlasapi.specs import DatabaseUsersPermissionsSpecs
from atlasapi.errors import ErrAtlasNotFound, ErrAtlasConflict

class AtlasServiceBinding():
    """ Service Catalog : Atlas Service Binding """
    
    def __init__(self, backend):
        """ Constructor
        
        Args:
            backend (AtlasBrokerBackend): Atlas Broker Backend
        
        """
        self.backend = backend
    
    def find(self, binding_id, instance):
        """ find an instance
        
        Create a new instance and populate it with data stored if it exists.
        
        Args:
            binding_id (string): UUID of the binding
            instance (AtlasServiceInstance): instance
            
        Returns:
            AtlasServiceBinding
        
        """
        binding = AtlasServiceBinding.Binding(binding_id, instance)
        self.backend.storage.populate(binding)
        return binding
    
    def bind(self, binding, parameters):
        """ Create the binding
        
        Args:
            binding (AtlasServiceBinding): Existing or New binding
            parameters (dict): Parameters for the binding
            
        Returns:
            Binding.
            
        Raises:
            ErrBindingAlreadyExists: If binding exists but with different parameters
        
        """
        
        if not binding.isProvisioned():
            # Update binding parameters
            binding.parameters = parameters
            
            #  Credentials
            creds = self.backend.config.generate_binding_credentials(binding)
            
            # Binding
            p = self.backend.config.generate_binding_permissions(
                binding,
                DatabaseUsersPermissionsSpecs(creds["username"],creds["password"])
                )
            
            try:
                self.backend.atlas.DatabaseUsers.create_a_database_user(p)
            except ErrAtlasConflict:
                # The user already exists. This is not an issue because this is possible that we
                # created it in a previous call that failed later on the broker.
                pass
            
            self.backend.storage.store(binding)
            
            # Bind done
            return Binding(BindState.SUCCESSFUL_BOUND,
                           credentials = creds)
        
        elif binding.parameters == parameters:
            # Identical so nothing to do
            return Binding(BindState.IDENTICAL_ALREADY_EXISTS)
        
        else:
            # Different parameters ...
            raise ErrBindingAlreadyExists()
    
    def unbind(self, binding):
        """ Unbind the instance
        
        Args:
            binding (AtlasServiceBinding): Existing or New binding
            
        """
        
        username = self.backend.config.generate_binding_username(binding)
        
        try:
            self.backend.atlas.DatabaseUsers.delete_a_database_user(username)
        except ErrAtlasNotFound:
            # The user does not exist. This is not an issue because this is possible that we
            # removed it in a previous call that failed later on the broker.
            # This cover a manually deleted user case too.
            pass

        self.backend.storage.remove(binding)
    
    class Binding:
        """ Binding """
        
        def __init__(self, binding_id, instance):
            """ Constructor
            
            Args:
                binding_id (string): UUID of the binding
                instance (AtlasServiceInstance): instance
            
            """
            
            self.binding_id = binding_id
            self.instance = instance
            self.provisioned = True
        
        def isProvisioned(self):
            """ is already stored on the storage
            
            Returns:
            
                True -- We populate the content of the binding with stored information 
                False -- The binding is new
                
            """
            return self.provisioned
            
        def __eq__(self, other):
            return type(other) is AtlasServiceBinding.Binding and self.binding_id == other.binding_id and self.instance == other.instance
        
