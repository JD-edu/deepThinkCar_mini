
## deepThinkCar 자율주행 2단계: 딥러닝용 데이터 라벨링 

### 2단계에서는...
1단계에서 OpenCV로 차선인식 주행을 잘 수행했다면 /data 폴더에 "car_video.avi"라는 이름의 동영상이 생깁니다. 이 동영상은 1단계에서 수행한 차선인식 주행영상이 래코딩 되어 있습니다.    
<pre><code>
pi@raspberrypi:~/deeptcar/data $ ls
car_video.avi
</code></pre>

2단계에서는 이 "car_video.avi"를 라벨링해서 딥러닝용 데이터셋을 생성합니다. 

### 필요한 모듈 import 하기 
2단계 딥러닝용 데이터 라벨링을 위해서 다음 파이썬 모듈들을 임포트 해야 합니다. cv2 모듈은 OpenCV 모듈 입니다. CobitOpencvLaneDetect 모듈은 실제적으로 OpenCV를 이용해서 차선을 인식하고, 차선의 각도를 파악해서 알려주는 모듈 입니다. 이것 외에 필요한 모듈을 import 합니다. 
```python
import cv2
from cobit_opencv_lane_detect import CobitOpencvLaneDetect
import os 
```
### 필요한 모듈 객체 만들기 
딥러닝 데이터 라벨링을 시작하기 전에 필요한 모듈의 객체를 생성하고 초기화를 합니다. 
영상 속에 나오는 차선인식에 사용할 OpenCV 기반의 차선인식모듈의 객체를 만듭니다.
```python
cv_detector = CobitOpencvLaneDetect()
```
### 동영상 재생을 위한 코드 
data 폴더의 "car_video.avi" 동영상을 OpenCV 방식으로 재생하기 위한 코드를 실행합니다. 
```python
video_file = "data/car_video.avi"
cap = cv2.VideoCapture(video_file)
```
### 기존 라벨링된 데이터셋 삭제 
기존에 라벨링 된 데이터셋이 남아 있을 수 있습니다. 이 데이털르 삭제하는 코드를 실행합니다. 라즈베리파이 OS 명령인 "rm" 명령을 사용해서 data 폴더에 PNG 파일드을 삭제 합니다. 
```python
os.system("rm ./data/*.png")
```
### 데이터셋 라벨링 
딥러닝용 데이터셋 라벨링은 다음과 같은 방법으로 진행합니다. 
1. "car_video.avi"의 동영상의 프레임 이미지를 한장씩 가져 옵니다. 이 단계를 실행하는 코드는 다음과 같습니다.
```python
ret, img_org = cap.read()
```
2. 이 프레임 이미지를 "cv_detector"를 통해서 프로세싱해서 차선의 각도를 얻습니다. 이 단계를 실행하는 코드는 다음과 같습니다. 
```python 
lanes, img_lane = cv_detector.get_lane(img_org)
angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
```
3. 차선의 각도와 프레임 이미지를 이용해서 데이터를 라벨링 합니다. 라벨링 방식은 프레임 이지미를 PNG로 저장할 때, 프레임 이미지를 파일로 저장할 때  파일이름을 다음과 같이 정합니다.   
      
##### car_video.avi + 프레임 인덱스 번호 + 차선인식 각도
   
4. "car_video.avi" 동영상이 모두 끝날 때까지 동영상의 모든 프레임을 이렇게 처리하여 별도의 PNG 파일로 저장합니다. 
   
딥러닝 트레이닝을 실행할 때, 이 PNG 이미지와 이 이미지에 기록된 차선각도 두가지 요로를 가지고 트레이닝을 진행합니다. 이 모든 것을 수행하는 코드는 다음과 같습니다. 
```python
while True:
    ret, img_org = cap.read()
    if ret:
        lanes, img_lane = cv_detector.get_lane(img_org)
        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
        if img_angle is None:
	    pass
	else:
            cv2.imwrite("%s_%03d_%03d.png" % (video_file, index, angle), img_org)
            index += 1	
        if cv2.waitKey(1) & 0xFF == ord('q'):
	    break
    else:
        print("cap error")
	break
```

### 라벨링의 마무리 및 다음단계 
영상에서 모든 프레임을 뽑아서 라벨링 처리를 하면 코드는 자동으로 종료가 됩니다. 라벨링을 종료하는 코드는 다음과 같습니다.    
```python
cap.release()
cv2.destroyAllWindows()
```
2단계 다음은 딥러닝 트레이닝을 실행하여 추론파일을 생성하는 단계입니다.    
다음 링크를 통해서 다음 단계로 갈 수 있습니다.    
[3단계 딥러닝을 위한 데이터 트레이닝](https://cobit-git.github.io/deepThinkCar_doc/step_3)   

### 링크
[라즈베리파이 OS 이미지 만들기](https://cobit-git.github.io/deepThinkCar_doc/os)      
[라즈베리파이 소프트웨어 설치 및 셋업](https://cobit-git.github.io/deepThinkCar_doc/setup)      
[deepThinkCar 조립](https://cobit-git.github.io/deepThinkCar_doc/assembly)    
[deepThinkCar 라즈베리파이 VNC 환경 구축](https://cobit-git.github.io/deepThinkCar_doc/vnc)    
[deepThinkCar 하드웨어 테스트](https://cobit-git.github.io/deepThinkCar_doc/hardware)     
[1단계 OpenCV 차선인식 주행](https://cobit-git.github.io/deepThinkCar_doc/step_1)     
[2단계 차선인식 데이터 라벨링](https://cobit-git.github.io/deepThinkCar_doc/step_2)     
[3단계 딥러닝 트레이닝](https://cobit-git.github.io/deepThinkCar_doc/step_3)     
[4단계 딥러닝 차선인식 주행](https://cobit-git.github.io/deepThinkCar_doc/step_4)  






