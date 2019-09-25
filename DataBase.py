serverList = {}  # Dictionary of Nagios XI servers

serverList['my_nagios'] = {  # Nagios XI server information
    'apikey': '',  # API token of Nagios XI user
    'ip': '',  # IP of Nagios XI server
    'userSSH': '',  # SSH username of Nagios XI server
    'passSSH': '',  # SSH Password of Nagios XI server
    'comm': ''  # SNMP v2c community Value
}

# Command for Cisco networking host environmental value monitoring services notification limit values
# percentage following -w for warning limit, -c for critical limit
checkcommand = {
    'Check Cpu': '!cpu!-w 70 -c 80!!!!!',
    'Check Mem': '!mem!-w 15 -c 5!!!!!',
    'Check Temp': '!temp!-w 50 -c 80!!!!!',
    'Check Fan': '!fan!-w 1 -c 2!!!!!',
    'Check Psu': '!ps!-w 1 -c 1!!!!!'
}
