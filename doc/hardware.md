
## deepThinkCar 하드웨어 테스트
deepThinkCar 하드웨어 조립이 끝이 나면, deepThinkCar의 하드웨어 상태를 테스트 합니다. 테스트 해야 할 하드웨어는 다음과 같습니다. 

1. 뒷바퀴 구동용 DC 기어드 모터 2쌍 
2. 앞바퀴 조향용 서보모터 
3. Pi카메라 

각각의 하드웨어를 테스트 하기위해 준비된 파이썬 코드를 실행해서 테스트를 합니다.  

### 뒷바퀴 구동용 DC기어드 모터 테스트 
뒷바퀴 구동용 DC기어드 모터 1쌍을 테스트하기 위해 "test_l9110_dc_motor.py" 코드를 사용합니다. 테스트를 위해서는 다음과 같이 코드를 실행을 합니다.   
이 코드는 test_code 폴더에서 실행합니다. 
<pre><code>
$python3 test_l9110_dc_motor.py
</code></pre>
![image](https://user-images.githubusercontent.com/76054530/127595231-5bfaeabf-d835-4dd6-acfd-c98bdf4a9774.png)

이 코드를 실행했을 때, DC모터가 20% -> 40% -> 60% -> 80% -> 100% 속도의 순서로 바퀴가 회전을 하면 정상입니다. 

### 앞바퀴 조향용 서보모터 
앞바퀴 조향용 서보모터를 테스트하기 위해 "test_servo_angle_control.py" 코드를 사용합니다. 테스트를 위해서는 다음과 같이 코드를 실행을 합니다.    
이 코드는 test_code 폴더에서 실행합니다. 
<pre><code>
$python3 test_servo_angle_control.py
</code></pre>
![image](https://user-images.githubusercontent.com/76054530/127595570-dc9493eb-3201-4b46-b730-e75b603b925b.png)

이 코드를 실행했을 때, 서보모터가 150도 -> 90도 -> 30도 이렇게 반복 동작합니다. 

### Pi 카메라 
Pi 카메라를 테스트하기 위해 "test_opencv_video.py" 코드를 사용합니다. 테스트를 위해서는 다음과 같이 코드를 실행을 합니다.    
이 코드는 test_code  폴더에서 실행합니다.    
<pre><code>
$python3 test_opencv_video.py
</code></pre>
![image](https://user-images.githubusercontent.com/76054530/127595646-7c19f192-9d07-44e1-8b32-131989db6b3f.png)

이 코드를 실행했을 때, 카메라 윈도 창이 열리고 카메라 영상이 디스플레이 되면 정상입니다. 테스트를 종료하려면 카메라 영상이 디스플레이 되는 윈도에서 'q'키를 입력합니다.     
![image](https://user-images.githubusercontent.com/76054530/127595713-3f3bca11-f36a-405d-a12a-bb0930180849.png)

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

