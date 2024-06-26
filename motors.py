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

STEP_LENGTH = 0.1

motor_x = 0
motor_y = 0
speed = 100

try:
    with open("route", "r") as file:
        line = file.readline()
        while line != "":
            target_x, target_y = line.split(",")
            target_x, target_y = float(target_x), float(target_y)
            rotation_x = CW if target_x > motor_x else CCW
            rotation_y = CW if target_y > motor_y else CCW
            run_steps(DIR_X, STEP_X, rotation_x, speed, (target_x - motor_x) / STEP_LENGTH)
            run_steps(DIR_Y, STEP_Y, rotation_y, speed, (target_y - motor_y) / STEP_LENGTH)
            motor_x = target_x
            motor_y = target_y

except KeyboardInterrupt:
    None
    GPIO.cleanup()