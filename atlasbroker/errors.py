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

"""errors module

All Specific Exceptions
"""

class ErrClusterNotFound(Exception):
    """Cluster not found
    
    Constructor
    
    Args:
        cluster (str): Atlas cluster name
    """
    def __init__(self, cluster):
        super().__init__("The cluster %s is not available on Atlas.", cluster)

class ErrClusterConfig(Exception):
    """Cluster configuration not found
    
    We need the configuration during the binding to set the connection string
    
    Constructor
    
    Args:
        cluster (str): Atlas cluster name
    """
    def __init__(self, cluster):
        super().__init__("The cluster configuration for %s is not available.", cluster)

class ErrStorageMongoConnection(Exception):
    """The storage is not able to communicate with MongoDB
    
    Constructor
    
    Args:
        during (str): When the issue occurs
    """
    def __init__(self, during):
        super().__init__("The storage is not able to communicate with MongoDB [%s]", during)

class ErrStorageTypeUnsupported(Exception):
    """Type unsupported
    
    Constructor
    
    Args:
        type_obj (type): Type of the object not supported (type(obj))
    """
    def __init__(self, type_obj):
        super().__init__("Type [%s] unsupported", str(type_obj))

class ErrStorageRemoveInstance(Exception):
    """Failed to remove the instance
    
    Constructor
    
    Args:
        instance_id (str): UUID of the instance
    """
    def __init__(self, instance_id):
        super().__init__("Failed to remove the instance %s", instance_id)

class ErrStorageRemoveBinding(Exception):
    """Failed to remove the binding
    
    Constructor
    
    Args:
        binding_id (str): UUID of the binding
    """
    def __init__(self, binding_id):
        super().__init__("Failed to remove the binding %s", binding_id)

class ErrStorageStore(Exception):
    """Failed to store the instance or binding"""
    def __init__(self):
        super().__init__("Failed to store the instance or binding.")

class ErrStorageFindInstance(Exception):
    """Failed to find the instance
    
    Constructor
    
    Args:
        instance_id (str): UUID of the instance
    """
    def __init__(self, instance_id):
        super().__init__("Failed to find the instance %s.", instance_id)

class ErrPlanUnsupported(Exception):
    """Plan not supported
    
    Constructor
    
    Args:
        plan_id (str): UUID of the plan
    """
    def __init__(self, plan_id):
        super().__init__("Plan [%s] not supported.", plan_id)
