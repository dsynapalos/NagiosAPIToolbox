import clients as CL
import json
import requests as req
import re
from datetime import datetime, timedelta

headers = {'content-type': 'application/json'}
global bandwidth_total, internet_total

def search_logs(event, event_log):
    for item in event_log:
        if event["object_id"] == item["object_id"]:
            return item
    return None


def gather_Bandwidth(start, end):
    global bandwidth_total, internet_total
    band_url = "https://" + CL.Clients[CL.Index]['HOST'] + "/nagiosxi/api/v1/objects/statehistory?starttime=" + str(
        int(start)) + "&endtime=" + str(int(end)) + "&" + "apikey=" + CL.Clients[CL.Index]['API_KEY']

    body = json.dumps({})

    band_request = req.request('GET', url=band_url, data=body, headers=headers, verify=False)

    if band_request.status_code is not 200:
        print('BandWidth request error')
        exit(-1)
    band_content = json.loads(band_request.text)

    tmp = band_content["stateentry"]
    bandwidth_total = 0
    internet_total = 0
    event_log = []
    for event in reversed(tmp):

        if "Bandwidth" in event["service_description"]:
            startPoint = search_logs(event, event_log)
            if event["state"] != "0" and startPoint == None:
                event_log.append(event)
                bandwidth_total += 1
            elif event["state"] == "0" and startPoint != None:
                if (startPoint["service_description"].find("Internet") != -1):
                    if (startPoint["output"].find("Mbps") != -1):

                        splitted = startPoint["output"].split()

                        FMT = '%Y-%m-%d %H:%M:%S'
                        downtimePeriod = datetime.strptime(event["state_time"], FMT) - datetime.strptime(
                        startPoint["state_time"], FMT)
                        if (downtimePeriod > timedelta(minutes=25) or (
                                float(splitted[5][:-4]) > 90 and downtimePeriod > timedelta(minutes=10)) or (
                                float(splitted[7][:-4]) > 90) and downtimePeriod > timedelta(minutes=10)):
                            internet_total += 1

