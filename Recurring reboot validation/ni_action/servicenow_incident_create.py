from lib.base_action import BaseAction

class ServiceNowCreateIncident(BaseAction):

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowCreateIncident, self).__init__(config)


    def run(self,company,requested_by,short_description,description,cmdb_ci,category,subcategory,assignment_group,impact):
        
        # REST API URL
        # endpoint = '/api/now/table/incident?sysparm_fields=number'
        # scripted/Customized API for NTT Data
        #endpoint = '/api/ntt11/incident_automation_stackstorm/CreateIncident'
        endpoint = '/api/now/table/incident'
        
        # the below input fields only for Rest API
        # 'requested_by': requested_by,
        
        payload = {
                'u_requested_by': 'Automation UAT Service',
                'short_description': short_description,
                'description': description,
                'cmdb_ci': cmdb_ci,
                'category' : category,
                'subcategory' : subcategory,
                'assignment_group': assignment_group,
                'impact': impact,
                'urgency': 4
            }

        inc = self.sn_api_call('POST', endpoint, payload=payload)
        #inc = ""
        return inc
