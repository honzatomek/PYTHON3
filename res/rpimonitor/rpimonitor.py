#!/usr/bin/python3
'''
Monitors current RaspberryPi performance stats and prints them on screen.
''' 

# general imports
from subprocess import PIPE, Popen
import psutil
import argparse
import os
from time import sleep
import json


class Value:
    __s = [21, 3, 8, 4]          # spacing
    __a = ['<', '^', '>', '<']   # align
    __d = '='                    # delimiter

    def __init__(self, description, value, fmt, units):
        self.description = description
        self.value = value
        if '{0:' not in fmt:
            self.fmt = '{0:' + fmt + '}'
        else:
            self.fmt = fmt
        self.units = units

    def __str__(self):
        out = ''
        for i in range(4):
            out += '{' + str(i) + ':' + self.__a[i] + str(self.__s[i]) + '}'

        out = out.format(self.description, self.__d, self.fmt.format(self.value), ' ' + self.units)
        return out


class Monitor:
    def __init__(self):
        self.__cpu_temp = Value('CPU Temperature', 0.0, '{0:0.2f}', "'C")
        self.__cpu_usage = Value('CPU Usage', 0.0, '{0:0.2f}', '%')
        self.__cpu_count = Value('CPU Count', 0, '{0:0.0f}', '')
        self.__cpu_freq_current = Value('CPU Frequency Current', '0.0', '{0:0.2f}', 'Hz')
        self.__cpu_freq_min = Value('CPU Frequency Min', '0.0', '{0:0.2f}', 'Hz')
        self.__cpu_freq_max = Value('CPU Frequency Max', '0.0', '{0:0.2f}', 'Hz')

        self.__ram_total = Value('RAM Total', '0.0', '{0:0.2f}', 'MiB')
        self.__ram_used = Value('RAM Used', '0.0', '{0:0.2f}', 'MiB')
        self.__ram_free = Value('RAM Free', '0.0', '{0:0.2f}', 'MiB')
        self.__ram_avail = Value('RAM Available', '0.0', '{0:0.2f}', 'MiB')
        self.__ram_perc_used = Value('RAM Percent Used', '0.0', '{0:0.2f}', '%')

        self.__disk_total = Value('Disk Total', '0.0', '{0:0.2f}', 'GiB')
        self.__disk_used = Value('Disk Used', '0.0', '{0:0.2f}', 'GiB')
        self.__disk_free = Value('Disk Free', '0.0', '{0:0.2f}', 'GiB')
        self.__disk_perc_used = Value('Disk Percent Used', '0.0', '{0:0.2f}', '%')

    def __str__(self):
        out = 'CPU:\n'
        for v in [self.__cpu_temp, self.__cpu_usage, self.__cpu_count, 
                  self.__cpu_freq_current, self.__cpu_freq_min, self.__cpu_freq_max]:
            # print(v)
            out += '{0}\n'.format(str(v))

        out += '\nRAM:\n'
        for v in [self.__ram_total, self.__ram_used, self.__ram_free, 
                  self.__ram_avail, self.__ram_perc_used]:
            out += '{0}\n'.format(str(v))
            
        out += '\nDISK:\n'
        for v in [self.__disk_total, self.__disk_used, self.__disk_free, self.__disk_perc_used]:
            out += '{0}\n'.format(str(v))

        return out

    def __get_cpu_temperature_coarse(self):
        '''
        Function to get current CPU temperature. Returns float in Celsius.
        Also contained in /sys/class/thermal/thermal_zone/temp. Precision to units of Celsius.
        '''
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output[output.index(b'=') + 1:output.rindex(b"'")])

    def __get_cpu_temperature_fine(self):
        '''
        Function to get current CPU temperature. Returns float in Celsius.
        Contained in /sys/class/thermal/thermal_zone/temp. Precision to the 3rd decimal.
        '''
        process = Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output.decode()) * 0.001
    
    def __get_values(self):
        self.__cpu_temp.value = self.__get_cpu_temperature_fine()
        self.__cpu_usage.value = psutil.cpu_percent(0.1, False)
        self.__cpu_count.value = psutil.cpu_count()
        cpu = psutil.cpu_freq()
        self.__cpu_freq_current.value = cpu.current
        self.__cpu_freq_min.value = cpu.min
        self.__cpu_freq_max.value = cpu.max

        ram = psutil.virtual_memory()
        self.__ram_total.value = ram.total / 2**20  
        self.__ram_used.value = ram.used / 2**20  
        self.__ram_free.value = ram.free / 2**20  
        self.__ram_avail.value = ram.available / 2**20  
        self.__ram_perc_used.value = ram.percent 

        disk = psutil.disk_usage('/')
        self.__disk_total.value = disk.total / 2**30
        self.__disk_used.value = disk.used / 2**30
        self.__disk_free.value = disk.free / 2**30
        self.__disk_perc_used.value = disk.percent

    def monitor(self, out='print'):
        self.__get_values()
        if out == 'print':
            return str(self)
        elif out == 'json':



    def get_dict(self):
        self.__get_values()
        data = {'CPU': {self.__cpu_temp.description: self.__cpu_temp.value,
                        self.__cpu_usage.description: self.__cpu_usage.value,
                        self.__cpu_count.description: self.__cpu_count.value,
                        self.__cpu_freq_current.description: self.__cpu_freq_current.value,
                        self.__cpu_freq_min.description: self.__cpu_freq_min.value,
                        self.__cpu_freq_max.description: self.__cpu_freq_max.value},
                'RAM': {self.__ram_total.description: self.__ram_total.value,
                        self.__ram_used.description: self.__ram_used.value,
                        self.__ram_free.description: self.__ram_free.value,
                        self.__ram_avail.description: self.__ram_avail.value,
                        self.__ram_perc_used.description: self.__ram_perc_used.value},
                'DISK': {self.__disk_total.description: self.__disk_total.value,
                         self.__disk_used.description: self.__disk_used.value,
                         self.__disk_free.description: self.__disk_free.value,
                         self.__disk_perc_used.description: self.__disk_perc_used.value}}

        return data


if __name__ == '__main__':
    '''
    Main entrypoint of the monitor script.
    '''
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=True)
    parser.add_argument('-n', '--number', metavar='number', type=int, default=-1,
                        help='how many times the stat shall be run, default=-1 => indefinetly')
    parser.add_argument('-d', '--delay', metavar='delay', type=float, default=5.0,
                        help='delay inbetween stat refresh in seconds, default = 5.0 s')
    args = parser.parse_args()

    try:
        m = Monitor()
        m.object_for_json()
        _i = 0
        while (_i < args.number) or (args.number == -1):
            os.system('clear')
            print(m.monitor(out='print'))
            _i += 1
            sleep(args.delay)
    except KeyboardInterrupt:
        pass
    finally:
        pass

