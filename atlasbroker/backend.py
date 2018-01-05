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

"""Backend module

Used by the broker and all sub-modules to
- expose few common services (Storage, Config, Atlas, ...)
- dispatch some calls
"""

from .servicebinding import AtlasServiceBinding
from .serviceinstance import AtlasServiceInstance
from .storage import AtlasBrokerStorage
from atlasapi.atlas import Atlas

class AtlasBrokerBackend:
    """Backend for the Atlas Broker
    
    Expose all services to serve Broker requests
    
    Constructor 
    
    Args:
        config (Config): Configuration of the Atlas Broker
    """
    
    def __init__(self, config):
        self.config = config
        self.storage = AtlasBrokerStorage(self.config.mongo["uri"],
                                          self.config.mongo["timeoutms"],
                                          self.config.mongo["db"],
                                          self.config.mongo["collection"])
        self.atlas = Atlas(self.config.atlas["user"],
                           self.config.atlas["password"],
                           self.config.atlas["group"])
        self.service_instance = AtlasServiceInstance(self)
        self.service_binding = AtlasServiceBinding(self)
        
    def find(self, _id, instance = None):
        """ Find
        
        Args:
            _id (str): instance id or binding Id
            
        Keyword Arguments:
            instance (AtlasServiceInstance.Instance): Existing instance
            
        Returns:
            AtlasServiceInstance.Instance or AtlasServiceBinding.Binding: An instance or binding. 
        """
        
        if instance is None:
            # We are looking for an instance
            return self.service_instance.find(_id)
        else:
            # We are looking for a binding
            return self.service_binding.find(_id, instance)

    def create(self, instance, parameters, existing=True):
        """Create an instance
        
        Args:
            instance (AtlasServiceInstance.Instance): Existing or New instance
            parameters (dict): Parameters for the instance
            
        Keyword Arguments:
            existing (bool): True (use an existing cluster), False (create a new cluster)
        
        Returns:
            ProvisionedServiceSpec: Status
        """
        return self.service_instance.create(instance, parameters, existing)
    
    def delete(self, instance):
        """Delete an instance
        
        Args:
            instance (AtlasServiceInstance.Instance): Existing instance
        
        Returns:
            DeprovisionServiceSpec: Status
        """
        return self.service_instance.delete(instance)
    
    def bind(self, binding, parameters):
        """Binding to an instance
        
        Args:
            binding (AtlasServiceBinding.Binding): Existing or New binding
            parameters (dict): Parameters for the binding
            
        Returns:
            Binding: Status
        """
        return self.service_binding.bind(binding, parameters)

    def unbind(self, binding):
        """Unbinding an instance
        
        Args:
            binding (AtlasServiceBinding.Binding): Existing binding
        """
        self.service_binding.unbind(binding)
