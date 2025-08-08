import time
import board
from adafruit_motorkit import MotorKit
import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

kit = MotorKit(i2c=board.I2C())

def algorithm():
    tolerence = 5
    x = y = radius = None
    des_distance =  25 #set a minimum distance between the ball and the car(car will move forward and backward to keep this distance)
    #set the desired coordinates so that the ball always stays at the origin
    des_coordX = 0 
    des_coordY = 0
    while True:
        data_bytes, addr = sock.recvfrom(1024)
        data = json.loads(data_bytes.decode())
        #x_prev = x
        #y_prev = y
        #radius_prev = radius
        x = data.get("x")
        y = data.get("y")
        radius = data.get("radius")

        #print(f"Ball at ({x},{y}), Radius: {radius}")
        if(radius is None or abs(radius-des_distance) <= tolerence):
            #if the ball is not detected or the ball is at the desired distance, stop the car
            stop()
        elif(radius > des_distance):
            #if new radius is bigger than the previous radius, the ball is closer so move back
            backward(0.35)
            
        elif(radius < des_distance):
            forward(0.35)


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

#forward(0.5)
#backward(0.5)
#steer(0.3,1)
#time.sleep(0.5)
algorithm()
#stop()
