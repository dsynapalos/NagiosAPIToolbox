import SSHFunctions as sf
import RESTFunctions as rf
import json


def setupHostsAndServices(serverName, hostiplist, hostnamelist=[], values=[0.75, 0.75, 0.85, 0.85]):
    """ This function will automatically setup Cisco network hosts and services in a new Nagios server.

    :param serverName: Server ID
    :param hostiplist: List of host ips'. Critical component!!
    :param hostnamelist: List of host names. Only provide if you are sure of 1-to-1 correct hostname assignment. By
    default will assign the device's sysName as Nagios Host Name
    :param values: Values for Bandwidth services: [WarningDown, WarningUp, CriticalDown, CriticalUp]. Hardcoded to 0.75
    Warning UP/DOWN, 0.85 Critical UP/DOWN.
    :return: A dictionary of results.
    """
    totalDict = {}
    totalDict['Hosts'] = {}
    hostList = ''
    if hostnamelist != []:

        hostDict = {}
        if len(hostiplist) == len(hostnamelist):
            for i in range(0, len(hostiplist)):
                hostDict[hostnamelist[i]] = {'ip': hostiplist[i]}

        snmpable, notsnmpable, notpingable = sf.filterHosts(serverName, hostiplist)
        for hostName in hostDict.keys():

            if hostDict[hostName] in snmpable:
                hostList += hostName + ','
                result = rf.createHost(serverName, hostName, hostDict[hostName]['ip']).strip()
                pgresult = rf.createPingService(serverName, hostName).strip()
                totalDict['Hosts'][hostName] = {'HostResult': result,
                                                'PingResult': pgresult,
                                                'ServicesResults': {}}
                serviceToDoDict, sysName = sf.getActiveIntefaceList(serverName, hostDict[hostName]['ip'])
                sf.touchRRD(serverName, hostDict[hostName]['ip'], serviceToDoDict)
                for activeInterface in serviceToDoDict.keys():
                    desc = serviceToDoDict[activeInterface]['Desc']
                    alias = serviceToDoDict[activeInterface]['Alia']

                    if int(serviceToDoDict[activeInterface]['Band']) > 999 and int(
                            serviceToDoDict[activeInterface]['Band']) < 999999:
                        scale = 'K'
                        factor = 1000
                    elif int(serviceToDoDict[activeInterface]['Band']) > 999999:
                        scale = 'M'
                        factor = 1000000
                    else:
                        scale = 'B'
                        factor = 1

                    scaledValues = [int(serviceToDoDict[activeInterface]['Band']) * values[0] / factor,
                                    int(serviceToDoDict[activeInterface]['Band']) * values[1] / factor,
                                    int(serviceToDoDict[activeInterface]['Band']) * values[2] / factor,
                                    int(serviceToDoDict[activeInterface]['Band']) * values[3] / factor]

                    stresult = rf.createStatusService(serverName, hostName, desc, alias, activeInterface).strip()

                    bwresult = rf.createBandwidthService(serverName, hostName, hostDict[hostName]['ip'], desc, alias,
                                                         activeInterface, scaledValues, scale).strip()

                    totalDict['Hosts'][hostName]['ServicesResults'][desc + ' ' + alias] = {'StatusResult': stresult,
                                                                                           'BandwidthResult': bwresult}

            else:
                continue

    else:
        snmpable, notsnmpable, notpingable = sf.filterHosts(serverName, hostiplist)

        for ip in snmpable:

            serviceToDoDict, hostName = sf.getActiveIntefaceList(serverName, ip)

            hostList += hostName + ','
            result = rf.createHost(serverName, hostName, ip)
            pgresult = rf.createPingService(serverName, hostName).strip()
            totalDict['Hosts'][hostName] = {'HostResult': result,
                                            'PingResult': pgresult,
                                            'ServicesResults': {}}
            sf.touchRRD(serverName, ip, serviceToDoDict)
            for activeInterface in serviceToDoDict.keys():
                desc = serviceToDoDict[activeInterface]['Desc']
                alias = serviceToDoDict[activeInterface]['Alia']

                if int(serviceToDoDict[activeInterface]['Band']) > 999 and int(
                        serviceToDoDict[activeInterface]['Band']) < 999999:
                    scale = 'K'
                    factor = 1000
                elif int(serviceToDoDict[activeInterface]['Band']) > 999999:
                    scale = 'M'
                    factor = 1000000
                else:
                    scale = 'B'
                    factor = 1

                scaledValues = [int(serviceToDoDict[activeInterface]['Band']) * values[0] / factor,
                                int(serviceToDoDict[activeInterface]['Band']) * values[1] / factor,
                                int(serviceToDoDict[activeInterface]['Band']) * values[2] / factor,
                                int(serviceToDoDict[activeInterface]['Band']) * values[3] / factor]

                stresult = rf.createStatusService(serverName, hostName, desc, alias, activeInterface).strip()

                bwresult = rf.createBandwidthService(serverName, hostName, ip, desc, alias,
                                                     activeInterface, scaledValues, scale).strip()

                totalDict['Hosts'][hostName]['ServicesResults'][desc + ' ' + alias] = {'StatusResult': stresult,
                                                                                       'BandwidthResult': bwresult}

    sf.pushPlugin(serverName)
    coresult = rf.createCheckCustomCommand(serverName)
    totalDict['CheckCommand'] = coresult
    seresult = rf.createCheckService(serverName, hostList[:-1])
    totalDict['CheckServices'] = seresult
    print(json.dumps(totalDict, indent=4))
    rf.applyConf(serverName)
    return totalDict
