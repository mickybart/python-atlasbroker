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

"""service module

Core of the Atlas broker
"""

from openbrokerapi.service_broker import *
from openbrokerapi.api import *
from openbrokerapi.errors import ErrBindingDoesNotExist, ErrInstanceDoesNotExist

from .backend import AtlasBrokerBackend
from .errors import ErrPlanUnsupported

class AtlasBroker(Service):
    """Atlas Broker
    
    Implement a service broker by overriding methods of Service
    
    Constructor
    
    Args:
        config (config): Configuration of the broker
    """
    def __init__(self, config):
        super().__init__(
            id=config.broker["id"],
            name=config.broker["name"],
            description=config.broker["description"],
            bindable=config.broker["bindable"],
            plans=config.broker["plans"],
            tags=config.broker["tags"],
            requires=config.broker["requires"],
            metadata=config.broker["metadata"],
            dashboard_client=config.broker["dashboard_client"],
            plan_updateable=config.broker["plan_updateable"],
        )
        
        # Create the AtlasBrokerBackend
        self._backend = AtlasBrokerBackend(config)

    def provision(self, instance_id: str, service_details: ProvisionDetails, async_allowed: bool) -> ProvisionedServiceSpec:
        """Provision the new instance
        
        see openbrokerapi documentation
        
        Returns:
            ProvisionedServiceSpec
        """
        
        if service_details.plan_id == self._backend.config.UUID_PLANS_EXISTING_CLUSTER:
            # Provision the instance on an Existing Atlas Cluster
            
            # Find or create the instance
            instance = self._backend.find(instance_id)
            
            # Create the instance if needed
            return self._backend.create(instance, service_details.parameters, existing=True)
        
        # Plan not supported
        raise ErrPlanUnsupported(service_details.plan_id)

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        """Unbinding the instance
        
        see openbrokerapi documentation
        
        Raises:
            ErrBindingDoesNotExist: Binding does not exist.
        """
        
        # Find the instance
        instance = self._backend.find(instance_id)
        
        # Find the binding
        binding = self._backend.find(binding_id, instance)
        if not binding.isProvisioned():
            # The binding does not exist
            raise ErrBindingDoesNotExist()
        
        # Delete the binding
        self._backend.unbind(binding)

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        """Update
        
        Not implemented. Not used by Kubernetes Service Catalog.
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        """Binding the instance
        
        see openbrokerapi documentation
        """
        
        # Find the instance
        instance = self._backend.find(instance_id)
        
        # Find or create the binding
        binding = self._backend.find(binding_id, instance)
        
        # Create the binding if needed
        return self._backend.bind(binding, details.parameters)

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
        """Deprovision an instance
        
        see openbrokerapi documentation
        
        Raises:
            ErrInstanceDoesNotExist: Instance does not exist.
        """
        
        # Find the instance
        instance = self._backend.find(instance_id)
        if not instance.isProvisioned():
            # the instance does not exist
            raise ErrInstanceDoesNotExist()
        
        return self._backend.delete(instance)

    def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
        """Last Operation
        
        Not implemented. We are not using asynchronous operation on Atlas Broker.
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

