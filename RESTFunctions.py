import DataBase as DB
import requests as req
import json
import urllib3
import re
from pandas import *
from datetime import datetime,timedelta
import os


import clients as CL
import CSVFunctions as CO
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
minimum = False


def applyConf(serverName):
    ''' Applies the configuration in Nagios XI

    :param serverName: Server ID.
    :return:
    '''
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/system/applyconfig?apikey=' + \
          DB.serverList[serverName]['apikey']
    print(req.request('POST', url, verify=False).text)


def putServiceConfig(change, service, host, serverName):
    """ Applies a change to the configuration of a Service

    :param change: Change to be made
    :param service: Service to be modified
    :param host: Host of Service
    :param serverName: Server ID
    :return: Request text
    """
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service/' \
          + host + '/' + service + '?apikey=' + DB.serverList[serverName]['apikey'] + change
    b = req.request('PUT', url + '&pretty=1&applyconfig=1', verify=False)

    return b.text.strip()


def createCheckService(serverName, hostList):
    """ Create the Service for the Check Cisco monitoring OID

    :param serverName: Server ID
    :param hostList: List of hosts to be added to service
    :return: Dictionary of results
    """
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey']

    body = {
        'config_name': 'Check CPU',
        'host_name': hostList,
        'service_description': 'Check CPU',
        'check_command': 'check_cisco_custom\!' + DB.serverList[serverName]['comm'] + '\!cpu\!-w 75 -c 85',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    cpu = req.request('POST', url, data=body, verify=False).text.strip()

    body = {
        'config_name': 'Check MEM',
        'host_name': hostList,
        'service_description': 'Check MEM',
        'check_command': 'check_cisco_custom\!' + DB.serverList[serverName]['comm'] + '\!mem\!-w 15 -c 5',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    mem = req.request('POST', url, data=body, verify=False).text.strip()

    body = {
        'config_name': 'Check PSU',
        'host_name': hostList,
        'service_description': 'Check PSU',
        'check_command': 'check_cisco_custom\!' + DB.serverList[serverName]['comm'] + '\!ps\!-w 1 -c 1',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    psu = req.request('POST', url, data=body, verify=False).text.strip()

    body = {
        'config_name': 'Check FAN',
        'host_name': hostList,
        'service_description': 'Check FAN',
        'check_command': 'check_cisco_custom\!' + DB.serverList[serverName]['comm'] + '\!fan\!-w 1 -c 2',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    fan = req.request('POST', url, data=body, verify=False).text.strip()

    body = {
        'config_name': 'Check TEMP',
        'host_name': hostList,
        'service_description': 'Check TEMP',
        'check_command': 'check_cisco_custom\!' + DB.serverList[serverName]['comm'] + '\!temp\!-w 50 -c 70',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    temp = req.request('POST', url, data=body, verify=False).text.strip()

    return {'CPU': cpu,
            'MEM': mem,
            'PSU': psu,
            'TEMP': temp,
            'FAN': fan, }


def createPingService(serverName, hostName):
    """ Creates the Ping service for a host

    :param serverName: Server ID
    :param hostName: Host ID
    :return: Result
    """
    body = {
        'host_name': hostName,
        'service_description': 'Ping',
        'check_command': 'check_ping\!3000,80%\!5000,100%',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey']
    request = req.request('POST', url, data=body, verify=False).text
    return request


def createBandwidthService(serverName, hostName, hostip, intDesc, intAlias, activeInterface, values, scale):
    """ Creates the Bandwidth service for a particular Interface

    :param serverName: Server ID
    :param hostName: Host ID
    :param hostip: IP of host
    :param intDesc: Interface Description
    :param intAlias: Interface Alias
    :param activeInterface: Interface Index number
    :param values: Limit Values
    :param scale: Scale in mega,kilo or bytes
    :return: Result in text
    """
    if len(values) == 2:
        wd, wu, cd, cu = values[0], values[0], values[1], values[1]
    else:
        wd, wu, cd, cu = values[0], values[1], values[2], values[3]

    body = {
        'host_name': hostName,
        'service_description': intDesc + ' ' + intAlias + ' Bandwidth',
        'check_command': 'check_xi_service_mrtgtraf!' + hostip + '_' + activeInterface + '.rrd!' + str(wd) + ',' + str(
            wu)
                         + '!' + str(cd) + ',' + str(cu) + '!' + scale,
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 60,
        'notification_period': '24x7'
    }

    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey']
    request = req.request('POST', url, data=body, verify=False).text
    return request


def createStatusService(serverName, hostName, intDesc, intAlias, activeInterface):
    """ Creates the Status service for a particular Interface

    :param serverName: Server ID
    :param hostName: Host ID
    :param intDesc: Interface Description
    :param intAlias: Interface Alias
    :param activeInterface: Interface Index number
    :return: Result in text
    """
    body = {
        'host_name': hostName,
        'service_description': intDesc + ' ' + intAlias + ' Status',
        'check_command': 'check_xi_service_ifoperstatus!' + DB.serverList[serverName][
            'comm'] + '!' + activeInterface + '!-v 2 -p 161',
        'check_interval': 5,
        'retry_interval': 1,
        'max_check_attempts': 5,
        'check_period': '24x7',
        'contacts': 'nagiosadmin',
        'notification_interval': 6,
        'notification_period': '24x7'
    }
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey']
    request = req.request('POST', url, data=body, verify=False).text
    return request


def getServiceConfig(service, host, serverName):
    ''' Returns the configuration of a particular service.

    :param service: Service Description.
    :param host: Config Name.
    :param serverName: Server ID.
    :return: String.
    '''
    url = 'https://' + CL.Clients[CL.Index]['HOST'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          CL.Clients[CL.Index]['API_KEY'] + '&config_name=' + host \
          + '&service_description=' + service + '&pretty=1'
    return req.request('GET', url, verify=False).text


def getAllHostsList(serverName):
    ''' Returns the hosts in a server.

    :param serverName: Server ID.
    :return: List.
    '''
    print('Getting hosts')
    hostList = []
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/objects/hoststatus?apikey=' + \
          DB.serverList[serverName]['apikey'] + '&pretty=1'
    for host in json.loads(req.request('GET', url, verify=False).text)['hoststatus']:
        hostList.append(host['name'])
    return sorted(hostList)


def getHostsbyService(serverName, service, toggle=True):
    ''' Returns the hosts registered into a service.

    :param serverName: Server ID.
    :param service: Service Description.
    :param toggle: True (Default) for included, False for Excluded hosts.
    :return: List.
    '''
    allHosts = getAllHostsList(serverName)
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey'] + '&pretty=1' + '&config_name=' + service

    checkHosts = json.loads(req.request('GET', url, verify=False).text)[0]['host_name']
    checkHostList = []
    for host in allHosts:
        if toggle == True:
            if host in checkHosts and host != 'localhost':
                checkHostList.append(host)
        else:
            if host not in checkHosts and host != 'localhost':
                checkHostList.append(host)
    return checkHostList


def getHostIP(serverName, hostName):
    ''' Returns the IP of a server.

    :param serverName: Server ID.
    :param hostName: Host Name
    :return: String.
    '''
    msg = 'Host not Found'
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/objects/host?apikey=' + \
          DB.serverList[serverName]['apikey'] + '&pretty=1'
    for host in json.loads(req.request('GET', url, verify=False).text)['host']:
        if host['host_name'] == hostName:
            return host['address']
        else:
            continue
    return msg


def getAllServiceConfigs(serverName, hostList=[]):
    ''' Returns the config of every service on a list of hosts.

    :param serverName: Server ID.
    :param hostList: List of Host Names (Default empty list for every host).
    :return: Dict.
    '''
    serviceList = {}
    print('Getting services by host')
    if hostList == []:
        hostList = getAllHostsList(serverName)
    for host in hostList:
        url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
              DB.serverList[serverName]['apikey'] + '&pretty=1&config_name=' + host
        request = req.request('GET', url, verify=False).text
        services = json.loads(request)
        for config in services:
            try:
                if config['config_name'] in serviceList:
                    serviceList[config['config_name']].append(config['service_description'])
                else:
                    serviceList[config['config_name']] = [config['service_description']]
            except:
                continue
    return serviceList


def getServiceByKeyword(serverName, keywords=[[], []], hostlist=[]):
    ''' Returns dictionary of service configs, selected by keyword.

    :param serverName: Server ID.
    :param keywords: List of lists of Keywords (Default list of empty lists for every service).
                     First internal list should contain desirable keywords and second internal list should contain
                     undesirable keywords. The logical function is OR in both occasions.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return: Dict
    '''
    keywordList = keywords[0]
    keywordNOTList = keywords[1]
    keyList = {}
    keyNotList = {}
    finalList = {}
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    servicelist = getAllServiceConfigs(serverName, hostlist)
    print('Managing keywords')
    try:
        for keyword in keywordList:
            keySubList = {}
            for host in servicelist.keys():
                for service in servicelist[host]:

                    if re.search(keyword, service):
                        if host in keySubList:
                            keySubList[host].append(service)
                        else:
                            keySubList[host] = [service]
            if keyword in keyList:
                keyList[keyword].append(keySubList)
            else:
                keyList[keyword] = [keySubList]
    except:
        pass
    try:
        for keyword in keywordNOTList:
            keySubList = {}
            for host in servicelist.keys():
                for service in servicelist[host]:

                    if re.search(keyword, service):
                        if host in keySubList:
                            keySubList[host].append(service)
                        else:
                            keySubList[host] = [service]

            if keyword in keyList:
                keyNotList[keyword].append(keySubList)
            else:
                keyNotList[keyword] = [keySubList]
    except:
        pass

    for host in hostlist:
        try:
            for service in servicelist[host]:
                correct = 0
                for key in keyList:
                    try:
                        if service in keyList[key][0][host]:
                            correct += 1
                        else:
                            correct = 0
                            break

                        for key in keyNotList:
                            if service not in keyNotList[key][0][host] and correct != 0:
                                continue
                            else:
                                correct = 0
                                break
                    except:
                        correct = 0
                if correct == len(keyList.values()):
                    if host in finalList:
                        finalList[host].append(service)
                    else:
                        finalList[host] = [service]
        except:
            continue

    print('Keyword-dependant service list collected')
    print(finalList)
    return finalList


def changeSelectedServices(server, keyword, values, change='bandlimits', hostlist=[]):
    ''' Makes a change to a list of services. Implemented to change Bandwidth Monitoring service's Notification values.
        Values supplied should follow a format of [WarningDown, WarningUp, CriticalDown, CriticalUp].

    :param server: Server ID.
    :param keyword: List of lists of Keywords.
    :param values: Values of changes to be implemented.
    :param change: Type of change to be implemented.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    servicelist = getServiceByKeyword(server, keyword, hostlist)
    if hostlist == []:
        hostlist = list(servicelist.keys())
    results = {}
    for host in hostlist:
        for service in servicelist[host]:

            runnConfig = getServiceConfig(service, host, server)
            a = re.search('^check_xi_service_mrtgtraf!(.+rrd)\!(.+)\!(.+)\!(.)',
                          json.loads(runnConfig)[0]['check_command'])
            if a.group(3) == '!':
                warn, crit, scale = re.search('(.+)!(.+)!(.)', a.group(2)).group(1), \
                                    re.search('(.+)!(.+)!(.)', a.group(2)).group(2), \
                                    re.search('(.+)!(.+)!(.)', a.group(2)).group(3)
            else:
                warn, crit, scale = a.group(2), a.group(3), a.group(4)

            b = re.search('(.+),(.+)', warn)
            c = re.search('(.+),(.+)', crit)

            if b == None:
                warnDown, warnUp = float(warn), float(warn)
            else:
                warnDown, warnUp = float(b.group(1)), float(b.group(2))

            if c == None:
                critDown, critUp = float(crit), float(crit)
            else:
                critDown, critUp = float(c.group(1)), float(c.group(2))

            if scale in ['K', 'k']:
                s = 1000
            elif scale in ['B', 'b']:
                s = 1000000
            else:
                s = 1
            if values[0] == '': values[0] = warnDown
            if values[1] == '': values[1] = warnUp
            if values[2] == '': values[2] = critDown
            if values[3] == '': values[3] = critUp

            if change == 'bandlimits':
                config = '&check_command=check_xi_service_mrtgtraf!' + a.group(1) + '!' + str(values[0] * s) + ',' \
                         + str(values[1] * s) + '!' + str(values[2] * s) + ',' + str(values[3] * s) + '!' + scale
                print(putServiceConfig(config, service, host, server))
                print(config)
                print(getServiceConfig(service, host, server))


def setMinimumLimits(server, keyword, values, hostlist=[]):
    ''' Sets minimum Bandwidth Monitoring service's Notification values. Values supplied should follow a format of 
        [WarningDown, WarningUp, CriticalDown, CriticalUp].

    :param server: Server ID.
    :param keyword: List of lists of Keywords.
    :param values: Minimum values in.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    servicelist = getServiceByKeyword(server, keyword, hostlist)
    if hostlist == []:
        hostlist = list(servicelist.keys())
    resplist = []
    results = {}
    for host in hostlist:
        try:
            results[host] = []
            for service in servicelist[host]:

                print(service)
                runnConfig = getServiceConfig(service, host, server)
                a = re.search('^check_xi_service_mrtgtraf!(.+rrd)\!(.+)\!(.+)\!(.)',
                              json.loads(runnConfig)[0]['check_command'])

                if a.group(3) == '!':
                    warn, crit, scale = re.search('(.+)!(.+)!(.)', a.group(2)).group(1), \
                                        re.search('(.+)!(.+)!(.)', a.group(2)).group(2), \
                                        re.search('(.+)!(.+)!(.)', a.group(2)).group(3)
                else:
                    warn, crit, scale = a.group(2), a.group(3), a.group(4)

                b = re.search('(.+),(.+)', warn)
                c = re.search('(.+),(.+)', crit)
                if b == None:
                    warnDown, warnUp = float(warn), float(warn)
                else:
                    warnDown, warnUp = float(b.group(1)), float(b.group(2))

                if c == None:
                    critDown, critUp = float(crit), float(crit)
                else:
                    critDown, critUp = float(c.group(1)), float(c.group(2))
                if scale in ['K', 'k']:
                    s = 1000
                elif scale in ['B', 'b']:
                    s = 1000000
                else:
                    s = 1

                if minimum:
                    config = '&check_command=check_xi_service_mrtgtraf!' + a.group(1) + '!' \
                             + str(min(values[0] * s, warnDown)) + ',' \
                             + str(min(values[1] * s, warnUp)) + '!' \
                             + str(min(values[2] * s, critDown)) + ',' \
                             + str(min(values[3] * s, critUp)) + '!' + scale
                else:
                    config = '&check_command=check_xi_service_mrtgtraf!' + a.group(1) + '!' \
                             + str(values[0] * s) + ',' \
                             + str(values[1] * s) + '!' \
                             + str(values[2] * s) + ',' \
                             + str(values[3] * s) + '!' + scale

                resp = putServiceConfig(config, service, host, server)
                print(resp)
                resplist.append(resp[7:-4])
                results[host].append({service: {'oldvalues': [warnDown, warnUp, critDown, critUp],
                                                'newvalues': [values[0] * s, values[1] * s, values[2] * s,
                                                              values[3] * s],
                                                'scale': scale
                                                }})
        except:
            continue
        print(resplist)

    return results


def displaySelectedServices(server, keyword, hostlist=[]):
    ''' Displays, returns and exports a dictionary of services.

    :param server: Server ID.
    :param keyword: List of lists of Keywords.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return: Dictionary
    '''
    resultdict = {}
    index = 0
    servicelist = getServiceByKeyword(server, keyword, hostlist)
    if hostlist == []:
        hostlist = list(servicelist.keys())
    print('Parsing results')
    for host in hostlist:
        for service in servicelist[host]:
            try:
                runnConfig = getServiceConfig(service, host, server)

                a = re.search('^check_xi_service_mrtgtraf!(.+rrd)\!(.+)\!(.+)\!(.)',
                              json.loads(runnConfig)[0]['check_command'])
                if a.group(3) == '!':
                    warn, crit, scale = re.search('(.+)!(.+)!(.)', a.group(2)).group(1), \
                                        re.search('(.+)!(.+)!(.)', a.group(2)).group(2), \
                                        re.search('(.+)!(.+)!(.)', a.group(2)).group(3)
                else:
                    warn, crit, scale = a.group(2), a.group(3), a.group(4)

                b = re.search('(.+),(.+)', warn)
                c = re.search('(.+),(.+)', crit)

                if b == None:
                    warnDown, warnUp = float(warn), float(warn)
                else:
                    warnDown, warnUp = float(b.group(1)), float(b.group(2))

                if c == None:
                    critDown, critUp = float(crit), float(crit)
                else:
                    critDown, critUp = float(c.group(1)), float(c.group(2))

                if scale in ['K', 'k']:
                    s = 1000
                elif scale in ['B', 'b']:
                    s = 1000000
                else:
                    s = 1
            except:
                continue
            index += 1
            resultdict[index] = {
                'Host': host,
                'Service': service,
                'WarningDown': warnDown,
                'WarningUp': warnUp,
                'CritDown': critDown,
                'CritUp': critUp,
                'Scale': scale,
                'MBScaledWarningDown': warnDown / s,
                'MBScaledWarningUp': warnUp / s,
                'MBScaledCritDown': critDown / s,
                'MBScaledCritUp': critUp / s}

    res = DataFrame.from_records(resultdict, index=['Host', 'Service', 'WarningDown', 'WarningUp', 'CritDown', 'CritUp',
                                                    'Scale', 'MBScaledWarningDown', 'MBScaledWarningUp',
                                                    'MBScaledCritDown', 'MBScaledCritUp']).T
    res.to_excel('Excel.xlsx')
    print('Results where also exported in a Results.xlsx file in the working directory.')
    return resultdict


def getServiceConfigbyFile(serverName, file):
    ''' Returns a dictionary of service configurations from a file of hosts and services.

    :param serverName: Server ID.
    :param file: Excel file of Hosts and Services.
    :return: Dictionary
    '''
    xls = ExcelFile(file)

    configList = {}
    df = xls.parse(xls.sheet_names[0]).to_dict()

    for count in range(1, len(df['Host'])):
        url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' \
              + DB.serverList[serverName]['apikey'] + '&pretty=1&config_name=' \
              + df['Host'][count] + '&service_description=' + df['Service'][count]
        request = req.request('GET', url, verify=False).text
        services = json.loads(request)
        for config in services:
            try:
                if config['config_name'] in configList:
                    configList[config['config_name']].append(config['service_description'])
                else:
                    configList[config['config_name']] = [config['service_description']]
            except:
                continue
        return configList


def removeHostfromService(serverName, service, hostlist=[]):
    ''' Excludes a list of Hosts from a Service

    :param serverName: Server ID.
    :param hostlist: List of Host Names (Default empty list for every host).
    :param service: Config Name
    :return:
    '''
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
          DB.serverList[serverName]['apikey'] + '&pretty=1&config_name=' + service
    request = req.request('GET', url, verify=False).text

    services = json.loads(request)
    for host in hostlist:
        if host in services[0]['host_name']:
            if len(services[0]['host_name']) == 1:
                services[0]['host_name'] = '*'
            else:
                services[0]['host_name'] = services[0]['host_name'].remove(host)
    print(services[0])
    print(service)
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service/' + services[0]['config_name'] \
          + '/' + services[0]['service_description'] + '?apikey=' + DB.serverList[serverName]['apikey'] \
          + '&host_name=' + str(services[0]['host_name']) + '&pretty=1&applyconfig=1'
    print(req.request('PUT', url, verify=False).text)


def findManualServices(serverName):
    ''' Returns a dictionary of manually implemented services (services with config_name differing from hostnames).

    :param serverName: Server ID.
    :return: Dictionary.
    '''
    manualServices = []
    hostlist = getAllHostsList(serverName)
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' \
          + DB.serverList[serverName]['apikey'] + '&pretty=1'
    serviceConfigs = json.loads(req.request('GET', url, verify=False).text)
    for item in serviceConfigs:
        if item['config_name'] not in hostlist:
            manualServices.append(item['config_name'])
    return manualServices


def deleteHostServices(serverName, hostlist=[]):
    ''' Deletes the automatically implemented services of a host.

    :param serverName: Server ID.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    for service in findManualServices(serverName):
        removeHostfromService(serverName, service, hostlist=hostlist)
    oblist = getAllServiceConfigs(serverName, hostlist)
    for host in oblist.keys():
        for service in oblist[host]:
            print(req.request('GET', 'http://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service' \
                                                                                   '?apikey='
                              + DB.serverList[serverName]['apikey'] + '&pretty=1&config_name=' \
                              + host + '&service_description=' + service + '&pretty=1', verify=False).text)

            url = 'http://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service' \
                                                                '?apikey=' + DB.serverList[serverName][
                      'apikey'] + '&pretty=1&host_name=' \
                  + host + '&service_description=' + service + '&applyconfig=1'
            servrequest = req.request('DELETE', url, verify=False).text
            print(servrequest)


def deleteHosts(serverName, hostlist=[]):
    ''' Deletes a list of hosts.

    :param serverName: Server ID.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    deleteHostServices(serverName, hostlist)
    strhost = ''

    for host in hostlist:
        strhost = strhost + ('&host_name[]=' + host)
    url = 'http://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/host' \
                                                        '?apikey=' + DB.serverList[serverName][
              'apikey'] + strhost + '&applyconfig=1'
    print(url)
    hostrequest = req.request('DELETE', url, verify=False).text
    print(hostrequest)


def createHost(serverName, hostName, ipAddr):
    ''' Creates a host.

    :param serverName: Server ID.
    :param hostName: Host Name.
    :param ipAddr: IP of host.
    :return:
    '''
    hostTemplate = {
        "host_name": hostName,
        "use": [
            "xiwizard_switch_host"
        ],
        "address": ipAddr,
        "parents": [
            ''
        ],
        "max_check_attempts": "5",
        "check_interval": "5",
        "retry_interval": "1",
        "check_period": "xi_timeperiod_24x7",
        "contacts": [
            "nagiosadmin"
        ],
        "contact_groups": [
            "xi_contactgroup_all"
        ],
        "notification_interval": "60",
        "notification_period": "xi_timeperiod_24x7",
        "notes": '',
        "icon_image": "switch.png",
        "statusmap_image": "switch.png",
        "_xiwizard": "switch",
        "register": "1"
    }

    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/host?apikey=' + \
          DB.serverList[serverName]['apikey']
    request = req.request('POST', url, data=hostTemplate, verify=False).text
    return request


def addHosttoCheckService(serverName, hostlist=[]):
    ''' Adds a host to the list of Check services.

    :param serverName: Server ID.
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    servicelist = {}
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/command?apikey=' + \
          DB.serverList[serverName]['apikey'] + '&pretty=1&command_name=Check_cisco_custom'
    if req.request('GET', url, verify=False).text[0:8] == "[\n    \n]":
        url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/command?apikey=' + \
              DB.serverList[serverName]['apikey'] + '&pretty=1"'
        body = {'command_name': 'Check_cisco_custom',
                'command_line': '/usr/local/nagios/libexec/check_cisco.pl -H $HOSTADDRESS$ -C $ARG1$ -t $ARG2$ $ARG3$',
                'applyconfig': '1'}
    else:
        pass

    for name in ['Check Cpu', 'Check Mem', 'Check Temp', 'Check Fan', 'Check Psu']:
        changetoggle = 0
        url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' + \
              DB.serverList[serverName]['apikey'] + '&pretty=1&config_name=' + name
        check = req.request('GET', url, verify=False).text

        if check[0:8] == "[\n    \n]":

            servicelist[name] = {'config_name': name,
                                 'host_name': hostlist,
                                 'service_description': name,
                                 'check_command': 'Check_cisco_custom!' + DB.serverList[serverName]['comm'] +
                                                  DB.checkcommand[name],
                                 'max_check_attempts': '5',
                                 'check_period': '24x7',
                                 'notification_period': '24x7',
                                 'register': '1',
                                 'check_interval': '5',
                                 'retry_interval': '5',
                                 'notification_interval': '5',
                                 'contacts': 'nagiosadmin',
                                 'applyconfig': '1'}

            url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service?apikey=' \
                  + DB.serverList[serverName]['apikey'] + '&pretty=1&applyconfig=1'

            request = req.request('POST', url, data=servicelist[name], verify=False).text
            print(request)

        else:

            serviceHosts = json.loads(check)
            for host in hostlist:
                if host not in serviceHosts[0]['host_name']:
                    changetoggle = 1
                    serviceHosts[0]['host_name'].append(host)
            if changetoggle == 1:
                url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/service/' \
                      + serviceHosts[0]['config_name'] + '/' + serviceHosts[0]['service_description'] + '?apikey=' \
                      + DB.serverList[serverName]['apikey'] + '&host_name=' \
                      + str(serviceHosts[0]['host_name'])[1:-1].replace(' ', '').replace("'", '') \
                      + '&pretty=1&applyconfig=1'

                request = req.request('PUT', url, verify=False).text
                print(request)


def findWarnings(serverName, hostlist=[]):
    ''' Produces an Excel log of recent warnings
    
    :param serverName: Server ID
    :param hostlist: List of Host Names (Default empty list for every host).
    :return:
    '''
    if hostlist == []:
        hostlist = getAllHostsList(serverName)
    instancelist = {}
    for host in hostlist:

        url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/objects/statehistory?apikey=' \
              + DB.serverList[serverName]['apikey'] + '&host_name=' + host + '&pretty=1'
        request = req.request('GET', url, verify=False).text
        services = []
        try:

            for change in json.loads(request)["stateentry"]:
                services.append(change['service_description'])
            instancelist[host] = {}

        except:
            continue
        uservices = []

        for item in services:
            if (item not in uservices) and (item != {}):
                uservices.append(item)
        for service in uservices:
            for item in json.loads(request)["stateentry"]:
                if item['service_description'] == service:
                    try:
                        instancelist[host][service] += 1
                    except:
                        instancelist[host][service] = 1
    newinstancelist = {}
    with open('temp.txt', 'w', newline='') as wr:
        wr.write('host|service|number of warnings\n')
        for host in instancelist.keys():
            for service in instancelist[host]:
                wr.write(host + '|' + service + '|' + str(instancelist[host][service]) + '\n')
                newinstancelist[host + ' / ' + service] = instancelist[host][service]

    print(json.dumps(newinstancelist, indent=4))

    df = read_csv('temp.txt', delimiter='|')
    with ExcelWriter('Out.xlsx') as writer:
        df.to_excel(writer, sheet_name='CorrectDataSheet', index=False)
    os.remove('temp.txt')


def createCheckCustomCommand(serverName):
    ''' Implements a service to check cpu, memory, psu, fan and temperature values returned by Cisco networking hosts.
    
    :param serverName: Server ID
    :return: Request Response
    '''
    body = {
        'command_name': 'check_cisco_custom',
        'command_line': '/usr/local/nagios/libexec/check_cisco.pl -H $HOSTADDRESS$ -C $ARG1$ -t $ARG2$ $ARG3$'
    }
    url = 'https://' + DB.serverList[serverName]['ip'] + '/nagiosxi/api/v1/config/command?apikey=' + \
          DB.serverList[serverName]['apikey']
    request = req.request('POST', url, data=body, verify=False).text
    return request


def getFullStateHistory(customer,start,end):
    headers = {'content-type': 'application/json'}
    url = "https://" + CL.Clients[CL.Index]['HOST'] + "/nagiosxi/api/v1/objects/statehistory?apikey=" + \
          CL.Clients[CL.Index]['API_KEY'] + "&starttime=" + str(int(start)) + "&endtime=" + str(int(end))

    response = req.request("GET", url, headers=headers, verify=False)

    # print(response.status_code)
    # print(url)
    # print(response.text)

    json_data = json.loads(response.text)
    if json_data["recordcount"] == "0":
        print("No entries", json_data)
        exit()
    stateEntries = json_data["stateentry"]

    return stateEntries


def getBandwidthScale(customer,host,service):

    runnConfig = getServiceConfig(service, host, customer)
    a = re.search('^check_xi_service_mrtgtraf!(.+rrd)\!(.+)\!(.+)\!(.)',
                  json.loads(runnConfig)[0]['check_command'])
    if a.group(3) == '!':
        warn, crit, scale = re.search('(.+)!(.+)!(.)', a.group(2)).group(1), \
                            re.search('(.+)!(.+)!(.)', a.group(2)).group(2), \
                            re.search('(.+)!(.+)!(.)', a.group(2)).group(3)
    else:
        warn, crit, scale = a.group(2), a.group(3), a.group(4)

    scaleText="< >"

    if scale in ['B', 'b']:
        scaleText = 'B/s'
    elif scale in ['K', 'k']:
        scaleText = 'Kb/s'
    elif scale in ['M', 'm']:
        scaleText = 'Mb/s'
    elif scale in ['G', 'g']:
        scaleText = 'Gb/s'


    return scaleText


downtime = []
internetBandwidth = []

def getAllHostsAvailability(customer, start, end):
    headers = {'content-type': 'application/json'}
    url = "https://" + CL.Clients[CL.Index]['HOST'] + "/nagiosxi/api/v1/objects/hostavailability?apikey=" + \
          CL.Clients[CL.Index]['API_KEY'] + "&starttime=" + str(int(start)) + "&endtime=" + str(int(end))

    response = req.request("GET", url, headers=headers, verify=False)

    json_data = json.loads(response.text)
    allHostsList = json_data["hostavailability"]
    count = 0
    up = 0
    down = 0
    unreachable = 0
    hostAvail={}
    for host in allHostsList:
        up += float(host["percent_total_time_up"])
        unreachable += float(host["percent_total_time_unreachable"])
        down += float(host["percent_total_time_down"])
        count+=1
        hostAvail[host["host_name"]]={}
        hostAvail[host["host_name"]]["up"] = host["percent_total_time_up"]
        hostAvail[host["host_name"]]["down"] = host["percent_total_time_down"]


    meanUP=up/count
    meanUnreachable=unreachable/count
    meanDown=down/count

    return meanUP, meanUnreachable, meanDown, count, hostAvail
def getAllServicesAvailability(customer, start, end):
    headers = {'content-type': 'application/json'}
    url = "https://" + CL.Clients[CL.Index]['HOST'] + "/nagiosxi/api/v1/objects/serviceavailability?apikey=" + \
          CL.Clients[CL.Index]['API_KEY'] + "&starttime=" + str(int(start)) + "&endtime=" + str(int(end))

    response = req.request("GET", url, headers=headers, verify=False)

    json_data = json.loads(response.text)
    allServicesList = json_data["serviceavailability"]
    count = 0
    ok = 0
    warning = 0
    critical = 0
    for service in allServicesList:
        ok += float(service["percent_total_time_ok"])
        warning += float(service["percent_total_time_warning"])
        critical += float(service["percent_total_time_critical"])
        count += 1

    meanOK = ok/count
    meanWwarning = warning/count
    meanCritical = critical/count
    return meanOK, meanWwarning, meanCritical, count

def searchIfExists(alert, matrix):
    for e in matrix:
        if alert["object_id"] == e["object_id"]:
            return e
    return None
def getHostAvailability(customer, start, end, host):
    headers = {'content-type': 'application/json'}
    url = "https://" + CL.Clients[CL.Index]['HOST'] + "/nagiosxi/api/v1/objects/hostavailability?apikey=" + \
          CL.Clients[CL.Index]['API_KEY'] + "&host=" + host + "&starttime=" + str(int(start)) + "&endtime=" + str(int(end))

    response = req.request("GET", url, headers=headers, verify=False).text

    json_data = json.loads(response)
    tmp = json_data["hostavailability"][0]

    tmp2 = {}

    tmp2["up"] = (tmp["percent_total_time_up"])
    tmp2["down"] = (tmp["percent_total_time_down"])

    return tmp2
def getAllHostsDowntimes(customer, start, end, outputdir,minutesFilterOut,stateEntries):

    statusLog = []
    i = 0
    downtimes_total = 0

    for e in reversed(stateEntries):
        i += 1
        if e["service_description"] == {}: # Status change refers to host
            startPoint = searchIfExists(e, statusLog)
            if e["state"] != "0" and startPoint == None:
                # print(e["state_time"], e["host_name"],e["service_description"], ":",  e["output"], e["state_change"], e["state"], e["state_type"])
                statusLog.append(e)
            elif e["state"] == "0" and startPoint != None: # Host has recovered
                FMT = '%Y-%m-%d %H:%M:%S'
                downtimePeriod = datetime.strptime(e["state_time"], FMT) - datetime.strptime(
                    startPoint["state_time"], FMT)
                if (downtimePeriod > timedelta(minutes=minutesFilterOut)):
                    # print(downtimePeriod,":",e["state_time"],e["host_name"], e["service_description"], startPoint["output"])
                    try:
                        hostavail = getHostAvailability(customer, start, end, startPoint["host_name"])
                        downtime.append((startPoint["host_name"], startPoint["service_description"],
                                         startPoint["state_time"], e["state_time"],
                                         startPoint["output"], downtimePeriod, hostavail["up"], hostavail["down"]))
                    except Exception as exception:
                        print("Couldn't get availability for host:" + startPoint["host_name"] + " error:", exception)

                downtimes_total += 1
                statusLog.remove(startPoint)


    print("downtimes total:" + str(downtimes_total))
    print("downtimes" + str(len(downtime)))
    print("statusLog", statusLog)
    stillDown=[]

    for entry in statusLog:
        downtimePeriod = datetime.fromtimestamp(end) - datetime.strptime(entry["state_time"], FMT)
        hostavail = getHostAvailability(customer, start, end, entry["host_name"])
        stillDown.append((entry["host_name"], entry["service_description"],
                                         entry["state_time"], end,
                                         entry["output"], downtimePeriod, hostavail["up"], hostavail["down"]))

    downtime.sort()
    formatedStart = str(datetime.utcfromtimestamp(start).strftime('%Y-%m-%d'))
    formatedEnd = str(datetime.utcfromtimestamp(end).strftime('%Y-%m-%d'))

    #CO.output(downtime, 'Host Downtimes' + formatedStart + "-" + formatedEnd, False, outputdir, 1, True,
    #                  str(downtimes_total))
    CO.output(downtime, 'Host Downtimes', False, "Stats Working Dir", 1, True, str(downtimes_total))
    CO.output(stillDown, 'Hosts that are still down', False, "Stats Working Dir", 1, True, str(downtimes_total))


    return downtimes_total, downtime, statusLog, stillDown


def getAllInterfacesAvailability(customer, start, end, outputdir, minutesFilterOut, stateEntries):

    i = 0
    statusLog = []
    interfaceAvaillability = []
    warningsNo = 0

    for e in reversed(stateEntries):
        i += 1
        if "Status" in e["service_description"] and not "Power" in e["service_description"]:
            startPoint=searchIfExists(e, statusLog)
            if e["state"]!="0" and startPoint == None :
                #print(e["state_time"], e["host_name"],e["service_description"], ":",  e["output"], e["state_change"], e["state"], e["state_type"])
                statusLog.append(e)
                pass
            elif e["state"]=="0" and startPoint != None :
                FMT = '%Y-%m-%d %H:%M:%S'
                downtimePeriod=datetime.strptime(e["state_time"], FMT) - datetime.strptime(startPoint["state_time"], FMT)
                if( downtimePeriod>timedelta(minutes=minutesFilterOut) and not ("SNMP error" in startPoint["output"]) ):
                #if (downtimePeriod > timedelta(minutes=20) and not "SNMP error" in startPoint["output"]):
                    print(e)
                    #print(downtimePeriod,":",e["state_time"],e["host_name"], e["service_description"], startPoint["output"])
                    interfaceAvaillability.append((startPoint["host_name"], startPoint["service_description"],
                                                   startPoint["state_time"], e["state_time"],
                                                   startPoint["output"], downtimePeriod))
                statusLog.remove(startPoint)
                warningsNo += 1

    stillDown = []

    for entry in statusLog:
        downtimePeriod = datetime.fromtimestamp(end) - datetime.strptime(entry["state_time"], FMT)
        #serviceAvail = getServiceAvailability(customer, start, end, entry["host_name"])
        stillDown.append((entry["host_name"], entry["service_description"],
                          entry["state_time"], end,
                          entry["output"], downtimePeriod))

    interfaceAvaillability.sort()
    print("interfaceAvaillability",interfaceAvaillability)
    print("Servstilldown",stillDown)

    formatedStart=str(datetime.utcfromtimestamp(start).strftime('%Y-%m-%d'))
    formatedEnd=str(datetime.utcfromtimestamp(end).strftime('%Y-%m-%d'))

    #CO.output(interfaceAvaillability, 'Interface Downtimes' + formatedStart + "-" + formatedEnd, False, outputdir, 1, False, " ")
    CO.output(interfaceAvaillability, 'Interface Downtimes', False, "Stats Working Dir", 1, False, " ")
    CO.output(stillDown, 'Interfaces that are still down', False, "Stats Working Dir", 1, False, str(warningsNo))

    return warningsNo, interfaceAvaillability, statusLog, stillDown

def getAllBandwidthAlerts(customer, start, end, outputdir,stateEntries):

    alertBandwidth = []
    internetBandwidth = []

    i = 0
    bandwidth_total = 0
    tmpMatrix = []

    for e in reversed(stateEntries):

        i += 1
        if "Bandwidth" in e["service_description"]:
            startPoint = searchIfExists(e, tmpMatrix)
            if e["state"] != "0" and startPoint == None:
                tmpMatrix.append(e)
                bandwidth_total += 1
                pass
            elif e["state"] == "0" and startPoint != None:

                if (startPoint["service_description"].find("Internet") == -1):
                    if (startPoint["output"].find("Mbps") != -1):
                        splitted_incoming = re.split(' in: ', startPoint["output"])[1]
                        splitted_incoming = re.split('Mbps', splitted_incoming)[0]
                        splitted_outgoing = re.split(' Out: ', startPoint["output"])[1]
                        splitted_outgoing = re.split('Mbps', splitted_outgoing)[0]

                        FMT = '%Y-%m-%d %H:%M:%S'
                        downtimePeriod = datetime.strptime(e["state_time"], FMT) - datetime.strptime(
                            startPoint["state_time"], FMT)
                        if (downtimePeriod > timedelta(minutes=25) or (
                                float(splitted_outgoing) > 90 and downtimePeriod > timedelta(minutes=10)) or (
                                float(splitted_incoming) > 90) and downtimePeriod > timedelta(minutes=10)):
                            alertBandwidth.append((startPoint["host_name"], startPoint["service_description"],
                                                   startPoint["state_time"], e["state_time"],
                                                   startPoint["output"], downtimePeriod))

                        tmpMatrix.remove(startPoint)
                    elif (startPoint["output"].find("Kbps") != -1):
                        splitted_incoming = re.split(' in: ', startPoint["output"])[1]
                        splitted_incoming = re.split('Kbps', splitted_incoming)[0]
                        splitted_outgoing = re.split(' Out: ', startPoint["output"])[1]
                        splitted_outgoing = re.split('Kbps', splitted_outgoing)[0]

                        FMT = '%Y-%m-%d %H:%M:%S'
                        downtimePeriod = datetime.strptime(e["state_time"], FMT) - datetime.strptime(
                            startPoint["state_time"], FMT)
                        if (downtimePeriod > timedelta(minutes=25) or (
                                float(splitted_outgoing) > 90000 and downtimePeriod > timedelta(
                                minutes=10)) or (
                                float(splitted_incoming) > 90000) and downtimePeriod > timedelta(minutes=10)):
                            alertBandwidth.append((startPoint["host_name"], startPoint["service_description"],
                                                   startPoint["state_time"], e["state_time"],
                                                   startPoint["output"], downtimePeriod))

                        tmpMatrix.remove(startPoint)


                elif "CRITICAL" in startPoint["output"] or "WARNING" in startPoint["output"]:
                    FMT = '%Y-%m-%d %H:%M:%S'
                    downtimePeriod = datetime.strptime(e["state_time"], FMT) - datetime.strptime(
                        startPoint["state_time"], FMT)

                    print(downtimePeriod, ":", e["state_time"], e["host_name"], e["service_description"],
                          startPoint["output"])
                    alertBandwidth.append((startPoint["host_name"], startPoint["service_description"],
                                           startPoint["state_time"], e["state_time"],
                                           startPoint["output"], downtimePeriod))
                    tmpMatrix.remove(startPoint)

                pass

    formatedStart = str(datetime.utcfromtimestamp(start).strftime('%Y-%m-%d'))
    formatedEnd = str(datetime.utcfromtimestamp(end).strftime('%Y-%m-%d'))
    #

    for e in alertBandwidth[:]:
        if "Internet" in e[1]:
            alertBandwidth.remove(e)
            internetBandwidth.append(e)
        else:
            pass

        # print(e[1])
    print("bandwidth total:" + str(bandwidth_total))
    print("internet bandwidth total:" + str(len(internetBandwidth)))

    for e in internetBandwidth[:]:

        if e[5] < timedelta(minutes=10):
            internetBandwidth.remove(e)

            print(e[5])

    #CO.output(alertBandwidth, 'Important Bandwidth' + formatedStart + "-" + formatedEnd, False, outputdir, 1,
    #                  False, bandwidth_total)

    #CO.output(internetBandwidth, 'Internet Bandwidth' + formatedStart + "-" + formatedEnd, False, outputdir, 1,
    #                  False, len(internetBandwidth))

    CO.output(alertBandwidth, 'Important Bandwidth', False, "Stats Working Dir", 1, False, bandwidth_total)

    CO.output(internetBandwidth, 'Internet Bandwidth', False, "Stats Working Dir", 1, False,
                      len(internetBandwidth))

    return str(bandwidth_total), str(len(internetBandwidth))
