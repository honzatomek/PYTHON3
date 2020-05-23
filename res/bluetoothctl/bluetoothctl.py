#!/usr/local/bin/python3.7
'''
Module to automate bluetoothctl service
'''

# <-------------------------------------------------------------- global imports --->
import time
import pexpect
import subprocess
import sys
import re


# <------------------------------------------------------------ global variables --->
BLOCK = '[\x1b[0;92mNEW\x1b[0m]'


# <--------------------------------------------------------- main body of module --->
class BluetoothctlError(Exception):
    '''
    Exception for bluetoothctl command
    '''
    pass


class Bluetoothctl:
    '''
    Class wrapper for bluetoothctl command on linux
    '''


    def __init__(self):
        '''
        Create a bluetoothctl process in background
        '''
        self.child = pexpect.spawn('bluetoothctl', echo=False)


    def get_output(self, command='help', pause=0):
        '''
        Run a command in bluetoothctl prompt and return output as a list of lines.
        '''
        self.child.send(f'{command}\r\n'.encode('ascii'))
        time.sleep(pause)
        start_failed = self.child.expect(['#', pexpect.EOF])

        if start_failed:
            raise BluetoothctlError('[-] Bluetoothctl failed after running ' + command)

        out = self.child.before.decode('ascii').split('\r\n')[:-1]

        return [o for o in out if not BLOCK in o]


    def scan_on(self):
        '''
        Start bluetooth scanning process
        '''
        try:
            out = self.get_output('scan on')
        except BluetoothctlError as e:
            print(e)
            return None


    def scan_off(self):
        '''
        Stop bluetooth scanning process
        '''
        try:
            out = self.get_output('scan off')
        except BluetoothctlError as e:
            print(e)
            return None


    def power_on(self):
        '''
        Turn controller power on
        '''
        try:
            out = self.get_output('power on')
        except BluetoothctlError as e:
            print(e)
            return None


    def power_off(self):
        '''
        Turn controller power off
        '''
        try:
            out = self.get_output('power off')
        except BluetoothctlError as e:
            print(e)
            return None


    def pairable_on(self):
        '''
        Make controller pairable
        '''
        try:
            out = self.get_output('pairable on')
        except BluetoothctlError as e:
            print(e)
            return None


    def pairable_off(self):
        '''
        Make controller unpairable
        '''
        try:
            out = self.get_output('pairable off')
        except BluetoothctlError as e:
            print(e)
            return None


    def discoverable_on(self):
        '''
        Make controller discoverable
        '''
        try:
            out = self.get_output('discoverable on')
        except BluetoothctlError as e:
            print(e)
            return None


    def discoverable_off(self):
        '''
        Make controller non-discoverable
        '''
        try:
            out = self.get_output('discoverable off')
        except BluetoothctlError as e:
            print(e)
            return None


    def parse_controller(self, ctrl_string):
        '''
        Parse controller mac address and name
        '''
        controller = {}
        try:
            ctrl_position = ctrl_string.index('Controller')
        except ValueError:
            pass
        else:
            if ctrl_position > -1:
                attribute_list = ctrl_string[ctrl_position:].split(' ', 2)
                controller = {'mac_address': attribute_list[1], 'name': attribute_list[2]}
                if '[default]' in controller['name']:
                    controller['name'] = controller['name'].replace('[default]', '').rstrip()
                    controller['default'] = True
                else:
                    controller['default'] = False

                return controller


    def list_controllers(self):
        '''
        List available controllers
        '''
        try:
            out = self.get_output('list')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            controllers = []
            for line in out:
                controller = self.parse_controller(line)
                if controller:
                    controllers.append(controller)

            return controllers


    def parse_info(self, info_string):
        '''
        Parse controller or device info
        '''
        info = {}
        info['UUID'] = {}
        for line in info_string:
            line = line.strip()
            if 'not available' in line:
                return None
            if line.split(' ')[0].strip() in ['Controller', 'Device']:
                info.setdefault(line.split(' ')[0].strip(), line.split(' ')[1])
            elif line.startswith('UUID:'):
                tmp = line.split(':', 2)[1]
                info['UUID'].setdefault(tmp.split('(')[0].strip(), tmp.split('(')[1].strip(')'))
            else:
                info.setdefault(line.split(':', 1)[0].strip(), line.split(':', 1)[1].strip())

        return info


    def get_controller_info(self, mac_address=''):
        '''
        Show controller info, if mac_address = '' then default controller
        '''
        try:
            if not mac_address:
                out = self.get_output('show')
            else:
                out = self.get_output(f'show {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            controller = self.parse_info(out)

            return controller


    def select_controller(self, mac_address):
        '''
        Select default bluetooth controller by mac address
        '''
        try:
            out = self.get_output(f'select {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None


    def parse_device_info(self, info_string):
        '''
        Parse a string corresponding to a device.
        '''
        device = {}
        block_list = ['removed']
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index('Device')
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(' ', 2)
                    device = {'mac_address': attribute_list[1], 'name': attribute_list[2]}

        return device


    def get_available_devices(self):
        '''
        Return a list of tuples off paired and discoverable devices.
        '''
        try:
            out = self.get_output('devices')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            if len(out) == 0:
                return None
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)

            return available_devices


    def get_paired_devices(self):
        '''
        Return a list of tuples of paired devices.
        '''
        try:
            out = self.get_output('paired-devices')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)

            return paired_devices


    def get_discoverable_devices(self):
        '''
        Filter paired devices out of available .
        '''
        available = self.get_available_devices()
        paired = self.get_paired_devices()

        return [d for d in available if d not in paired]


    def get_device_info(self, mac_address=''):
        '''
        Get device info by mac address.
        '''
        try:
            out = self.get_output(f'info {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            if 'Missing device address argument' in out:
                raise BluetoothctlError('Missing device mac address argument')

            device = self.parse_info(out)

            return device


    def pair(self, mac_address):
        '''
        Try to pair with a device by MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'pair {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['Failed to pair', 'Pairing successful', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def trust(self, mac_address):
        '''
        Trust a device by MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'trust {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['not available', 'trust succeeded', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def untrust(self, mac_address):
        '''
        Untrust a device by MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'untrust {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['not available', 'untrust succeeded', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def block(self, mac_address):
        '''
        Block a device by MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'block {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['not available', 'block succeeded', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def unblock(self, mac_address):
        '''
        Unblock a device by MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'unblock {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['not available', 'unblock succeeded', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def remove(self, mac_address):
        '''
        Remove paired device bz MAC address, return success of the operation.
        '''
        try:
            out = self.get_output(f'remove {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['not available', 'Device has been removed', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def connect(self, mac_address):
        '''
        Try to connect to a device by MAC address, return success of the operation.
        '''
        try:
            # out = self.get_output(f'connect {mac_address}', 2)
            out = self.get_output(f'connect {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['Failed to connect', 'Connection successful', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def disconnect(self, mac_address):
        '''
        Try to disconnect a device by MAC address, return success of the operation.
        '''
        try:
            # out = self.get_output(f'disconnect {mac_address}', 2)
            out = self.get_output(f'disconnect {mac_address}')
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(['Failed to disconnect', 'Successful disconnect', pexpect.EOF])
            success = True if res == 1 else False

            return success


    def get_version(self):
        '''
        Get bluetoothctl version
        '''
        try:
            out = self.get_output('version')
        except BluetoothctlError as e:
            print(e)
            return None
        else:

            return out

    
    def is_connected(self, mac_address):
        '''
        Check if a device is connected and return True/False
        '''
        try:
            device = self.get_device_info(mac_address)
        except BluetoothctlError as e:
            print(e)
            return False
        else:
            if device:
                connected = True if device['Connected'] == 'yes' else False
            else:
                connected = False
            
            return connected


# <-------------------------------------------------------------------- solo run --->
if __name__ == '__main__':
    bl = Bluetoothctl()
    print(f'[+] Starting {__file__}')
    print(bl.get_version())
