## deepThinkCar-mini용 라즈베리파이 보드 셋업 및 필요 소프트웨어 설치

### 라즈베리파이 보드 연결 
라즈베리파이 OS 이미지를 만든 후에는 라즈베리파이 보드를 부팅하고 보드를 셋업하는 작업을 해야 합니다. 아래 링크는 라즈베리파이 보드 셋업을 잘 설명하고 있습니다.   

[라즈베리파이 보드 셋업(영문)](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up)

라즈베리파이 보드를 셋업하기 위해서는 모니터/키보드/마우스를 라즈베리파이에 연결해서 사용하는 것이 좋습니다. 연결하는 방법은 아래 그림을 참고하 주십시오.       
라즈베리파이 OS 이미지가 있는 SD카드를 라즈베리파이 SD카드 슬롯에 삽입합니다. 그리고 전원 단자에 전원을 연결합니다. 라즈베리파이는 1A 전후의 많은 전류를 소모 합니다.    
따라서 PC의 USB 포트를 전원으로 사용하지 마십시오. 향후 설명할 deepThinkCar의 배터리를 사용하거나 스마트폰 충전용 USB 충전기를 사용하는 것이 좋습니다.    

![image](https://user-images.githubusercontent.com/76054530/125740222-dffcaeeb-1982-445d-b534-761ebd2c9a01.png)    
출처: 라즈베리파이 재단   

### 라즈베리파이 보드 일반 셋업 
라즈베리파이를 최초로 부팅했을 때는 여러가지 셋업 작업을 해야 합니다. 셋업해야 할 작업은 지역설정, WiFi, 모니터 해상도, 인터페이스 셋업이 있습니다. 
상세한 셋업은 다음 링크를 참고해 주십시오. 

[라즈베리파이 최초 부팅 셋업](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/4)   

다만 주의해야 할 것은 가능하면 지역 설정은 대한민국/서울로 하지만 "Use English Language"와 "Use US keyboard"를 체크해서 영어와 영문키보드를 사용하는 것으로 정합니다.    
개발 혹은 코딩교육용으로는 한글보다는 영어 및 영문 키보드로 설정하는 것이 좋습니다.    

![image](https://user-images.githubusercontent.com/76054530/125741576-5d470544-34ec-48c3-8fd2-c29dd48d039c.png)

### 라즈베리파이 인터페이스 셋업 
보드의 일반 셋업이 끝이나면 라즈베리파이 인터페이스를 셋업 합니다. 인터페이스를 셋업하려면 "Raspberry Pi Configuration"을 실행해야 합니다.    
"Raspberry Pi Configuration"은 다음 그림을 참고해서 실행하면 됩니다. 

![image](https://user-images.githubusercontent.com/96219601/208640912-867bba1f-2169-41c0-bfec-9279ee837c09.png)

인터페이스 셋업 화면이 실행이 되면 아래 그림과 같은 셋업 윈도가 뜨기 됩니다. 
![image](https://user-images.githubusercontent.com/96219601/208641239-33cb071f-9f8a-4c11-8b6b-dec72c1b254c.png)

이 인터페이스 셋업 윈도에서 "SSH", "VNC", "SPI", "I2C", "Serial Port"를 활성화 시킵니다.   
이후에는 라즈베리파이를 재부팅하면 인터페이스 셋업이 끝이 납니다.  

### 라즈베리파이 소프트웨어 업데이트 
본격적으로 deepThinkCar-mini에 필요한 라이브러리를 설치하기 전에 라즈베리파이의 OS를 업데이트 해야 합니다. OS 업데이트는 터미널 프로그램에서 다음과 같이 합니다. 

<pre><code>
$sudo apt update
$sudo apt full-upgrade
</code></pre>

### 파이썬3 설치 
deepThinkCar-mini는 파이썬3를 사용하여 코딩 합니다. 라즈베리파이 OS (64bit)에는 파이썬3와 파이썬 필수 툴인 pip3가 이미 설치되어 있습니다. 
터미널 프로그램을 실행해서 다음과 같이 확인하년 설치된 파이썬3와 pip3의 버전을 확인 할 수 있습니다. 
<pre><code>
pi@raspberrypi:~/deepThinkCar-mini/test_code $ python3 --version
Python 3.9.2
pi@raspberrypi:~/deepThinkCar-mini/test_code $ pip3 --version
pip 20.3.4 from /usr/lib/python3/dist-packages/pip (python 3.9)
</code></pre>

### OpenCV 설치
OpenCV는 deepThinkCar-mini의 카메라에서 출력되는 이미지를 프로세싱하는 컴퓨터 비젼 라이브러리 입니다. deepThinkCar-mini 자율주행 파이썬 코드는 OpenCV 라이브러리를 사용하여 차선인식을 수행합니다. deepThinkCar-mini는 라즈베리파이 OS(64비트)를 사용합니다. 라즈베리파이 OS (64비트)는 OpenCV와 텐서플로를 일반 윈도 PC와 동일한 방법으로 설치할 수 있습니다.    

<pre><code>
$pip3 install opencv-python
$pip3 install opencv-contrib-python
</code></pre>

![image](https://user-images.githubusercontent.com/96219601/208644496-1c78dd04-5e24-4b67-9bd8-ed1c354d6af7.png)

OpenCV가 제대로 설치되어야 하는지 체크 할 수 있습니다. 터미널 프로그램을 열어서 파이썬3 프롬프트를 실행하고 다음과 같이 체크해서 버전이 제대로 표시되면 설치가 성공한 것 입니다. 
``` python
pi@raspberrypi:~ $ python3
Python 3.9.2 (default, Feb 28 2021, 17:03:44) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.6.0'
```

### 텐서플로
텐서플로는 구글에서 제공하는 딥러닝 라이브러리 입니다. deepThinkCar-mini 자율주행 코드는 텐서플로 라이브러리를 사용하여 딥러닝을 실행합니다. 텐서플로 라이브러리를 pip3를 사용해서 설치 합니다. 
<pre><code>
$ sudo pip3 install tensorflow
</code></pre>

![image](https://user-images.githubusercontent.com/96219601/208645461-623283fb-4965-485c-907f-e0516b6c18fe.png)

텐서플로가  제대로 설치되어야 하는지 체크 할 수 있습니다. 터미널 프로그램을 열어서 파이썬3 프롬프트를 실행하고 다음과 같이 체크해서 버전이 제대로 표시되면 설치가 성공한 것 입니다.
```python

```
에전에는 딥러닝 라이브러리인 Keras를 설치해야 하는데, 이제는 Keras가 텐서플로에 통합이 되어, 별도로 설치할 필요가 없습니다.  
#### 가끔 pip3를 통해서 텐서플로는 설치되었는데 텐서플로가 import가 되지 않는 현상이 있습니다. 이럴 경우, SD카드의 OS를 삭제하고 처음부터 다시 셋업 작업ㅇ르 진행해 보시기 바랍니다.  

### 에이다프루트 서보 제어모듈(Adafruit=circuitpython-servokit)
deepThinkCar 앞바퀴를 제어하는 서보모터를 동작시키기 위해서 이 라이브러리가 필요합니다. 이 라이브러리는 다음과 같이 설치가 가능합니다. 

<pre><code>
$pip3 install adafruit-circuitpython-servokit
</code></pre>

이 라이브러리를 사용하는 방법은 아래 링크을 참고하면 됩니다.     
[에이다프루이트 서보킷 라이브러리 ](https://circuitpython.readthedocs.io/projects/servokit/en/latest/)

이 라이브러리가 제대로 설치가 되었는지 확인하려면 터미널 프로그램에서 다음과 같이 파이썬3 프롬프트로 확인할 수 있습니다. 
``` python
pi@raspberrypi:~ $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from adafruit_servokit import ServoKit
>>> 
```

### OpenCV 카메라 사용 셋업 
라즈베리파이 OS 64비트는 지금(2022년 12월 20일)은  pi 카메라 - OpenCV를 이용하여 비디오를 처리할 수 없습니다. 글서 legacy camera를 사용할 수 있도록 셋업을 해야 합니다. 이것을 셋업하기 위해서는 터미널을 열고 다음과 같이 입력을 합니다. 
<pre><code>
$ sudo raspi-config
</code></pre>

위 명령을 실행하면 아래와 같은 화면이 나옵니다. 여기서 'Interface Options'를 선택합니다.   
![image](https://user-images.githubusercontent.com/96219601/208649683-a861f1a5-6f3a-44ad-b179-4ba52c12c14e.png)

그러면 다음과 같이 화면이 나옵니다. 여기서 'Legacy camera'를 선택합니다.   
![image](https://user-images.githubusercontent.com/96219601/208650348-14d32e7b-b415-492c-a455-7346958a5dcf.png)

그 다음에는 'Legacy camera'를 enable 합니다.   
![image](https://user-images.githubusercontent.com/96219601/208650188-449ef42c-f6c7-439d-9ffc-617dfde64f47.png)

이렇게 'Legacy camera'를 enable하면 OpenCV를 통해서 pi 카메라를 제어할 수 있습니다.    

### 라즈베리파이 소프트웨어 셋업 이후 
라즈베리파이 소프트웨어 셋업이 끝난 후에는 deepThinkCar-mini의 하드웨어를 조립 단계로 넘어갑니다. deepThinkCar-mini 하드웨어 조립은 아래 링크를 클릭해 주십시오.   
[deepThinkCar 하드웨어 조립](https://jd-edu.github.io/deepThinkCar_mini/hardware)

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
