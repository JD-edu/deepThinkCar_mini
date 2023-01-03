import cv2
import numpy as np
import time
from jd_car_motor_l9110 import JdCarMotorL9110
from adafruit_servokit import ServoKit
import pygame
import os 

# pygame setup
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("deepThinkCar")

key="no key"
font = pygame.font.SysFont("arial",30)  
text1 = font.render("Remote Control deepThinkCar",True,(255,255,255)) 
text2 = font.render("s: start car",True,(255,255,255))  
text3 = font.render("SPACE: stop car",True,(255,255,255))
text4 = font.render("LEFT: left turn",True,(255,255,255))  
text5 = font.render("RIGHT: right turn",True,(255,255,255))  
text6 = font.render("d: erase recored image",True,(255,255,255)) 
text7 = font.render(key,True,(255,255,255))  

# DC motor and servo control object 
motor = JdCarMotorL9110()
servo = ServoKit(channels=16)

# Camera object and setup resolution
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

# Find ./data folder for labeling data
try:
    if not os.path.exists('./data'):
        os.makedirs('./data')
except OSError:
    print("failed to make ./data folder")


# Servo offset. You can get offset from calibration.py
servo_offset = 0
angle = 90
servo.servo[0].angle = angle + servo_offset

isDriving = False
run = True
index = 0
# real driving routine 
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        key = 'left'
        text7 = font.render(key,True,(255,255,255))  
        angle -= 5
        if angle < 40:
            angle = 40
        cv2.imwrite("%s_%03d_%03d.png" % ("./data/RC",index, angle), img_org)
        index += 1
    elif keys[pygame.K_RIGHT]:
        key = 'right'
        text7 = font.render(key,True,(255,255,255)) 
        angle += 5
        if angle > 150:
            angle = 150
        cv2.imwrite("%s_%03d_%03d.png" % ("./data/RC",index, angle), img_org)
        index += 1
    
    if keys[pygame.K_s]:
        key = 'start'
        text7 = font.render(key,True,(255,255,255)) 
        isDriving = True
        print("recording start")
    if keys[pygame.K_SPACE]:
        key = 'stop'
        text7 = font.render(key,True,(255,255,255)) 
        isDriving = False
        print("Recording stop")
    if keys[pygame.K_d]:
        key = 'erase'
        text7 = font.render(key,True,(255,255,255)) 
        try:
            os.system("rm ./data/*.png")
        except:
            print("file error")
        
        print("recording start")
       
    ret, img_org = cap.read()
    if ret:
        print(angle)
        cv2.imshow("deepThinkCar", img_org)
        if isDriving == True:
            motor.motor_move_forward(30)
        else:
            motor.motor_stop()
        servo.servo[0].angle = angle + servo_offset
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("cap error")
        
    screen.fill((0,0,0))
    screen.blit(text1, (100, 50))
    screen.blit(text2, (100, 100))
    screen.blit(text3, (100, 150))
    screen.blit(text4, (100, 200))
    screen.blit(text5, (100, 250))
    screen.blit(text6, (100, 300))
    screen.blit(text7, (100, 350))
   
    pygame.display.update()
 
        
pygame.quit()
motor.motor_stop()
cap.release()
cv2.destroyAllWindows()

