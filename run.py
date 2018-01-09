from atlasbroker.broker import Broker
from atlasbroker.config import Config

# secret.json file example :
#
# {
#     "mongo" : {
#         "uri": "",
#         "db": "",
#         "timeoutms": 5000,
#         "collection" : ""
#     },
#     "atlas" : {
#         "user": "",
#         "password" : "",
#         "group" : ""
#     }
# }
#
secrets = Config.load_json("secret.json")

config = Config(secrets["atlas"], secrets["mongo"])

# OR
#
# Custom config ?
#
# class CustomConfig(Config):
#     PARAMETER_NAMESPACE="ns"
#     
#     def generate_binding_username(self, binding):
#         return binding.binding_id + '-rw'
#
#     def generate_instance_dbname(self, instance):
#         return instance.parameters[self.PARAMETER_NAMESPACE]
#
# config = CustomConfig(secrets["atlas"], secrets["mongo"])

Broker(config).run()
