#!/usr/bin/env python

from lib.base_action import BaseAction
import requests

class ServiceNowChangeUpdate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowChangeUpdate, self).__init__(config)

    def run(self, chg_id, worknotes):
        # Update Change
        method = "PUT"
        endpoint = '/api/now/table/change_request/' + chg_id
        payload = {
            'work_notes': worknotes
            }
        update_change_request = self.sn_api_call(method, endpoint, payload=payload)
        return update_change_request
