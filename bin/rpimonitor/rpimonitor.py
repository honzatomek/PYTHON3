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


# global variables


def get_cpu_temperature():
    '''
    Function to get current CPU temperature. Returns float in Celsius.
    Also contained in /sys/class/thermal/thermal_zone/temp
    '''
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index(b'=') + 1:output.rindex(b"'")])


def monitor():
    '''
    Function that returns current Raspberry stats as \n delimited string.
    '''
    cpu_temperature = get_cpu_temperature()
    stat = 'CPU Temperature       = {0:0.2f} C'.format(cpu_temperature)
    cpu_usage = psutil.cpu_percent(0.1, False)
    stat += '\nCPU Usage             = {0:0.2f} %'.format(cpu_usage)
    stat += '\nCPU Count             = {0:0.0f}'.format(psutil.cpu_count())
    freqs = psutil.cpu_freq()
    stat += '\nCPU Frequency Current = {0:0.2f} Hz'.format(freqs.current)
    stat += '\nCPU Frequency Min     = {0:0.2f} Hz'.format(freqs.min)
    stat += '\nCPU Frequency Max     = {0:0.2f} Hz'.format(freqs.max)
    stat += '\n'
    ram = psutil.virtual_memory()
    ram_total = ram.total / 2**20       # MiB.
    stat += '\nRAM Total             = {0:0.2f} MB'.format(ram_total)
    ram_used = ram.used / 2**20
    stat += '\nRAM Used              = {0:0.2f} MB'.format(ram_used)
    ram_free = ram.free / 2**20
    stat += '\nRAM Free              = {0:0.2f} MB'.format(ram_free)
    ram_available = ram.available / 2**20
    stat += '\nRAM Available         = {0:0.2f} MB'.format(ram_available)
    ram_percent_used = ram.percent
    stat += '\nRAM Percent Used      = {0:0.2f} %'.format(ram_percent_used)
    stat += '\n'
    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    stat += '\nDisk Total            = {0:0.2f} GB'.format(disk_total)
    disk_used = disk.used / 2**30
    stat += '\nDisk Used             = {0:0.2f} GB'.format(disk_used)
    disk_free = disk.free / 2**30
    stat += '\nDisk Free             = {0:0.2f} GB'.format(disk_free)
    disk_percent_used = disk.percent
    stat += '\nDisk Percent          = {0:0.2f} %'.format(disk_percent_used)
    
    # stat = stat.split('\n')
    # stat = [a.split('=') for a in stat]
    # mx = max([len(a[0]) for a in stat])
    # for line in stat:
    #     if line[0] != '':
    #         line[0] = line[0] + (mx - len(line[0])) * ' '
    # stat = '\n'.join(['='.join(row) for row in stat])

    return stat


def main(number=-1, delay=5.0):
    '''
    Main script function, controls screen cleaning, refreshing and
    printing the stats in selected manner.
    '''
    i = 1
    while (i < number) or (number == -1):
        os.system('clear')
        stat = monitor()
        print(stat)
        sleep(delay)
        i += 1
    os.system('clear')
    stat = monitor()
    print(stat)


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
    #  print(str(args.number) + ' ' + str(args.delay))
    try:
        main(args.number, args.delay)
    except KeyboardInterrupt:
        pass
    finally:
        pass

