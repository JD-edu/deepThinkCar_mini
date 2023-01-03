import RPi.GPIO as IO
import time



class JdCarMotorL9110():

    def __init__(self):
        self.motor1_r_pwmPin = 19
        self.motor1_r_dirPin = 13
        self.motor2_l_pwmPin = 12
        self.motor2_l_dirPin = 16
        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(self.motor1_r_pwmPin, IO.OUT)
        IO.setup(self.motor1_r_dirPin, IO.OUT)
        IO.setup(self.motor2_l_pwmPin, IO.OUT)
        IO.setup(self.motor2_l_dirPin, IO.OUT)
        self.motor1_pwm = IO.PWM(self.motor1_r_pwmPin, 100)
        self.motor1_pwm.start(0)
        self.motor2_pwm = IO.PWM(self.motor2_l_pwmPin, 100)
        self.motor2_pwm.start(0)

    def motor_move_forward(self, speed):
        if speed > 100:
            speed = 100
        self.motor1_pwm.ChangeDutyCycle(int(speed))
        self.motor2_pwm.ChangeDutyCycle(int(speed))
        
    def motor_stop(self):
        self.motor1_pwm.ChangeDutyCycle(0)
        self.motor2_pwm.ChangeDutyCycle(0)
       

if __name__ == '__main__':

    jd_motor = JdCarMotorL9110()
    while True:
        jd_motor.motor_move_forward(30)
        time.sleep(2)
        jd_motor.motor_stop()
        time.sleep(2)
        
    




