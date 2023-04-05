'''
1. importing necessary modules
'''
import cv2
from adafruit_servokit import ServoKit
from jd_deep_lane_detect import JdDeepLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110
import time

'''
2. Creating object from classes
  1) Servo handling object from ServoKit class 
  2) Deep learning lane detecting object from JdDeepLaneDetect class 
  3) DC motor handling object form JdCarMotorL9110 class 
'''
# Deep learning detector object
deep_detector = JdDeepLaneDetect("./models/lane_navigation_final.h5")
# DC motor object
motor = JdCarMotorL9110()
# Servo object 
servo = ServoKit(channels=16)

'''
3. Creating camera object and setting resolution of camera image
cv2.VideoCapture() function create camera object.  
'''
# Camera object: reading image from camera 
cap = cv2.VideoCapture(0)
# Setting camera resolution as 320x240
cap.set(3, 320)
cap.set(4, 240)

'''
4. Preparing deepThinkCar starting.
Before start driving, we need to adjust servo offset(wheel calibraton) 
and wheel control while motor stop.
It will prevents mis-driving of deepThinkCar. 
'''
# Servo offset. You can get offset from calibration.py
servo_offset = 5
servo.servo[0].angle = 90 + servo_offset

# Prepare real starting 
for i in range(30):
    ret, img_org = cap.read()
    if ret:
        angle_deep, img_angle = deep_detector.follow_lane(img_org)
        if img_angle is None:
            print("can't find lane...")
        else:
            print(angle_deep)
            if angle_deep > 40 and angle_deep < 140:
                servo.servo[0].angle = angle_deep + servo_offset	
            		
            cv2.imshow("img_angle", img_angle)
            cv2.waitKey(1)
    else:
        print("cap error")

'''
5. Starting motor before real driving 
'''
# Start motor 
motor.motor_move_forward(10)

'''
6. Perform real driving
In this part, we perform real OpenCV lane detecting driving.
When you press 'q' key, it stp deepThinkCar.
While on driving, driving is recorded. 
'''
# real driving routine
while cap.isOpened():
    ret, img_org = cap.read()
    # Find lane angle
    angle_deep, img_angle = deep_detector.follow_lane(img_org)
    if img_angle is None:
        print("can't find lane...")
    else:
        print(angle_deep)
        if angle_deep > 30 and angle_deep < 160:
            servo.servo[0].angle = angle_deep + servo_offset
        cv2.imshow("img_angle", img_angle)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
'''
7. Finishing the driving
Releasing occupied resources
'''   
motor.motor_stop()
cap.release()
cv2.destroyAllWindows()



        

