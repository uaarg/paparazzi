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

class ObstacleAdder(object):
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

    def add_obstacle(self, obstacle_id, shape, status, lat, lon, radius, alt):
        msg = PprzMessage("ground", "OBSTACLE")
        msg['id'] = obstacle_id
        msg['shape'] = shape
        msg['status'] = status
        msg['lat'] = lat
        msg['lon'] = lon
        msg['radius'] = radius
        msg['alt'] = alt
        print("Sending message: %s" % msg)
        self._interface.send(msg)


if __name__ == '__main__':
    ob = ObstacleAdder()
    ob.add_obstacle(obstacle_id=1, shape=1, status=1, lat=434624607, lon=12723454, radius=100, alt=1720000)
    ob.shutdown()
