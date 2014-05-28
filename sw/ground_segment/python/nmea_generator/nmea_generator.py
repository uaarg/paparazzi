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
        message = GPSMessage(*larg)

        print(message.data, file=sys.stderr) # Printing to stderr so that it appears in the Paparazzi Center terminal (stdout doesn't)


def main():
    messages_xml_map.ParseMessages()


    #Command line options
    parser = argparse.ArgumentParser(description="Listens to telemetry data to output nmea data on the specified port.")
    parser.add_argument("-d", "-device", "--device", help="Port. The serial port/device to output nmea data on.", default="/dev/ttyUSB1")
    args = parser.parse_args()

    global SERIAL_PORT
    SERIAL_PORT = args.device


    runner = Runner()


if __name__ == '__main__':
    main()