#!/usr/bin/env python
from lib.base_action import BaseAction
from datetime import datetime
import pytz

class CalculateUptimeThreshold(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(CalculateUptimeThreshold, self).__init__(config)

    def run(self, planned_start_date, uptime, os_flag):
        #print("planned_start_date: ", planned_start_date)
        timesplit = planned_start_date.split("-")
        #snpt = "2022-08-21T23:00:00+0000" # These 3 lines should be removed/commented while testing with live data
        #print("Server Next Patch time is present: ", snpt)
        #timesplit = snpt.split("-")
        time1 = timesplit[2].split(" ")[1].split(":")
        #print(int(timesplit[0]),int(timesplit[1]),int(timesplit[2].split("T")[0]),int(time1[0]), int(time1[1]), int(time1[2].split("+")[0]))
        changestarttime = datetime(int(timesplit[0]),int(timesplit[1]),int(timesplit[2].split(" ")[0]),int(time1[0]), int(time1[1]), int(time1[2].split("+")[0].split(".")[0]))
        #print(changestarttime)
        #converting to GMT and substracting from current time
        #timediffGMT = (datetime.now()).astimezone(pytz.timezone('GMT')) - changestarttime.astimezone(pytz.timezone('GMT'))
        #without converting to GMT
        gmtcurrenttime = datetime.now(pytz.timezone('GMT'))
        current_time_without_timezone = gmtcurrenttime.replace(tzinfo=None)
        timediff = current_time_without_timezone - changestarttime
        #print("time difference in GMT: ", timediffGMT, "time difference: ", timediff)
        #check the os type
        if os_flag == 1:
            uptimeinseconds = float(uptime) * 60
        else:
            #Doing the string manupulation for linux output which contains two values
            twovaluesuptime = uptime.split(" ")
            if len(twovaluesuptime) > 1:
                uptimeinseconds = float(twovaluesuptime[0])
            else:
                uptimeinseconds = float(uptime)
        uptimehours = round((uptimeinseconds/3600),4)
        thresholdhours = round((timediff.total_seconds()/3600),4)
        if uptimeinseconds > timediff.total_seconds():
            print(str(uptimehours)," hours which is more than Threshold value ", str(thresholdhours)," The server was not rebooted.")
            uptimeflag = 0
        else:
            print(str(uptimehours)," hours which is less than Threshold value", str(thresholdhours)," The server was successfully rebooted.")
            uptimeflag = 1

        return uptimeflag
