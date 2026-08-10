from pathlib import Path
import sys
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_3_lane_follower_opencv import run_opencv_lane_follower
from jd_drive_runtime import DryRunMotor, DryRunServo


class FakeCapture:
    def __init__(self, frames):
        self.frames = list(frames)
        self.released = False

    def read(self):
        if self.frames:
            return True, self.frames.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeWriter:
    def __init__(self):
        self.frames = []
        self.released = False

    def write(self, frame):
        self.frames.append(frame.copy())

    def release(self):
        self.released = True


class FakeLaneDetector:
    def __init__(self, visible, error_after=None):
        self.visible = iter(visible)
        self.angle_calls = 0
        self.error_after = error_after

    def get_lane(self, image):
        return (['lane'] if next(self.visible) else []), image

    def get_steering_angle(self, image, _lanes):
        if self.error_after is not None and self.angle_calls >= self.error_after:
            raise RuntimeError('OpenCV steering failed')
        self.angle_calls += 1
        return 90, image


def usable_frame():
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    image[:, :160] = 255
    return image


class OpenCvLaneFollowerTest(unittest.TestCase):
    def run_case(self, visible, detector=None):
        capture = FakeCapture([usable_frame() for _ in visible])
        motor = DryRunMotor()
        servo = DryRunServo()
        summary = run_opencv_lane_follower(
            capture,
            detector or FakeLaneDetector(visible),
            motor,
            servo,
            speed=20,
            servo_offset=-15,
            is_video=True,
            preview=False,
            warmup_frames=2,
            ready_lane_frames=2,
            lost_lane_limit=2,
        )
        return summary, capture, motor, servo

    def test_no_lane_never_starts(self):
        summary, capture, motor, servo = self.run_case([False, False])
        self.assertEqual(0, summary['motor_start_events'])
        self.assertEqual([], servo.angles)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)

    def test_starts_after_ready_frames_and_stops_on_lane_loss(self):
        summary, capture, motor, servo = self.run_case(
            [True, True, True, False, False]
        )
        self.assertEqual(1, summary['motor_start_events'])
        self.assertGreaterEqual(summary['motor_stop_events'], 1)
        self.assertEqual([75.0, 75.0, 75.0], servo.angles)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)

    def test_error_after_start_stops_and_releases(self):
        capture = FakeCapture([usable_frame(), usable_frame()])
        motor = DryRunMotor()
        detector = FakeLaneDetector([True, True], error_after=1)
        with self.assertRaisesRegex(RuntimeError, 'steering failed'):
            run_opencv_lane_follower(
                capture,
                detector,
                motor,
                DryRunServo(),
                speed=20,
                servo_offset=-15,
                is_video=True,
                preview=False,
                warmup_frames=1,
                ready_lane_frames=1,
            )
        self.assertEqual(1, motor.start_count)
        self.assertEqual(1, motor.stop_count)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)

    def test_wall_clock_limit_stops_and_releases_without_starting(self):
        capture = FakeCapture([usable_frame()])
        motor = DryRunMotor()
        ticks = iter([0.0, 2.0])
        summary = run_opencv_lane_follower(
            capture,
            FakeLaneDetector([True]),
            motor,
            DryRunServo(),
            speed=20,
            servo_offset=-15,
            is_video=False,
            preview=False,
            max_frames=10,
            max_seconds=1.0,
            monotonic_fn=lambda: next(ticks),
        )
        self.assertTrue(summary['complete'])
        self.assertTrue(summary['time_limit_reached'])
        self.assertEqual(0, summary['valid_frames'])
        self.assertEqual(0, motor.start_count)
        self.assertTrue(capture.released)

    def test_recording_keeps_every_valid_frame_and_releases_writer(self):
        capture = FakeCapture([usable_frame(), usable_frame(), usable_frame()])
        writer = FakeWriter()
        summary = run_opencv_lane_follower(
            capture,
            FakeLaneDetector([True, False, True]),
            DryRunMotor(),
            DryRunServo(),
            speed=20,
            servo_offset=-15,
            is_video=True,
            preview=False,
            recording_writer=writer,
        )
        self.assertEqual(3, summary['recorded_frames'])
        self.assertEqual(3, len(writer.frames))
        self.assertTrue(writer.released)
        self.assertTrue(capture.released)


if __name__ == '__main__':
    unittest.main()
