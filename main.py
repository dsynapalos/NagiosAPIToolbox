#!/usr/bin/python3
"""
title           :NagiosAPIToolbox
description     :This is a compilation of individual functions and tools consuming the Nagios XI Restful API.
                Refer to the RESTFunctions and SSHFunctions files for individual function usage and content.
                Refer to the Initial Setup file for automated network device host and service setup.
author          :dsynapalos@algosystems.gr
date            :25-09-2019
version         :v1
usage           :Populate the DataBase file with information on your particular Nagios XI application.
                Identify any useful function, insert into main and execute from command line or from your favorite IDE.
notes           :This project is intended to provide a basis of reference for fellow developers focusing heavily on
                Cisco networking objects monitoring via Nagios XI.
python_version  :3.7.2
"""

# Favorite Modules
import requests as req
import json
import urllib3
import base64
from datetime import datetime
import re
import sys
import os
import RESTFunctions as RF
import SSHFunctions as SF
import InitialSetup as IS

urllib3.disable_warnings()

FILENAME = os.path.realpath(__file__).replace('\\', '/')
DIRECTORY = os.path.dirname(FILENAME).replace('\\', '/')


def main():
    try:
        print(json.dumps(json.loads(""), indent=4))
    except:
        print('Error: {}'.format(sys.exc_info()))
        exit()


if __name__ == '__main__':
    main()
