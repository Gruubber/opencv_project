from adafruit_motorkit import MotorKit
import time
kit = MotorKit()

kit.motor1.throttle = 0.0
kit.motor2.throttle = 0.5
kit.motor3.throttle = 0.0
kit.motor4.throttle = 0.0
time.sleep(1)
kit.motor1.throttle = 0
kit.motor2.throttle = 0
kit.motor3.throttle = 0
kit.motor4.throttle = 0
