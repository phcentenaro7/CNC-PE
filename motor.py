import RPi.GPIO as GPIO
from time import sleep
import sys
        
#Clockwise/Counterclockwise rotation values
CW = 1 #Away from motor
CCW = 0 #Closer to motor

#GPIO pin setup
DIR_X = 11
DIR_X_VAL = CW
STEP_X = 12
ENA_X = 23
DIR_Y = 16
DIR_Y_VAL = CW
STEP_Y = 18
ENA_Y = 21
SENSOR_X_BEGIN = 22
SENSOR_Y_BEGIN = 24
RED_BUTTON = 37
YELLOW_BUTTON = 33
GREEN_BUTTON = 35
RED_LED = 36
YELLOW_LED = 38
GREEN_LED = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR_X, GPIO.OUT)
GPIO.setup(STEP_X, GPIO.OUT)
GPIO.setup(ENA_X, GPIO.OUT)
GPIO.setup(DIR_Y, GPIO.OUT)
GPIO.setup(STEP_Y, GPIO.OUT)
GPIO.setup(ENA_Y, GPIO.OUT)
GPIO.setup(SENSOR_X_BEGIN, GPIO.IN)
GPIO.setup(SENSOR_Y_BEGIN, GPIO.IN)
GPIO.setup(RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(YELLOW_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GREEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
CM = 16000
SLEEP_TIME = 0.0000001
GPIO.output(GREEN_LED, GPIO.HIGH)
GPIO.output(ENA_X, GPIO.LOW)
GPIO.output(ENA_Y, GPIO.LOW)

EMERGENCY = 0
START_STATE = 1
AT_ORIGIN = 2
ROUTING = 3
STATE = START_STATE
        
#Speed in steps per second
def run_steps(dir_pin, step_pin, ena_pin, sensor_pin, rotation, sleep_time, steps):
    for step in range(int(steps)):
        if GPIO.input(RED_BUTTON) == GPIO.HIGH:
            GPIO.output(RED_LED, GPIO.HIGH)
            GPIO.output(YELLOW_LED, GPIO.LOW)
            GPIO.output(GREEN_LED, GPIO.LOW)
            sleep(3)
            STATE = EMERGENCY
            return
        GPIO.output(dir_pin, rotation)
        if sensor_pin != 0 and GPIO.input(sensor_pin) == 0:
            GPIO.output(step_pin, GPIO.LOW)
            return
        else:
            GPIO.output(step_pin, GPIO.HIGH)
        sleep(sleep_time)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(sleep_time)

try:
    while True:
        GPIO.output(GREEN_LED, GPIO.HIGH)
        if GPIO.input(GREEN_BUTTON) == 1 and STATE == START_STATE:
            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(YELLOW_LED, GPIO.HIGH)
            run_steps(DIR_Y, STEP_Y, ENA_Y, SENSOR_Y_BEGIN, CCW, SLEEP_TIME, sys.maxsize)
            run_steps(DIR_X, STEP_X, ENA_X, SENSOR_X_BEGIN, CCW, SLEEP_TIME, sys.maxsize)
            STATE = AT_ORIGIN
            GPIO.output(GREEN_LED, GPIO.HIGH)
        elif GPIO.input(YELLOW_BUTTON) == GPIO.HIGH and STATE == AT_ORIGIN:
            STATE = ROUTING
            GPIO.output(GREEN_LED, GPIO.LOW)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CW, SLEEP_TIME, 3.7*CM)
            run_steps(DIR_X, STEP_X, ENA_X, 0, CW, SLEEP_TIME, 6.35*CM)
            sleep(5)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CCW, SLEEP_TIME, 1.6*CM)
            sleep(5)
            run_steps(DIR_X, STEP_X, ENA_X, 0, CW, SLEEP_TIME, 1.5*CM)
            sleep(5)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CW, SLEEP_TIME, 1.6*CM)
            sleep(5)
            GPIO.output(YELLOW_LED, GPIO.LOW)
            STATE = START_STATE
        elif STATE == EMERGENCY:
            if GPIO.input(RED_BUTTON) == GPIO.HIGH:
                GPIO.output(RED_LED, GPIO.LOW)
                GPIO.output(GREEN_LED, GPIO.HIGH)
                STATE = START_STATE

except KeyboardInterrupt:
    GPIO.output(RED_LED, GPIO.LOW)
    GPIO.output(YELLOW_LED, GPIO.LOW)
    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.cleanup()
