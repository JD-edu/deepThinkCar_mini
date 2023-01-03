import RPi.GPIO as IO
import time
# motor 1 GPIO pin assignment  
pwmPin1 = 19
dirPin1 = 13
# motor 2 GPIO pin assignment
pwmPin2 = 12
dirPin2 = 16
# PWM setting 
IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(pwmPin1, IO.OUT)
IO.setup(dirPin1, IO.OUT)
IO.setup(pwmPin2, IO.OUT)
IO.setup(dirPin2, IO.OUT)
# PWM1  (motor 1 start)
p1 = IO.PWM(pwmPin1, 100)
p1.start(0)
# PWM2 (motor 2 start) 
p2 = IO.PWM(pwmPin2, 100)
p2.start(0)

print("DC motor test start...")
for a in range(2):
    print("DC motor power 40%")
    p1.ChangeDutyCycle(40)
    p2.ChangeDutyCycle(40)
    time.sleep(2)
    print("DC motor power 60%")
    p1.ChangeDutyCycle(60)
    p2.ChangeDutyCycle(60)
    time.sleep(2)
    print("DC motor power 80%")
    p1.ChangeDutyCycle(80)
    p2.ChangeDutyCycle(80)
    time.sleep(2)
    print("DC motor power 100%")
    p2.ChangeDutyCycle(100)
    p2.ChangeDutyCycle(100)
    time.sleep(2)
print("DC motor test completed")
IO.output(dirPin1, False) 
IO.output(pwmPin1, False)
IO.output(dirPin2, False) 
IO.output(pwmPin2, False)
IO.cleanup() 
