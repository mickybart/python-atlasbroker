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

"""Broker"""

from openbrokerapi.api import *
from openbrokerapi.log_util import *

from atlasbroker.service import AtlasBroker

def getApi(config):
    """Get Api for the broker
    
    Returns:
        Blueprint: section for the broker
    """
    api = get_blueprint([AtlasBroker(config)], None, basic_config())
    return api
