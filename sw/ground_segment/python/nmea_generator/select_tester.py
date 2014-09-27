import select
import subprocess


def monitorIperfInit(proc):
    inputs = [proc.stdout]
    inputready, outputready, exceptready = select.select(inputs, [], [])
    return inputready

def monitorIperf(inputready):
    for s in inputready:
        if s == proc.stdout:
            # grab iperf line
            line = proc.stdout.readlines()[-1]
            print(line)
            # iperfParseOneLine(line)

def iperfHandler(iperf_cmd = "/usr/bin/iperf", iperf_interval = 1):
    """
    Constructs the iperf server command, runs instance, and handles it.
    """
    from subprocess import Popen, PIPE
    iperfData = []

    # construct command
    iperf_cmd += (" -s -i %d -y c" % iperf_interval)

    # start process
    iperf_process = Popen(iperf_cmd, shell=True, stdout=PIPE)

    return iperf_process

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

def onIvyMessage():
    print("lol")

def main():
    # monitor iperf stream for events
    # if there's an event on the iperf stream
    # then grab whatever gps message we see on the ivy bus at that time
    # and log it
    iperfProc = iperfHandler()
    inputs = [iperfProc.stdout]
    iperfData = []
    while 1:
        inputready, outputready, exceptready = select.select(inputs, [], [])
        for s in inputready:
            if s == iperfProc.stdout and iperfProc.stdout.readline != '':
                # grab iperf line
                line = iperfProc.stdout.readline()
                iperfData.append(iperfParseOneLine(line))

if __name__ == '__main__':
    main()
