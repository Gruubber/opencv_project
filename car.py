import time
import board
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

def left_speed(speed):#set the speed of the motors on the left side
    kit.motor1.throttle = speed
    kit.motor4.throttle = speed

def right_speed(speed):#set the speed of the motors on the right side
    kit.motor2.throttle = speed
    kit.motor3.throttle = speed

def steer(speed,direction):
    #direction is -1 to +1, -1 for left and 1 for right
    left_side = speed + (direction / 2)
    right_side = speed - (direction / 2)

    #ensure the speed of motors is always between 0 and 1 for smooth turning
    left_side = min(1.0,max(0.0,left_side)) 
    right_side = min(1.0,max(0.0,right_side))

    left_speed(left_side)
    right_speed(right_side)

def forward(speed):
    left_speed(speed)
    right_speed(speed)

def backward(speed):
    left_speed(-1*speed)
    right_speed(-1*speed)

def stop():
    left_speed(0)
    right_speed(0)

forward(0.4)
time.sleep(0.5)
stop()
