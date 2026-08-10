
# deepThinkCar-mini: 멘토와 함께 만드는 딥러닝 자율주행자동차 키트 

### 라즈베리파이 5에서는 테스트되지 않았습니다. 

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

#### 5단계: 객체 인식과 차선 추종 결합

5단계에서는 사람·자동차·트럭·정지 표지판의 정지 정책을 차선 추종과
결합합니다. 실제 구동 전에는 녹화 영상과 `--drive` 없는 카메라
검증을 먼저 실행합니다.

[5단계 딥러닝 오브젝트 디텍팅 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_5)

#### 현재 환경에서 다시 실행한 기록
2026년 8월 7일에 2~5단계를 현재 Python/Keras/OpenCV 환경에서 직접 다시 실행하고, 녹화 영상 기반 dry-run과 아직 남은 실제 주행 안전 조건을 기록했습니다.

[2~5단계 실제 검증 기록 (2026-08-07)](doc/verified_step_2_to_5_2026-08-07.md)

#### 현재 차량으로 멀티트랙 데이터 다시 수집

한 트랙의 연속 프레임을 무작위로 나누면 배경과 코너 순서를 외운 결과를
검증 성능으로 오인할 수 있다. 현재 카메라 높이와 검정 테이프 규격은
유지하되, 직선·좌우 코너·S자 배치와 시작 위치를 바꾼 독립 녹화를 최소
3개 만든다. Pi의 RealVNC 터미널에서는 다음처럼 15초 제한 수집을 한다.

```bash
./run_opencv_data_collection.sh layout_a_run1 drive
./run_opencv_data_collection.sh layout_b_run1 drive
./run_opencv_data_collection.sh layout_c_holdout drive
```

원본 AVI를 PC로 복사한 뒤 각 영상을 별도 출력 디렉터리로 변환한다.
기본 품질 정책은 정상 밝기의 프레임에서 서로 교차하지 않고 폭이 타당한
검정 테이프 경계 두 개가 검출될 때만, 이전 프레임에 의존하지 않는 raw
OpenCV 각도를 저장한다.

```bash
python3 jd_2_get_train_data.py \
  --video /path/to/layout_a_run1.avi \
  --output-dir /path/to/labeled/layout_a_run1 \
  --sample-every 2
```

모든 run 폴더의 상위 디렉터리를 지정하고 `run` 분리를 사용한다. 이
모드는 독립 녹화가 3개보다 적거나 학습·검증 데이터에 좌회전, 중앙,
우회전 표본이 각각 5개보다 적으면 학습을 시작하지 않는다.

```bash
python3 PC_run_code/jd_deep_learning.py \
  --data-dir /path/to/labeled \
  --output-dir /path/to/training_output \
  --split-strategy run \
  --validation-run-prefix layout_c_holdout \
  --epochs 50 \
  --batch-size 32
```

#### 현재 안전 실행 순서

실차 출력은 저장된 서보 중앙값이 있을 때만 허용한다. 먼저 모터를 끈
상태에서 중앙값을 맞추고 `s`로 저장한다.

```bash
python3 test_code/calibration.py
```

검정 테이프 두 줄 트랙은 녹화 파일을 덮어쓰지 않는 OpenCV 전용
실행기로 먼저 확인한다. `--drive`가 없으면 모터와 서보 출력은 없다.

```bash
# 1) 모터 출력 없이 120프레임 카메라/차선 검출 확인
python3 jd_safe_drive_trial.py

# 2) 같은 검사를 다시 통과한 뒤 DRIVE를 직접 입력해야 저속 주행
python3 jd_safe_drive_trial.py --drive
```

안전 시험 실행기는 차선 검출률 60% 이상일 때만 다음 단계로 진행하며,
첫 실차 주행의 속도는 20%, 길이는 200프레임 또는 10초 중 먼저 도달한
한계를 넘길 수 없게 제한한다.
사람과 장애물이 없는 평평한 폐쇄 트랙에서 전원 스위치를 바로 끌 수 있는
상태로 실행한다. 이 코드는 장애물 인식을 하지 않으므로 일반 도로나 사람
근처에서는 실행하지 않는다.

`models/lane_navigation_candidate_20260807.h5`는 오늘 데이터로 학습한
비교 후보다. 같은 주행에서 나눈 검증만 거쳤으므로 실제 주행 기본
모델로 승격하지 않았으며, 새로 촬영한 미사용 영상에서 비교할 때만
`--model`로 명시한다.

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


