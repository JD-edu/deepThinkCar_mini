# jtjin0916/deepcar 데이터 재학습 기록

이 디렉터리는 `jtjin0916/deepcar`의 학습 데이터를 확인한 뒤 현재
브랜치의 안전한 학습 스크립트로 다시 학습한 결과다. 기본 실차 모델은
교체하지 않았다.

## 데이터 출처와 동일성

- 확인한 원본: `https://github.com/jtjin0916/deepcar`
- 원본 commit: `fb8654d8767b3585ebf59195d669155b1c4841ad`
- 원본 경로: `PC_run_code/data`
- 이미지: 파일명 끝에 조향각이 들어 있는 PNG 329장
- 원본과 이 저장소의 Git tree: 모두 `cee9494ee37ad4b887ba03276f7d979922505d29`
- 학습 스크립트가 계산한 dataset SHA-256: `d052dd36fe240898c30257fc96937872dde0fdee694219477889cfb792e9a687`

두 저장소의 데이터 tree가 이미 같았기 때문에 파일을 다시 복사하지
않았다. 외부 저장소에는 별도 `LICENSE` 파일이 없으므로, 재배포 권한은
저장소 소유자에게 별도로 확인해야 한다.

## 실행 명령

```bash
python3 PC_run_code/jd_deep_learning.py \
  --data-dir PC_run_code/data \
  --output-dir PC_run_code/output/jtjin0916_deepcar_20260810_seed20260810 \
  --epochs 50 \
  --batch-size 32 \
  --validation-fraction 0.2 \
  --temporal-group-size 20 \
  --seed 20260810
```

환경은 Python 3.12.3, TensorFlow 2.21.0, Keras 3.15.1, NumPy 2.5.1,
OpenCV 5.0.0, NVIDIA GeForce RTX 5050 Laptop GPU다. TensorFlow가 compute
capability 12.0a용 사전 컴파일 커널을 포함하지 않아 PTX JIT 경고가
나왔지만 학습과 추론은 정상 완료됐다.

## 결과

| 항목 | 결과 |
| --- | ---: |
| 전체 이미지 | 329 |
| 학습 / 검증 | 260 / 69 |
| 좌우 반전 후 학습 이미지 | 520 |
| 요청 / 완료 epoch | 50 / 21 |
| 최적 epoch | 11 |
| 후보 MAE / RMSE | 4.93° / 6.00° |
| 후보 최대 절대 오차 | 14.16° |
| H5 SHA-256 | `d3d9cb90f53175d47c1f90cf8555d734f280c130387ac5e37b2a75b58c165a7d` |

같은 69장에서는 `models/lane_navigation_final.h5`가 MAE 14.93°,
원본의 `PC_run_code/output/lane_navigation_final.h5`가 MAE 1.91°였다.
후자는 이 329장으로 이미 학습됐을 가능성이 커서 검증 이미지 누수를
배제할 수 없다. 이 비교는 `model_comparison.json`에 보존했다.

## 안전 결론

`lane_navigation_candidate.h5`는 학습·저장·재로드와 200프레임 제한
오프라인 영상 실행을 통과했다. 그러나 검증 범위가 90~113°로 치우쳤고
같은 주행 세션에서 분리한 데이터이므로 **실차 기본 모델로 승격하지
않는다**. `lane_navigation_best_normalized_do_not_deploy.keras`는 출력이
정규화된 내부 checkpoint라 런타임에 넣으면 안 된다.
