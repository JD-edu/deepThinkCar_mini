from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_4_lane_follower_deep import run_lane_follower
from jd_drive_runtime import (
    DryRunMotor,
    DryRunServo,
    MotorWatchdog,
    read_frame,
    safe_servo_angle,
    shutdown_runtime,
)


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


class FakeLaneGuard:
    def __init__(self, visible):
        self.visible = iter(visible)

    def get_lane(self, frame):
        return (['lane'] if next(self.visible) else []), frame


class FakeDeepDetector:
    def __init__(self, angle=90, error=None, successes_before_error=0):
        self.angle = angle
        self.error = error
        self.successes_before_error = successes_before_error
        self.calls = 0

    def follow_lane(self, frame):
        if self.error is not None and self.calls >= self.successes_before_error:
            raise self.error
        self.calls += 1
        return self.angle, frame


def frame():
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    image[:, :160] = 255
    return image


class DeepLaneRunnerTest(unittest.TestCase):
    def test_camera_frame_normalization_preserves_real_right_side(self):
        high_resolution = np.zeros((480, 640, 3), dtype=np.uint8)
        high_resolution[:, 320:] = 255
        ok, normalized = read_frame(FakeCapture([high_resolution]))
        self.assertTrue(ok)
        self.assertEqual((240, 320, 3), normalized.shape)
        self.assertGreater(float(normalized[:, 240:].mean()), 200.0)

    def test_camera_frame_normalization_crops_confirmed_black_padding(self):
        padded = np.zeros((240, 640, 3), dtype=np.uint8)
        padded[:, :320] = 120
        ok, normalized = read_frame(FakeCapture([padded]))
        self.assertTrue(ok)
        self.assertEqual((240, 320, 3), normalized.shape)
        self.assertAlmostEqual(120.0, float(normalized.mean()))

    def test_servo_angle_is_clamped_and_unsafe_prediction_is_rejected(self):
        self.assertEqual(140.0, safe_servo_angle(138, 5))
        self.assertEqual(50.0, safe_servo_angle(40, 5))
        with self.assertRaisesRegex(ValueError, 'safety envelope'):
            safe_servo_angle(10, 5)

    def run_case(self, frames, visible, detector=None, **overrides):
        capture = FakeCapture(frames)
        motor = DryRunMotor()
        servo = DryRunServo()
        options = {
            'speed': 37,
            'servo_offset': 5,
            'is_video': True,
            'preview': False,
            'warmup_frames': 2,
            'ready_lane_frames': 2,
            'lost_lane_limit': 2,
        }
        options.update(overrides)
        summary = run_lane_follower(
            capture,
            detector or FakeDeepDetector(),
            FakeLaneGuard(visible),
            motor,
            servo,
            **options,
        )
        return summary, capture, motor, servo

    def test_never_starts_without_frames(self):
        summary, capture, motor, _servo = self.run_case([], [])
        self.assertEqual(0, summary['motor_start_events'])
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)

    def test_starts_after_ready_frames_and_stops_after_lane_loss(self):
        frames = [frame() for _ in range(5)]
        summary, _capture, motor, servo = self.run_case(
            frames,
            [True, True, True, False, False],
        )
        self.assertEqual(1, summary['motor_start_events'])
        self.assertGreaterEqual(summary['motor_stop_events'], 1)
        self.assertFalse(motor.is_moving)
        self.assertEqual([95.0, 95.0, 95.0], servo.angles)

    def test_inference_error_stops_motor_and_releases_camera(self):
        capture = FakeCapture([frame(), frame()])
        motor = DryRunMotor()
        servo = DryRunServo()
        with self.assertRaisesRegex(RuntimeError, 'inference failed'):
            run_lane_follower(
                capture,
                FakeDeepDetector(
                    error=RuntimeError('inference failed'),
                    successes_before_error=1,
                ),
                FakeLaneGuard([True, True]),
                motor,
                servo,
                speed=37,
                servo_offset=5,
                is_video=True,
                preview=False,
                warmup_frames=1,
                ready_lane_frames=1,
            )
        self.assertEqual(1, motor.start_count)
        self.assertEqual(1, motor.stop_count)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)

    def test_watchdog_stops_motor_and_runner_reports_timeout(self):
        capture = FakeCapture([frame(), frame()])
        raw_motor = DryRunMotor()
        motor = MotorWatchdog(
            raw_motor,
            timeout_seconds=0.05,
            check_interval_seconds=0.005,
        )

        class BlockingSecondInference:
            calls = 0

            def follow_lane(self, image):
                self.calls += 1
                if self.calls == 2:
                    self.assert_watchdog_timeout()
                return 90, image

            @staticmethod
            def assert_watchdog_timeout():
                if not motor.wait_for_timeout(1.0):
                    raise AssertionError('motor watchdog did not expire')

        summary = run_lane_follower(
            capture,
            BlockingSecondInference(),
            FakeLaneGuard([True, True]),
            motor,
            DryRunServo(),
            speed=37,
            servo_offset=5,
            is_video=True,
            preview=False,
            warmup_frames=1,
            ready_lane_frames=1,
        )

        self.assertFalse(summary['complete'])
        self.assertTrue(summary['watchdog_timed_out'])
        self.assertEqual(1, raw_motor.start_count)
        self.assertEqual(1, raw_motor.stop_count)
        self.assertFalse(raw_motor.is_moving)
        self.assertTrue(capture.released)

    def test_cleanup_continues_after_motor_and_servo_errors(self):
        events = []

        class BrokenMotor:
            def motor_stop(self):
                events.append('motor_stop')
                raise RuntimeError('motor stop failed')

        class BrokenServo:
            def shutdown(self):
                events.append('servo_shutdown')
                raise RuntimeError('servo shutdown failed')

        class TrackingCapture:
            def release(self):
                events.append('capture_release')

        with patch(
            'jd_drive_runtime.cv2.destroyAllWindows',
            side_effect=lambda: events.append('destroy_windows'),
        ):
            errors = shutdown_runtime(
                BrokenMotor(),
                BrokenServo(),
                TrackingCapture(),
                preview=True,
            )

        self.assertEqual(
            ['motor_stop', 'servo_shutdown', 'capture_release', 'destroy_windows'],
            events,
        )
        self.assertEqual(2, len(errors))
        self.assertIn('motor stop', errors[0])
        self.assertIn('servo shutdown', errors[1])


if __name__ == '__main__':
    unittest.main()
