#!/usr/bion/env python

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

__all__ = ['servicenow_recurring_server_reboot_validation']

class servicenow_recurring_server_reboot_validation(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(servicenow_recurring_server_reboot_validation, self).__init__(sensor_service=sensor_service,
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
        #sn_change_endpoint = '/api/now/table/change_request?sysparm_query=active=true^change_state=2'
        sn_change_endpoint = '/api/now/table/change_request?sysparm_query=active=true^state=6'
        # Commenting the below line as the company id is being changed to Graphic Packaging 
        #sn_change_endpoint = sn_change_endpoint + '^company.sys_id='+self.som_company_sys_id
        sn_change_endpoint = sn_change_endpoint + '^company.sys_id=3a55564c4f4b3ac0e480e3414210c7e2'
        #sn_change_endpoint = sn_change_endpoint + '^priority=3^ORpriority=4'
        #sn_change_endpoint = sn_change_endpoint + '^sys_created_on>=javascript:gs.beginningOfYesterday()'
        #sn_change_endpoint = sn_change_endpoint + "^sys_created_onBETWEENjavascript:gs.dateGenerate('2022-03-20','00:00:00')@javascript:gs.dateGenerate('2022-03-25','23:59:59')"
        #sn_change_endpoint = sn_change_endpoint + "^end_dateRELATIVEGT@hour@ago@18^end_dateRELATIVELT@hour@ago@-18"
        sn_change_endpoint = sn_change_endpoint + '^end_dateRELATIVEGT@minute@ahead@1^end_dateRELATIVELT@minute@ahead@15'
        #sn_change_endpoint = sn_change_endpoint + '^end_date<javascript:gs.minutesAgoStart(-15)'
        #sn_change_endpoint = sn_change_endpoint + '^start_dateRELATIVEGT@hour@ago@24^end_dateRELATIVELT@minute@ahead@15'
        # Changes specific to TR - Automation Autoreboot validation
        #sn_change_endpoint = sn_change_endpoint + '^descriptionLIKEAutoreboot'
        sn_change_endpoint = sn_change_endpoint + '^ANDshort_descriptionLIKE[TR - Automation]'
        sn_change_endpoint = sn_change_endpoint + '&sysparm_fields=number,assignment_group,company,cmdb_ci,description,short_description,sys_id,priority,start_date, end_date, state'
        sn_change_url = "https://{0}{1}".format(self.sn_url, sn_change_endpoint)
        print("URL: {}".format(sn_change_url))
        sn_change_result = requests.request('GET', sn_change_url, auth=(self.sn_username, self.sn_password), headers=self.servicenow_headers, verify=False)
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
                self.check_description(chg)

    def get_company_and_ag_and_ciname(self, chg):
        configuration_item_env = ''
        if chg['assignment_group'] and chg['assignment_group']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=chg['assignment_group']['link'])
            assign_group = response['name']
        else:
            self._logger.info('Assignment Group not found for change: ' + chg['number'])
            assign_group = ''

        if chg['company'] and chg['company']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                   url=chg['company']['link'])
            company = response['name']
        else:
            self._logger.info('Company not found for change: ' + chg['number'])
            company = ''

        if chg['cmdb_ci'] and chg['cmdb_ci']['link']:
            try:
                response = self.base_action.sn_api_call(method='GET',
                                                   url=chg['cmdb_ci']['link'])
                configuration_item_name = response['name']
                configuration_item_env = response['u_environment'].lower()
            except error as e:
                print(e)
                configuration_item_name = ''
                configuration_item_env = ''

        else:
            self._logger.info('Company not found for change: ' + chg['number'])
            configuration_item_name = ''

        return assign_group, company,configuration_item_name,configuration_item_env

    def betweenString(self,value, a, b):
        # Find and validate before-part.
        pos_a = value.find(a)
        if pos_a == -1: return ""
        # Find and validate after part.
        pos_b = value.rfind(b)
        if pos_b == -1: return ""
        # Return middle part.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b: return ""
        return value[adjusted_pos_a:pos_b]

    def afterString(self,value, a):
        # Find and validate first part.
        pos_a = value.rfind(a)
        if pos_a == -1: return ""
        # Returns chars after the found string.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= len(value): return ""
        return value[adjusted_pos_a:]

    def beforeString(self,value, a):
        # Find first part and return slice before it.
        pos_a = value.find(a)
        if pos_a == -1: return ""
        return value[0:pos_a]

    def check_description(self, chg):
        desc = chg['description'].lower()
        short_desc = chg['short_description']
        assign_group, company, configuration_item_name, configuration_item_env = self.get_company_and_ag_and_ciname(chg)
        #if 'autoreboot' in desc:
        if assign_group == '':
            check_uptime = False
            os_type = ''
        else:
            check_uptime = True
            os_type = 'windows' if 'intel' in assign_group.lower() else 'linux'
        
        if "graphicpkg.pri" in desc:
            ci_address_intial = desc.split('graphicpkg.pri')[1].split()[0]
            Find_Between = self.betweenString(ci_address_intial,"(",")")
            ci_address = Find_Between.strip()
        else:
            ci_address = short_desc.split(',')[0].split()[-1]
        payload = {
            'assignment_group': assign_group,
            'ci_address': ci_address,
            'os_type': os_type,
            'configuration_item_name': configuration_item_name,
            'configuration_item_env': configuration_item_env,
            'customer_name': company,
            'detailed_desc': chg['description'],
            'change_id': chg['number'],
            'change_sys_id': chg['sys_id'],
            'short_desc': chg['short_description'],
            'planned_start_date': chg['start_date'],
            'planned_end_date': chg['end_date']
            }
        print("Payload data is: {}".format(payload))
        self._sensor_service.dispatch(trigger='ntt_itsm.recurring_server_reboot_validation', payload=payload)

    def check_ci_address(self, short_desc):
        ip_check = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        ip_format = re.findall(ip_check, short_desc)
        ip_value = []
        ip_address = ''

        for i in ip_format:
            test = i.split('.')
            if len(test) == 4:
                for j in test:
                    if (int(j) >= 0) and (int(j) < 256):
                        ip_value.append(j)
        if len(ip_value) == 4:
            ip_address = self.convert_list_to_string(ip_value)
        return ip_address


    def convert_list_to_string(self, list_elements):
        string_value = ""
        cnt = 0
        for item in list_elements:
            if cnt == 0:
                string_value += item
            else:
                string_value += '.'+item
            cnt += 1
        return string_value


    def cleanup(self):
        pass
    def add_trigger(self, trigger):
        pass
    def update_trigger(self, trigger):
        pass
    def remove_trigger(self, trigger):
        pass

