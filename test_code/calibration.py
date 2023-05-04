# To calibrate front wheel, run this code.
# deepThinkCar will drive 5 second.
# Check moving curve and adjust offset.
from adafruit_servokit import ServoKit
import RPi.GPIO as IO
import time
# offset value 
offset = 1
# Servo 
servo = ServoKit(channels=16)
angle = 90
servo.servo[0].angle = angle+offset
# motor 1 and 2 setting 
pwmPin1 = 19
dirPin1 = 13

pwmPin2 = 12
dirPin2 = 16

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(pwmPin1, IO.OUT)
IO.setup(dirPin1, IO.OUT)
IO.setup(pwmPin2, IO.OUT)
IO.setup(dirPin2, IO.OUT)
p2 = IO.PWM(pwmPin2, 100)
p2.start(0)
p1 = IO.PWM(pwmPin1, 100)
p1.start(0)
print("Start moving for calibration...")
p1.ChangeDutyCycle(35)
p2.ChangeDutyCycle(35)
time.sleep(5)
print("Calibration completed.")
IO.output(dirPin1, False) 
IO.output(pwmPin1, False)
IO.output(dirPin2, False) 
IO.output(pwmPin2, False)
IO.cleanup() 




