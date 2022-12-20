## deepThinkCar-mini에 사용할 라즈베리파이 OS 이미지 만들기 

라즈베리파이 OS 이미지를 만드는 방법은 여러가지 있습니다. 이 중에서 많이 사용되는 두가지 방법을 사용해서 라즈베리파이 OS 이지미를 만들 수 있습니다.
첫번째 방법은 라즈베리파이 재단에서 권장하는 Raspberry Pi Imager를 사용하는 방업입니다. 두번째는 balenaEcher라는 프로그램을 사용하여 이미지를 만들 수 있습니다. 

### Raspberry Pi Imager를 사용하여 OS 이미지 만들기 
#### 개요 및 다운로드 하기 
Raspberry Pi Imager는 OS 이미지 다운로드와 SD카트 라이팅을 한번에 할 수 있는 라이팅 툴 입니다. 다운로드를 받으려면 다음 사이트에서 다운로드 받을 수 있습니다.   
[다운로드](https://www.raspberrypi.org/software/)
#### Raspberry Pi Image 사용법 
라즈베리파이 OS를 이미지를 만들려면 먼저 Raspberry Pi Imager를 실행합니다. 
![image](https://user-images.githubusercontent.com/76054530/125730638-d5382a8e-d0c4-4c94-a7b6-a428a8768aeb.png)   
그 다음에는 "CHOOS OS"를 클릭합니다. 클릭을 하면 여러가지 OS가 제시되는데 "Raspbery PI OS (Others)" -> "Raspberry Pi OS 64bit"를 선택합니다.   
![image](https://user-images.githubusercontent.com/96219601/206336444-c7b94ca4-0606-4941-9467-7a509446e25b.png)
![image](https://user-images.githubusercontent.com/96219601/206336183-175da2f7-8c41-4d28-b319-d2eeb17ff1c3.png)

그 다음에는 OS 이미지를 라이팅 할 SD카드를 선택합니다. 미리 PC에 16GB의 SD카드를 연결해 놓아야 합니다. SD카드가 연결되어 있으면 위 그림과 같이 SD카드가 용량과 함께 표시되는 것을 볼 수 있습니다.
![image](https://user-images.githubusercontent.com/76054530/125731640-0dde51e3-eb39-4b19-88a2-35ae9013cffa.png)   
SD카드 연결를 선택했으면 그 다음에는 "WRITE"를 클락합니다. 그러면 아래 그림과 같이 라이팅이 시작이 됩니다.    
SD카드 라이팅이 완료되면 SD카드를 PC에서 뽑아서 라즈베리파이의 SD카드 슬롯에 넣고 전원을 넣으면 부팅이 됩니다.   
초기에는 셋팅을 편하게 하기 위해서 모니터/키모드/마우스를 라즈베리파이에 연결을 해 놓고 라즈베리파이 셋업을 하는 것이 편리합니다.
![image](https://user-images.githubusercontent.com/76054530/125731053-6599c2d0-460b-4222-8932-82360e83afc9.png)   
간혹 아래 그림처럼 SD카드 이미지 라이팅이 실패하는 경우가 생깁니다. SD카드 리더기의 문제일 가능성이 있습니다. 이럴 경우에는 BalenaEcher를 사용하여 이미지를 라이팅 해야합니다.
![image](https://user-images.githubusercontent.com/76054530/125731337-65715557-c4b1-4fbc-a467-4746ba7d54cd.png)   
### balenaEtcher를 사용하여 OS 이미지 만들기 
#### 개요 및 다운로드 하기 
balenaEtcher는 라즈베리파이 OS를 별도로 다운 받아놓고 SD카드에 라이팅을 할 수 있습니다. 상황에 따라 라즈베리파이 OS 다운로드 시간이 많이 걸리는 경우가 종종 있는데 OS이미지를 계속 라이팅을 하려면 balenaEtcher가 더 편리합니다. beleanEtcher는 아래 링크에서 다운 받을 수 있습니다. 
[balenaEtcher](https://www.balena.io/etcher/)
#### balenaEtcher 사용법 
balenaEtcher는 미리 라즈베리파이 OS를 다운받아 놓고 SD카드 라이팅이 가능합니다. 그래서 먼저 아래 링크에서 "Raspbery PI OS (64bit)"를 다은로드 받습니다.    
경우에 따라서는 다운로드에 시간이 많이 걸릴 수 있습니다. [라즈베라파이 64bit](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit)
     
OS 이미지를 다운 받은 후에는 balenaEtcher를 실행합니다. 이 프로그램을 실행하면 다음과 같은 화면을 볼 수 있습니다.    
![image](https://user-images.githubusercontent.com/76054530/125732538-e59a94e1-6e6d-4618-b2ae-98cff665fded.png)          
여기서 "Flash from file"을 클릭합니다. 팝업 윈도에서 다운받은 라즈베리파이 OS이미지를 찾아서 선택합니다. 현재(2022/12/20) 다운로드된 이미지의 이름은 "2022-09-22-raspios-bullseye-arm64.img"입니다.       
![image](https://user-images.githubusercontent.com/76054530/125734129-b5f0a8d5-2092-4460-a97a-b2d68816f634.png)          
라이팅할 이미지를 선택하면 자동적으로 balenaEtcher의 "Select target" 버튼이 활성화 됩니다. 이 버튼을 클릭하면 연결되어 있는 SD카드의 리스트가 보입니다.      
![image](https://user-images.githubusercontent.com/76054530/125734389-83c5c384-c9db-4dc4-90f6-876f91d934d9.png)    
SD카드의 리스트 중에서 "Mass Storage Devie USB Device"를 선택합니다. "Show 2 hidden" 은 건드리지 않습니다.     
![image](https://user-images.githubusercontent.com/76054530/125734614-89dc25cb-c2af-415e-9210-65588d0c6a40.png)   
SD카드를 선택한 후 "Select"를 클릭하면 원래의 화며으로 돌아옵니다. 이 때 "Flash" 버튼이 활성화 된 것을 볼 수 있습니다.       
이 "Flash" 버튼을 클릭하면 SD카드에 OS 이미지를 라이팅 하기 시작합니다. OS 이미지 라이팅을 한 후에는 검사 작업이 진행 됩니다. 모두 합쳐서 20분 이상의 시간이 소요 됩니다.       
![image](https://user-images.githubusercontent.com/76054530/125734798-54b5e9fb-e750-461c-8d6b-586a4bb33406.png)    

### OS 이미지 완성이후 
라즈베리파이 OS이미지를 SD카드에 라이팅한 후에는 라즈베리파이 셋업을 진행합니다. 라즈베리파이 셋업은 아래 링크를 클릭해 주십시오.       
[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/setup)

### 링크
[라즈베리파이 OS 이미지 만들기](https://jd-edu.github.io/deepThinkCar_mini/os)      
[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/setup)      
[deepThinkCar-mini 조립](https://jd-edu.github.io/deepThinkCar_mini/assembly)    
[deepThinkCar-mini 라즈베리파이 VNC 환경 구축](https://jd-edu.github.io/deepThinkCar_mini/vnc)    
[deepThinkCar-mini 하드웨어 테스트](https://jd-edu.github.io/deepThinkCar_mini/hardware)     
[1단계 OpenCV 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/step_1)     
[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/step_2)     
[3단계 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/step_3)     
[4단계 딥러닝 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/step_4)  
