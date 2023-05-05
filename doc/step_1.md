
## DeeptCar 자율주행 1단계: OpenCV 차선인식 주행  

### 1단계에서는...
1단계에서는 OpenCV를 이용한 차선인식 주행을 실행할 수 있습니다. 카메라 영상을 이용해서 차선을 인식하는 기능은 이미 ADAS(Advanced Driver Assistance System)라는 이름으로 사용화 되어 있습니다. Deep-mini는 OpenCV 라이브러리를 이용해서 ADAS와 유사하면서 기초적인 차선인식 주행을 실행할 수 있습니다. 1단계에서는 OpenCV를 통한 차선인식 주행을 할 뿐 아니라 차선을 따라 주행하는 영상 데이터를 얻을 수 있습니다. 2단계에서는 이 영상 데이터를 가공해서 딥러닝 트레이닝에 필요한 데이터셋을 얻는 라벨링 작업을 하게 됩니다. 

### 필요한 모듈 import 하기 
1단계 차선인식 주행을 위해서 다음 파이썬 모듈들을 임포트 해야 합니다. cv2 모듈은 OpenCV 모듈 입니다. ServoKit 모듈은 앞바퀴 조향용 서보모터를 제어하기 위한 모듈 입니다.     
JdOpencvLaneDetect 모듈은 실제적으로 OpenCV를 이용해서 차선을 인식하고, 차선의 각도를 파악해서 알려주는 차선인식모듈 입니다.     
JdCarMotorL9110 모듈은 뒷바퀴 기어드 DC모터를 제어하는 모듈 입니다. 

```python
import cv2
import os 
from adafruit_servokit import ServoKit
from jd_opencv_lane_detect import JdOpencvLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110
import time 
```

### 필요한 모듈 객체 만들기 
차선인식 주행을 시작하기 전에 필요한 모듈의 객체를 생성하고 초기화를 합니다. 
1. 앞바퀴 서보 모터 제어를 위한 SerovKit 모듈의 객체를 만듭니다. 
2. 차선인식에 사용할 OpenCV기반 차선인식모듈의 객체를 만듭니다. 
3. 뒷바퀴 구동용 DC모터를 위한 L9110 DC 모터 드라이버 모듈의 객체를 만듭니다. 

```python
# Servo object 
servo = ServoKit(channels=16)
# OpenCV line detector object
cv_detector = JdOpencvLaneDetect()
# DC motor object 
motor = JdCarMotorL9110()
```

### 카메라 셋팅하기 
DeeptCar 전방에 설치된 Pi카메라를 셋팅합니다. 해상도를 320x240으로 셋팅 합니다. 그 이상의 해상도는 WiFi와 VNC를 통한 원격 제어에 문제가 생기게 됩니다. 

```python
# Camera object: reading image from camera 
cap = cv2.VideoCapture(0)
# Setting camera resolution as 320x240
cap.set(3, 320)
cap.set(4, 240)
```

### 영상 레코딩 준비
Pi카메라 영상을 레코딩 하기 위해서 셋팅을 합니다. 레코딩 된 영상은 /data 폴더에 car_video.avi 라는 이름으로 저장 됩니다. 
먼저 영상을 저장할 /data 폴터를 준비합니다. 폴더가 없을 경우 폴더를 만듭니다. 

```python
# Find ./data folder for labeling data
try:
    if not os.path.exists('./data'):
        os.makedirs('./data')
except OSError:
    print("failed to make ./data folder")
```

/data 폴더를 만든 후에는 OpenCV를 이용해서 비디오를 레코딩하기 위한 객체들을 만듭니다. 두가지 객체가 필요합니다. 첫번째는 "cv2.VideoWriter_fourcc()"함수를 사용하여 비디오 압축 표준을 정합니다. 라즈베리파이의 경우에는 "XVID" 표준을 사용합니다. 두번째는 OpenCV 비디오 레코딩 객체를 만드는 것입니다. "cv2.VideoWriter()" 함수를 이용해서 비디오 레코딩 객체를 만듭니다. 이 비디오 레코딩 객체를 통해서 자율주행차의 주행영상을 녹화하게 됩니다. 

```python    
# Create video codec object. We use 'XVID' format for Raspberry pi.
fourcc =  cv2.VideoWriter_fourcc(*'XVID')
#fourcc =  cv2.VideoWriter_fourcc('M','J','P','G')
# Video write object
video_orig = cv2.VideoWriter('./data/car_video.avi', fourcc, 20.0, (320, 240))
#video_orig = cv2.VideoWriter('./data/car_video_lane.avi', fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))
```

### 출발전 차선에 맞게 앞바퀴 스티어링 앵글 조정 
deep-mini는 출발 전에 앞바퀴 스티어링 앵글을 현재 차선의 굽어짐에 맞게 조정해야할 필요가 있습니다. OpenCV로 현재 차선의 굽어짐을 파악하는 데는 몇초의 시간이 필요합니다.    
출발을 바로 하면 OpenCV로 차선의 굽어짐을 파악하기도 전에 차선을 벗어날 가능성이 있습니다. 그래서 출발 전 몇초 동안은 뒷바퀴를 구동하지 않고 제자리에서 OpenCV를 먼저 구동합니다.    

```python
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
```
		
###  메인 루프 
앞바퀴 스티어링 앵글 조정이 끝나면 deep-mini를 출발시키고 차선인식 주행을 실행합니다. 아래 코드는 차선인식 주행을 하는 메인 루프 코드 입니다.  

```python
# Start motor 
motor.motor_move_forward(10)
while True:
    ret, img_org = cap.read()
    if ret:
        cv2.imshow('lane', img_org)
        video_orig.write(img_org)
        lanes, img_lane = cv_detector.get_lane(img_org)

        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
        if img_angle is None:
            print("angle image out!!")
            pass
        else:
            print(angle)
        servo.servo[0].angle = angle + servo_offset
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("cap error")
```

카메라를 통해서 이미지를 읽어오는 코드는 아래와 같습니다. 
```python
ret, img_org = cap.read()
```
이 이미지를 /data 폴더에 래코딩 하는 코드는 아래와 같습니다. 
```python
video_orig.write(img_org)
```
이 이미지를 사용해서 cv_detector.get_lane() 함수를 통해서 차선 이미지를 뽑아 냅니다. 
```python
anes, img_lane = cv_detector.get_lane(img_org)
```
이 차선 이미지를 이용해서 차선의 각도, 즉 앞바퀴 스티어링 각도를 결정합니다. 
```python
angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
```
### 앞바퀴 스티어링 각도를 이용한 서보 제어 
앞바퀴 스티어링 각도가 결정 되면 이 각도로 서보를 제어합니다. 서보 각도를 제어할 때, 주행 정밀도를 높이기 위해 필요하다면 오프셋 값을 조정할 수 있습니다. Deep-mini에 최적인 오프셋값은 하드웨어 테스트 단계에서 칼리브레이션 항목에서 얻을 수 있습니다. 
카메라의 이미지에 차선이 검출되지 않으면 그 이지미는 무시합니다. 
```python
if img_angle is None:
    print("angle image out!!")
        pass
else:
    print(angle)
        servo.servo[0].angle = angle + servo_offset
```

### 주행의 마무리 
딥러닝을 위해 필요한 영상 데이터는, 트랙의 길이에 따라 다르겠지만, 대략 30초 전후 입니다. 30초 정도 이미지가 래코딩 되었다면 'q'키를 입력해서 주행을 종료할 수 있습니다.    
종료를 처리하는 코드는 아래와 같습니다. 
```python
motor.motor_stop()
cap.release()
video_orig.release()
cv2.destroyAllWindows() 
```

### 그 다음 단계 
1단계로 OpenCV를 통해 차선인식 주행영상을 확보 했다면, 그 다음에는 딥러닝 트레이닝을 위한 데이터셋 라벨링을 해야 합니다. 
다음 링크를 통해서 다음 단계로 갈 수 있습니다.    
[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/doc/step_2)   

### 링크
[라즈베리파이 OS 이미지 만들기](https://jd-edu.github.io/deepThinkCar_mini/doc/os)      
[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/doc/setup)       
[deepThinkCar-mini 조립](https://jd-edu.github.io/deepThinkCar_mini/doc/assembly)   
[deepThinkCar-mini 라즈베리파이 VNC 환경 구축](https://jd-edu.github.io/deepThinkCar_mini/doc/vnc)     
[deepThinkCar-mini 하드웨어 테스트](https://jd-edu.github.io/deepThinkCar_mini/doc/hardware)     
[1단계 OpenCV 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_1)        
[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/doc/step_2)      
[3단계 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/doc/step_3)     
[4단계 딥러닝 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_4)    





