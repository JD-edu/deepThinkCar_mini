# `lane_navigation_candidate_20260807.h5` 모델 카드

## 상태

- 용도: 2026-08-07 학습 실험의 **후보 모델**
- 승격 상태: **승격 금지**
- 기본 런타임 모델: `models/lane_navigation_final.h5`
- 실제 주행: 독립 영상 비교와 저속 안전 검증 전까지 사용하지 않음

이 파일은 오늘 촬영한 데이터로 학습 과정을 다시 확인하기 위해 만들었다. 학습 당시 실험 출력의 이름은 `lane_navigation_final.h5`였지만, 기존 기본 모델을 덮어쓰지 않도록 저장소에 반영할 때 `lane_navigation_candidate_20260807.h5`로 분리했다.

## 파일과 데이터 provenance

| 항목 | 값 |
| --- | --- |
| 모델 파일 SHA-256 | `ce07ad73d807a318b4ade87deed75644ed4b30f14d3d3d8096b64a9bbb8c457b` |
| 원본 영상 SHA-256 | `40756fbec00a31418a9d29ae8a2fc5ac6ebb2f1f719ab23fbc1dfa7ccd4e62fd` |
| 원본 영상 | XviD, 320×240, 20 FPS, 405 frames |
| 라벨 데이터 | 278 labeled / 127 lane-not-detected |
| 라벨 각도 | 60~138°, 평균 94.1547°, 중앙값 92° |
| 학습 환경 | Python 3.12.3, TensorFlow 2.21.0, Keras 3.15.1 |
| seed | `20260807` |

라벨은 사람이 직접 기록한 조향 ground truth가 아니라 같은 영상에 OpenCV 차선 검출을 적용해 만든 pseudo-label이다.

## 학습과 모델 계약

- 분할: source frame을 20장 단위 temporal group으로 묶음
- 학습/검증: 198장 / 80장
- 좌우 반전 후 학습 수: 396장
- target 정규화: `(angle - 90) / 90`
- 요청/완료 epoch: 80 / 16, best epoch 6
- 입력 계약: BGR 영상의 아래 절반 → YUV → Gaussian blur → 200×66 resize → `/255`
- 입력 shape: `(66, 200, 3)`
- 출력 계약: degree 단위의 조향각 스칼라 1개. 런타임은 0~180°만 허용함

배포용 H5에는 정규화 출력을 다시 degree로 바꾸는 layer가 포함돼 있다. 내부 checkpoint인 `lane_navigation_best_normalized_do_not_deploy.keras`는 정규화된 값을 출력하므로 런타임에 넣지 않는다.

## 동일 검증셋 비교

| 모델 | MAE | RMSE | 상관계수 |
| --- | ---: | ---: | ---: |
| 기존 기본 모델 | **6.8084°** | **7.7524°** | **0.9719** |
| 이 후보 모델 | 7.7677° | 8.8482° | 0.9175 |

상수 baseline 17.775°는 학습 세트 중앙값 94°를 검증 80장에 계속 예측한 값이다. 후보는 이 상수 baseline보다 낫지만 기존 기본 모델보다 낫지 않았다. H5 재로드 전후 최대 출력 차이는 약 `1.53e-05`였다.

## 알려진 한계와 승격 조건

- 학습과 검증이 같은 주행 영상에서 나왔다. temporal group을 나눴어도 인접 장면 상관은 남는다.
- 검증 라벨은 60~109°, 평균 80.8°로 왼쪽에 치우쳤다.
- 전체 데이터의 110~138° 오른쪽 급회전 구간이 검증셋에는 없다.
- 기존 기본 모델의 원래 학습 데이터 provenance도 확인하지 못했다.
- 학습에 사용한 405프레임 영상의 dry-run은 독립 테스트가 아니다.

승격하려면 학습에 넣지 않은 새 영상에서 기본 모델과 같은 조건으로 비교하고, 오른쪽 급회전을 포함한 검증셋과 실제 바퀴를 든 저속 안전 시험을 거쳐야 한다. 그 전에는 오프라인 비교에서만 다음처럼 명시적으로 선택한다.

```bash
python3 jd_4_lane_follower_deep.py \
  --model models/lane_navigation_candidate_20260807.h5 \
  --video data/car_video.avi \
  --headless
```

이 명령도 오늘 학습 영상의 재실행일 뿐이며 모델 승격 근거로 사용하지 않는다.
