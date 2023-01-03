## 라즈베리파이 프로그래밍을 위한 VNC 개발환경 셋업 
 
## 라즈베리파이를 모니터/키보드/마우스 없이 프로그래밍하기 
라즈베리파이로 파이썬 프로그래밍을 하기 위해서는 모니터/키보드/마우스를 라즈베리파이에 연결해서 프로그래밍 하는 것이 제일 편리합니다. 하지만 deepThinkCar는 모니터/키보드/마우스를 연결한 상태에서 파이썬 프로그래밍을 통해서 동작시키는 것이 불가능합니다. 그래서 deepThinkCar는 VNC 프로그램을 사용해서 원격으로 라즈베리파이 파이썬 프로그래밍을 합니다.    
VNC를 이용해서 라즈베리파이 파이썬 프로그래밍하는 방식은 아래 그림과 같이 설명 될 수 있습니다. 

![image](https://user-images.githubusercontent.com/76054530/157554069-abc0ad84-5bb0-4f84-9677-1b0fb4f5aade.png)

### PC에 VNC 설치하기
먼저 프로그래밍에 사용할 PC에 VNC 프로그램을 설치합니다. VNC는 다음 사이트에서 다은로드 받을 수 있습니다. 

[Real VNV Viewer 다운로드](https://www.realvnc.com/en/connect/download/viewer/)

VNC 프로그램은 서버프로그램과 뷰어프로그램으로 구성되는데, 서버프로그램은 라즈베피라이에서 동작합니다. 우리는 PC이 Viewer 프로그램을 설치하면 됩니다.   

### 라즈베피라이 와이파이 셋업 
VNC 프로그램을 PC에 설치했으면 그 다음에는 라즈베리파이의 와이파이를 세팅합니다. 아래 그림처럼 라즈베리파이의 와이파이를 셋팅하면 됩니다. 
PC와 비슷합니다. **주의 할 것은 PC와 라즈베리파이가 같은 AP에 연결이 되어야 합니다.** 

![image](https://user-images.githubusercontent.com/76054530/157556236-f6f5d64d-0ab3-4ac7-b838-ae65d200f04b.png)

### 라즈베리파이 IP 어드레스 얻기 
VNC 뷰어 프로그램은 라즈베리파이와 연결하기 위해서 IP주소가 필요합니다. 라즈베리파이의 IP주소를 얻기 위해서 라즈베리파이 터미널을 엽니다. 그리고 다음과 같이 명령을 내리면 라즈베리파이의 IP주소를 얻을 수 있습니다. IP주소는 인터넷에 연결되는 PC혹은 라즈베리파이의 주소 입니다. 
<pre><code>
pi@raspberrypi:~/deeptcar/data $ ifconfig
</code></pre>
![화면 캡처 2022-03-10 082947](https://user-images.githubusercontent.com/76054530/157556743-5fd7c3fa-02ec-4d19-bbe1-317843681e6a.png)

### VNC로 라즈베리파이 연결하기 
라즈베리파이의 IP주소가 파악이 되었으면 PC에서 VNC 뷰어를 실행합니다. 그리고 아래 그림과 같이 라즈베리파이의 PI주소를 입력하고 엔터를칩니다.

![화면 캡처 2022-03-10 083214](https://user-images.githubusercontent.com/76054530/157557016-63984cc4-9571-4174-8309-a17f7680ffb9.png)

그러면 VNC가 다음과 같이 아이디와 패스워드를 묻습니다. 

![image](https://user-images.githubusercontent.com/76054530/157557179-0ccba343-aaeb-454b-9271-ad214d1b9c3f.png)

**여기서 아이디는 pi 패스워드는 raspberry 입니다.** 

아이디와 패스워드를 입력하면 아래와 같이 라즈베리파이 화면이 PC에 디스플레이 됩니다. 

![화면 캡처 2022-03-10 083636](https://user-images.githubusercontent.com/76054530/157557729-37b3bdf7-f16a-435f-a909-0065c4aee7b3.png)


주의할 것은 꼭 라즈베리파이에 모니터를 연결한 상태에서 VNC연결을 하십시오.
그리고 VNC 연결이 끝이나면 라즈베리파이에 연결된 모니터를 제거해도 됩니다. 그렇지 않으면 아래와 같은 화면이 뜨고 제대로 동작되지 않습니다.   
이것은 해상도 문제로 발생을 합니다. 이런 문제를 만나면 라즈베리파이에 모니터를 연결하고 재부팅합니다. 그리고 VNC로 연결을 하면 됩니다. 

![image](https://user-images.githubusercontent.com/76054530/157557620-6a3be992-df59-454d-b1f5-a8eba2aadbef.png)

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
