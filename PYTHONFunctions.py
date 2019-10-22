from datetime import datetime, timedelta
import re, os
import psutil
from platform import system as system_name
from subprocess import call as system_call


# Edited from https://stackoverflow.com/questions/2953462/pinging-servers-in-python
def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Ping command count option as function of OS
    param = '-n' if system_name().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    # Pinging
    return system_call(command) == 0


def exitOffice():
    ''' Kills Office processes

    :return:
    '''
    if system_name() == 'Windows':
        for proc in psutil.process_iter():
            if proc.name() == 'EXCEL.EXE' or proc.name() == 'WINWORD.EXE':
                psutil.Process(proc.pid).terminate()
