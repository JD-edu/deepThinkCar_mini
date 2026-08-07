from pathlib import Path
import sys
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_opencv_dnn_objectdetect_v3 import detect_hazards


class FakeDetectionModel:
    def __init__(self, classes, confidences, boxes):
        self.result = (
            np.asarray(classes),
            np.asarray(confidences),
            np.asarray(boxes),
        )

    def detect(self, _image, confThreshold):
        self.confidence_threshold = confThreshold
        return self.result


class ObjectDetectionSafetyTest(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((240, 320, 3), dtype=np.uint8)

    def test_stop_sign_is_a_hazard(self):
        model = FakeDetectionModel([13], [0.9], [[200, 50, 45, 42]])
        should_stop, _image, detections = detect_hazards(self.image, model=model)
        self.assertTrue(should_stop)
        self.assertEqual('stop sign', detections[0]['class_name'])

    def test_box_uses_width_and_height_not_bottom_right_coordinates(self):
        model = FakeDetectionModel([1], [0.8], [[250, 180, 40, 40]])
        should_stop, _image, detections = detect_hazards(self.image, model=model)
        self.assertTrue(should_stop)
        self.assertEqual([250, 180, 40, 40], detections[0]['box'])

    def test_small_hazard_and_unrelated_object_do_not_stop(self):
        model = FakeDetectionModel(
            [3, 17],
            [0.9, 0.9],
            [[10, 10, 20, 20], [30, 30, 80, 80]],
        )
        should_stop, _image, detections = detect_hazards(self.image, model=model)
        self.assertFalse(should_stop)
        self.assertEqual(2, len(detections))

    def test_class_specific_confidence_rejects_weak_person_but_keeps_stop_sign(self):
        weak_person = FakeDetectionModel([1], [0.70], [[10, 10, 80, 80]])
        should_stop, _image, _detections = detect_hazards(
            self.image,
            model=weak_person,
        )
        self.assertFalse(should_stop)

        stop_sign = FakeDetectionModel([13], [0.60], [[10, 10, 80, 80]])
        should_stop, _image, _detections = detect_hazards(
            self.image,
            model=stop_sign,
        )
        self.assertTrue(should_stop)

    def test_none_image_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'image'):
            detect_hazards(None, model=FakeDetectionModel([], [], []))


if __name__ == '__main__':
    unittest.main()
