#!/usr/bin/env python

from lib.base_action import BaseAction
import requests
from time import sleep

class ServiceNowGetAndCloseChangeTasks(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowGetAndCloseChangeTasks, self).__init__(config)

    def run(self, number, company, assignment_group, assigned_to, performance_rating, worknotes, u_test_results , chg_id):
        self.sn_username = self.config['servicenow']['username']
        self.sn_password = self.config['servicenow']['password']
        flag = 0
        assigned_to = "Integration Approver"
        while flag < 2:
            flag = flag + 1
            #payload_details
            method= 'GET'
            endpoint= '/api/sn_chg_rest/change/'+ chg_id +'/task'
            payload={
                "number": number,
                "company" : company
                }
            print("change request number is: ",number)
            # change the below URL when moving it to prod
            url = "hiltonuat.service-now.com"
            sn_url = "https://{0}{1}".format(url, endpoint)
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json'}
            try:
                #response = requests.request(method, sn_url, auth=(self.sn_username, self.sn_password), json=payload, headers=headers, verify=False)
                response = self.sn_api_call(method, endpoint, payload=payload)
            except Exception as e0:
                print(e0)

            print("Output is: {}".format(response.text))
            changetasks = []
            if response.status_code == 200:
                api_output = response.json()
                print(api_output["result"])
                for change_task in api_output["result"]:
                    ctasknumber = change_task["Number"]["value"].strip()
                    ctasksys_id = change_task["sys_id"]["value"].strip()
                    #print(ctasknumber)
                    if "Closed" in change_task['state']['display_value']:
                        print(change_task["Number"]["value"], "is closed, hence will not be picked up for closure again.")
                    else:
                        print(change_task["Number"]["value"], "is not closed")
                        # closing the change task
                        if performance_rating == 4:
                          # closing the change task as successful
                          method= 'PATCH'
                          endpoint= '/api/sn_chg_rest/change/' + chg_id + '/task/' + ctasksys_id
                          payload={
                              'assigned_to': "Automation UAT Service",
                              'u_performance_rating': performance_rating,
                              'work_notes': worknotes,
                              "state": 3,
                              "close_code": 4
                              }
                        else:
                          # closing the change task as failure
                          method= 'PATCH'
                          endpoint= '/api/sn_chg_rest/change/' + chg_id + '/task/' + ctasksys_id
                          payload={
                              'assigned_to': "Automation UAT Service",
                              'u_performance_rating': performance_rating,
                              'work_notes': worknotes,
                              "state": 3,
                              "close_code": 4
                              }
                        sn_url = "https://{0}{1}".format(url, endpoint)
                        try:
                            #response1 = requests.request(method, sn_url, auth=(self.sn_username, self.sn_password), json=payload, headers=headers, verify=False)
                            response1 = self.sn_api_call(method, endpoint, payload=payload)
                        except Exception as e:
                            print(e)
                        sleep(5)
                        print("Ctask {} closure Output is: {}".format(ctasknumber, response1.text))
                        changetasks.append(change_task["Number"]["value"])
        # Proceeding with the change closure
        if performance_rating == 4:
          # close change as successful
          method= 'PATCH'
          endpoint = '/api/now/table/change_request/' + chg_id
          payload = {
              "state": 5,
              "close_code": 4
              }
        else:
          # close change as failed
          method= 'PATCH'
          endpoint = '/api/now/table/change_request/' + chg_id
          payload = {
              "state": 5,
              "close_code": 4
              }
        sn_url = "https://{0}{1}".format(url, endpoint)
        #response = requests.request(method, sn_url, auth=(self.sn_username, self.sn_password), json=payload, headers=headers, verify=False)
        response = self.sn_api_call(method, endpoint, payload=payload)
        print("Output is: {}".format(response.text))
        return changetasks
