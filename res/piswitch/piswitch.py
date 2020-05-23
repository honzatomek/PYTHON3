#!/usr/bin/python3.5
'''
Script to handle Pi Switch v1.1 breakout board.
    PIN_EIGHT needs to be 1 and connected to PS to disable automatic shutdown after
    2 minutes.
    
    PIN_SEVEN waits for 1 - signal to turn RPi off.
'''

# global imports -------------------------------------------------------------->
# Import the modules to send commands to the system and access GPIO pins
import subprocess
import RPi.GPIO as GPIO
import time
import datetime


# global variables ------------------------------------------------------------>
# Map pin 7 and 8 on the Pi Switch PCB to chosen pins on the Raspberry Pi header
# The PCB numbering is a legacy with the original design of the board
LOG_FILE = '/home/pi/log/piswitch.log'
PIN_SEVEN = 7
PIN_EIGHT = 11
STATUS = {'ok': '[+]', 'error': '[-]', 'info': '[i]'}


# auxiliary functions --------------------------------------------------------->
def now():
    '''
    Returns current date and time in YYYYMMDD-HHMMSS format
    '''
    return '{0:%Y%m%d-%H%M%S}'.format(datetime.datetime.now())


def log(text='', level=0, stat='ok'):
    '''
    Creates an entry in the LOG_FILE, if text is not supplied, writes current
    date and time
    '''
    if text == '':
        text = now()
    if stat not in STATUS.keys():
        stat = 'info'
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write('{0} {1} {2}\n'.format(STATUS[stat], level * '\t', text))


def shutdown():
    '''
    Send "sudo shutdown" command to terminal.
    '''
    message = '{0} Shutdown'.format(now())
    print(message)
    log(message, 1, 'ok')
    GPIO.output(PIN_EIGHT, 0) 
    GPIO.output(PIN_EIGHT, 0) # Bring down PinEight so that the capacitor can discharge and remove power to the Pi
    subprocess.call('shutdown', shell=False) # Initiate OS Shutdown
    
    
def poweroff():
    '''
    Send "sudo poweroff" command to terminal.
    '''
    message = '{0} Poweroff'.format(now())
    print(message)
    log(message, 1, 'ok')
    GPIO.output(PIN_EIGHT, 0) # Bring down PinEight so that the capacitor can discharge and remove power to the Pi
    subprocess.call('poweroff', shell=False) # Initiate OS Poweroff


def reboot():
    '''
    Send "sudo reboot" command to terminal.
    '''
    message = '{0} Reboot'.format(now())
    print(message)
    log(message, 1, 'ok')
    GPIO.output(PIN_EIGHT, 0) # Bring down PinEight so that the capacitor can discharge and remove power to the Pi
    subprocess.call('reboot', shell=False) # Initiate OS Reboot


def loop():
    '''
    Function to keep the script running in background
    '''
    message = '{0} Waiting for button press on PIN {1}.'.format(now(), PIN_SEVEN)
    print(message)
    log(message, 1, 'ok')
    # input()
    while True:
        time.sleep(1)


def rising(pin):
    '''
    Callback for button press
    '''
    # RISING_START = time.time()
    time.sleep(0.1) # sleep 100ms to avoid triggering a shutdown when a spike occured
    if GPIO.input(PIN_SEVEN) == True:
        time.sleep(1.9) # sleep the rest to 2s to distinguish long press from short press
        if GPIO.input(PIN_SEVEN) == True: # long press
            # message = '{0} Reboot.'.format(now())
            # print(message)
            # log(message, 1, 'ok')
            reboot()
        else: # short press
            # message = '{0} Poweroff.'.format(now())
            # print(message)
            # log(message, 1, 'ok')
            poweroff()


# main script function -------------------------------------------------------->
def piswitch():
    '''
    Main function to be run to handle Pi Switch v1.1 breakout board.
    '''
    try:
        message = '{0} Script {1} started.'.format(now(), __file__)
        print(message)
        log(message, 0, 'ok')

        GPIO.setmode(GPIO.BOARD) # Set pin numbering to board numbering
        GPIO.setup(PIN_SEVEN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set up PinSeven as an input
        GPIO.setup(PIN_EIGHT, GPIO.OUT, initial=1) # Setup PinEight as output
    
        # Set up interrupt to look for button press  
        GPIO.add_event_detect(PIN_SEVEN, GPIO.RISING, callback=rising, bouncetime=200)
    
        loop()
    except Exception as e:
        message = '{0} Script {1} has ended with exception: {2}'.format(now(), __file__, e)
        print(message)
        log(message, 1, 'error')


# Script main entry point ----------------------------------------------------->
if __name__ == '__main__':
    piswitch()

