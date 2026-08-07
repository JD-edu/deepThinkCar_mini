# deepThinkCar-mini 2~5단계 실제 검증 기록 (2026-08-07)

- `record_id`: `DAPIER-2026-08-07-deepthinkcar-step2-5`
- 상태: 오늘 영상의 변환·학습과 PC/Pi 녹화 영상 dry-run까지 확인함
- 미완료: 독립 영상 평가, 실제 카메라 연속 추론, 실제 모터 주행

오늘은 공식 문서의 2~5단계를 현재 Python/Keras/OpenCV 환경에서 다시 실행하고 있다. 이 글은 완성된 자율주행 결과가 아니라, 직접 실행한 범위와 아직 확인하지 못한 범위를 나눈 학습 기록이다.

## 먼저 확인한 실행 환경

| 구분 | 직접 확인한 환경 | 이번 작업에서 한 일 |
| --- | --- | --- |
| PC | Python 3.12.3, TensorFlow 2.21.0, Keras 3.15.1, NumPy 2.5.1, OpenCV 5.0.0, scikit-learn 1.9 | 데이터 검증, CPU 학습, 녹화 영상 dry-run |
| PC GPU | NVIDIA GPU는 보이지만 현재 TensorFlow wheel이 해당 compute capability용 바이너리를 포함하지 않아 PTX JIT 경고가 발생함 | 이번 학습은 `CUDA_VISIBLE_DEVICES=-1`로 CPU에서 실행 |
| 라즈베리파이 | Python 3.13.5, TensorFlow 2.21, Keras 3.15.1, NumPy 2.2.4, OpenCV 5.0 | 당시 4·5단계 실행 코드와 기본·후보 모델 배포, staging 테스트와 녹화 영상 dry-run |

환경 버전이 원본 문서가 작성된 때보다 많이 올라가 있어서, 예전 API를 그대로 실행하기보다 현재 Keras/OpenCV에서 다시 불러오고 검사할 수 있게 코드를 고치고 있다.

## 2단계: 녹화 영상을 보존하면서 라벨 데이터 만들기

오늘 촬영한 `data/car_video.avi`를 먼저 읽기 전용으로 검사했다.

- 코덱/크기: XviD(MPEG-4), 320×240
- 프레임 속도: 20 FPS
- 전체 프레임/길이: 405장, 20.25초
- 디코딩 결과: 405장 모두 읽힘
- 원본 SHA-256: `40756fbec00a31418a9d29ae8a2fc5ac6ebb2f1f719ab23fbc1dfa7ccd4e62fd`

기존 스크립트에는 `data/*.png`를 지우는 흐름이 있었다. 이번에는 기존 자료를 지우거나 다른 주행과 섞지 않도록 실행마다 별도 출력 디렉터리를 만들고, `manifest.csv`와 `summary.json`을 함께 남기도록 바꿨다. 파일명 끝의 `_DDD.png`에는 조향각 0~180도만 허용한다.

```bash
python3 jd_2_get_train_data.py \
  --video data/car_video.avi \
  --output-dir data/lane_dataset_20260807_164456 \
  --zip lane_dataset_20260807_164456.zip
```

| 항목 | 직접 확인한 결과 |
| --- | ---: |
| 읽은 프레임 | 405 |
| 라벨 PNG 생성 | 278 |
| 차선을 찾지 못해 건너뜀 | 127 |
| 라벨 생성 비율 | 68.642% |
| 조향각 범위 | 60~138° |
| 조향각 평균 / 중앙값 | 94.15° / 92° |

278개 PNG가 모두 320×240으로 다시 열리는지, 파일명 조향각과 manifest가 일치하는지, ZIP이 손상되지 않았는지 확인했다. 변환 전후 원본 AVI 해시는 같았고 기존 PNG 310개는 삭제되지 않았다. 변환 코드 단위 테스트 4개도 통과했다.

127개 미검출 프레임은 억지 라벨로 넣지 않고 누락으로 남겼다. 이 라벨은 사람이 직접 조향한 ground truth가 아니라 현재 OpenCV 검출기가 만든 pseudo-label이라는 한계도 있다.

## 3단계: 오늘 데이터로 후보 모델 학습

저장소의 기존 `models/lane_navigation_final.h5`는 오늘 촬영한 데이터로 만든 모델이 아니다. 현재 Keras 3에서 `compile=True` 기본 방식으로 열면 예전 `keras.metrics.mse` 역직렬화 오류도 났다. 런타임에서 `compile=False`로 불러오면 기존 모델은 정상 추론하므로, 이 호환성 오류 자체는 모델 교체 이유가 아니다.

오늘 데이터에 맞춘 학습 과정을 직접 확인하기 위해 278장으로 새 모델을 학습했다. 처음에는 각도를 그대로 회귀해 예측이 약 84~85°에 뭉쳤고, flip 증강을 끈 실험도 검증 MAE가 15.73°로 더 나빴다. 이후 목표를 `(angle - 90) / 90`으로 정규화하고 좌우 반전 라벨을 `180 - angle`로 바꿨다.

```bash
DATA_DIR=/path/to/lane_dataset/data
TRAINING_OUT=/path/to/new-training-output

CUDA_VISIBLE_DEVICES=-1 python3 PC_run_code/jd_deep_learning.py \
  --data-dir "$DATA_DIR" \
  --output-dir "$TRAINING_OUT" \
  --epochs 80 \
  --batch-size 32 \
  --validation-fraction 0.2 \
  --temporal-group-size 20 \
  --seed 20260807
```

원본 프레임 번호를 20장 단위 temporal group으로 나눠 198장은 학습, 80장은 검증에 사용했다. 학습 세트는 좌우 반전 후 396장이 됐다. 80 epoch를 요청했지만 early stopping으로 16 epoch에서 끝났고 최선은 6 epoch였다.

같은 검증 80장에 기존 기본 모델도 다시 적용했다.

| temporal-group 검증 80장 | MAE | 상관계수 |
| --- | ---: | ---: |
| 학습 세트 중앙값 94°를 계속 내는 상수 baseline | 17.775° | 해당 없음 |
| 기존 기본 모델 `lane_navigation_final.h5` | **6.8084°** | **0.9719** |
| 오늘 학습한 후보 모델 | 7.7677° | 0.9175 |

후보 모델의 RMSE는 8.8482°였고, H5를 다시 로드했을 때 내보내기 전 모델과 최대 출력 차이는 약 `1.53e-05`였다. 학습·저장·재로드 경로는 동작했지만 같은 검증셋에서 기존 기본 모델보다 더 낫다고 볼 수 없었다. 따라서 기존 모델은 `models/lane_navigation_final.h5`로 유지하고, 새 파일은 `models/lane_navigation_candidate_20260807.h5`로 분리해 **승격하지 않았다**. 후보의 상세 provenance와 배포 금지 조건은 [후보 모델 메타데이터](../models/lane_navigation_candidate_20260807.md)에 적었다.

### 이 검증으로 아직 말할 수 없는 것

- 학습과 검증이 같은 한 번의 영상에서 나왔다. 20프레임 group 분할은 중복을 줄일 뿐, group 경계의 인접 장면까지 독립적으로 만들지는 못한다.
- 검증 80장의 라벨 범위는 60~109°, 평균은 80.8°로 왼쪽 조향에 치우쳤다. 전체 데이터에 있는 110~138° 오른쪽 급회전 구간은 검증셋에 없다.
- 기존 모델의 원래 학습 데이터 provenance는 확인하지 못했다. 이번 내부 비교에서 더 낮은 MAE가 나왔다는 사실만 확인했다.
- 오늘 영상 전체를 다시 돌린 결과는 학습에 사용한 영상의 재실행이지 독립 테스트가 아니다.

다음 모델 승격 판단에는 학습에 전혀 넣지 않은 새 주행 영상과 실제 저속 주행이 필요하다.

## 4단계: 기본 모델의 Pi 녹화 영상 dry-run

`jd_4_lane_follower_deep.py`의 기본 모델 경로는 계속 `models/lane_navigation_final.h5`다. `--drive`가 없으면 dry-run 모터·서보만 사용하고, `--video`와 `--drive`는 동시에 쓸 수 없게 했다.

Pi가 재연결된 뒤 최신 코드와 기본·후보 모델의 SHA-256이 PC 파일과 같은지 확인했다. staging 복사본에서 선택한 19개 테스트가 통과한 뒤 파일을 배포하고, Pi의 오늘 영상으로 다음 명령을 실행했다.

```bash
python3 jd_4_lane_follower_deep.py \
  --video data/car_video.avi \
  --headless
```

| Pi 기본 모델 dry-run | 결과 |
| --- | ---: |
| 유효 프레임 | 405 |
| lane / no-lane 프레임 | 278 / 127 |
| 예측 수 | 278 |
| 예측 범위 / 평균 | 60~108° / 86.3957° |
| 가상 motor start / stop | 4 / 4 |
| watchdog timeout / cleanup error | 없음 / 없음 |
| 실제 하드웨어 출력 | 없음 (`drive_enabled=false`) |

모델 입력 `(66, 200, 3)`과 스칼라 출력을 시작 전에 확인하며, 프레임 품질 저하·연속 차선 소실·추론 예외에는 정지한다. 실제 구동 모드에는 1초 기본 motor watchdog을 두고, 종료나 예외가 나면 모터 정지 후 서보 중앙 복귀·PWM 해제·카메라 해제를 차례로 시도한다.

이 결과는 녹화 파일에서 제어 판단 루프가 끝까지 실행된다는 뜻이다. 실제 카메라 지연과 차체가 트랙을 도는 성능은 아직 검증하지 않았다.

## 5단계: 객체 정지 정책과 차선 추종 결합

객체 검출과 차선 추종은 같은 한 프레임을 사용하도록 바꿨다. 사람, 자동차, 트럭, 정지 표지판을 위험 후보로 보고, threshold를 통과한 위험 객체가 있으면 즉시 정지한다. 다시 출발하려면 5개 연속 clear 프레임과 lane-ready 상태가 모두 필요하다.

모든 클래스에 confidence 0.4를 그대로 적용한 초기 실험에서는 405장 중 351장이 위험으로 판정돼 사용할 수 없었다. 현재 최소 박스 크기는 40픽셀이며 클래스별 정지 threshold는 다음과 같다.

- 사람·자동차·트럭: 0.75
- 정지 표지판: 0.55

Pi에서 기본 모델과 오늘 영상으로 실행했다.

```bash
python3 jd_5_object_detection_opencv.py \
  --video data/car_video.avi \
  --headless
```

| Pi 5단계 dry-run | 결과 |
| --- | ---: |
| 유효 프레임 | 405 |
| lane / no-lane 프레임 | 278 / 127 |
| 0.4 1차 후보 누적 | car 448, person 1113, truck 153 |
| 실제 정지 threshold 통과 | person 1건 |
| hazard 프레임 | 1 |
| 예측 범위 / 평균 | 60~108° / 86.3957° |
| 가상 motor start / stop | 5 / 5 |
| watchdog timeout / cleanup error | 없음 / 없음 |
| 실제 하드웨어 출력 | 없음 (`drive_enabled=false`) |

1차 후보 누적 수는 프레임 수나 실제 객체 수가 아니다. 한 프레임의 여러 low-confidence 후보를 누적한 진단값이다. threshold를 통과한 person 1건도 ground truth가 없어 실제 사람인지 오검출인지 확정하지 않았다.

정지 표지판 경로는 공개 도메인 사진 한 장으로 따로 확인했다.

- 320×240 fixture: stop sign confidence 0.898, box `[47, 45, 215, 152]`, 정지 판정
- 화면에서 약 80픽셀로 축소한 fixture: confidence 0.685, 약 78×59 box, 정지 판정
- 약 60픽셀 크기: confidence 0.42로 현재 0.55 threshold 미달

이 결과는 공개 이미지 fixture에서 검출 함수와 정지 정책이 연결됐다는 뜻이다. 실제 카메라, 인쇄한 표지판, 거리 변화에서의 검출률은 아직 확인하지 않았다.

## 보조 실행기: 녹화하지 않는 OpenCV 차선 추종

`jd_3_lane_follower_opencv.py`도 추가했다. 파일명의 `jd_3`은 실행 순서를 위한 이름이며, 공식 문서의 3단계인 PC 모델 학습을 대체하지 않는다. 이 실행기는 영상을 새로 녹화하지 않고 OpenCV 조향만 dry-run하거나 저속 구동하기 위한 보조 코드다.

PC에서 오늘 영상 사본을 끝까지 dry-run했을 때 405프레임 중 lane 276, no-lane 129였고, 조향각은 60~138°, 평균 94.148°였다. 관련 단위 테스트 3개가 통과했다. Pi에도 코드 설치와 같은 3개 테스트 통과까지 확인했지만, Pi의 전체 AVI 출력은 네트워크 연결이 다시 끊겨 수집하지 못했다.

## 현재 Pi 상태와 남은 안전 gate

Pi는 한 차례 재연결돼 당시 4·5단계 코드와 두 모델을 배포하고 기본 모델 dry-run까지 완료했다. 이후 네트워크 응답과 기존 SSH control socket이 다시 사라져 추가 후보 모델 실행과 OpenCV 전체 영상 출력을 완료하지 못했다. 따라서 단순히 “Pi 미배포”라고 적는 것도, 현재 계속 온라인이라고 적는 것도 정확하지 않다.

그 뒤 PC에서 추가한 녹화·수동조작 안전 보강과 `--drive`의 저장된
캘리브레이션 필수 조건은 아직 Pi에 다시 동기화하지 못했다. Pi에 이미
저장된 중앙값은 확인했지만, 재연결 뒤 최신 커밋과 파일 해시를 다시
맞추기 전에는 PC 저장소를 최종 기준으로 본다.

실제 모터 주행은 아직 실행하지 않았다. 다음 항목을 확인한 뒤에만 `--drive`를 사용한다.

1. Pi 네트워크와 카메라 프레임이 안정적으로 유지되는지 다시 확인한다.
2. 모터 전원을 끈 상태에서 실제 카메라 연속 추론과 처리 속도를 측정한다.
3. 저장된 서보 중앙값, 안전 각도, watchdog, 비상 정지를 바퀴가 들린 상태에서 확인한다.
4. 후보 모델은 새 독립 영상에서 기본 모델보다 낫다는 근거가 생기기 전까지 실제 주행에 사용하지 않는다.
5. 5단계는 실제 표지판 거리별 검출과 정지 거리를 확인한다.
6. 주변을 비우고 즉시 전원을 끌 수 있을 때 기본 모델로 짧은 저속 주행부터 시작한다.

## 이번에 직접 실행한 주요 테스트

```bash
python3 test_code/test_train_data_conversion.py
CUDA_VISIBLE_DEVICES=-1 TF_CPP_MIN_LOG_LEVEL=2 python3 test_code/test_deep_training.py
CUDA_VISIBLE_DEVICES=-1 TF_CPP_MIN_LOG_LEVEL=2 python3 test_code/test_deep_lane_detect.py
CUDA_VISIBLE_DEVICES=-1 TF_CPP_MIN_LOG_LEVEL=2 python3 test_code/test_deep_lane_runner.py
CUDA_VISIBLE_DEVICES=-1 TF_CPP_MIN_LOG_LEVEL=2 python3 test_code/test_object_detection_safety.py
CUDA_VISIBLE_DEVICES=-1 TF_CPP_MIN_LOG_LEVEL=2 python3 test_code/test_object_aware_runner.py
python3 test_code/test_opencv_lane_follower.py
```

현재까지 확인한 핵심은 변환·학습·저장·Pi 비구동 추론 경로가 실행된다는 것이다. 독립 영상과 실제 저속 주행에서 차선을 유지하고 안전하게 멈추는지는 다음 실습으로 남아 있다.
