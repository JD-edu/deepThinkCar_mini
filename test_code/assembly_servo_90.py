from adafruit_servokit import ServoKit
import time

while True:
  servo = ServoKit(channels=16)
  angle = 90
  servo.servo[0].angle = angle
