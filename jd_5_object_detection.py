import cv2
import socket
from adafruit_servokit import ServoKit
from jd_deep_lane_detect import JdDeepLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110
import time
import imutils
import base64

'''
Raspberry pi IP address. Put your Raspberry pi IP address here.
Port number for remote control data
Port number for video streaming  
'''
PI_IP = '172.31.98.78'
TCP_PORT = 9998
VIDEO_PORT = 9999
OFFSET = 0

BUFF_SIZE = 65536

deep_detector = JdDeepLaneDetect("./models/lane_navigation_final.h5")
motor = JdCarMotorL9110()
servo = ServoKit(channels=16)

cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

servo_offset = 5
servo.servo[0].angle = 90 + servo_offset

# Setting UDP socket for video streaming (Rpi -> PC)
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
socket_address = (PI_IP, VIDEO_PORT)
server_socket.bind(socket_address)
print('Listening at:',socket_address)

print('Waiting UDP connection... ')
msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
print('GOT connection from ',client_addr)

for i in range(30):
    ret, img_org = cap.read()
    if ret:
        angle_deep, img_angle = deep_detector.follow_lane(img_org)
        if img_angle is None:
            print("can't find lane...")
        else:
            print(angle_deep)
            servo.servo[0].angle = angle_deep + servo_offset			
            cv2.imshow("img_angle", img_angle)
            cv2.waitKey(1)
    else:
        print("cap error")

motor.motor_move_forward(30)


while cap.isOpened():
    ret, img_org = cap.read()
   
    frame = imutils.resize(img_org,width=400)
    # Encoding as JPEG 
    encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
    message = base64.b64encode(buffer)
    try:
        # Sending to client 
        server_socket.sendto(message,client_addr)
    except:
        print("UDP communication error")
    angle_deep, img_angle = deep_detector.follow_lane(img_org)
    if img_angle is None:
        print("can't find lane...")
    else:
        print(angle_deep)
        servo.servo[0].angle = angle_deep + servo_offset
        cv2.imshow("img_angle", img_angle)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

server_socket.close()
cap.release()
cv2.destroyAllWindows()



        

