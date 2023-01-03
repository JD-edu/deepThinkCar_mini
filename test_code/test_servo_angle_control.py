import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print("Start servo motor test...")
for i in range(2):
    print("Servo angle 130")
    kit.servo[0].angle = 130
    time.sleep(1)
    print("Servo angle 90")
    kit.servo[0].angle = 90
    time.sleep(1)
    print("Servo angle 60")
    kit.servo[0].angle = 60
    time.sleep(1)
print("Servo motor test completed")
kit.servo[0].angle = 90
time.sleep(1)

