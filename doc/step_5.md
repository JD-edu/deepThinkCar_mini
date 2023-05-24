## deepThinkCar-mini 자율주행 5단계: 오브젝트 디텍팅 

### 5단계에서는 ...
4단계까지 딥러닝 기반의 차선인식을 주로 다루었습니다. 하지만 실제 자율주행자동차는 차선 뿐 아니라, 보행자, 주변 차량, 교통 표지판 등 여러기지 브젝트를 분별할 수 있어야 합니다. 이번 장에서는 deep-mini를 통한 오브젝트 디텍션 방법을 학습 합니다. 라즈베리파이의 성능 한계로 때문에 차선인식 주행과 오브젝트 디텍션을 같이 실행할 경우, 속도가 매우 느립니다. 더 강력한 컴퓨터를 사용한다면 정상속도로 차선인식 주행과 오브젝트 디텍션을 실습할 수 있을 것 입니다.

### 필요한 모둘 임포트 하기 
5단계 오브젝트 디텍팅 자율주행을 위해서는 다음 파이썬 모듈을 임포트 합니다. cv2 모듈은 OpenCV를 사용하기 위한 모듈입니다. JdDeepLaneDetect모듈은 딥러닝 추론파일을 이용해서 차선을 인식하고, 차선의 각도를 파악해서 알려주는 차선인식모듈 입니다.  obj모듈은 mobileNet-SSD V3를 이용해서 오브젝트 디텍팅을 해주는 모듈입니다. 

'''python
import cv2
#from adafruit_servokit import ServoKit
from jd_deep_lane_detect import JdDeepLaneDetect
#from jd_car_motor_l9110 import JdCarMotorL9110

import time

import jd_opencv_dnn_objectdetect_v3 as obj
'''
