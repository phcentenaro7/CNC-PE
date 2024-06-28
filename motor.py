import RPi.GPIO as GPIO
from time import sleep
import sys
        
#Speed in steps per second
def run_steps(dir_pin, step_pin, ena_pin, sensor_pin, rotation, sleep_time, steps):
    for steps in range(steps):
        GPIO.output(dir_pin, rotation)
        if sensor_pin != 0 and GPIO.input(sensor_pin) == 0:
            GPIO.output(step_pin, GPIO.LOW)
            GPIO.output(ena_pin, GPIO.HIGH)
            return
        else:
            GPIO.output(ena_pin, GPIO.LOW)
            GPIO.output(step_pin, GPIO.HIGH)
        sleep(sleep_time)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(sleep_time)
        
#Clockwise/Counterclockwise rotation values
CW = 1 #Away from motor
CCW = 0 #Closer to motor

#GPIO pin setup
DIR_X = 8
DIR_X_VAL = CW
STEP_X = 10
ENA_X = 23
DIR_Y = 16
DIR_Y_VAL = CW
STEP_Y = 18
ENA_Y = 21
SENSOR_X_BEGIN = 22
SENSOR_Y_BEGIN = 19
START_BUTTON = 37
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR_X, GPIO.OUT)
GPIO.setup(STEP_X, GPIO.OUT)
GPIO.setup(ENA_X, GPIO.OUT)
GPIO.setup(DIR_Y, GPIO.OUT)
GPIO.setup(STEP_Y, GPIO.OUT)
GPIO.setup(ENA_Y, GPIO.OUT)
GPIO.setup(SENSOR_X_BEGIN, GPIO.IN)
GPIO.setup(SENSOR_Y_BEGIN, GPIO.IN)
GPIO.setup(START_BUTTON, GPIO.IN)
CM = 16000
SLEEP_TIME = 0.0000001

try:
    while True:
        if GPIO.input(START_BUTTON) == 1:
            run_steps(DIR_Y, STEP_Y, ENA_Y, SENSOR_Y_BEGIN, CCW, SLEEP_TIME, sys.maxsize)
            run_steps(DIR_X, STEP_X, ENA_X, SENSOR_X_BEGIN, CCW, SLEEP_TIME, sys.maxsize)
            sleep(3)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CW, SLEEP_TIME, 5*CM)
            run_steps(DIR_X, STEP_X, ENA_X, 0, CW, SLEEP_TIME, 9*CM)
            sleep(3)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CCW, SLEEP_TIME, 2*CM)
            sleep(3)
            run_steps(DIR_X, STEP_X, ENA_X, 0, CW, SLEEP_TIME, 2*CM)
            sleep(3)
            run_steps(DIR_Y, STEP_Y, ENA_Y, 0, CW, SLEEP_TIME, 2*CM)
            sleep(3)

except KeyboardInterrupt:
    None
    GPIO.cleanup()
