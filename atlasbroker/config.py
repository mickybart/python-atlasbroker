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

"""
config module

Permit to manage global configurations
"""

from pwgen import pwgen
from atlasapi.atlas import Atlas
from atlasapi.specs import RoleSpecs
from openbrokerapi.catalog import ServiceMetadata, ServicePlan
import json
from .errors import ErrClusterConfig

class Config:
    """Configuration for AtlasBroker and sub-modules
    
    This class can be overriden and so adapted by every compagnies to
    set different policy about naming convention, password generation etc.
    
    You should check those main functions used by the broker:
        generate_instance_dbname
        generate_binding_credentials
        generate_binding_username
        generate_binding_permissions
        
    Constructor
    
    Args:
        atlas_credentials (dict): Atlas credentials eg: {"userame" : "", "password": "", "group": ""}
        mongo_credentials (dict): Mongo credentials eg: {"uri": "", "db": "", "timeoutms": 5000, "collection": ""}
        
    Keyword Arguments:
        clusters (list): List of cluster with uri associated. If not provided, it will be populate from Atlas.
    """
    
    # Common keys used by the broker
    # (parameters on the k8s instance yaml definition)
    PARAMETER_DATABASE="database"
    PARAMETER_CLUSTER="cluster"
    
    # UUID
    UUID_SERVICES_CLUSTER = "2a04f349-4aab-4fcb-af6d-8e1749a77c13"
    UUID_PLANS_EXISTING_CLUSTER = "8db474d1-3cc0-4f4d-b864-24e3bd49b874"
    
    def __init__(self, atlas_credentials, mongo_credentials, clusters=None):
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
        """Load JSON file
        
        Args:
            json_file (str): filename of a json file
            
        Returns:
            dict: content of the file
        """
        try:
            with open(json_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def generate_instance_dbname(self, instance):
        """Generate a Database name
        
        This function permit to define the database name for this instance.
        
        IMPORTANT: Multiple calls of this function with the same instance should return the same database name.
        
        The UUID is a good way to set it but if you need to share a database accross multiple namespaces,
        you need to return a static name independant of the UUID.
        It is not possible in the current broker api to bind to an instance from another namespace. So each namespace need
        its own instance object despite that we want to share a database.
        
        Atlas Broker is able to manage muliple instance UUID set to a unique database with a static name.
        
        You have 2 way to do it:
        - You can create each instance with the same parameters and to generate a static name based on those parameters only.
        - You can set a static name directly on instance parameters with the key value of Config.PARAMETER_DATABASE. If this key exists, this function will never be called.
        
        Args:
            instance (AtlasServiceInstance.Instance): An instance
            
        Returns:
            str: The database name
        """
        return 'instance-' + instance.instance_id
    
    def generate_binding_credentials(self, binding):
        """Generate binding credentials
        
        This function will permit to define the configuration to
        connect to the instance.
        Those credentials will be stored on a secret and exposed to a a Pod.
        
        We should at least returns the 'username' and 'password'.
        
        Args:
            binding (AtlasServiceBinding.Binding): A binding
            
        Returns:
            dict: All credentials and secrets.
            
        Raises:
            ErrClusterConfig: Connection string to the cluster is not available.
        """
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
        """Generate binding username
        
        We don't need anything static here. The UUID is a good way to create a username.
        
        IMPORTANT: Multiple calls of this function with the same binding should return the same username.
        
        Args:
            binding (AtlasServiceBinding.Binding): A binding
        
        Returns:
            str: The username to the database
        """
        return binding.binding_id
    
    def generate_binding_permissions(self, binding, permissions):
        """Generate Users pemissions on the database
        
        Defining roles to the database for the users.
        We can pass extra information into parameters of the binding if needed (see binding.parameters).
        
        Args:
            binding (AtlasServiceBinding.Binding): A binding
            permissions (atlasapi.specs.DatabaseUsersPermissionsSpecs): Permissions for Atlas
        
        Returns:
            atlasapi.specs.DatabaseUsersPermissionsSpecs: Permissions for the new user
        """
        permissions.add_roles(binding.instance.get_dbname(),
                              [RoleSpecs.dbAdmin,
                               RoleSpecs.readWrite])
        return permissions
