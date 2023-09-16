import RPi.GPIO as GPIO
from datetime import datetime, time, timedelta, timezone
import time as cputime
from suntime import Sun, SunTimeException
from dateutil import tz

# Flag for backup operation using fixed times
manualMode = True

# Flag for extra debug info
debug = False

# In case a localtime is necessary
tzcampinas = tz.gettz('America/Sao_Paulo')

# Coordinates for Campinas, Sao Paulo
latitude = -27.88
longitude = -47.06

# Making sure the first loop (on reboot/startup) will always update
lastMinute = 999
lastDay = 99

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

GPIO.setup(chan_list, GPIO.OUT)
GPIO.output(chan_list, GPIO.HIGH)

# Initial declaration necessary for global scope access
# light_turnOn
# light_turnOn_time
# light_turnOff
# light_turnOff_time
turnedOn = False

def print_light_status():
    global turnedOn
    if debug:
        if turnedOn:
            print("Lights are currently ON")
        else:
            print("Lights are currently OFF")
    return

def set_times(sunrise, sunset):
    global light_turnOn
    global light_turnOn_time
    global light_turnOff
    global light_turnOff_time

    # Version for machine's local time
    # sunrise = sun.get_local_sunrise_time()
    # sunset = sun.get_local_sunset_time()

    light_turnOn = sunset + timedelta(minutes=20)
    light_turnOn_time = time(light_turnOn.hour, light_turnOn.minute, tzinfo=tz.tzutc())
    light_turnOff = sunrise + timedelta(minutes=30)
    light_turnOff_time = time(light_turnOff.hour, light_turnOff.minute, tzinfo=tz.tzutc())
    return

def init():
    global manualMode
    global sunrise
    global sunset
    try:
        sun = Sun(latitude, longitude)
        sunrise = sun.get_sunrise_time()
        sunset = sun.get_sunset_time()
        set_times(sunrise, sunset)
        manualMode = False
        if debug:
            print("Initialization finalized, correctly set to AUTO TIME mode.")
    except SunTimeException as e:
        manualMode = True
        if debug:
            print("SunTime failed. Error: {0}.".format(e))
            print("!!! SWITCHING TO MANUAL TIME MODE !!!")

# Method that will get current sunrise and sunset times
# and the light times accordingly
def update_sun_times():
    global manualMode
    try:
        sun = Sun(latitude, longitude)
        sunrise = sun.get_sunrise_time()
        sunset = sun.get_sunset_time()
        set_times(sunrise, sunset)
        if (manualMode == True):
            manualMode = False
            if debug:
                print("=== Sun times successfully acquired ===")
                print("<<< Switching to AUTO TIME mode >>>")
        elif (manualMode == False):
            if debug:
                print("=== Sun times successfully updated ===")
        return True
    except SunTimeException as e:
        manualMode = True
        if debug:
            print("SunTime failed. Error: {0}.".format(e))
            print("!!! SWITCHING TO MANUAL TIME MODE !!!")
        return False

# ======================LOOP FOR AUTOMATIC MODE================================
def loopAuto():
    global lastMinute
    global lastDay
    global turnedOn
    currentTime = time(datetime.now(tz.tzutc()).hour, datetime.now(tz.tzutc()).minute, tzinfo=tz.tzutc())
    currentDay = datetime.now(tz.tzutc()).day
    
    if (currentTime.minute == lastMinute):
        if debug:
            print ("AUTO: Current minute same as last: {} UTC".
                   format(currentTime.strftime('%H:%M')))
        cputime.sleep(20)
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

        cputime.sleep(20)
    return
# ======================LOOP FOR MANUAL MODE===================================
def loopManual():
    global lastMinute
    global lastDay
    global turnedOn
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

        cputime.sleep(20)
    return

# ======================MAIN LOOP==============================================
try:
    init()
    if debug:
        print ('Sunset at {} UTC and Sunrise at {} UTC'.
           format(sunset.strftime('%H:%M'), sunrise.strftime('%H:%M')))
        print ('Lights turn on at {} UTC and turn off at {} UTC'.
           format(light_turnOn_time.strftime('%H:%M'), light_turnOff_time.strftime('%H:%M')))
        print ('BACKUP MANUAL TIME: Lights turn on at {} UTC and turn off at {} UTC'.
           format(turnOn.strftime('%H:%M'), turnOff.strftime('%H:%M')))
    while True:
        # print_light_status()
        if manualMode == False:
            loopAuto()
        elif manualMode == True:
            loopManual()

except KeyboardInterrupt:
    if debug:
        print ("Ended by keyboard interrupt")
    
except Exception as e:
    if debug:
        print ("Ended by general exception")
        print (f"Error: {str(e)}")

finally:
    GPIO.cleanup()
    if debug:
        print ("Passed by Finally block")
