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

"""
config

Permit to manage global configurations
"""

from pwgen import pwgen
from atlasapi.atlas import Atlas
from atlasapi.specs import RoleSpecs
from openbrokerapi.catalog import ServiceMetadata, ServicePlan
import json
from .errors import ErrClusterConfig

class Config:
    """ Configuration for AtlasBroker and sub-modules """
    
    # Common keys used by the broker
    #  openbrokerapi parameters
    PARAMETER_DATABASE="database"
    PARAMETER_NAMESPACE="ns"
    PARAMETER_CLUSTER="cluster"
    
    # UUID
    UUID_SERVICES_CLUSTER = "2a04f349-4aab-4fcb-af6d-8e1749a77c13"
    UUID_PLANS_EXISTING_CLUSTER = "8db474d1-3cc0-4f4d-b864-24e3bd49b874"
    
    def __init__(self, atlas_credentials, mongo_credentials, clusters=None):
        """ Constructor"""
        
        self.atlas = atlas_credentials
        self.mongo = mongo_credentials
        
        # Broker Service configuration
        self.broker = {
            "id" : self.UUID_SERVICES_CLUSTER,
            "name" : "atlas-mongodb-cluster",
            "description" : "Atlas/MongoDB for applications",
            "bindable" : True,
            "plans" : [
                ServicePlan(id=self.UUID_PLANS_EXISTING_CLUSTER,
                            name="atlas-mongodb-existing-cluster",
                            description="Atlas/MongoDB: Configure an existing cluster",
                            metadata=None,
                            free=False,
                            bindable=True),
                ],
            "tags" : ['atlas', 'mongodb'],
            "requires" : None,
            "metadata" : ServiceMetadata(
                displayName='Atlas - MongoDB Cloud Provider',
                imageUrl=None,
                longDescription=None,
                providerDisplayName=None,
                documentationUrl=None,
                supportUrl=None,
                ),
            "dashboard_client" : None,
            "plan_updateable" : False,
        }
            
        # Clusters configuration
        if clusters:
            self.clusters = clusters
        else:
            # load from Atlas
            atlas = Atlas(self.atlas["user"],
                        self.atlas["password"],
                        self.atlas["group"])
            self.clusters = {}
            for cluster in atlas.Clusters.get_all_clusters(iterable=True):
                uri = cluster["mongoURIWithOptions"].replace('mongodb://', 'mongodb://%s:%s@').replace('/?','/%s?')
                self.clusters[cluster["name"]] = uri
            
    def load_json(json_file):
        try:
            with open(json_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def generate_instance_dbname(self, parameters):
        """ Generate a Database name based on the namespace
        
        Args:
            parameters (dict): Parameters of the k8s Service Instance yaml
        
        """
        return parameters[self.PARAMETER_NAMESPACE]
    
    def generate_binding_credentials(self, binding):
        uri = self.clusters.get(binding.instance.get_cluster(), None)
        
        if not uri:
            raise ErrClusterConfig(cluster)
        
        # partial credentials
        creds = {"username" : self.generate_binding_username(binding),
                "password" : pwgen(32, symbols=False),
                "database" : binding.instance.get_dbname()}
        
        # uri
        uri = uri % (
            creds["username"],
            creds["password"],
            creds["database"])
        
        creds["uri"] = uri
        
        # return creds
        return creds
    
    def generate_binding_username(self, binding):
        return binding.binding_id
    
    def generate_binding_permissions(self, binding, permissions):
        permissions.add_roles(binding.instance.get_dbname(),
                              [RoleSpecs.dbAdmin,
                               RoleSpecs.readWrite])
        return permissions
