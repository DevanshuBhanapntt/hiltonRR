#!/usr/bin/env python
# Copyright 2021 NTT Technologies
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
from lib.base_action import BaseAction
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import ast

KEY_DICT = {
    'servicenow': 'servicenow.change_processing',
    'helix': 'helix.change_processing'
}


class itsmprocessingchangeremove(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmprocessingchangeremove, self).__init__(config)

    def run(self, change_id):
        itsm_tool = self.config['itsm_tool']
        inc_st2_key = KEY_DICT[itsm_tool]
        st2_client = self.st2_client_get()
        processing_incs = st2_client.keys.get_by_name(inc_st2_key)

        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        if change_id in processing_incs:
            processing_incs.remove(change_id)
            incs_str = str(processing_incs)
            kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
            st2_client.keys.update(kvp)

            result = {
                'key': inc_st2_key,
                'value': incs_str
            }
        else:
            result = "The given Change ID was not found in the list"

        return result
