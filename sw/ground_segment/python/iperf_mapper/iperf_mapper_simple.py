#!/usr/bin/python
import argparse
import re
import pprint


def iperfParseOneLine(line):
	"""
	CSV input expected from iperf:
	20140926183812,127.0.0.1,5001,127.0.0.1,50482,4,0.0-1.0,1181220864,9449766912
	20140926183813,127.0.0.1,5001,127.0.0.1,50482,4,1.0-2.0,1150156800,9201254400
	20140926183814,127.0.0.1,5001,127.0.0.1,50482,4,2.0-3.0,1214382080,9715056640
	20140926183815,127.0.0.1,5001,127.0.0.1,50482,4,3.0-4.0,1255800832,10046406656
	20140926183816,127.0.0.1,5001,127.0.0.1,50482,4,4.0-5.0,1203896320,9631170560
	20140926183817,127.0.0.1,5001,127.0.0.1,50482,4,5.0-6.0,1278869504,10230956032
	20140926183818,127.0.0.1,5001,127.0.0.1,50482,4,6.0-7.0,1274544128,10196353024
	
	timestamp,source_address,source_port,destination_address,destination_port,interval,transferred_bytes,bits_per_second
	"""
	
	fields = line.split(',')
	keys = [
	    'timestamp',
	    'source_address',
	    'source_port',
	    'destination_address',
	    'destination_port',
	    'interval',
	    'transferred_bytes',
	    'bits_per_second'
	    ]
	parseDict = dict(zip(keys, fields))
	return parseDict

def ppzTimestamp(start_time, seconds_offset):
	return start_time + round(seconds_offset)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "-iperf", "--iperf")
	parser.add_argument("-p", "-ppzlog", "--ppzlog")
	args = parser.parse_args()
	iperf_log = args.iperf
	ppz_log = args.ppzlog

	# for pretty printing data structures
	pp = pprint.PrettyPrinter(indent=4)

	iperfData = []
	with open(iperf_log, 'r') as f:
		# f.readline() # get rid of first date line
		for line in f:
			parsedIperfLine = iperfParseOneLine(line)
			iperfData.append(parsedIperfLine)

	pp.pprint(iperfData)
	# Should use the actual paparazzi module for parsing messages from xml descriptions
	ppzData = []
	ppzKeys = ['offset_time', 'utm_east', 'utm_north', 'alt', 'utm_zone']
	gpsRegex = re.compile("^([^ ]+) [0-9] GPS [0-9] ([^ ]+) ([^ ]+) [^ ]+ ([^ ]+) [^ ]+ [^ ]+ [^ ]+ [^ ]+ ([^ ]+) [^ ]+$")
	with open(ppz_log, 'r') as f:	
		for line in f:
			m = gpsRegex.match(line)
			if m:
				print("matched")
				offset_time, utm_east, utm_north, alt, utm_zone = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
				parsedPpzLine = [offset_time, utm_east, utm_north, alt, utm_zone]
				parsedPpzDict = dict(zip(ppzKeys, parsedPpzLine))
				ppzData.append(parsedPpzDict)

	pp.pprint(ppzData)	

if __name__ == "__main__":
	main()
