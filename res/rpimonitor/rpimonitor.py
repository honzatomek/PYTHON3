#!/usr/bin/python3
'''
Monitors current RaspberryPi performance stats and prints them on screen.
''' 

# <---------------------------------------------------------------------------- general imports --->
from subprocess import PIPE, Popen
import psutil
import argparse
import os
import json
from time import sleep
import paho.mqtt.client as mqtt

# <--------------------------------------------------------------------------- global variables --->
TEMP_FILE = '/sys/class/thermal/thermal_zone0/temp'


class Value:
    __s = [21, 3, 8, 4]          # spacing
    __a = ['<', '^', '>', '<']   # align
    __d = '='                    # delimiter

    def __init__(self, description, value, fmt, units, function=None, arguments=None, child=None, div=1):
        self.description = description
        self.value = value
        if '{0:' not in fmt:
            self.fmt = '{0:' + fmt + '}'
        else:
            self.fmt = fmt
        self.units = units
        self.callback = function
        self.arguments = arguments
        self.child = child
        self.divide = div

    def __str__(self):
        out = ''
        for i in range(4):
            out += '{' + str(i) + ':' + self.__a[i] + str(self.__s[i]) + '}'

        out = out.format(self.description, self.__d, self.fmt.format(self.value), ' ' + self.units)
        return out

    def __iter__(self):
        yield ('description', self.description)
        yield ('value', self.fmt.format(self.value))
        yield ('units', self.units)

    def get_value(self):
        if self.callback:
            command = 'self.callback('
            if self.arguments:
                command += ', '.join([str(a) for a in self.arguments])
            command += ')'
            if self.child:
                command += '.' + self.child
            self.value = eval(command) / self.divide
        else:
            raise Exception('No callback function specified for {0}.'.format(self.description))

    def val(self):
        return '{0} {1}'.format(self.fmt.format(self.value), self.units)


class RPiMonitor:
    def __init__(self):
        self.__data = {'CPU': {'Temperature': Value('CPU Temperature', 0.0, '{0:0.2f}', "'C", self.get_cpu_temp_prec),
                               'Usage': Value('CPU Usage', 0.0, '{0:0.2f}', '%', psutil.cpu_percent, (0.1, False)),
                               'Count': Value('CPU Count', 0, '{0:0.0f}', '', psutil.cpu_count),
                               'Frequency Current': Value('CPU Frequency Current', '0.0', '{0:0.2f}', 'Hz', psutil.cpu_freq, child='current'),
                               'Frequency Min': Value('CPU Frequency Min', '0.0', '{0:0.2f}', 'Hz', psutil.cpu_freq, child='min'),
                               'Frequency Min': Value('CPU Frequency Max', '0.0', '{0:0.2f}', 'Hz', psutil.cpu_freq, child='max')},
                       'RAM': {'Total': Value('RAM Total', '0.0', '{0:0.2f}', 'MiB', psutil.virtual_memory, child='total', div=2**20),
                               'Used': Value('RAM Used', '0.0', '{0:0.2f}', 'MiB', psutil.virtual_memory, child='used', div=2**20),
                               'Free': Value('RAM Free', '0.0', '{0:0.2f}', 'MiB', psutil.virtual_memory, child='free', div=2**20),
                               'Available': Value('RAM Available', '0.0', '{0:0.2f}', 'MiB', psutil.virtual_memory, child='available', div=2**20),
                               'Percent Used': Value('RAM Percent Used', '0.0', '{0:0.2f}', '%', psutil.virtual_memory, child='percent')},
                       'DISK': {'Total': Value('Disk Total', '0.0', '{0:0.2f}', 'GiB', psutil.disk_usage, ['\"/\"'], 'total', 2**30),
                                'Used': Value('Disk Used', '0.0', '{0:0.2f}', 'GiB', psutil.disk_usage, ['\"/\"'], 'used', 2**30),
                                'Free': Value('Disk Free', '0.0', '{0:0.2f}', 'GiB', psutil.disk_usage, ['\"/\"'], 'free', 2**30),
                                'Percent Used': Value('Disk Percent Used', '0.0', '{0:0.2f}', '%', psutil.disk_usage, ['\"/\"'], 'percent')}}
        self.measure()

    def __str__(self):
        out = ''
        for category in self.__data.keys():
            out += str(category) + ':\n'
            for item in self.__data[category].keys():
                out += '{0}\n'.format(str(self.__data[category][item]))
            out += '\n'
        return out[:-1]

    def __iter__(self):
        for category in self.__data.keys():
            for item in self.__data[category].keys():
                yield dict(self.__data[category][item])

    def dict(self):
        data = dict()
        for category in self.__data.keys():
            if category not in data.keys():
                data.setdefault(category, dict())
            for item in self.__data[category].keys():
                data[category].setdefault(item, dict(self.__data[category][item]))
        return data

    def get_cpu_temp(self):
        '''
        Function to get current CPU temperature. Returns float in Celsius.
        Also contained in /sys/class/thermal/thermal_zone/temp. Precision to units of Celsius.
        '''
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output[output.index(b'=') + 1:output.rindex(b"'")])

    def get_cpu_temp_prec(self):
        '''
        Function to get current CPU temperature. Returns float in Celsius.
        Contained in /sys/class/thermal/thermal_zone/temp. Precision to the 3rd decimal.
        '''
        process = Popen(['cat', TEMP_FILE], stdout=PIPE)
        output, _error = process.communicate()
        return float(output.decode()) * 0.001
   
    def measure(self):
        for c in self.__data.keys():
            for i in self.__data[c].keys():
                self.__data[c][i].get_value()

    def stats(self, out_type='print'):
        self.measure()
        if out_type == 'print':
            return str(self)
        elif out_type == 'json':
            return json.dumps(self.dict())
        elif out_type == 'dict':
            return self.dict()
        elif out_type == 'raw':
            return self.__data

if __name__ == '__main__':
    '''
    Main entrypoint of the monitor script.
    '''
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=True)
    parser.add_argument('-n', '--number', metavar='number', type=int, default=-1,
                        help='how many times the stat shall be run, default=-1 => indefinetly')
    parser.add_argument('-d', '--delay', metavar='delay', type=float, default=10.0,
                        help='delay inbetween stat refresh in seconds, default = 10.0 s')

    args = parser.parse_args()

    try:
        m = RPiMonitor()
        _i = 0
        client = mqtt.Client(client_id="rpimonitor")  # , clean_session=True, userdata=None, protocol='MQTTv311', transport="tcp")
        # client.connect('37.143.112.18', 1883, 60)
        client.connect('localhost', 1883, 60)
        while (_i < args.number) or (args.number == -1):
            os.system('clear')
            print(m.stats(out_type='print'))
            stats = m.stats(out_type='raw')
            for cat in stats:
                for key in stats[cat]:
                    # print("'rpimonitor/{0}/{1}' - '{2}'".format(cat, key, stats[cat][key].val()))
                    client.publish('rpimonitor/{0}/{1}'.format(cat, key), payload='{0}'.format(stats[cat][key].val()), qos=0, retain=False)
            _i += 1
            sleep(args.delay)
    except KeyboardInterrupt:
        pass
    finally:
        pass

