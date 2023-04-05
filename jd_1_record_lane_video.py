'''
1. importing necessary modules
'''
import cv2
import os 
from adafruit_servokit import ServoKit
from jd_opencv_lane_detect import JdOpencvLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110

'''
2. Creating object from classes
  1) Servo handling object from ServoKit class 
  2) OpenCV lane detecting object from JdOpencvLaneDetect class 
  3) DC motor handling object form JdCarMotorL9110 class 
'''
# Servo object 
servo = ServoKit(channels=16)
# OpenCV line detector object
cv_detector = JdOpencvLaneDetect()
# DC motor object 
motor = JdCarMotorL9110()

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
4. Creating data folder, if not exist
Video file that come from OpenCV driving is saved here. 
'''
# Find ./data folder for labeling data
try:
    if not os.path.exists('./data'):
        os.makedirs('./data')
except OSError:
    print("failed to make ./data folder")
    
'''
5. Creating video recording object
In this first step, we record deepThinkCar driving as AVI video file.
To do this we have to use cv2.VideoWrite_forcc() and cv2.Video_writer()
For more info, refer OpenCV tutorial.
'''
# Create video codec object. We use 'XVID' format for Raspberry pi.
fourcc =  cv2.VideoWriter_fourcc(*'XVID')
#fourcc =  cv2.VideoWriter_fourcc('M','J','P','G')
# Video write object
video_orig = cv2.VideoWriter('./data/car_video.avi', fourcc, 20.0, (320, 240))
#video_orig = cv2.VideoWriter('./data/car_video_lane.avi', fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))

'''
6. Preparing deepThinkCar starting.
Before start driving, we need to adjust servo offset(wheel calibraton) 
and wheel control while motor stop.
It will prevents mis-driving of deepThinkCar. 
'''
# Servo offset. You can get offset from calibration.py
servo_offset = 1
servo.servo[0].angle = 90 + servo_offset

# Prepare real starting 
for i in range(30):
    ret, img_org = cap.read()
    if ret:
        lanes, img_lane = cv_detector.get_lane(img_org)
        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
        if img_angle is None:
            print("can't find lane...")
            pass
        else:
            print(angle)
            servo.servo[0].angle = angle + servo_offset			
    else:
        print("camera error")
'''
7. Starting motor before real driving 
'''
# Start motor 
motor.motor_move_forward(10)

'''
8. Perform real driving
In this part, we perform real OpenCV lane detecting driving.
When you press 'q' key, it stp deepThinkCar.
While on driving, driving is recorded. 
'''
# real driving routine 
while True:
    ret, img_org = cap.read()
    if ret:
        # camera image writing 
        video_orig.write(img_org)
        # Find lane angle
        lanes, img_lane = cv_detector.get_lane(img_org)
        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
        if img_angle is None:
            print("can't find lane...")
            pass
        else:
            cv2.imshow('lane', img_angle)
            print(angle)
            servo.servo[0].angle = angle + servo_offset
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("cap error")
'''
9. Finishing the driving
Releasing occupied resources
'''
motor.motor_stop()
cap.release()
video_orig.release()
cv2.destroyAllWindows()


