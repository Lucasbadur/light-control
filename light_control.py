import RPi.GPIO as GPIO
import datetime
import time
#import atexit
#
#def exit_handler():
#    GPIO.cleanup()
#    print("Atexit block")
#    
#atexit.register(exit_handler)

# GPIO.setmode(GPIO.BCM) # GPIO numbers instead of board numbers
GPIO.setmode(GPIO.BOARD)

debug = False

turnOn = 18
turnOff = 6

in1 = 11
in2 = 13
in3 = 15
in4 = 16

chan_list = (in1, in2, in3, in4)

lastMinute = 999

turnedOn = False

GPIO.setup(chan_list, GPIO.OUT)
#GPIO.setup(in2, GPIO.OUT)
#GPIO.setup(in3, GPIO.OUT)
#GPIO.setup(in4, GPIO.OUT)

GPIO.output(chan_list, GPIO.HIGH)
# GPIO.output(in2, GPIO.HIGH)
# GPIO.output(in3, GPIO.HIGH)
# GPIO.output(in4, GPIO.HIGH)

try:
    while True:
        currentTime = datetime.datetime.now()
        if (currentTime.minute == lastMinute):
            if debug:
                print ("Current minute same as last")
                print(currentTime)
            time.sleep(10)
        else:
            if (turnedOn == False):
                if (currentTime.hour >= turnOn or currentTime.hour < turnOff):
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.LOW)
                    turnedOn = True
                    if debug:
                        print("Lights changed to ON")
                    
            elif (turnedOn == True):
                if (currentTime.hour >= turnOff and currentTime.hour < turnOn):
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.HIGH)
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.HIGH)
                    turnedOn = False
                    if debug:
                        print("Lights changed to OFF")
                    
            lastMinute = currentTime.minute
            if debug:
                print("Updated current minute")
                print(currentTime)
            time.sleep(10)

except KeyboardInterrupt:
    # GPIO.cleanup()
    print ("Ended by keyboard interrupt")
    
except:
    # GPIO.cleanup()
    print ("Ended by general exception")

finally:
    GPIO.cleanup()
    print ("Passed by Finally block")