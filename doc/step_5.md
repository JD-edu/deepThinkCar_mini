## deepThinkCar-mini 자율주행 5단계: 오브젝트 디텍팅 

### 5단계에서는 ...
4단계까지 딥러닝 기반의 차선인식을 주로 다루었습니다. 하지만 실제 자율주행자동차는 차선 뿐 아니라, 보행자, 주변 차량, 교통 표지판 등 여러기지 브젝트를 분별할 수 있어야 합니다. 이번 장에서는 deep-mini를 통한 오브젝트 디텍션 방법을 학습 합니다. 라즈베리파이의 성능 한계로 때문에 차선인식 주행과 오브젝트 디텍션을 같이 실행할 경우, 속도가 매우 느립니다. 더 강력한 컴퓨터를 사용한다면 정상속도로 차선인식 주행과 오브젝트 디텍션을 실습할 수 있을 것 입니다.

### 필요한 모둘 임포트 하기 
5단계 오브젝트 디텍팅 자율주행을 위해서는 다음 파이썬 모듈을 임포트 합니다. cv2 모듈은 OpenCV를 사용하기 위한 모듈입니다. JdDeepLaneDetect모듈은 딥러닝 추론파일을 이용해서 차선을 인식하고, 차선의 각도를 파악해서 알려주는 차선인식모듈 입니다.  obj모듈은 mobileNet-SSD V3를 이용해서 오브젝트 디텍팅을 해주는 모듈입니다. 

```python
import cv2
from adafruit_servokit import ServoKit
from jd_deep_lane_detect import JdDeepLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110
import time
import jd_opencv_dnn_objectdetect_v3 as obj
```

### 필요한 모듈 객체 만들기 
오브젝트 디텍팅 주행을 시작하기 전에 필요한 모듈의 객채를 생성하고 초기화 합니다. 오브젝트 디텍팅 주행은 기본적으로 딥러닝 차선인식을 같이 동작시킵니다. 
1.  차선인식에 사용할 딥러닝 차선인식모듈의 객체를 만듭니다. 이 때 model 폴더의 추론파일을 로드 합니다. 
2.  뒷바퀴 구동용 DC모터를 위한 L9110 DC 모터 드라이버 모듈의 객체를 만듭니다.
3.  앞바퀴 서보 모터 제어를 위한 SerovKit 모듈의 객체를 만듭니다. 

```python
# Deep learning detector object
deep_detector = JdDeepLaneDetect("./models/lane_navigation_final.h5")
# DC motor object
motor = JdCarMotorL9110()
# Servo object 
servo = ServoKit(channels=16)
```
라즈베리파이의 경우 성능부족으로 딥러닝 차선인식과 오브젝트 디텍팅이 동시에 구현이 어려우면 어느 쪽 한가지 기능을 막고 주행 시험을 해야합니다. 가장 간단한 방법은 딥러닝 차선인식 코드와 모터 스타트 코드를 주석으로 막으면 됩니다. 

### 카메라 셋팅하기 
deepThinkCar 전방에 설치된 Pi카메라를 셋팅합니다. 해상도를 OpenCV 주행때와 같게 320x240으로 셋팅 합니다. 그 이상의 해상도는 WiFi와 VNC를 통한 원격 제어에 문제가 생기게 됩니다.

```python
# Camera object: reading image from camera 
cap = cv2.VideoCapture(0)
# Setting camera resolution as 320x240
cap.set(3, 320)
cap.set(4, 240)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```
### 출발전 차선에 맞게 앞바퀴 스티어링 앵글 조정 
deepThinkCar는 출발 전에 앞바퀴 스티어링 앵글을 현재 차선의 굽어짐에 맞게 조정해야할 필요가 있습니다. 딥러닝으로 현재 차선의 굽어짐을 파악하는 데는 약간의 시간이 필요합니다.    
출발을 바로 하면 딥러닝으로 차선의 굽어짐을 파악하기도 전에 차선을 벗어날 가능성이 있습니다. 그래서 출발 전 몇초 동안은 뒷바퀴를 구동하지 않고 제자리에서 딥러닝으로 먼저 차선인식을 구동합니다. 

```python
# Prepare real starting 
for i in range(30):
    ret, img_org = cap.read()
    if ret:
        angle_deep, img_angle = deep_detector.follow_lane(img_org)
        if img_angle is None:
            print("can't find lane...")
        else:
            print(angle_deep)
            if angle_deep > 130:
                angle_deep = 130
            elif angle_deep < 50:
                angle_deep = 50

            #servo.servo[0].angle = angle_deep + servo_offset	
            		
            cv2.imshow("img_angle", img_angle)
            cv2.waitKey(1)
    else:
        print("cap error")
```
### 메인 루프  
앞바퀴 스티어링 앵글 조정이 끝나면 deep-mini를 출발시키고, 딥러닝 차선인식과 오브젝트 디텍팅을 같이 실행합니다. 성능의 문제가 있으면 딥러닝 차선인식 기능을 담당하는 코드를 주석으로 막습니다. 

```python
# real driving routine
while cap.isOpened():
    #isStop, isImg, stopImage = objectDetectThread.getStopSign()
    ret,  img = cap.read()
 
    isStop, img = obj.isStopSignDetected(img)
    
    cv2.imshow('object detection', img)


    if  isStop == False:
        ret,  img_org = cap.read()

        # Find lane angle
        if ret :
            angle_deep, img_angle = deep_detector.follow_lane(img_org)
            if img_angle is None:
                print("can't find lane...")
            else:
                print(angle_deep)
                if angle_deep > 130:
                    angle_deep = 130
                elif angle_deep < 50:
                    angle_deep = 50
    
                #servo.servo[0].angle = angle_deep + servo_offset
                #motor.motor_move_forward(25)
                cv2.imshow("img_angle", img_angle)
    else:
        pass
        #motor.motor_stop()
            
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
```

카메라를 통해서 이지미를 읽어오는 코드는 다음과 같습니다. 
```python
ret, img_org = cap.read()
```
이 이미지를 입력값으로 deep_detector.follow_lane() 함수를 통해서 차선 각도를 추출합니다. 코드는 다음과 같습니다. 
```python
angle_deep, img_angle = deep_detector.follow_lane(img_org)
```

### 오브젝트 디텍팅  
mobileNet SSD v3로 오브젝트 디텍팅하는 코드는 다음과 같습니다. "jd_opencv_dnn_objectdetect_v3.py"에서 디텍팅할 오브젝트를 정할 수 있는데 현재는 "사람", "자동차", "정지교통신호"를 감지합니다. 그리고 특히 "정지교통신호"를 감지하면 "isStop" 변수를 사용하여 deep-mini를 멈출 수 있습니다. 

```python
    isStop, isImg, stopImage = objectDetectThread.getStopSign()
    ret,  img = cap.read()
 
    isStop, img = obj.isStopSignDetected(img)
    
    cv2.imshow('object detection', img)
   
```

