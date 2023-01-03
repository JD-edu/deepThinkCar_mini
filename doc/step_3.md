## 이 문서에 나오는 방법은 라즈베리파이 32비트를 사용합니다. deepThinkCar는 2022년 10월부터 라즈베리파이 64비트 버전을 사용합니다. 다음 링크의 문서를 참고해 주십시오. 

[딥씽크카 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/step_3)

## deepThinkCar-mini 자율주행 3단계: 딥러닝 트레이닝 

### 3단계에서는...
3단계에서는 2단계에서 라벨링 된 데이터를 CNN을 통해서 딥러닝 트레이닝을 실행합니다. 이 단계는 라즈베리파이에서 실행하지 않고 PC에서 실행하게 됩니다.    
라즈베리파이는 CNN을 통한 딥러닝 트레이닝을 실행하기에는 성능이 많이 부족해서 PC를 이용합니다. CNN 딥러닝 트레이닝을 하기 위해서는 다음의 단계를 실행합니다. 

### deepThinkCar/data 폴더의 라벨링 데이터를 PC로 옮깁니다. 
라즈베리파이의 워킹 폴더인 deepThinkCar-mini/data 폴더에 저장된 라벨링 데이터인 PNG 파일들을 압축합니다.    
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
   
### PC 파이썬에 텐서플로 개발환경 구축 
CNN 딥러닝 트레이닝을 실행하려면 여러가지 라이브러리를 설치해야 합니다. 이 과정이 복잡한 편이어서 미리 만들어진 파이썬용 아나콘다 가상환경을 사용합니다. 

#### 아나콘다 다운로드 및 설치
아나콘다로 가상환경을 사용하기 위해서 PC에 아나콘다가 설치되어 있지 않다면 아나코다를 설치합니다. 아나콘다를 설치하는 방법은 아래의 URL을 참고하면 됩니다.    
   
[아나콘다 윈도 설치](https://docs.anaconda.com/anaconda/install/windows/)
 
#### deepThinkCar용 아나콘다 가상환경 다운로드 
아나콘다가 PC에 잘 설치가 되었으면 deepThinkCar 트레이닝용 가상환경을 다운로드 받습니다.    
<pre><code>
C:\Users\user\Downloads>git clone https://github.com/cobit-git/deepThinkCar-tf-PC.git
Cloning into 'deepThinkCar-tf-PC'...
remote: Enumerating objects: 617, done.
remote: Counting objects: 100% (617/617), done.
remote: Compressing objects: 100% (608/608), done.
remote: Total 617 (delta 12), reused 606 (delta 8), pack-reused 0R
Receiving objects: 100% (617/617), 51.12 MiB | 22.53 MiB/s, done.
Resolving deltas: 100% (12/12), done.

C:\Users\user\Downloads>
</code></pre>

#### YML 파일을 이용한 deepThinkCar용 아나콘다 가상환경 설치 
deepThinkCar 아나코다 가상환경을 다운로드 했으면, YML 파일을 이용하여 가상환경을 설치합니다. 다운로드 받은 deepThinkCar용 아나콘다 가상화경에 보면 "cobitlab.yml"이라는 파일이 있습니다. 이 YML 환경파일을 이용해서 deepThinkCar용 아나콘다 가상환경을 만들 수 있습니다.
아나콘다에서 "Ananconda PowerShell Prompt"를 실행합니다.    
![image](https://user-images.githubusercontent.com/76054530/126259373-2343277b-3438-4770-b5e8-a5dc66d3f5de.png)   
그러면 다음과 같은 윈도 파워쉘 기반의 프롬프트윈도가 열립니다.    
![image](https://user-images.githubusercontent.com/76054530/126259745-43d96931-6e75-480d-9c43-bbf60b510dca.png)   
이 프롬프트에서 다음과 같이 명령을 입력해서 현재 만들어진 가상환경을 확인합니다.    
   
<pre><code>
(base) PS C:\Users\user> conda env list
# conda environments:
#

base                  *  C:\Users\user\anaconda3

(base) PS C:\Users\user>
</code></pre>
   
아나콘다를 처움 설치하고 가상환경을 만들지 않았다면 "base" 가상환경만 존재 합니다. deepThinkCar용 가상환경을 만들기 전에 다은로드 받은 deepThinkCar용 아나콘다 가상환경 소스코드 폴더로 이동합니다.   그리고 "ls" 명령을 입력해서 deepThinkCar용 아나콘다 가상환경 파일들을 확인합니다. 

<pre><code>
(base) PS C:\Users\user\Downloads> cd .\deepThinkCar-tf-PC\
(base) PS C:\Users\user\Downloads\deepThinkCar-tf-PC> ls


    디렉터리: C:\Users\user\Downloads\deepThinkCar-tf-PC


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----      2021-07-20  오후 12:14                data
d-----      2021-07-20  오후 12:14                docs
d-----      2021-07-20  오후 12:14                output
d-----      2021-07-20  오후 12:14                sphinx-gen-doc
d-----      2021-07-20  오후 12:14                __pycache__
-a----      2021-07-20  오후 12:14           2206 cobit-tensor-env.yml
-a----      2021-07-20  오후 12:14           5715 cobitlab.yml
-a----      2021-07-20  오후 12:14           8744 cobit_deep_learning.py
-a----      2021-07-20  오후 12:14            171 README.md


(base) PS C:\Users\user\Downloads\deepThinkCar-tf-PC>
</code></pre>

이 중에서 "cobitlab.yml" 환경파일을 이용해서 deepThinkCar용 아나콘다 가상환경을 만들게 됩니다. YML 환경파일을 확인 했으면 다음과 같이 명령을 입력합니다. 
<pre><code>
(base) PS C:\Users\user\Downloads\deepThinkCar-tf-PC> conda env create --file cobitlab
</code></pre>

4분 정도 지나고 다음과 같은 메시지가 프롬프트 윈도에 나타나면 가상환경 설치가 완료된 것입니다. 설치된 가상환경의 이름은 자동으로 "cobitlab_win"으로 만들어 집니다. 
<pre><code>
done
#
# To activate this environment, use
#
#     $ conda activate cobitlab_win
#
# To deactivate an active environment, use
#
#     $ conda deactivate

(base) PS C:\Users\user\Downloads\deepThinkCar-tf-PC>
</code></pre>   

"cobitlab_win" 가상환경의 설치가 완료된 후, 다음과 같은 명령을 통해 가상환경을 활성화 합니다. 

<pre><code>   
(base) PS C:\Users\user\Downloads\deepThinkCar-tf-PC> conda activate cobitlab_win
(cobitlab_win) PS C:\Users\user\Downloads\deepThinkCar-tf-PC>
</code></pre>   

### CNN 딥러닝 트레이닝 실행 
이제 CNN 딥러닝 트레이닝을 실행 할 준비가 되었습니다. 트레이닝을 하기 위해서 라벨링 데이터를 준비합니다. 먼저 'deepThinkCar-tf-PC" 폴더에 있는 data 폴더를 삭제합니다.  
그 다음에 deepThinkCar 라즈베리파이에서 주피터 노트북을 통해 다운받은 "car_video_angle.zip" 파일을  "deepThinkCar-tf-PC" 폴더로 이동합니다. 그리고 압축을 풉니다. 그러면 라벨링 데이터가 담긴 data 폴더가 새로 생깁니다. 
<pre><code>
(cobitlab_win) PS C:\Users\user\Downloads\deepThinkCar-tf-PC\data> ls


    디렉터리: C:\Users\user\Downloads\deepThinkCar-tf-PC\data


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----      2021-07-20  오후 12:14         101330 car_video.avi_000_085.png
-a----      2021-07-20  오후 12:14         103780 car_video.avi_001_081.png
-a----      2021-07-20  오후 12:14         103361 car_video.avi_002_085.png
-a----      2021-07-20  오후 12:14         103336 car_video.avi_003_081.png
...
</code></pre> 

딥러닝 트레이닝을 실행하는 "cobit_deep_learning.py" 스크립트는 data 폴더에서 라벨링 데이터를 읽어서 트레이닝을 합니다. 따라서 이 data 폴더에 라벨링 데이터가 있어야 합니다. 
라벨링 데이터 준비가 되었으면 다음과 같은 명령을 통해 CNN 딥러닝 트레이닝을 진행합니다.

<pre><code>
(cobitlab_win) PS C:\Users\user\Downloads\deepThinkCar-tf-PC> python .\cobit_deep_learning.py
</code></pre>
   
   
<pre><code>  
(cobitlab_win) PS C:\Users\user\Downloads\deepThinkCar-tf-PC> python .\cobit_deep_learning.py
tf.__version__: 2.3.0
keras.__version__: 2.4.3
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

Epoch10/10까지 실행하는데 40분~50분 정도의 시간이 소요됩니다. 실행이 끝이나면 output 폴더에 추론파일인 "lane_navigation_final.h5' 파일이 생성됩니다. 이 추론파일을 이용해서 딥러닝 자율주행을 실행하게 됩니다. 

### 추론파일을 라즈베리파이로 전달하기 
딥러닝 트레이닝으로 생성된 추론파일은 deepThinkCar 라즈베리파이로 다시 전달이 되어야 합니다. 추론파일을 PC에서 라즈베리파이로 전달 할 때도 주피터 노트북을 사용하여 전달합니다.    
추론파일은 라즈베리파이 deepThinkCar 폴더의 models 폴더에 전달하면 됩니다. 

![image](https://user-images.githubusercontent.com/76054530/126271416-a2126999-f99f-4416-9287-07b29cc35035.png)

먼저 주피터 노트북에서 deepThinkCar/midels 폴더로 이동합니다. 주피터 노트북 오른쪽 윗쪽에 "upload" 버턴을 클릭해서 추론파일인 "lane_navigation_final.h5'를 업로드 합니다.    
업로드가 제댜로 되었다면 다음과 같이 주피터 노트북에 디스플레이이 됩니다. 

![image](https://user-images.githubusercontent.com/76054530/126324322-8526ea70-bdb8-474f-80ab-a4d5971ced77.png)

### 다음 단계
3단계에서 딥러닝 트레이닝을 통해서 추론파일을 생성하고, 이 추론파일을 deepThinkCar 라즈베리파이로 업로드 했습니다. 그 다음 단계인 4단계에서는 이 추론파일을 이용해서 딥러닝 자율주행을 실행할 수 있었습니다. 다음 링크를 통해서 4단계로 갈 수 있습니다.    
[4단계 입러닝 자율주행하기](https://cobit-git.github.io/deepThinkCar_doc/step_4)

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

