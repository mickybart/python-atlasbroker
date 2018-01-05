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

"""broker module"""

from flask import Flask
from .apis.health import getApi as health
from .apis.broker import getApi as broker

class Broker:
    """Broker
    
    Service composition with blueprint provided from apis.
    The broker is based on Flask
    
    Constructor
    
    Args:
        config (Config): The broker configuration
    """
    def __init__(self, config):
        self.app = Flask(__name__)
        self.app.register_blueprint(health())
        self.app.register_blueprint(broker(config))

    def run(self):
        """Start the broker server"""
        self.app.run(host='0.0.0.0')
