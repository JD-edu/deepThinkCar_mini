from contextlib import redirect_stderr
from datetime import datetime
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_drive_runtime import DryRunMotor, DryRunServo
from jd_remote_control import (
    ManualCommand,
    build_argument_parser,
    create_session_directory,
    load_runtime_center_angle,
    run_remote_control,
)


class FakeCapture:
    def __init__(self, results):
        self.results = list(results)
        self.released = False

    def read(self):
        if self.results:
            return self.results.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeUi:
    def __init__(self, commands, fail_draw_at=None):
        self.commands = list(commands)
        self.draw_count = 0
        self.fail_draw_at = fail_draw_at
        self.closed = False

    def poll(self):
        if self.commands:
            return self.commands.pop(0)
        return ManualCommand(quit=True)

    def draw(self, **_state):
        self.draw_count += 1
        if self.draw_count == self.fail_draw_at:
            raise RuntimeError('pygame draw failed')

    def close(self):
        self.closed = True


class HeartbeatMotor(DryRunMotor):
    def __init__(self):
        super().__init__()
        self.heartbeat_count = 0

    def heartbeat(self):
        self.heartbeat_count += 1
        return True


def frame(width=320):
    image = np.full((240, width, 3), 120, dtype=np.uint8)
    if width == 640:
        image[:, 320:] = 0
    return image


class RemoteControlSafetyTest(unittest.TestCase):
    def test_default_parser_never_enables_hardware_and_caps_speed(self):
        args = build_argument_parser().parse_args([])
        self.assertFalse(args.drive)
        self.assertEqual(20, args.speed)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build_argument_parser().parse_args(['--speed', '38'])

    def test_drive_requires_saved_calibration_but_dry_run_does_not(self):
        with patch('jd_remote_control.load_center_angle', return_value=90) as loader:
            load_runtime_center_angle(False)
            loader.assert_called_once_with(require_saved=False)
        with patch('jd_remote_control.load_center_angle', return_value=91) as loader:
            load_runtime_center_angle(True)
            loader.assert_called_once_with(require_saved=True)

    def test_session_directories_are_unique_and_existing_data_survives(self):
        fixed_now = lambda: datetime(2026, 8, 7, 12, 0, 0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / 'existing_training.png'
            existing.write_bytes(b'keep me')
            first = create_session_directory(root, now_fn=fixed_now)
            second = create_session_directory(root, now_fn=fixed_now)

            self.assertNotEqual(first, second)
            self.assertEqual(b'keep me', existing.read_bytes())
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())

    def test_camera_failure_never_applies_start_and_stops_immediately(self):
        capture = FakeCapture([(False, None)])
        motor = DryRunMotor()
        servo = DryRunServo()
        ui = FakeUi([ManualCommand(start=True, left=True)])

        summary = run_remote_control(
            capture,
            motor,
            servo,
            ui,
            '.',
            speed=20,
            center_angle=95,
            preview=False,
            camera_error_limit=1,
            sleep_fn=lambda _seconds: None,
        )

        self.assertEqual(0, summary['motor_start_events'])
        self.assertFalse(motor.is_moving)
        self.assertEqual([], servo.angles)
        self.assertTrue(capture.released)
        self.assertTrue(servo.closed)
        self.assertTrue(ui.closed)

    def test_steering_uses_current_normalized_frame_and_heartbeat(self):
        capture = FakeCapture(
            [
                (True, frame(width=640)),
                (True, frame()),
            ]
        )
        motor = HeartbeatMotor()
        servo = DryRunServo()
        ui = FakeUi(
            [
                ManualCommand(start=True, left=True),
                ManualCommand(quit=True),
            ]
        )
        writes = []

        def writer(path, image):
            writes.append((path, image.shape))
            return True

        summary = run_remote_control(
            capture,
            motor,
            servo,
            ui,
            'session',
            speed=20,
            center_angle=95,
            preview=False,
            image_writer=writer,
        )

        self.assertTrue(summary['complete'])
        self.assertEqual(1, summary['saved_frames'])
        self.assertEqual((240, 320, 3), writes[0][1])
        self.assertTrue(writes[0][0].endswith('_085.png'))
        self.assertEqual([90.0], servo.angles)
        self.assertEqual(1, motor.heartbeat_count)
        self.assertEqual(1, motor.start_count)
        self.assertEqual(1, motor.stop_count)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)
        self.assertTrue(ui.closed)

    def test_held_direction_key_moves_and_saves_on_every_frame(self):
        frame_count = 10
        capture = FakeCapture([(True, frame()) for _ in range(frame_count)])
        motor = DryRunMotor()
        servo = DryRunServo()
        ui = FakeUi(
            [ManualCommand(left=True) for _ in range(frame_count)]
            + [ManualCommand(quit=True)]
        )
        writes = []

        summary = run_remote_control(
            capture,
            motor,
            servo,
            ui,
            'session',
            speed=20,
            center_angle=90,
            preview=False,
            image_writer=lambda path, _image: writes.append(path) or True,
        )

        self.assertEqual(frame_count, summary['saved_frames'])
        self.assertEqual(45.0, summary['steering_angle_at_exit'])
        self.assertEqual(frame_count, len(servo.angles))
        self.assertEqual(45.0, servo.angles[-1])
        self.assertTrue(writes[-1].endswith('_045.png'))

    def test_loop_exception_stops_and_releases_everything(self):
        capture = FakeCapture([(True, frame()), (True, frame())])
        motor = DryRunMotor()
        servo = DryRunServo()
        ui = FakeUi(
            [ManualCommand(start=True), ManualCommand()],
            fail_draw_at=2,
        )

        with self.assertRaisesRegex(RuntimeError, 'pygame draw failed'):
            run_remote_control(
                capture,
                motor,
                servo,
                ui,
                '.',
                speed=20,
                center_angle=95,
                preview=False,
            )

        self.assertEqual(1, motor.start_count)
        self.assertEqual(1, motor.stop_count)
        self.assertFalse(motor.is_moving)
        self.assertTrue(capture.released)
        self.assertTrue(servo.closed)
        self.assertTrue(ui.closed)


if __name__ == '__main__':
    unittest.main()
