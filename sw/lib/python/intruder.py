#!/usr/bin/env python

from __future__ import print_function

import sys
from os import path, getenv

# if PAPARAZZI_SRC not set, then assume the tree containing this
# file is a reasonable substitute
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")

from ivy_msg_interface import IvyMessagesInterface
from pprz_msg.message import PprzMessage

class IntruderAdder(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self._interface = IvyMessagesInterface(self.message_recv)

    def message_recv(self, ac_id, msg):
        if self.verbose:
            print("Got msg %s" % msg.name)

    def shutdown(self):
        print("Shutting down ivy interface...")
        self._interface.shutdown()

    def __del__(self):
        self.shutdown()

    def add_intruder(self, intruder_id, name, lat, lon, alt, course, speed, climb, itow):
        msg = PprzMessage("ground", "INTRUDER")
        msg['id'] = intruder_id
        msg['name'] = name
        msg['lat'] = lat
        msg['lon'] = lon
        msg['alt'] = alt
        msg['course'] = course
        msg['speed'] = speed
        msg['climb'] = climb
        msg['itow'] = 0
        print("Sending message: %s" % msg)
        self._interface.send(msg)

    def new_intruder(self, intruder_id, name):
        msg = PprzMessage("ground", "INTRUDER")
        msg['id'] = intruder_id
        msg['name'] = name
        msg['itow'] = 0
        print("Sending message: %s" % msg)
        self._interface.send(msg)


if __name__ == '__main__':
    ia = IntruderAdder()
    ia.add_intruder(intruder_id=1, name=1)
    ia.add_intruder(intruder_id=1, name=1, lat=434624607, lon=12723454, alt=1720000, course=30, speed=5.0, climb=2.0, itow=10)
    ia.shutdown()
