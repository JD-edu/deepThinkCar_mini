
# deepThinkCar-mini: 멘토와 함께 만드는 딥러닝 자율주행자동차 키트  

###  알아보기 
deepThinkCar-mini는 라즈베리파이 기반의 자율주행자동차 키트 입니다. 기존 deepThibCar를 좀 더 개량하고 기능을 추가한 버전입니다. OpenCV와 딥러닝을 사용하여 차선인식 자율주행 배울 수 있고, 추가적인 하드웨어장치를 이용하면 보행자나 교통신호를 식별하는 오브젝트 디텍션을 학습 할 수 있습니다. 또한 ADAS 기능을 테스트 할 수 있습니다.  
#### OpenCV를 이용한 차선인식
deepThinkCar-mini는 오픈소스 컴퓨터 비젼 라이브러리인 OpenCV를 사용해서 차선을 인식하는 기능을 구현해 볼 수 있습니다. 아주 단순한 방법으로 차선을 인식하는 방법과 ADAS에 실제로 사용되는 방법까지 구현 할 수 있습니다. 
#### 딥러닝 차선인식 주행(Behavior Cloning)
deepThinkCar-mini는 최근에 주목받고 있는 딥러닝 기술을 이용하여 차선인식 주행을 구현해 볼 수 있습니다. OpenCV로 차선인식 주행을 몇 번 실행 하면서 얻은 데이터를 트레이닝 하여 추론모델을 생성하고, 이 추론모델을 이용하여 딥러닝 차선주행을 구현합니다.
#### ADAS 기능 
deepThinkCar-mini는 초음파센서와 카메라를 이용해서 현재 현장에서 사용되고 있는 ADAS를 실제와 같이 구현 및 학습할 수 있습니다. 

### deepThinkCar-mini 키트 준비하기 

#### 라즈베리파이 OS 이미지 만들기 
deepThinkCar-mini는 라즈베리파이를 기반으로 동작을 합니다. 따라서 먼저 라즈베리파이 OS 이미지를 만들어야 합니다. 라즈베리파이 OS이미지를 만드는 방법은 아래 링크를 참고해 주십시오.  
    
[라즈베리파이 OS 이미지 만들기](https://jd-edu.github.io/deepThinkCar_mini/doc/os)   
    
deepThinkCar-mini는 라즈베리파이 3B, 3B+, 4에서 테스트 되었습니다. 라즈베리파이 이미지를 만든 다음에는 라즈베리파이 셋업을 합니다.
   
#### 라즈베리파이 소프트웨어 셋업 
라즈베리파이의 OS 이미지를 만든 후에는 deepThinkCar-mini를 활용할 수 있도록 필요한 소프트웨어를 설치하고 셋업해야 합니다. 설치하고 셋업할 소프트웨어는 다음과 같습니다. 
1. OpenCV 라이브러리 
2. 텐서플로 딥러닝 라이브러리 
3. 에이다프루트 서보모터 라이브러리 

라즈베리파이 소프트웨어 셋업 및 설치하는 방법은 아래 링크를 참고해 주십시오. 

[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/doc/setup)

deepThinkCar-mini는 라즈베리파이 3B, 3B+, 4에서 테스트 되었습니다. 라즈베리파이 셋업 이후에는 deepThinkCar-mini 하드웨어를 조립합니다. 

### deepThinkCar-mini 조립
라즈베리파이 부분의 셋업이 모두 완료되면, deepThinkCar-mini를 조립하고 테스트를 실행합니다. 

#### deepThinkCar조립
deepThinkCar-mini는 조립이 되지 않은 부품 상태로 제공이 됩니다. deepThinkCar-mini를 시용하기 위해서는 차체를 조립해야 합니다. 조립순서는 아래 링크를 참고해 주십시오. 

[deepThinkCar-mini 조립](https://jd-edu.github.io/deepThinkCar_mini/doc/assembly)   

#### VNC 개발환경 셋업
deepThinkCar-mini를 프로그래밍해서 자율주행을 하려면 라즈베리파이 VNC 코딩 환경을 만들어야 합니다. deepThinkCar-mini는 움직이는 자동차이기 때문에 모니터/키보드/마우스를 이용해서 프로그래밍 하는 것이 불가능 합니다. 따라서 VNC를 이용해서 프로그래밍 하는 환경을 만들어야 합니다.    
VNC 개발환경을 구축하는 방법은 아래 링크를참고해 주십시오.    

[deepThinkCar-mini 라즈베리파이 VNC 환경 구축](https://jd-edu.github.io/deepThinkCar_mini/doc/vnc)

deepThinkCar-mini의 라즈베리파이 VNC 개발환경은 라즈베리파이 3B, 3B+, 4에서 테스트 되었습니다. VNC 개발환경 구축에 이어서 deepThinkCar-mini를 테스트 합니다. 

#### deepThinkCar-mini 하드웨어 테스트
deepThinkCar-mini 조립이 끝이나면 하드웨어를 테스트 합니다. 테스트 할 하드웨어는 다음과 같습니다. 
1. PI 카메라 
2. 뒷바퀴 구동용 DC모터 
3. 앞바퀴 조향용 서보모터 
4. 앞바퀴 조향 오프셋 조종
5. 전원 스위칭 (배터리, 파워뱅크)

deepThinkCar-mini 하드웨어를 테스트 하는 방법은 아래 링크를 참고해 주십시오. 

[deepThinkCar-mini 하드웨어 테스트](https://jd-edu.github.io/deepThinkCar_mini/doc/hardware)

### 자율주행하기 
#### 1단계: OpenCV 기반 차선인식 주행
1단계에서는 OpenCV를 이용해서 차선인식 주행을 실행합니다. 차선인식 주행을 실행해서 딥러닝 트레이닝에 사용할 데이터셋을 같이 얻습니다. 
OpenCV 기반 차선인식 주행을 하는 파이썬 코드에 대한 설명은 다음 링크를 참고해 주십시오. 

[1단계 OpenCV 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_1)

#### 2단계: 차선인식 데이터 라벨링 
2단계에서는 1단계에서 얻은 차선인식주행 데이터셋을 라벨링을 합니다. 데이터셋이 라벨링이 되면 딥러닝 트레이닝을 할 수 있습니다. 
데이터셋 라벨링을 하는 파이썬 코드에 대한 설명은 다음 링크를 참고해 주십시오. 

[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/doc/step_2) 

#### 3단계: 딥러닝 트레이닝 
3단계에서는 OpenCV를 통해 얻은 데이터셋을 딥러닝 신경망으로 트레이닝을 합니다. 실제 트레이닝은 라즈베리파이에서 실행하지 않고 PC에서 실행하게 됩니다.   
트레이닝을 수행하면 추론파일을 생성해 줍니다. 딥러닝 트레이닝을 실행하는 방법에 대한 설명은 다음 링크를 참고해 주십시오. 

[3단계 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/doc/step_3) 

#### 4단계: 딥러닝 기반 차선인식 주행 
4단계에서는 딥러닝 트레이닝을 통해 얻은 추론 파일을 이용해서 딥러닝 기반의 차선인식 주행을 수행 합니다. 
데이터셋의 정확도, 데이터셋의 양에 따라 딥러닝 차선인식 주행의 정확도를 비교할 수 있습니다. 
딥러닝 차선인식 주행에 대한 설명은 다음 링크를 참고해 주십시오.

[4단계 딥러닝 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_4)  

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


