from pathlib import Path
import sys
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_5_object_detection_opencv import run_object_aware_follower
from jd_drive_runtime import DryRunMotor, DryRunServo


class FakeCapture:
    def __init__(self, frames):
        self.frames = list(frames)
        self.read_count = 0
        self.released = False

    def read(self):
        self.read_count += 1
        if self.frames:
            return True, self.frames.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeLaneGuard:
    def get_lane(self, frame):
        return ['lane'], frame


class FakeDeepDetector:
    def follow_lane(self, frame):
        return 90, frame


class FakeHazardDetector:
    def __init__(self, hazard_flags, error=None, successes_before_error=0):
        self.flags = iter(hazard_flags)
        self.error = error
        self.successes_before_error = successes_before_error
        self.calls = 0

    def __call__(self, frame):
        if self.error is not None and self.calls >= self.successes_before_error:
            raise self.error
        self.calls += 1
        hazard = next(self.flags)
        detections = []
        if hazard:
            detections.append(
                {
                    'class_name': 'stop sign',
                    'is_hazard_class': True,
                    'triggers_stop': True,
                }
            )
        return hazard, frame, detections


def frame():
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    image[:, :160] = 255
    return image


class ObjectAwareRunnerTest(unittest.TestCase):
    def test_hazard_stops_immediately_and_clear_frames_are_required_to_resume(self):
        capture = FakeCapture([frame() for _ in range(8)])
        motor = DryRunMotor()
        servo = DryRunServo()
        summary = run_object_aware_follower(
            capture,
            FakeDeepDetector(),
            FakeLaneGuard(),
            FakeHazardDetector([False, False, True, False, False, False, False, False]),
            motor,
            servo,
            speed=25,
            servo_offset=5,
            is_video=True,
            preview=False,
            warmup_frames=2,
            ready_lane_frames=2,
            clear_frames_to_resume=2,
        )
        self.assertEqual(1, summary['hazard_frames'])
        self.assertEqual(2, summary['motor_start_events'])
        self.assertGreaterEqual(summary['motor_stop_events'], 2)
        self.assertFalse(motor.is_moving)
        self.assertEqual(9, capture.read_count)
        self.assertTrue(capture.released)

    def test_detector_error_always_stops_and_releases(self):
        capture = FakeCapture([frame(), frame()])
        motor = DryRunMotor()
        with self.assertRaisesRegex(RuntimeError, 'detector failed'):
            run_object_aware_follower(
                capture,
                FakeDeepDetector(),
                FakeLaneGuard(),
                FakeHazardDetector(
                    [False],
                    error=RuntimeError('detector failed'),
                    successes_before_error=1,
                ),
                motor,
                DryRunServo(),
                speed=25,
                servo_offset=5,
                is_video=True,
                preview=False,
                warmup_frames=1,
                ready_lane_frames=1,
                clear_frames_to_resume=1,
            )
        self.assertEqual(1, motor.start_count)
        self.assertEqual(1, motor.stop_count)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)


if __name__ == '__main__':
    unittest.main()
