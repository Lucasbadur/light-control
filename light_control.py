import RPi.GPIO as GPIO
from datetime import datetime, time, timedelta, timezone
import time as cputime
from suntime import Sun, SunTimeException
from dateutil import tz

# Flag for backup operation using fixed times
manualMode = False

# Flag for extra debug info
debug = True

# In case a localtime is necessary
tzcampinas = tz.gettz('America/Sao_Paulo')

# Coordinates for Campinas, Sao Paulo
latitude = -27.88
longitude = -47.06

# GPIO.setmode(GPIO.BCM) # GPIO numbers instead of board numbers
GPIO.setmode(GPIO.BOARD)

# Use UTC time
turnOn = time(21,15, tzinfo=tz.tzutc())
turnOff = time(9,20, tzinfo=tz.tzutc())

# Setting which ports to use
relay1 = 11
relay2 = 13
relay3 = 15
relay4 = 16
chan_list = (relay1, relay2, relay3, relay4)

# Making sure the first loop (on reboot/startup) will always update
lastMinute = 999
lastDay = 99

turnedOn = False

GPIO.setup(chan_list, GPIO.OUT)
GPIO.output(chan_list, GPIO.HIGH)

# Initial declaration necessary for global scope access
try:
    sun = Sun(latitude, longitude)
    sunrise = sun.get_sunrise_time()
    sunset = sun.get_sunset_time()
    # Version for machine's local time
    # sunrise = sun.get_local_sunrise_time()
    # sunset = sun.get_local_sunset_time()
    light_turnOn = sunset + timedelta(minutes=20)
    light_turnOn_time = time(light_turnOn.hour, light_turnOn.minute, tzinfo=tz.tzutc())
    light_turnOff = sunrise + timedelta(minutes=30)
    light_turnOff_time = time(light_turnOff.hour, light_turnOff.minute, tzinfo=tz.tzutc())
except SunTimeException as e:
    if debug:
        print("SunTime failed. Error: {0}.".format(e))
        print("!!! SWITCHING TO MANUAL TIME MODE !!!")
    manualMode = True

# Method that will get current sunrise and sunset times
# and the light times accordingly
def update_sun_times():
    try:
        sun = Sun(latitude, longitude)
        sunrise = sun.get_sunrise_time()
        sunset = sun.get_sunset_time()
        # Version for machine's local time
        # sunrise = sun.get_local_sunrise_time()
        # sunset = sun.get_local_sunset_time()
        light_turnOn = sunset + timedelta(minutes=20)
        light_turnOn_time = time(light_turnOn.hour, light_turnOn.minute, tzinfo=tz.tzutc())
        light_turnOff = sunrise + timedelta(minutes=30)
        light_turnOff_time = time(light_turnOff.hour, light_turnOff.minute, tzinfo=tz.tzutc())
        if (manualMode == True):
            if debug:
                print("=== Sun times acquired, switching to sunrise/sunset mode ===")
            manualMode = False
        elif (manualMode == False):
            if debug:
                print("=== Sun times updated ===")
        return True
    except SunTimeException as e:
        if debug:
            print("SunTime failed. Error: {0}.".format(e))
            print("!!! SWITCHING TO MANUAL TIME MODE !!!")
        manualMode = True
        return False

if debug:
    print ('Sunrise at {} UTC and Sunset at {} UTC'.
       format(sunrise.strftime('%H:%M'), sunset.strftime('%H:%M')))
    print ('Lights will turn on at {} UTC and turn off at {} UTC'.
       format(light_turnOn_time.strftime('%H:%M'), light_turnOff_time.strftime('%H:%M')))
    print ('BACKUP MANUAL TIME: Lights will turn on at {} UTC and turn off at {} UTC'.
       format(turnOn.strftime('%H:%M'), turnOff.strftime('%H:%M')))

# ======================MAIN LOOP==============================================
try:
    while True:
# ======================LOOP FOR AUTOMATIC MODE================================
        while manualMode == False:
            currentTime = time(datetime.now(tz.tzutc()).hour, datetime.now(tz.tzutc()).minute, tzinfo=tz.tzutc())
            currentDay = datetime.now(tz.tzutc()).day
            
            if (currentTime.minute == lastMinute):
                if debug:
                    print ("AUTO: Current minute same as last: {} UTC".
                           format(currentTime.strftime('%H:%M')))
                cputime.sleep(10)
            else:
                if (turnedOn == False):
                    if (currentTime >= light_turnOn_time or currentTime < light_turnOff_time):
                        GPIO.output(chan_list, GPIO.LOW)
                        turnedOn = True
                        if debug:
                            print("AUTO: Lights changed to ON")
                        
                elif (turnedOn == True):
                    if (currentTime >= light_turnOff_time and currentTime < light_turnOn_time):
                        GPIO.output(chan_list, GPIO.HIGH)
                        turnedOn = False
                        if debug:
                            print("AUTO: Lights changed to OFF")
                        
                lastMinute = currentTime.minute
                
                
                if (currentDay != lastDay):
                    update_sun_times()
                lastDay = currentDay
                if debug:
                    print("AUTO: Updated current minute: {} UTC".
                          format(currentTime.strftime('%H:%M')))
                cputime.sleep(10)
# ======================LOOP FOR MANUAL MODE===================================
        while manualMode == True:
            currentTime = time(datetime.now(tz.tzutc()).hour, datetime.now(tz.tzutc()).minute, tzinfo=tz.tzutc())
            currentDay = datetime.now(tz.tzutc()).day
            if (currentTime.minute == lastMinute):
                if debug:
                    print ("MANUAL: Current minute same as last: {} UTC".
                           format(currentTime.strftime('%H:%M')))
                cputime.sleep(10)
            else:
                if (turnedOn == False):
                    if (currentTime >= turnOn or currentTime < turnOff):
                        GPIO.output(chan_list, GPIO.LOW)
                        turnedOn = True
                        if debug:
                            print("MANUAL: Lights changed to ON")
                        
                elif (turnedOn == True):
                    if (currentTime >= turnOff and currentTime < turnOn):
                        GPIO.output(chan_list, GPIO.HIGH)
                        turnedOn = False
                        if debug:
                            print("MANUAL: Lights changed to OFF")
                        
                lastMinute = currentTime.minute
                
                
                if (currentDay != lastDay):
                    update_sun_times()
                lastDay = currentDay
                if debug:
                    print("MANUAL: Updated current minute: {} UTC".
                          format(currentTime.strftime('%H:%M')))
                cputime.sleep(10)
# =============================================================================
except KeyboardInterrupt:
    if debug:
        print ("Ended by keyboard interrupt")
    
except:
    if debug:
        print ("Ended by general exception")

finally:
    GPIO.cleanup()
    if debug:
        print ("Passed by Finally block")