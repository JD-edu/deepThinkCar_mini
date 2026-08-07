import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import jd_drive_runtime  # Load NumPy once before temporary sys.modules patches.


class FakeCamera:
    def __init__(self, frames=None):
        self.released = False
        self.frames = list(frames or [])
        self.read_count = 0

    def set(self, *_args):
        return True

    def read(self):
        self.read_count += 1
        if self.frames:
            return self.frames.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeServoChannel:
    angle = None


class FakeFrame:
    shape = (240, 320, 3)
    ndim = 3


class FakeVideoWriter:
    def __init__(self, *args):
        self.args = args
        self.frames = []
        self.released = False

    def isOpened(self):
        return True

    def write(self, frame):
        self.frames.append(frame)

    def release(self):
        self.released = True


class FakeServoKit:
    def __init__(self, channels):
        self.servo = [FakeServoChannel() for _ in range(channels)]


class FakeMotor:
    instance = None

    def __init__(self):
        self.move_speeds = []
        self.stop_count = 0
        FakeMotor.instance = self

    def motor_move_forward(self, speed):
        self.move_speeds.append(speed)

    def motor_stop(self):
        self.stop_count += 1


class LaneRunnerSafetyTest(unittest.TestCase):
    def run_lane_script(
        self,
        camera,
        argv,
        monotonic_values,
        lane_visibility=None,
    ):
        FakeMotor.instance = None
        lane_visibility = list(lane_visibility or [])

        cv2_module = types.ModuleType('cv2')
        cv2_module.VideoCapture = lambda _index: camera
        cv2_module.VideoWriter_fourcc = lambda *_codec: 0
        cv2_module.VideoWriter = FakeVideoWriter
        cv2_module.destroyAllWindows = lambda: None
        cv2_module.imshow = lambda *_args: None
        cv2_module.waitKey = lambda _delay: 0

        servo_module = types.ModuleType('adafruit_servokit')
        servo_module.ServoKit = FakeServoKit

        lane_module = types.ModuleType('jd_opencv_lane_detect')
        class FakeDetector:
            def get_lane(self, frame):
                visible = lane_visibility.pop(0) if lane_visibility else False
                return (['lane'] if visible else []), frame

            def get_steering_angle(self, frame, lanes):
                return (90, frame) if lanes else (0, None)

        lane_module.JdOpencvLaneDetect = FakeDetector

        motor_module = types.ModuleType('jd_car_motor_l9110')
        motor_module.JdCarMotorL9110 = FakeMotor

        fake_modules = {
            'cv2': cv2_module,
            'adafruit_servokit': servo_module,
            'jd_opencv_lane_detect': lane_module,
            'jd_car_motor_l9110': motor_module,
        }
        script = PROJECT_ROOT / 'jd_1_record_lane_video.py'

        raised = None
        try:
            with patch.dict(sys.modules, fake_modules):
                with patch.dict(
                    os.environ,
                    {'DEEPTHINKCAR_LIBCAMERIFY_ACTIVE': '1'},
                    clear=False,
                ):
                    with patch.object(sys, 'argv', [str(script), *argv]):
                        with patch(
                            'jd_servo_config.load_center_angle',
                            return_value=90.0,
                        ):
                            with patch('time.sleep', return_value=None):
                                with patch(
                                    'time.monotonic',
                                    side_effect=monotonic_values,
                                ):
                                    runpy.run_path(
                                        str(script),
                                        run_name='__main__',
                                    )
        except SystemExit as error:
            raised = error

        return raised

    def test_zero_camera_frames_never_start_motor(self):
        camera = FakeCamera()
        raised = self.run_lane_script(camera, [], [0.0, 0.0, 11.0])

        self.assertIsNotNone(raised)
        self.assertIn('camera returned no frames', str(raised))
        self.assertEqual([], FakeMotor.instance.move_speeds)
        self.assertGreaterEqual(FakeMotor.instance.stop_count, 1)
        self.assertTrue(camera.released)

    def test_camera_check_waits_through_early_read_failures(self):
        delayed_frames = [(False, None)] * 80
        delayed_frames += [(True, FakeFrame())] * 30
        camera = FakeCamera(delayed_frames)
        raised = self.run_lane_script(
            camera,
            ['--camera-check'],
            [0.0] * 200,
        )

        self.assertIsNotNone(raised)
        self.assertEqual(0, raised.code)
        self.assertEqual(110, camera.read_count)
        self.assertEqual([], FakeMotor.instance.move_speeds)
        self.assertTrue(camera.released)

    def test_one_early_lane_frame_followed_by_misses_never_starts_motor(self):
        camera = FakeCamera([(True, FakeFrame())] * 30)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'new-recording.avi'
            raised = self.run_lane_script(
                camera,
                ['--output', str(output)],
                [0.0] * 200,
                lane_visibility=[True] + [False] * 29,
            )

        self.assertIsNone(raised)
        self.assertEqual([], FakeMotor.instance.move_speeds)
        self.assertGreaterEqual(FakeMotor.instance.stop_count, 1)
        self.assertTrue(camera.released)

    def test_existing_output_is_preserved_and_hardware_is_not_initialized(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'existing.avi'
            original = b'keep this recording'
            output.write_bytes(original)

            raised = self.run_lane_script(
                FakeCamera(),
                ['--output', str(output)],
                [0.0],
            )

            self.assertIsNotNone(raised)
            self.assertEqual(2, raised.code)
            self.assertEqual(original, output.read_bytes())
            self.assertIsNone(FakeMotor.instance)

    def test_one_reacquired_lane_frame_does_not_restart_motor(self):
        warmup = [True] * 30
        lose_lane_and_stop = [False] * 15
        single_reacquired_frame = [True]
        visibility = warmup + lose_lane_and_stop + single_reacquired_frame
        camera = FakeCamera([(True, FakeFrame())] * len(visibility))

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'reacquire-recording.avi'
            raised = self.run_lane_script(
                camera,
                ['--output', str(output)],
                [0.0] * 200,
                lane_visibility=visibility,
            )

        self.assertIsNone(raised)
        self.assertEqual([37], FakeMotor.instance.move_speeds)
        self.assertGreaterEqual(FakeMotor.instance.stop_count, 2)
        self.assertTrue(camera.released)


if __name__ == '__main__':
    unittest.main()
