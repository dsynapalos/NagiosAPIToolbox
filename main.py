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

FILENAME = os.path.realpath(__file__).replace('\\', '/')
DIRECTORY = os.path.dirname(FILENAME).replace('\\', '/')
DATES = []

import RESTFunctions as RF
import SSHFunctions as SF
import DOCXFunctions as DF
import PYTHONFunctions as PF
import DocumentConstruction as DC
import InitialSetup as IS
import clients as CL
import ReportDataGathering as RD

urllib3.disable_warnings()
global Index

def main(argv):
    startDT = None
    endDT = None

    # Validate Input Parameters
    if len(sys.argv) == 8:

        day = int(sys.argv[1])
        mon = str(sys.argv[2])
        year = int(sys.argv[3])

        dayto = int(sys.argv[4])
        monto = str(sys.argv[5])
        yearto = int(sys.argv[6])

        CL.Index = str(sys.argv[7])

        mon = PF.convert_month_to_int(mon)
        monto = PF.convert_month_to_int(monto)

        try:
            startDT = datetime(year, mon, day)
            endDT = datetime(yearto, monto, dayto)
        except Exception as e:
            print("Error with input arguments(8): ", e)
            print(
                "Correct usage is : <./main.py> <start day> <mon> <year> <end day> <mon> <year> <customer site>, where year is optional")
            sys.exit()

    elif len(sys.argv) == 6:
        day = int(sys.argv[1])
        mon = str(sys.argv[2])

        dayto = int(sys.argv[3])
        monto = str(sys.argv[4])

        CL.Index = str(sys.argv[5])


        mon = PF.convert_month_to_int(mon)
        monto = PF.convert_month_to_int(monto)

        try:
            startDT = datetime(datetime.now().year, mon, day)
            endDT = datetime(datetime.now().year, monto, dayto)
        except Exception as e:
            print("Error with input arguments(6): ", e)
            print(
                "Correct usage is : <./main.py> <start day> <mon> <year> <end day> <mon> <year> <customer site>, where year is optional")
            sys.exit()

    elif len(sys.argv) == 5:
        day = int(sys.argv[1])
        mon = str(sys.argv[2])
        year = int(sys.argv[3])

        CL.Index = str(sys.argv[4])


        mon = PF.convert_month_to_int(mon)

        try:
            startDT = datetime(year, mon, day)
            endDT = datetime.now()
        except Exception as e:
            print("Error with input arguments(5): ", e)
            print(
                "Correct usage is : <./main.py> <start day> <mon> <year> <end day> <mon> <year> <customer site>, where year is optional")
            sys.exit()


    elif len(sys.argv) == 4:
        day = int(sys.argv[1])
        mon = str(sys.argv[2])


        CL.Index = str(sys.argv[3])
        mon = PF.convert_month_to_int(mon)

        try:
            startDT = datetime(datetime.now().year, mon, day)
            endDT = datetime.now()
        except Exception as e:
            print("Error with input arguments(4): ", e)
            print(
                "Correct usage is : <./main.py> <start day> <mon> <year> <end day> <mon> <year> <customer site>, where year is optional")
            sys.exit()
    else:
        print(
            "Correct usage is : <./main.py> <start day> <mon> <year> <end day> <mon> <year> <customer site>, where year is optional")
        sys.exit()
    '''
    # check Nagios Reachability
    pingNagios = PF.checkNagiosReachability(nagiosInstance["ip"], reChecks=2)
    if not pingNagios:
        mail.sendMail(nagiosInstance["url"], message="Auto reporting failed ",
                      body="Nagios unreachable, Failed to communicate with Nagios Server, no ping <br><br> ping IP: " +
                           nagiosInstance["ip"],
                      event_date=datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), customer=customer)
        sys.exit()
    '''
    # Convert datetimes to Nagios API format




    starttime = (startDT - datetime(1970, 1, 1)).total_seconds() - 7200  # subtract two hours
    endtime = (endDT - datetime(1970, 1, 1)).total_seconds() - 7200  # subtract two hours

    RD.gather_Bandwidth(starttime, endtime)

    PF.exitOffice()

    CL.intialize_content_vars(sys.argv)

    PF.screenshots(starttime, endtime)

    DC.constructDocument(CL.Index, CL.template)

    PF.clean_up()




if __name__ == '__main__':
    main(sys.argv[1:])
