#!/usr/bin/env python

# This file is part of paparazzi.

# paparazzi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# paparazzi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with paparazzi; see the file COPYING.  If not, write to
# the Free Software Foundation, 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""This program listens to ivy messages from the plane and output's
nmea data on the specified port. It's not fully implemented yet."""

from __future__ import print_function
import logging
import sys
import os
import argparse
from ivy.std_api import *
import utm
import time
from datetime import datetime, timedelta
import httplib, urllib    #html python modules

#Constants
LOGIN_PATH = "/api/login"
TELEM_PATH = "/api/interop/uas_telemetry"
SERVER_INFO_PATH = "/api/interop/server_info"
USERNAME = 'uaarg'
PASSWORD = 'uaarg'

PPRZ_HOME = os.getenv("PAPARAZZI_HOME")
PPRZ_LIB_PYTHON = os.path.join(PPRZ_HOME, "sw/lib/python/pprz_msg")
sys.path.append(PPRZ_LIB_PYTHON)

import messages_xml_map

class GPSMessage:
    def __init__(self, sender, values):

        self.raw_sender = sender
        self.values = values.split(" ")
        self.names = messages_xml_map.message_dictionary['telemetry']["GPS"]

        if len(self.values) != len(self.names):
            raise(Exception("Error in Nmea generator: received malformed GPS message (has %s values, expected %s)." % (len(self.values), len(self.names))))

        self.data = {name:value for value, name in zip(self.values, self.names)}

class Runner:

    def __init__(self):

        self.message_name = "GPS"

        if self.message_name not in messages_xml_map.message_dictionary['telemetry']:
            raise(Exception("Nmea generator needs the %s message to work." % (self.message_name,)))

        self.conn = httplib.HTTPConnection("localhost", 8080)
        self.initIvy()

    def initIvy(self):
        # initialising the bus
        #Connect
        #Login Creds
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        params = urllib.urlencode({'username': USERNAME, 'password': PASSWORD })
        #Send Message
        self.conn.request("POST", LOGIN_PATH, params, self.headers)
        #Server Response
        response = self.conn.getresponse()
        print(response.read() + '\n', file=sys.stderr)
        self.message_name = "GPS"
        #Saving Login Cookie Credentials
        setcookie = response.getheader("Set-Cookie")
        contenttype = response.getheader("Content-type")
        self.headers = {"Accept": "text/plain", "Cookie" : setcookie, "Content-type" : "application/x-www-form-urlencoded"}

        IvyInit("Nmea_Generator",   # application name for Ivy
                "READY",            # ready message
                0,                  # main loop is local (ie. using IvyMainloop)
                lambda x,y: y,      # handler called on self.connection/deself.connection
                lambda x,y: y       # handler called when a diemessage is received
                )

        # starting the bus
        logging.getLogger('Ivy').setLevel(logging.WARN)
        IvyStart("")
        First_Message = True
        IvyBindMsg(self.onIvyMessage, "^([^ ]+) %s (.*)$" % (self.message_name,))


    def onIvyMessage(self, agent, *larg):

        message = GPSMessage(*larg)

        ######CORDINATES########################################################################################
        northing = float(message.data['utm_north']) / 100
        easting = float(message.data['utm_east']) / 100
        zone = int(message.data['utm_zone'])
        GPS=utm.to_latlon(easting, northing, zone, northern=True)

        #Aquire the GPS Lat and Long
        GPSLat=GPS[0]
        GPSLong=GPS[1]

        #If GPS mode is 3, there is a GPS fix
        if message.data['mode']=="3":
            GPSFix=1
        else:
            GPSFix=0

        #Find Altitude in Meters
        alt=(int(message.data['alt'])/1000)

        ###### TIME ###########################################################################################
        timeNow=datetime.now()
        #HOURS
        if timeNow.hour <10:
            timeNow_string_h = '0'+ str(timeNow.hour)
        else:
            timeNow_string_h = str(timeNow.hour)
        #MINUTES
        if timeNow.minute <10:
            timeNow_string_m = '0'+ str(timeNow.minute)
        else:
            timeNow_string_m = str(timeNow.minute)
        #SECONDS
        if timeNow.second <10:
            timeNow_string_s = '0'+ str(timeNow.second)
        else:
            timeNow_string_s = str(timeNow.second)
        #MILLASECONDS
        timeNow_string_ms='000'
        timeNow_string="%s%s%s.%s" % (timeNow_string_h,timeNow_string_m,timeNow_string_s,timeNow_string_ms)

        #Posting
        if GPSFix == 1:
            params = urllib.urlencode({'latitude': GPSLat, 'longitude': GPSlong, 'altitude_msl': alt, 'uas_heading': 10})
            self.conn.request("POST", TELEM_PATH, params, self.headers)
            response = self.conn.getresponse()


            #print response.status, response.reason
            #print response.read()



def main():
    messages_xml_map.parse_messages()
    #Command line options
    parser = argparse.ArgumentParser(description="Listens to telemetry data to output nmea data on the specified port.")
    parser.add_argument("-d", "-device", "--device", help="Port. The serial port/device to output nmea data on.", default="/dev/ttyUSB0")
    args = parser.parse_args()
    global SERIAL_PORT
    SERIAL_PORT = args.device
    runner = Runner()

if __name__ == '__main__':
    main()
