#!/usr/bin/env python

from st2reactor.sensor.base import PollingSensor
from st2client.models.keyvalue import KeyValuePair
import requests
import ast
import re
import socket
import os
from st2client.client import Client
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ['servicenow_change_move_to_implementation_in_progress']

class servicenow_change_move_to_implementation_in_progress(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(servicenow_change_move_to_implementation_in_progress, self).__init__(sensor_service=sensor_service,
                                                       config=config,
                                                       poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self.base_action = base_action.BaseAction(config)

    def setup(self):
        self.sn_username = self._config['servicenow']['username']
        self.sn_password = self._config['servicenow']['password']
        self.sn_url = self._config['servicenow']['url']
        self.som_company_sys_id =  self.config['servicenow']['company_sys_id']
        self.servicenow_headers = {'Content-type': 'application/json',
                                   'Accept': 'application/json'}
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)

    def poll(self):
        # Query for all open change requests
        #Change state values
        #draft: 1
        #review: 2
        #planning in progress: 3
        #pending approval: 4
        #scheduled: 5
        #implementation in progress: 6
        #completed: 7
        #closed: 8
        #cancelled: 9
        sn_change_endpoint = '/api/now/table/change_request?sysparm_query=active=true^state=3'
        # Commenting the below line as the company id is being changed to Graphic Packaging
        #sn_change_endpoint = sn_change_endpoint + '^company.sys_id=d24ed6834f32724067badefd0210c728'
        #sn_change_endpoint = sn_change_endpoint + '^priority=3^ORpriority=4'
        #sn_change_endpoint = sn_change_endpoint + "^start_date<javascript:gs.beginningOfLast15Minutes()^start_date>javascript:gs.beginningOfLast45Minutes()"
        # Changes specific to TR - Automation Autoreboot validation
        #sn_change_endpoint = sn_change_endpoint + '^descriptionLIKEAutoreboot'
        #sn_change_endpoint = sn_change_endpoint + '^descriptionLIKEAutomation Control Section'
        sn_change_endpoint = sn_change_endpoint + '^short_descriptionLIKE%5BTR%20-%20Automation'
        sn_change_endpoint = sn_change_endpoint + '&sysparm_fields=number,assignment_group,company,cmdb_ci,description,short_description,sys_id,priority,start_date, end_date, state'
        sn_change_url = "https://{0}{1}".format(self.sn_url, sn_change_endpoint)
        print("URL: {}".format(sn_change_url))
        proxy1= { 'https': 'http://10.80.40.19:80' }
        sn_change_result = requests.request('GET', sn_change_url, auth=(self.sn_username, self.sn_password), headers=self.servicenow_headers, verify=False, proxies=proxy1)
        sn_change_result.raise_for_status()
        sn_change_requests = sn_change_result.json()['result']
        print("Servicenow change requests are: {}".format(sn_change_requests))
        self.check_change_requests(sn_change_requests)

    def check_change_requests(self, sn_change_requests):
        ''' Create a trigger to run cleanup on any open change requests that are not being processed '''
        chg_st2_key = 'servicenow.change_processing'
        processing_chg_requests = self.st2_client.keys.get_by_name(chg_st2_key)
        print("Processing change requests are: {}".format(processing_chg_requests))
        processing_chg_requests = [] if processing_chg_requests is None else ast.literal_eval(processing_chg_requests.value)
        print("Old change requests are: {}".format(processing_chg_requests))
        for chg in sn_change_requests:
            #Skip any change request that are currnetly being processed
            if chg['number'] in processing_chg_requests:
                print('In continue')
                continue
            else:
                print("In else")
                self._logger.info('Processing change request:' + chg['number'])
                processing_chg_requests.append(chg['number'])
                chg_str = str(processing_chg_requests)
                kvp = KeyValuePair(name=chg_st2_key, value=chg_str)
                self.st2_client.keys.update(kvp)
                print("Check description")
                #trigger payload
                payload = {
                    'chg_id': chg['sys_id'],
                    'number': chg['number']
                    }
                #dispatching the trigger
                print("Dispatching the trigger")
                print("Payload data is: {}".format(payload))
                self._sensor_service.dispatch(trigger='ntt_itsm.servicenow_change_move_to_implementation_in_progress', payload=payload)


    def cleanup(self):
        pass
    def add_trigger(self, trigger):
        pass
    def update_trigger(self, trigger):
        pass
    def remove_trigger(self, trigger):
        pass
