## deepThinkCar-mini 자율주행 3단계: 딥러닝 트레이닝 

### 3단계에서는...
3단계에서는 2단계에서 라벨링 된 데이터를 CNN을 통해서 딥러닝 트레이닝을 실행합니다. 이 단계는 라즈베리파이에서 실행하지 않고 PC에서 실행하게 됩니다.    
라즈베리파이는 CNN을 통한 딥러닝 트레이닝을 실행하기에는 성능이 많이 부족해서 PC를 이용합니다. CNN 딥러닝 트레이닝을 하기 위해서는 다음의 단계를 실행합니다. 

### /deepThinkCar-mini/data 폴더의 라벨링 데이터를 PC로 옮깁니다. 
라즈베리파이의 워킹 폴더인 /deepThinkCar-mini/data 폴더에 저장된 라벨링 데이터인 PNG 파일들을 압축합니다.    
압축을 하는 이유는 라즈베리파이에서 PC로 라벨링 데이터를 쉽게 전달하기 위해서 입니다. 압축을 하기 위해서는 다음 코드를 실행합니다.    
<pre><code>
$python3 jd_label_data_compress.py
['./data/car_video.avi_016_075.png', './data/car_video.avi_143_104.png',  ...
... './data/car_video.avi_158_097.png']
$ ls -al
...
-rw-r--r--  1 pi pi 17087793 Jul 20 11:29 car_image_angle.zip
...
</code></pre>

압축을 위해 "jp_label_data_compress.py" 스크립트를 실행하면 "car_image_angle.zip"이라는 압축파일이 하나 생깁니다.    
이 파일을 USB 메모리스틱을 이용해서 PC로 옮겨야 합니다. 
   
###  PC 파이썬에 텐서플로 개발환경 구축하기 
먼저 deep-mini 소스코드를 github로부터 로컬 PC에도 다운로드를 받습니다. 여기에는 /PC_run_code라는 폴더가 있고 여기에 CNN 트레이닝을 진행할 코드가 들어 있습니다. 
CNN 딥러닝 트레이닝을 실행하려면 여러가지 라이브러리를 설치해야 합니다. 이를 위해서는 두가지 방법이 있습니다. 

- 구글의 colab을 이용하는 방법
- 내 로컬 PC에 딥러닝을 위한 파이썬 모듈을 모두 설치하는 방법 

우선 내 로컬 PC에 딥러닝을 위한 파이썬 모듈을 모듀 설치하는 벙법을 설명합니다. 그 다음에 구글 colab을 이용하는 방법을 설명하겠습니다. 

#### 필요한 모듈을 설치하기 
##### 스탠다드 파이썬 모듈 
CNN 딥러닝 트레이닝을 실행하기 위해서는 야러가지 파이썬 모듈을 설치해애 합니다. 제일 먼저 필요한 파이썬 모듈은 다음과 같습니다. 이 모듈들은 파이썬을 설치할 때 같이 설치되는 스탠다드 라이브러리 이므로 별도 설치할 필요는 없습니다. 

<pre><code>
import os
import random
import fnmatch
import datetime
import pickle
</code></pre>

##### numpy 설치 
그 다음에는 딥러닝에 많이 쓰이는 행렬연산에 사용되는 라이브러리인 numpy를 설치합니다. numpy는 다음과 같이 설치가 가능합니다. 

<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install numpy
</code></pre>

##### tensorflow 설치 
그 다음에는 구글에서 개발한 딥러닝 라이브러리인 tensorflow 라이브러리를 설치합니다. tensorflow는 다음과 같이 설치가 가능합니다. 지금까지는 (2023년 5월 4일) 파이썬 3.11 버전에서는 tensorflow가 제대로 설치가 되지 않기 때문에 3.10 버전의 파이썬을 설치해야 합니다. 

<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install tensorflow
</code></pre>

##### scikit-learn 설치 
그 다음에는 딥러닝용 수치 데이터를 처리하는 라이브러리인 scikit-learn을 설치합니다. scikit-learn은 다음과 같이 설치가 가능합니다. 

<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install sk-learn
</code></pre>

##### 이미지 처리용 파이썬 라이브러리 설치 
그 다음에는 여러가지 이미지 처리용 파이썬 라이브러리를 설치합니다. OpenCV, imgaug, matplotlib등 입니다. 각 라이브러리는 다음과 같이 설치가 가능합니다. 

- OpenCV: 카메라 처리, 이미지 스케일링 등을 수행하는 컴퓨터 비젼 라이브러리 
<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install opencv-python
</code></pre>

- imgaug: 딥러닝에 사용되는 데이터 가상화에 사용되는 라이브러리
<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install imgaug
</code></pre>

- matplotlib: 딥러닝 트레이닝 결과를 그래프로 디스플레이 해주는 라이브러리 
<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code>pip install matplotlib
</code></pre>

### CNN 딥러닝 트레이닝 실행 
이제 CNN 딥러닝 트레이닝을 실행 할 준비가 되었습니다. 트레이닝을 하기 위해서 라벨링 데이터를 준비합니다. 먼저 /deepThinkCar-miin/PC_run_code 폴더에 있는 /data 폴더를 삭제합니다.  
그 다음에 deep-mini키트의 라즈베리파이에서 USB 메모리 스틱으로 카피한 "car_video_angle.zip" 파일을  PC의 /deepThinkCar-mini/PC_run_code 폴더로 이동합니다. 그리고 압축을 풉니다. 그러면 라벨링 데이터가 담긴 data 폴더가 새로 생깁니다. 

<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code> ls


    디렉터리: C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code\data


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----      2021-07-20  오후 12:14         101330 car_video.avi_000_085.png
-a----      2021-07-20  오후 12:14         103780 car_video.avi_001_081.png
-a----      2021-07-20  오후 12:14         103361 car_video.avi_002_085.png
-a----      2021-07-20  오후 12:14         103336 car_video.avi_003_081.png
...
</code></pre> 

딥러닝 트레이닝을 실행하는 "jd_deep_learning.py" 스크립트는 data 폴더에서 라벨링 데이터를 읽어서 트레이닝을 합니다. 따라서 이 data 폴더에 라벨링 데이터가 있어야 합니다. 
라벨링 데이터 준비가 되었으면 다음과 같은 명령을 통해 CNN 딥러닝 트레이닝을 진행합니다.

<pre><code>
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code> python jd_deep_learning.py
</code></pre>
   
   
<pre><code>  
PS C:\Users\user\Downloads\deepThinkCar-mini\PC_run_code> python jd_deep_learning.py
Training data: 152
Validation data: 38
2021-07-20 14:50:24.137791: I tensorflow/core/platform/cpu_feature_guard.cc:142] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN)to use the following CPU instructions in performance-critical operations:  AVX AVX2
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
Model: "Nvidia_Model"
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
conv2d (Conv2D)              (None, 31, 98, 24)        1824
_________________________________________________________________
conv2d_1 (Conv2D)            (None, 14, 47, 36)        21636
_________________________________________________________________
conv2d_2 (Conv2D)            (None, 5, 22, 48)         43248
_________________________________________________________________
conv2d_3 (Conv2D)            (None, 3, 20, 64)         27712
_________________________________________________________________
dropout (Dropout)            (None, 3, 20, 64)         0
_________________________________________________________________
conv2d_4 (Conv2D)            (None, 1, 18, 64)         36928
_________________________________________________________________
flatten (Flatten)            (None, 1152)              0
_________________________________________________________________
dropout_1 (Dropout)          (None, 1152)              0
_________________________________________________________________
dense (Dense)                (None, 100)               115300
_________________________________________________________________
dense_1 (Dense)              (None, 50)                5050
_________________________________________________________________
dense_2 (Dense)              (None, 10)                510
_________________________________________________________________
dense_3 (Dense)              (None, 1)                 11
=================================================================
Total params: 252,219
Trainable params: 252,219
Non-trainable params: 0
_________________________________________________________________
None
WARNING:tensorflow:From .\cobit_deep_learning.py:198: Model.fit_generator (from tensorflow.python.keras.engine.training) is deprecated and will be removed in a future version.
Instructions for updating:
Please use Model.fit, which supports generators.
Epoch 1/10
 15/300 [>.............................] - ETA: 2:25 - loss: 2526.5979
</code></pre>

Epoch100/100까지 실행하는데 40분~50분 정도의 시간이 소요됩니다. 실행이 끝이나면 output 폴더에 추론파일인 "lane_navigation_final.h5' 파일이 생성됩니다. 이 추론파일을 이용해서 딥러닝 자율주행을 실행하게 됩니다. 

### 구글 colab을 이용해서 CNN 트레이닝을 실행하기 
이전에 로컬 PC에 다운로드한 deep-mini 소스코드 폴더에 /PC_run_code 폴더에 "jd_deep_learning.ipynb"라는 파일이 있습니다. 이 파일이 구굴의 코랩 주피터 노트북에서 실행이 되는 파이썬 코드입니다. 

#### 

### 추론파일을 라즈베리파이로 전달하기 
딥러닝 트레이닝으로 생성된 추론파일은 deep-mini 키트의 라즈베리파이 /deepThinkCar-mini/models 폴더에 전달하면 됩니다. USB 메모리스틱을 이용해서 PC에서 카피한 추론파일을 deep-mini 키트의 라즈베리파이로 카피합니다. 라즈베리파이의 /deepThinkCar-mini/model폴더에 카피하면 됩니다. 


### 다음 단계
3단계에서 딥러닝 트레이닝을 통해서 추론파일을 생성하고, 이 추론파일을 deep-mini 키트의 라즈베리파이로 업로드 했습니다. 그 다음 단계인 4단계에서는 이 추론파일을 이용해서 딥러닝 자율주행을 실행할 수 있었습니다. 다음 링크를 통해서 4단계로 갈 수 있습니다.    
[4단계 입러닝 자율주행하기](https://jd-edu.github.io/deepThinkCar_mini/doc/step_4)

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
[5단계 딥러닝 오브젝트 디텍팅 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_5) 

