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
import httplib, urllib, json    #html python modules

#Constants
LOGIN_PATH = "/api/login"
TELEM_PATH = "/api/interop/uas_telemetry"
OBST_PATH = "/api/interop/obstacles"
SERVER_INFO_PATH = "/api/interop/server_info"
USERNAME = 'testuser'
PASSWORD = 'testpass'

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
        self.initIvy()

    def initIvy(self):
        #HTTP_Connection
        self.conn = httplib.HTTPConnection("localhost", 8080)
        #Login Creds
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        params = urllib.urlencode({'username': USERNAME, 'password': PASSWORD })
        self.conn.request("POST", LOGIN_PATH, params, self.headers)
        response = self.conn.getresponse()
        print(response.read() + '\n', file=sys.stderr)

        #Saving Login Cookie Credentials
        setcookie = response.getheader("Set-Cookie")
        contenttype = response.getheader("Content-type")
        self.headers = {"Accept": "text/plain", "Cookie" : setcookie, "Content-type" : "application/x-www-form-urlencoded"}

        IvyInit("Interoperability",   # application name for Ivy
                "READY",            # ready message
                0,                  # main loop is local (ie. using IvyMainloop)
                lambda x,y: y,      # handler called on self.connection/deself.connection
                lambda x,y: y       # handler called when a diemessage is received
                )

        # starting the bus
        logging.getLogger('Ivy').setLevel(logging.WARN)
        IvyStart("")

        #Server Functions
        self.server_information()
        self.pull_obstacles()
        IvyBindMsg(self.uas_telemetry_message, "^([^ ]+) %s (.*)$" % (self.message_name,))

    def server_information(self):
        self.conn.request("GET", SERVER_INFO_PATH,"", self.headers)
        response = self.conn.getresponse()
        response_object=json.loads(response.read())     #JSON --> Python Dictionary
        server_message = response_object['server_info']['message']
        server_message_time = response_object['server_info']['message_timestamp']
        server_time = response_object['server_time']
        print('Server Message: ', file=sys.stderr)
        print(server_message, file=sys.stderr)
        print(server_message_time, file=sys.stderr)

    def pull_obstacles(self):
        self.conn.request("GET", OBST_PATH,"", self.headers)
        response = self.conn.getresponse()
        response_object=json.loads(response.read())     #JSON --> Python Dictionary
        print('Stationary Obstacles: ', file=sys.stderr)
        print(response_object['stationary_obstacles'], file=sys.stderr)
        print('Moving Obstacles: ', file=sys.stderr)
        print(response_object['moving_obstacles'], file=sys.stderr)

    def uas_telemetry_message(self, agent, *larg):
        message = GPSMessage(*larg)

        #Check GPS Fix
        if message.data['mode']=="3": GPSFix=1
        else: GPSFix=0

        northing = float(message.data['utm_north']) / 100
        easting = float(message.data['utm_east']) / 100
        zone = int(message.data['utm_zone'])

        #Lat & Long
        GPS=utm.to_latlon(easting, northing, zone, northern=True)
        GPSLat=GPS[0]
        GPSLong=GPS[1]

        #Altitude (ASL meters)
        self.alt=(int(message.data['alt'])/1000)

        outgoing_message = urllib.urlencode({'latitude': 10, 'longitude': 10, 'altitude_msl': 10, 'uas_heading': 10})
        self.conn.request("POST", TELEM_PATH, outgoing_message, self.headers)
        response = self.conn.getresponse()
        print(response.read() + '\n', file=sys.stderr)


    def nmea_time_stamp(self): 
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
