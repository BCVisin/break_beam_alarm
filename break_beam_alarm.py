# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import time
import datetime
import subprocess
import RPi.GPIO as GPIO

# <codecell>

#the counter to know how many times it has been tripped
TRIPPED = 0

#do we want to sound the alarms?
AUDIO = False

#The volume for the alarms in % (can be more than 100%)
VOLUME = '10'

#The MP3 files of the alarms (They will loop)
ALARM1_AUDIO_FILE = '/home/pi/alarms/alarm1.mp3'
ALARM2_AUDIO_FILE = '/home/pi/alarms/alarm2.mp3'

#set up some variables
PROCESS = None
BEGIN = datetime.datetime.now()

#how long should we wait till after the button is pressed to trigger an alarma again
BUTTON_GRACE_PERIOD = 5 #in seconds
#how long after an alarm is triggered should we wait to trigger the next alarm
BREAK_GRACE_PERIOD = 1 #in seconds

#Which doors do we want active (0 = none, 1 = Door 1, 2 = Door 2, 3 = All)
DOORS = 3

#setup the sensitivity threshold for the analog reading on the ADC chip
ANALOG_PIN0_SENSITIVITY = 900
ANALOG_PIN1_SENSITIVITY = 700
PATL = {0:ANALOG_PIN0_SENSITIVITY, 1:ANALOG_PIN1_SENSITIVITY}


# <codecell>

GPIO.setwarnings(False)

#Name and number the GPIO pins
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

LASER1 = 2
LASER2 = 3

BUTTON1 = 4
BUTTON2 = 18
ALARM1 = 14
ALARM2 = 15

TOGGLE = 17

GPIO.setmode(GPIO.BCM)

# set up the GPIO
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)


GPIO.setup(LASER1,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LASER2,GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(BUTTON1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(TOGGLE,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(ALARM1,GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(ALARM2,GPIO.OUT, initial=GPIO.HIGH)

# <codecell>

#the bit bangled implementation of the ADC chip
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False) 
        GPIO.output(cspin, False)
 
        commandout = adcnum
        commandout |= 0x18
        commandout <<= 3
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1
        return adcout

# <codecell>

#sense if the door has been tripped
def sense_trip(pins_and_trip_limit):
    
    #how many readings to take and average.  It takes about 2K reading as second
    average_count = 500
    
    patl = PATL
    
    #Block and wait till we sense it's tripped
    while True:
        #if we detect that the global PATL variable has changed, we don't want to block so we return false
        if PATL != patl:
            return False
        
        #set up the sum for the average
        light_sum = {x:0 for x in pins_and_trip_limit.keys()}
        #loop through to add it all up
        for i in range(0, average_count):
            for adc_pin in pins_and_trip_limit.keys():
                light_sum[adc_pin] += readadc(adc_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        #loop through to check if we crossd the threshold
        for adc_pin, tripped_limit in pins_and_trip_limit.items():
            if (light_sum[adc_pin] / average_count) < tripped_limit:
                #if we have return True
                return True

# <codecell>

#if we press the clear button we want to do stuff
def button_clear(channel):
    
    global TRIPPED
    global PROCESS
    global BEGIN
    
    #if the sensor has been tripped reset the counter, clear the alarms, and kill the process
    if TRIPPED > 0:
        TRIPPED = 0
        GPIO.output(ALARM1, GPIO.HIGH)
        GPIO.output(ALARM2, GPIO.HIGH)
        if PROCESS:
            PROCESS.kill()
    #otherwise we just want to reset the timer so we have time to cross the beam without the alarm going off
    else:
       BEGIN = datetime.datetime.now() 
    

# <codecell>


def toggle_doors(channel):
    
    """This toggle switch changes between none, door one, door two, or both"""
    
    global DOORS
    global PATL
    global BEGIN
    
    #reset the time so we don't accidently set the alarm off when switching
    BEGIN = datetime.datetime.now()
    
    #increment the doors
    DOORS += 1
    if DOORS > 3:
        #if we have reached 3, reset it to 0
        DOORS = 0
    
    #sensors off
    if DOORS == 0:
        PATL = {}
        GPIO.output(LASER1,GPIO.HIGH)
        GPIO.output(LASER2,GPIO.HIGH)
    #single door on
    elif DOORS == 1:
        PATL = {0:ANALOG_PIN0_SENSITIVITY}
        GPIO.output(LASER1,GPIO.HIGH)
        GPIO.output(LASER2,GPIO.LOW)
    #single door off
    elif DOORS == 2:
        PATL = {1:ANALOG_PIN1_SENSITIVITY}
        GPIO.output(LASER1,GPIO.LOW)
        GPIO.output(LASER2,GPIO.HIGH)
    #both doors on
    elif DOORS == 3:
        PATL = {0:ANALOG_PIN0_SENSITIVITY, 1:ANALOG_PIN1_SENSITIVITY}
        GPIO.output(LASER1,GPIO.LOW)
        GPIO.output(LASER2,GPIO.LOW)

    

# <codecell>

def main_loop():
    
    global TRIPPED
    global PROCESS
    global BEGIN
    global PATL
    
    #setup the callbacks to the buttons
    try:
        GPIO.add_event_detect(BUTTON2, GPIO.FALLING, callback=button_clear, bouncetime=500)
    except RuntimeError, e:
        print e
    
    try:
        GPIO.add_event_detect(BUTTON1, GPIO.FALLING, callback=button_clear,  bouncetime=500)
    except RuntimeError, e:
        print e
    
    try:
        GPIO.add_event_detect(TOGGLE, GPIO.FALLING, callback=toggle_doors, bouncetime=500)
    except RuntimeError, e:
        print e
    
    try:
        #run the loop
        while True:
            #block and wait on the sensor to return
            if sense_trip(PATL):
                #Only trip the sensor if we have gone past the grace period
                if (datetime.datetime.now() - BEGIN).seconds > BUTTON_GRACE_PERIOD or (TRIPPED and (datetime.datetime.now() - BEGIN).seconds > BREAK_GRACE_PERIOD):
                    #increment the trip counter
                    TRIPPED += 1
                    #reset the timer
                    BEGIN = datetime.datetime.now()
                    #if this not the first time it has been tripped, sound the second alarm
                    if TRIPPED > 1:
                        #turn on the alarm
                        GPIO.output(ALARM2, GPIO.LOW)
                        if AUDIO:
                            #if we have audio playing, kill it
                            if PROCESS:
                                PROCESS.kill()
                            #play the second alarm
                            PROCESS = subprocess.Popen(['mpg321', '--gain', VOLUME, '--loop', '0', ALARM2_AUDIO_FILE], stdin=subprocess.PIPE)
                    #this is the first time we have tripped the alarm
                    else:
                        #turn on the alarm
                        GPIO.output(ALARM1, GPIO.LOW)
                        if AUDIO:
                            #if we somehow have audio running, kill it
                            if PROCESS:
                                PROCESS.kill()
                            #play the first alarm
                            PROCESS = subprocess.Popen(['mpg321', '--gain', VOLUME, '--loop', '0', ALARM1_AUDIO_FILE], stdin=subprocess.PIPE)
            #returned false so we sleep a bit and run it again
            else:
                time.sleep(.2)
                
                
    except KeyboardInterrupt:
        #gracefully shutdown on a keyboard interrupt
        GPIO.remove_event_detect(BUTTON2)
        GPIO.remove_event_detect(BUTTON1)
        GPIO.remove_event_detect(TOGGLE)
        GPIO.cleanup()
        time.sleep(1)
            

# <codecell>

main_loop()

