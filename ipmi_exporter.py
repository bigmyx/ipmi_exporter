import subprocess
import itertools
import time
import logging
import os
from multiprocessing import Process, Manager
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY


try:
    IPS = os.getenv('TARGET_IPS').split(',')
except AttributeError:
    raise Exception("Mandatory `TARGET_IPS` environment variable is not set")

IPMI_USER = os.getenv('IPMI_USER', 'Administrator')
IPMI_PASSWD = os.getenv('IPMI_PASSWD', '')

REQURED = [
    "CPU1 Temp",
    "System Temp",
    "FAN1"
]
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

def _run_cmd(ip, tool, args, raw):
    logging.info("Collecting from target %s", ip)
    proc = subprocess.Popen(["ipmi-" + tool,
                             "-h", ip,
                             "-u", IPMI_USER,
                             "-p", IPMI_PASSWD,
                             "--driver-type", "LAN_2_0",
                            ] + args, stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    raw += out.split('\n')

def stripArr(arr):
    return [z.rstrip().lstrip() for z in arr]

class IpmiCollector(object):
    @REQUEST_TIME.time()
    def collect(self):
        metrics = {
            'temp': GaugeMetricFamily('ipmi_temp', 'Temperature', labels=['ip', 'id', 'entity']),
            'power': GaugeMetricFamily('ipmi_power', 'Power Usage', labels=['ip', 'type']),
        }
        raw = Manager().list([])
        raw2 = Manager().list([])

        for ip in IPS:
            # ipmi-sensors -h 192.168.1.125 -u Administrator -p ****** --driver-type LAN_2_0 --comma-separated-output
            p = Process(target=_run_cmd, args=(ip, 'sensors', ['--entity-sensor-names', '--comma-separated-output'], raw))
            logging.info("Start collecting the metrics")
            p.start()
            p.join()
            raw.pop(0)
            all_metrics = [x.split(',') for x in raw]
            # ipmi-dcmi -h 192.168.1.125 -u Administrator -p ****** --driver-type LAN_2_0 --get-system-power-statistics
            p2 = Process(target=_run_cmd, args=(ip, 'dcmi', ['--get-system-power-statistics'], raw2))
            p2.start()
            p2.join()

            power_metrics = [x.split(':') for x in raw2]
            power_metrics.pop(len(power_metrics) - 1)
            power_metrics = [stripArr(y) for y in power_metrics]

            for v in all_metrics:
                if len(v) < 2: continue
                if 'Temperature' == v[2] and v[3] != 'N/A':
                        metrics['temp'].add_metric([ip, v[0], v[1]], float(v[3]))
            for v in power_metrics:
                if len(v) < 2: continue
                print(v)
                if 'Current Power' == v[0]:
                    metrics['power'].add_metric([ip, 'currentPower'], int(v[1].split(' ')[0]))
                if 'Minimum Power over sampling duration' == v[0]:
                    metrics['power'].add_metric([ip, 'minSamplePower'], int(v[1].split(' ')[0]))
                if 'Maximum Power over sampling duration' == v[0]:
                    metrics['power'].add_metric([ip, 'maxSamplePower'], int(v[1].split(' ')[0]))
                if 'Average Power over sampling duration' == v[0]:
                    metrics['power'].add_metric([ip, 'avgSamplePower'], int(v[1].split(' ')[0]))

        for metric in metrics.values():
            yield metric


def main():
    REGISTRY.register(IpmiCollector())
    start_http_server(8000)
    while True:
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(format='ts=%(asctime)s level=%(levelname)s msg=%(message)s', level=logging.DEBUG)
    main()
