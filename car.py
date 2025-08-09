import time
import board
from adafruit_motorkit import MotorKit
import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

kp = 0.5
kd = 0.08

last_direction = 0.0
last_time = time.time()

kit = MotorKit(i2c=board.I2C())

def map_val(inp,in_min,in_max,out_min,out_max):
    return (((inp - in_min)/(in_max - in_min))*(out_max - out_min)) + out_min
'''
def algorithm():
    tolerence = 5
    x = y = radius = None
    des_distance =  25 #set a minimum distance between the ball and the car(car will move forward and backward to keep this distance)
    #set the desired coordinates so that the ball always stays at the origin
    des_coordX = 0 
    des_coordY = 0
    base_speed = 0.35
    while True:
        data_bytes, addr = sock.recvfrom(1024)
        data = json.loads(data_bytes.decode())
        #x_prev = x
        #y_prev = y
        #radius_prev = radius
        x = data.get("x")
        y = data.get("y")
        radius = data.get("radius")

        throttle = 0
        direction = 0

        #print(f"Ball at ({x},{y}), Radius: {radius}")


        if(radius is not None):
           radius_error = radius-des_distance
            #if the ball is detected and the ball is not at the desired distance
           if(abs(radius_error) > tolerance):
                if radius_error < 0: #move forward
                    throttle = base_speed
                else: #move backward
                    throttle = -1 * base_speed
            
        
        
        if(radius > des_distance):
            #if new radius is bigger than the desired distance, the ball is closer so move back
            throttle = -1*base_speed
            #if(x is not None and abs(abs(x) - des_coordX) > tolerence ):
                #write steering logic using the x-coordinates of the ball
               # direction = map_val(x,-300,300,-1,1)
                #steer(0.25,direction)

        if(x is not None and abs(abs(x) - des_coordX) > tolerence ):
            #write steering logic using the x-coordinates of the ball
            direction = map_val(x,-300,300,-1,1)
#            print(direction)
            #steer(0.25,direction)
        else:
            stop()
            
        elif(radius < des_distance):
            forward(0.35)
            #time.sleep(0.2)
            '''

'''


def left_speed(speed):#set the speed of the motors on the left side
    kit.motor1.throttle = speed
    kit.motor4.throttle = speed

def right_speed(speed):#set the speed of the motors on the right side
    kit.motor2.throttle = speed
    kit.motor3.throttle = speed
def algorithm():
    tolerence = 5
    x = y = radius = None
    des_distance =  25 #set a minimum distance between the ball and the car(car will move forward and backward to keep this distance)
    #set the desired coordinates so that the ball always stays at the origin
    des_coordX = 0
    des_coordY = 0
    base_speed = 0.25
    while True:
        data_bytes, addr = sock.recvfrom(1024)
        data = json.loads(data_bytes.decode())
        #x_prev = x
        #y_prev = y
        #radius_prev = radius
        x = data.get("x")
        y = data.get("y")
        radius = data.get("radius")

        if x is None or radius is None or abs(radius-des_distance) < tolerence:
            #stop the car if ball is not detected or the car is within the desired distance from the ball
            stop()
        else:
            #now calculate throttle and direction so that car is always at the right distance and centre to the ball
            if abs(des_coordX) > tolerence:
                direction = map(x,-300,300,-1,1)
            else:
                direction = 0 #drive straight
            steer(base_speed,direction) 

def steer(speed,direction):
    #direction is -1 to +1, -1 for left and 1 for right
    global last_time, last_direction
    curr_time = time.time()

    #change_direction variable tells us how fast is direction changing
    change_direction = (direction - last_direction)/(curr_time - last_time)

    #PD controller takes into account the error over time for smoother steering
    new_direction = (kp*direction) + (kd*change_direction)
    
    last_direction = direction
    last_time = curr_time

    left_side = speed + (new_direction / 2)
    right_side = speed - (new_direction / 2)

    #print(left_side," ", right_side)

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

#forward(0.5)
#backward(0.5)
#steer(0.3,1)
#time.sleep(0.5)
algorithm()
#stop()
