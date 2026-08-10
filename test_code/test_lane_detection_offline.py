import unittest
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jd_opencv_lane_detect import JdOpencvLaneDetect


HEIGHT = 240
WIDTH = 320
FLOOR_COLOR = (170, 180, 185)


def make_floor():
    return np.full((HEIGHT, WIDTH, 3), FLOOR_COLOR, dtype=np.uint8)


class LaneDetectionOfflineTest(unittest.TestCase):
    def setUp(self):
        self.detector = JdOpencvLaneDetect()

    def test_two_black_boundaries_are_detected(self):
        frame = make_floor()
        cv2.line(frame, (10, HEIGHT - 1), (100, HEIGHT // 2), (20, 20, 20), 14)
        cv2.line(frame, (310, HEIGHT - 1), (220, HEIGHT // 2), (20, 20, 20), 14)

        lanes, lane_image = self.detector.get_lane(frame)
        angle, heading_image = self.detector.get_steering_angle(lane_image, lanes)

        self.assertEqual(2, len(lanes))
        self.assertIsNotNone(heading_image)
        self.assertLessEqual(abs(angle - 90), 3)

    def test_raw_label_does_not_depend_on_previous_steering_state(self):
        frame = make_floor()
        cv2.line(frame, (10, HEIGHT - 1), (100, HEIGHT // 2), (20, 20, 20), 14)
        cv2.line(frame, (310, HEIGHT - 1), (220, HEIGHT // 2), (20, 20, 20), 14)
        lanes, lane_image = self.detector.get_lane(frame)
        self.detector.curr_steering_angle = 45

        raw_angle, heading_image = self.detector.get_raw_steering_angle(
            lane_image,
            lanes,
        )

        self.assertIsNotNone(heading_image)
        self.assertLessEqual(abs(raw_angle - 90), 3)
        self.assertEqual(45, self.detector.curr_steering_angle)

    def test_vertical_boundaries_are_not_discarded(self):
        frame = make_floor()
        cv2.line(frame, (70, HEIGHT - 1), (70, HEIGHT // 2), (10, 10, 10), 14)
        cv2.line(frame, (250, HEIGHT - 1), (250, HEIGHT // 2), (10, 10, 10), 14)

        lanes, _ = self.detector.get_lane(frame)

        self.assertEqual(2, len(lanes))

    def test_one_boundary_uses_expected_lane_width(self):
        frame = make_floor()
        cv2.line(frame, (20, HEIGHT - 1), (95, HEIGHT // 2), (20, 20, 20), 14)

        lanes, lane_image = self.detector.get_lane(frame)
        angle, heading_image = self.detector.get_steering_angle(lane_image, lanes)

        self.assertEqual(1, len(lanes))
        self.assertIsNotNone(heading_image)
        self.assertLess(angle, 90)

    def test_thin_floor_seam_is_rejected(self):
        frame = make_floor()
        cv2.line(frame, (0, HEIGHT - 20), (WIDTH, HEIGHT // 2), (70, 70, 70), 1)

        lanes, _ = self.detector.get_lane(frame)

        self.assertEqual([], lanes)

    def test_large_dark_object_is_rejected(self):
        frame = make_floor()
        cv2.rectangle(frame, (0, HEIGHT // 2), (85, HEIGHT - 1), (20, 20, 20), -1)

        lanes, _ = self.detector.get_lane(frame)

        self.assertEqual([], lanes)


if __name__ == '__main__':
    unittest.main()
