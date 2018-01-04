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

class ErrClusterNotFound(Exception):
    def __init__(self, cluster):
        super().__init__("The cluster %s is not available on Atlas.", cluster)

class ErrClusterConfig(Exception):
    def __init__(self, cluster):
        super().__init__("The cluster configuration for %s is not available.", cluster)

class ErrStorageMongoConnection(Exception):
    def __init__(self, during):
        super().__init__("The storage is not able to communicate with MongoDB during : %s", during)

class ErrStorageTypeUnsupported(Exception):
    def __init__(self, type_obj):
        super().__init__("Type [%s] unsupported", str(type_obj))

class ErrStorageRemoveInstance(Exception):
    def __init__(self, instance_id):
        super().__init__("Failed to remove the instance %s", instance_id)

class ErrStorageRemoveBinding(Exception):
    def __init__(self, binding_id):
        super().__init__("Failed to remove the binding %s", binding_id)

class ErrStorageStore(Exception):
    def __init__(self):
        super().__init__("Failed to store the instance or binding.")

class ErrStorageFindInstance(Exception):
    def __init__(self, instance_id):
        super().__init__("Failed to find the instance %s.", instance_id)

class ErrPlanUnsupported(Exception):
    def __init__(self, plan_id):
        super().__init__("Plan [%s] not supported.", plan_id)
