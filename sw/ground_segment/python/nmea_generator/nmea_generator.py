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
#import serial

GROUNDALT=135.636

PPRZ_HOME = os.getenv("PAPARAZZI_HOME")
sys.path.append(PPRZ_HOME + "/sw/lib/python")
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
        # initialising the bus
        IvyInit("Nmea_Generator",   # application name for Ivy
                "READY",            # ready message
                0,                  # main loop is local (ie. using IvyMainloop)
                lambda x,y: y,      # handler called on connection/deconnection
                lambda x,y: y       # handler called when a diemessage is received
                )

        # starting the bus
        logging.getLogger('Ivy').setLevel(logging.WARN)
        IvyStart("")
        IvyBindMsg(self.onIvyMessage, "^([^ ]+) %s (.*)$" % (self.message_name,))


    def onIvyMessage(self, agent, *larg):
        #outgoing=serial.Serial(SERIAL_PORT,4800) Pyserial
        message = GPSMessage(*larg)

        ######CORDINATES########################################################################################
        northing = float(message.data['utm_north']) / 100
        easting = float(message.data['utm_east']) / 100
        zone = int(message.data['utm_zone'])
        GPS=utm.to_latlon(easting, northing, zone, northern=True)

        #Aquire the GPS Lat and Long
        GPSLat=GPS[0] 
        GPSlong=GPS[1]

        #Determine N or S for NMEA
        if GPSLat>=0:
            a="N"
        elif GPSLat<0:
            a="S"
        
        #Determine W or E for NMEA
        if GPSlong>=0:
            A="E"
        elif GPSlong<0:
            A="W"

        #GPSLat to degrees and decimal minutes
        d = int(abs(GPSLat))
        md = abs(abs(GPSLat) - d) * 60
        m = float(md)
        DMS_Lat=""
        if d<10:
            DMS_Lat="0%d%.2f" % (d,m)
        else: 
            DMS_Lat="%d%.2f" % (d,m)

        #GPSlong to degrees and decimal minutes
        d = int(abs(GPSlong))
        md = abs(abs(GPSlong) - d) * 60
        m = float(md)
        DMS_Long=""
        if d>99:
            DMS_Long="%d%.2f" % (d,m)
        elif d<10:
            DMS_Long="00%d%.2f" % (d,m)
        else: 
            DMS_Long="0%d%.2f" % (d,m)

        #If GPS mode is 3, there is a GPS fix
        if message.data['mode']=="3":
            GPSFix=1
        else:
            GPSFix=0

        #Find Altitude
        alt=((int(message.data['alt'])/1000)-GROUNDALT)

        if alt<0:
            alt = 0

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

        ############### ADD CHECK SUM ############################################################################
        line = 'GPGGA,'+ timeNow_string+','+DMS_Lat+','+a+','+DMS_Long+','+A+','+str(GPSFix)+','+'5'+','+','+str(25)+','+str(alt)+','+','+','+',0000'
        calc_cksum=0
        for s in line:
            calc_cksum^=ord(s)
        calc_cksum = '*' + str(hex(calc_cksum))[2:4].upper()

        ############### COMPILE AND SEND ############################################################################
        line='$'+line+calc_cksum+'\n'
        print("Nmea message sent:", file=sys.stderr)
        print(str(alt), file=sys.stderr)
        print(line, file=sys.stderr)
        #outgoing.write(line) Pyserial
        #outgoing.close() Pyserial
        


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
