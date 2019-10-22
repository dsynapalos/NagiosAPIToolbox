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
import getopt
import RESTFunctions as RF
import SSHFunctions as SF
import DOCXFunctions as DF
import DocumentConstruction as DC
import InitialSetup as IS

urllib3.disable_warnings()

FILENAME = os.path.realpath(__file__).replace('\\', '/')
DIRECTORY = os.path.dirname(FILENAME).replace('\\', '/')


def main(argv):

    try:
        try:

            opts, args = getopt.getopt(argv, "hd:", ['help', 'dates'])
            opts_list = list(dict(opts).keys())
            print(opts_list)
        except getopt.GetoptError:
            print(FILENAME + ' -r -s "DD MM" -e "DD MM"')
            sys.exit(2)
        if '-h'in opts_list or '--help' in opts_list:
            print(FILENAME + ' -d "DD MM DD MM"')
            sys.exit()

        elif '-d' in opts_list or '--dates' in opts_list:

            start_day, start_month, end_day, end_month = [item for item in dict(opts)['-d'].split()]

    except:
        print('Error: {}'.format(sys.exc_info()))
        exit()


if __name__ == '__main__':
    main(sys.argv[1:])
