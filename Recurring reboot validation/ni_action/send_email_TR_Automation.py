#!/usr/bin/env python

from lib.base_action import BaseAction
import smtplib
import email.utils
from email.mime.text import MIMEText

class send_email_TR_Automation(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(send_email_TR_Automation, self).__init__(config)

    def run(self, receiver_emails, message_body, subject):
        port = 25 # verfiy once with the account team
        smtp_server = "155.16.123.161" # varies for different account
        sender_email = "noreply@nttdata.com"
        #receiver_email = "naveenkrishna.meruva@nttdata.com,Sreedevi.AN@nttdata.com" #this should come from the workflow
        receiver_email = receiver_emails
        password = ''
        # message body will be multiline as per the change's output
        messagebody = message_body
        message = MIMEText(messagebody)
        message['TO'] = email.utils.formataddr(('Recipient', receiver_email))
        message['From'] = email.utils.formataddr(('Testing TR Automation Email', sender_email))
        message['Subject'] = subject  #'Test Mail for TR Automation'

        server = smtplib.SMTP(smtp_server, port)
        server.set_debuglevel(True)
        try:
            server.sendmail(sender_email, [receiver_email], message.as_string())
        finally:
            server.quit()
