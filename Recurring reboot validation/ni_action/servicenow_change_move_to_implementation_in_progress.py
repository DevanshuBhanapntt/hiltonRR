#!/usr/bin/env python

from lib.base_action import BaseAction
import requests

class servicenow_change_move_to_implementation_in_progress(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(servicenow_change_move_to_implementation_in_progress, self).__init__(config)

    def run(self, chg_id):
        self.sn_username = self.config['servicenow']['username']
        self.sn_password = self.config['servicenow']['password']
        #Start Implementation Change
        
        method = 'PUT'
        #endpoint = '/api/ntt11/changestackstormautomation/start_implementation'
        endpoint = '/api/now/table/change_request/' + chg_id
        payload = {
            'state': -1,
            }
        
#        url = "hiltonuat.service-now.com"
#       sn_url = "https://{0}{1}".format(url, endpoint)
#        headers = {'Content-type': 'application/json',
#                   'Accept': 'application/json'}
        change_request_move_to_imp_in_progress = self.sn_api_call(method, endpoint, payload=payload)
        print("Output is: {}".format(change_request_move_to_imp_in_progress))
        return change_request_move_to_imp_in_progress
