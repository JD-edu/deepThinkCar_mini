from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_safe_drive_trial import main, safety_failures


def healthy_summary(*, drive_enabled, frames=120, lane_rate=0.8):
    return {
        'complete': True,
        'valid_frames': frames,
        'lane_frames': int(frames * lane_rate),
        'lane_rate': lane_rate,
        'steering_count': int(frames * lane_rate),
        'motor_start_events': 1,
        'camera_errors_at_exit': 0,
        'watchdog_timed_out': False,
        'time_limit_reached': False,
        'cleanup_errors': [],
        'drive_enabled': drive_enabled,
    }


class SafeDriveTrialTest(unittest.TestCase):
    def quiet_main(self, argv, **kwargs):
        return main(
            argv,
            camera_compat=lambda *_args, **_kwargs: False,
            sleep_fn=lambda _seconds: None,
            print_fn=lambda *_args, **_kwargs: None,
            **kwargs,
        )

    def test_safety_gate_accepts_a_healthy_preflight(self):
        self.assertEqual(
            [],
            safety_failures(
                healthy_summary(drive_enabled=False),
                expected_frames=120,
                minimum_lane_rate=0.6,
                expected_drive_enabled=False,
            ),
        )

    def test_safety_gate_rejects_low_lane_rate_and_watchdog_timeout(self):
        summary = healthy_summary(drive_enabled=False, lane_rate=0.3)
        summary['watchdog_timed_out'] = True
        failures = safety_failures(
            summary,
            expected_frames=120,
            minimum_lane_rate=0.6,
            expected_drive_enabled=False,
        )
        self.assertTrue(any('lane rate' in failure for failure in failures))
        self.assertTrue(any('watchdog' in failure for failure in failures))

    def test_camera_only_mode_never_requests_hardware(self):
        calls = []

        def session_runner(**kwargs):
            calls.append(kwargs)
            return healthy_summary(drive_enabled=False)

        result = self.quiet_main([], session_runner=session_runner)
        self.assertEqual(0, result)
        self.assertEqual(1, len(calls))
        self.assertFalse(calls[0]['drive'])

    def test_wrong_confirmation_does_not_run_hardware(self):
        calls = []

        def session_runner(**kwargs):
            calls.append(kwargs)
            return healthy_summary(drive_enabled=False)

        result = self.quiet_main(
            ['--drive'],
            session_runner=session_runner,
            calibration_loader=lambda **_kwargs: 90.0,
            input_fn=lambda _prompt: 'no',
        )
        self.assertEqual(3, result)
        self.assertEqual(1, len(calls))
        self.assertFalse(calls[0]['drive'])

    def test_missing_calibration_blocks_before_camera_preflight(self):
        calls = []

        def missing_calibration(**_kwargs):
            raise RuntimeError('saved calibration is required')

        result = self.quiet_main(
            ['--drive'],
            session_runner=lambda **kwargs: calls.append(kwargs),
            calibration_loader=missing_calibration,
            input_fn=lambda _prompt: 'DRIVE',
        )
        self.assertEqual(2, result)
        self.assertEqual([], calls)

    def test_exact_confirmation_runs_one_bounded_hardware_stage(self):
        calls = []

        def session_runner(**kwargs):
            calls.append(kwargs)
            return healthy_summary(
                drive_enabled=kwargs['drive'],
                frames=kwargs['max_frames'],
            )

        result = self.quiet_main(
            ['--drive'],
            session_runner=session_runner,
            calibration_loader=lambda **_kwargs: 90.0,
            input_fn=lambda _prompt: 'DRIVE',
        )
        self.assertEqual(0, result)
        self.assertEqual(2, len(calls))
        self.assertFalse(calls[0]['drive'])
        self.assertTrue(calls[1]['drive'])
        self.assertEqual(20, calls[1]['speed'])
        self.assertEqual(200, calls[1]['max_frames'])
        self.assertEqual(10.0, calls[1]['max_seconds'])

    def test_speed_and_duration_caps_cannot_be_overridden(self):
        with self.assertRaises(SystemExit):
            self.quiet_main(['--speed', '21'])
        with self.assertRaises(SystemExit):
            self.quiet_main(['--drive-frames', '201'])
        with self.assertRaises(SystemExit):
            self.quiet_main(['--min-lane-rate', '0.59'])


if __name__ == '__main__':
    unittest.main()
