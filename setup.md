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

![image](https://user-images.githubusercontent.com/76054530/125742284-d46cca9e-bd0b-42b1-8ee3-0820f8d2a06f.png)

인터페이스 셋업 화면이 실행이 되면 아래 그림과 같은 셋업 윈도가 뜨기 됩니다. 

![image](https://user-images.githubusercontent.com/76054530/125742457-61f1c74a-6ec1-482d-8efd-61d9e45a9489.png)

이 인터페이스 셋업 윈도에서 "Camera", "SSH", "VNC", "SPI", "I2C", "Serial Port"를 "Enalbe"을 체크해서 활성화 시킵니다.   
이후에는 라즈베리파이를 재부팅하면 인터페이스 셋업이 끝이 납니다.  

### 라즈베리파이 소프트웨어 업데이트 
본격적으로 deepThinkCar에 필요한 라이브러리를 설치하기 전에 라즈베리파이의 OS를 업데이트 해야 합니다. OS 업데이트는 터미널 프로그램에서 다음과 같이 합니다. 

<pre><code>
$sudo apt update
$sudo apt full-upgrade
</code></pre>

### 파이썬3 설치 
deepThinkCar-mini는 파이썬3를 사용하여 코딩 합니다. 라즈베리파이 OS (32bit)에는 파이썬3와 파이썬 필수 툴인 pip3가 이미 설치되어 있습니다. 
터미널 프로그램을 실행해서 다음과 같이 확인하년 설치된 파이썬3와 pip3의 버전을 확인 할 수 있습니다. 
<pre><code>
pi@raspberrypi:~/deepThinkCar/test_code $ python3 --version
Python 3.7.3
pi@raspberrypi:~/deepThinkCar/test_code $ pip3 --version
pip 18.1 from /usr/lib/python3/dist-packages/pip (python 3.7)
</code></pre>

### OpenCV 설치
OpenCV는 deepThinkCar-mini의 카메라에서 출력되는 이미지를 프로세싱하는 컴퓨터 비젼 라이브러리 입니다. deepThinkCar-mini 자율주행 파이썬 코드는 OpenCV 라이브러리를 사용하여 차선인식을 수행합니다.    
OpenCV는 현재 4.x 버전이 최신 버전 입니다. 하지만 라즈베리파이에서는 OpenCV 4.x 버전을 설치하는 것이 쉽지 않습니다. 그래서 deepThinkCar-mini는 OpenCV 3.4.6.27 버전을 설치 합니다.
설치하는 순서는 다음과 같습니다. 먼저 OpenCV 3.4.6.27 버전에 필요한 라이브러리들을 설치합니다. 

<pre><code>
$ sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
$ sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
$ sudo apt-get install libatlas-base-dev
$ sudo apt-get install libjasper-dev
</code></pre>

필요한 라이브러리 설치가 끝이나면 그 다음에는 OpenCV 라이브러리를 설치 합니다. 설치할 때, 3.4.6.27 버전을 아래 명령처럼 명시해 줍니다.
<pre><code>
$sudo pip3 install opencv-python==3.4.6.27
$sudo pip3 install opencv-contrib-python==3.4.6.27
</code></pre>
   
종종 설치하고자 하는 버전의 라이브러리가 없을 경우 설치가능한 버전을 알려줍니다. 예를 들어 OpenCV 3.4.6.29 버전을 설치하려고 한다면 아래와 같이 설치가능한 버전을 추천해 줍니다.    
이럴 경우 설치가능한 버전을 한가지 골라서 설치하면 됩니다. 
<pre><code>
pi@raspberrypi:~/deepThinkCar/test_code $ sudo pip3 install opencv-python==3.4.6.29
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting opencv-python==3.4.6.29
  Could not find a version that satisfies the requirement opencv-python==3.4.6.29 (from versions: 3.4.2.16, 3.4.2.17, 3.4.3.18, 3.4.4.19, 3.4.6.27, 3.4.7.28, 3.4.10.37, 3.4.11.39, 3.4.11.41, 3.4.11.43, 3.4.11.45, 3.4.13.47, 3.4.15.55, 4.0.1.24, 4.1.0.25, 4.1.1.26, 4.3.0.38, 4.4.0.40, 4.4.0.42, 4.4.0.44, 4.4.0.46, 4.5.1.48, 4.5.3.56)
No matching distribution found for opencv-python==3.4.6.29
</code></pre>

OpenCV가 제대로 설치되어야 하는지 체크 할 수 있습니다. 터미널 프로그램을 열어서 파이썬3 프롬프트를 실행하고 다음과 같이 체크해서 버전이 제대로 표시되면 설치가 성공한 것 입니다. 
``` python
pi@raspberrypi:~/deepThinkCar/test_code $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'3.4.6'
```
   
opencv-python 라이브러리와 opencv-contrib-python 라이브러리는 동일한 버전으로 설치가 되어야 합니다. 
이 레포지터리의 자율주행 코드는 OpenCV 3.4.6.27을 사용하여 테스트 되었습니다.

### 텐서플로
텐서플로는 구글에서 제공하는 딥러닝 라이브러리 입니다. deepThinkCar-mini 자율주행 코드는 텐서플로 라이브러리를 사용하여 딥러닝을 실행합니다. 텐서플로 라이브러리를 pip3를 사용해서 설치하려 하면 1.x 버전의 라이브러리가 설치 됩니다. 그래서 pip3는 텐서플로 설치에 사용할 수 없고 다음과 같은 방법으로 설치를 해야 합니다.    
먼저 텐서플로 2.3.0 ARM CPU용으로 빌드된 라이브러리를 다운 받습니다.    
[텐서플로 2.3.0 for ARM CPU](https://github.com/lhelontra/tensorflow-on-arm/releases/tag/v2.3.0)   
위 레포지터리는 Leonardo lontra라는 브라질 개발자가 텐서플로 소스코드를 라즈베리파이에 맞게 빌드하여 깃허브에 올린 것 입니다. 텐서플로 소스를 직접 빌드하는 것은 많이 어렵기 때문에 이 버전을 다운 받아 사용합니다. 다운을 받은 후에는 다음 순서로 설치를 진행합니다. 
<pre><code>
$ sudo -H pip3 install tensorflow-2.3.0-cp37-none-linux_armv7l.whl
</code></pre>

만약에 이전에 설치한 텐서플로가 있다면 먼저 이 명령을 사용하여 텐서플로를 제거합니다. 
<pre><code>
$ sudo pip3 uninstall tensorflow
</code></pre>
텐서플로가  제대로 설치되어야 하는지 체크 할 수 있습니다. 터미널 프로그램을 열어서 파이썬3 프롬프트를 실행하고 다음과 같이 체크해서 버전이 제대로 표시되면 설치가 성공한 것 입니다.
```python
pi@raspberrypi:~/deepThinkCar $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import tensorflow
>>> tensorflow.__version__
'2.3.0'
>>> 
```
이 레포지터리의 자율주행 코드는 텐서플로 2.3.0을 사용하여 테스트 되었습니다. 

### 케라스
케라스는 텐서플로와 같이 딥러닝에 사용되는 뉴럴네트워크 API 라이브러리 입니다. deepThinkCar-mini 자율주행 파이썬 코드는 텐서플로와 케라스를 사용하여 뉴럴네트워크 구성, 딥런닝 트레이닝, 추론 등을 수행합니다. 케라스를 설치하여면 다음과 같이 합니다.
<pre><code>
$pip3 install keras==2.4.3
</code></pre>

케라스는 pip3를 사용하여 설치할 수 있습니다. 다만 케라스를 제대로 파이썬에서 import 하려면 먼저 텐서플로를 설치해야 합니다.     
케라스가 제대로 설치되어야 하는지 체크 할 수 있습니다. 터미널 프로그램을 열어서 파이썬3 프롬프트를 실행하고 다음과 같이 체크해서 버전이 제대로 표시되면 설치가 성공한 것 입니다.
```python
pi@raspberrypi:~/deepThinkCar $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import keras
>>> 
```

이 레포지터리의 자율주행 코드는 케라스 2.4.3을 사용하여 테스트 되었습니다.

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


### 라즈베리파이 GPIO
deepThinkCar-mini는 DC모터 제어를 위해서 라즈베리파이 GPIO 라이브러리를 설치해야 합니다. GPIO 라이브러리는 터미널에서 다음과 같은 방법으로 설치가 가능합니다. 
<pre><code>
sudo apt-get install python-rpi.gpio
</code></pre>

이 라이브러리가 제대로 설치가 되었는지 확인하려면 터미널 프로그램에서 다음과 같이 파이썬3 프롬프트로 확인할 수 있습니다. 
```python
pi@raspberrypi:~ $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import RPi.GPIO as IO
>>> 
```

### 라즈베리파이 소프트웨어 셋업 이후 
라즈베리파이 소프트웨어 셋업이 끝난 후에는 deepThinkCar-mini의 하드웨어를 조립 단계로 넘어갑니다. deepThinkCar-mini 하드웨어 조립은 아래 링크를 클릭해 주십시오.   
[deepThinkCar 하드웨어 조립](https://jd-edu.github.io/deepThinkCar_mini/hardware)

### 링크
[라즈베리파이 OS 이미지 만들기](https://jd-edu.github.io/deepThinkCar_mini/os)      
[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/setup)      
[deepThinkCar 조립](https://jd-edu.github.io/deepThinkCar_mini/assembly)    
[deepThinkCar 라즈베리파이 VNC 환경 구축](https://jd-edu.github.io/deepThinkCar_mini/vnc)    
[deepThinkCar 하드웨어 테스트](https://jd-edu.github.io/deepThinkCar_mini/hardware)     
[1단계 OpenCV 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/step_1)     
[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/step_2)     
[3단계 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/step_3)     
[4단계 딥러닝 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/step_4)  
