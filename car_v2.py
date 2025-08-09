import time
import board
from adafruit_motorkit import MotorKit
import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

kp = 0.002
kd = 0.0

kp_t = 0.03
kd_t = 0.0

last_direction_error = 0.0
last_radius_error = 0.0
last_time = time.time()

kit = MotorKit(i2c=board.I2C())

def map_val(inp,in_min,in_max,out_min,out_max):
    return (((inp - in_min)/(in_max - in_min))*(out_max - out_min)) + out_min

def algorithm():
    tolerence = 5
    x = y = radius = None
    des_distance =  25 #set a minimum distance between the ball and the car(car will move forward and backward to keep this distance)
    base_speed = 0.3
    while True:
        data_bytes, addr = sock.recvfrom(1024)
        data = json.loads(data_bytes.decode())
        global last_time, last_direction_error, last_radius_error
        x = data.get("x")
        y = data.get("y")
        radius = data.get("radius")
        throttle = 0

        if x is None or radius is None:
            #stop the car if ball is not detected or the car is within the desired distance from the ball and at the centre
            stop()
            #change last states to prevent derivative spike
            last_direction_error = 0
            last_radius_error = 0
            last_time = time.time()
            continue

        curr_time = time.time()
        change_time = curr_time - last_time
        #prevent division by zero with change time
        if change_time == 0:
            change_time = 1e-6
        radius_error = des_distance - radius
        direction_error = x #since the desired x is at the origin 0 we will just write x

        if abs(radius_error) < tolerence and abs(x) < tolerence:
            stop()
        else:
            #now calculate throttle and direction so that car is always at the right distance and centre to the ball
            #set throttle accroding to the distance from the ball, if ball is furthur away the throttle will be high and 
            #as it approaches the ball it will slow down, so it should be a factor of radius_error
            change_radius_error = (radius_error - last_radius_error)/change_time
            change_direction = (direction_error - last_direction_error)/change_time

            #PD controller for throttle
            throttle = (radius_error * kp_t) + (change_radius_error * kd_t) 
            #clamp throttle between -base_speed to base_speed, for proper backward and forward operation
            throttle = max(-base_speed,min(base_speed,throttle))

            #PD controller for the direction 
            new_direction = (kp * direction_error) + (kd * change_direction)

            steer(throttle,new_direction) 

        last_time = curr_time
        last_direction_error = direction_error
        last_radius_error = radius_error

def left_speed(speed):#set the speed of the motors on the left side
    kit.motor1.throttle = speed
    kit.motor4.throttle = speed

def right_speed(speed):#set the speed of the motors on the right side
    kit.motor2.throttle = speed
    kit.motor3.throttle = speed

def steer(speed,direction):
    
    left_side = speed + direction
    right_side = speed - direction

    #ensure the speed of motors is always between -1 and 1 for smooth turning
    left_side = max(-1.0,min(1.0,left_side))
    right_side = max(-1.0,min(1.0,right_side))

    left_speed(left_side)
    right_speed(right_side)

def stop():
    left_speed(0)
    right_speed(0)

algorithm()

