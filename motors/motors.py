import RPi.GPIO as GPIO
from time import sleep

#Speed in steps per second
def run_steps(dir_pin, step_pin, rotation, speed, steps):
    GPIO.output(dir_pin, rotation)
    for step in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(1/(2*speed))
        GPIO.output(step_pin, GPIO.LOW)
        sleep(1/(2*speed))
        

#Clockwise/Counterclockwise rotation values
CW = 1
CCW = 0

#GPIO pin setup
DIR_X = 8
STEP_X = 10
DIR_Y = 16
STEP_Y = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR_X, GPIO.OUT)
GPIO.setup(STEP_X, GPIO.OUT)
GPIO.setup(DIR_Y, GPIO.OUT)
GPIO.setup(STEP_Y, GPIO.OUT)