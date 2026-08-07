from pathlib import Path
import sys
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_deep_lane_detect import JdDeepLaneDetect, img_preprocess


class FakeModel:
    input_shape = (None, 66, 200, 3)
    output_shape = (None, 1)

    def __init__(self, result):
        self.result = result

    def __call__(self, _inputs, training=False):
        if training:
            raise AssertionError('inference enabled training mode')
        return np.asarray([[self.result]], dtype=np.float32)


class DeepLaneDetectTest(unittest.TestCase):
    def test_scalar_prediction_is_rounded(self):
        detector = JdDeepLaneDetect(model=FakeModel(91.6))
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        self.assertEqual(92, detector.compute_steering_angle(frame))

    def test_non_finite_prediction_is_rejected(self):
        detector = JdDeepLaneDetect(model=FakeModel(float('nan')))
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        with self.assertRaisesRegex(RuntimeError, 'non-finite'):
            detector.compute_steering_angle(frame)

    def test_none_frame_is_rejected(self):
        detector = JdDeepLaneDetect(model=FakeModel(90))
        with self.assertRaisesRegex(ValueError, 'frame'):
            detector.follow_lane(None)

    def test_preprocess_contract(self):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        processed = img_preprocess(frame)
        self.assertEqual((66, 200, 3), processed.shape)
        self.assertEqual(np.float32, processed.dtype)
        self.assertTrue(np.isfinite(processed).all())


if __name__ == '__main__':
    unittest.main()
