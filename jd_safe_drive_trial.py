"""Two-stage, low-speed first-drive launcher for deepThinkCar-mini."""

import argparse
import json
import sys
import time

from jd_3_lane_follower_opencv import run_opencv_session
from jd_camera_compat import ensure_libcamerify
from jd_drive_runtime import speed_percentage
from jd_servo_config import load_center_angle


MAX_TRIAL_SPEED = 20
MAX_DRIVE_FRAMES = 200
MAX_DRIVE_SECONDS = 10.0
DEFAULT_PREFLIGHT_FRAMES = 120
MIN_PREFLIGHT_FRAMES = 60
DEFAULT_MIN_LANE_RATE = 0.60
WATCHDOG_TIMEOUT_SECONDS = 1.0


def positive_integer(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError('value must be positive')
    return value


def lane_rate(value):
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError('lane rate must be between 0 and 1')
    return value


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            'Run a motor-disabled lane preflight before a short, low-speed '
            'hardware trial.'
        )
    )
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--drive', action='store_true')
    parser.add_argument('--speed', type=speed_percentage, default=MAX_TRIAL_SPEED)
    parser.add_argument(
        '--preflight-frames',
        type=positive_integer,
        default=DEFAULT_PREFLIGHT_FRAMES,
    )
    parser.add_argument(
        '--drive-frames',
        type=positive_integer,
        default=MAX_DRIVE_FRAMES,
    )
    parser.add_argument(
        '--min-lane-rate',
        type=lane_rate,
        default=DEFAULT_MIN_LANE_RATE,
    )
    parser.add_argument('--headless', action='store_true')
    return parser


def safety_failures(
    summary,
    *,
    expected_frames,
    minimum_lane_rate,
    expected_drive_enabled,
):
    failures = []
    if summary.get('drive_enabled') is not expected_drive_enabled:
        failures.append('unexpected drive-enabled state')
    if not summary.get('complete', False):
        failures.append('run did not reach its frame limit')
    if summary.get('valid_frames', 0) < expected_frames:
        failures.append(
            'only %d/%d valid frames were processed'
            % (summary.get('valid_frames', 0), expected_frames)
        )
    measured_lane_rate = float(summary.get('lane_rate', 0.0))
    if measured_lane_rate < minimum_lane_rate:
        failures.append(
            'lane rate %.1f%% is below the %.1f%% gate'
            % (measured_lane_rate * 100.0, minimum_lane_rate * 100.0)
        )
    if summary.get('steering_count', 0) == 0:
        failures.append('no valid steering command was produced')
    if summary.get('motor_start_events', 0) == 0:
        failures.append('the ready-lane gate was never reached')
    if summary.get('camera_errors_at_exit', 0):
        failures.append('camera errors were present at exit')
    if summary.get('watchdog_timed_out', False):
        failures.append('the motor watchdog timed out')
    if summary.get('time_limit_reached', False):
        failures.append('the hard wall-clock time limit was reached')
    if summary.get('cleanup_errors'):
        failures.append('shutdown cleanup reported errors')
    return failures


def print_summary(label, summary, print_fn=print):
    print_fn('\n%s' % label)
    print_fn(json.dumps(summary, indent=2, sort_keys=True))


def run_trial(
    args,
    *,
    session_runner=run_opencv_session,
    calibration_loader=load_center_angle,
    input_fn=input,
    sleep_fn=time.sleep,
    print_fn=print,
):
    if args.drive:
        # Fail before opening the camera or touching any actuator.
        calibration_loader(require_saved=True)

    print_fn(
        'PRE-FLIGHT: motors and steering output are disabled; '
        'checking camera and black-tape lanes.'
    )
    preflight = session_runner(
        camera=args.camera,
        drive=False,
        speed=args.speed,
        headless=args.headless,
        max_frames=args.preflight_frames,
        max_seconds=None,
        warmup_frames=30,
        watchdog_timeout=WATCHDOG_TIMEOUT_SECONDS,
    )
    print_summary('Pre-flight summary', preflight, print_fn)
    failures = safety_failures(
        preflight,
        expected_frames=args.preflight_frames,
        minimum_lane_rate=args.min_lane_rate,
        expected_drive_enabled=False,
    )
    if failures:
        print_fn('\nBLOCKED: hardware drive was not attempted.')
        for failure in failures:
            print_fn('- %s' % failure)
        return 2

    if not args.drive:
        print_fn(
            '\nPASS: camera-only pre-flight succeeded. '
            'Run again with --drive for the guarded hardware trial.'
        )
        return 0

    print_fn(
        '\nBefore enabling the motor: use an empty, flat, isolated track; '
        'remove people and obstacles; keep the power switch within reach.'
    )
    try:
        confirmation = input_fn(
            "Type DRIVE to run at %d%% PWM for at most %d frames or %.0f seconds: "
            % (args.speed, args.drive_frames, MAX_DRIVE_SECONDS)
        )
    except EOFError:
        print_fn('CANCELLED: interactive confirmation was unavailable.')
        return 3
    if confirmation.strip() != 'DRIVE':
        print_fn('CANCELLED: motor output stayed disabled.')
        return 3

    for seconds in (3, 2, 1):
        print_fn('Motor trial starts in %d...' % seconds)
        sleep_fn(1)

    drive_summary = session_runner(
        camera=args.camera,
        drive=True,
        speed=args.speed,
        headless=args.headless,
        max_frames=args.drive_frames,
        max_seconds=MAX_DRIVE_SECONDS,
        warmup_frames=30,
        watchdog_timeout=WATCHDOG_TIMEOUT_SECONDS,
    )
    print_summary('Hardware trial summary', drive_summary, print_fn)
    failures = safety_failures(
        drive_summary,
        expected_frames=args.drive_frames,
        minimum_lane_rate=args.min_lane_rate,
        expected_drive_enabled=True,
    )
    if failures:
        print_fn('\nSTOPPED/FAILED: do not increase speed.')
        for failure in failures:
            print_fn('- %s' % failure)
        return 2

    print_fn('\nPASS: the bounded low-speed trial completed successfully.')
    return 0


def main(
    argv=None,
    *,
    session_runner=run_opencv_session,
    calibration_loader=load_center_angle,
    camera_compat=ensure_libcamerify,
    input_fn=input,
    sleep_fn=time.sleep,
    print_fn=print,
):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.speed > MAX_TRIAL_SPEED:
        parser.error(
            '--speed cannot exceed %d in the first-drive trial'
            % MAX_TRIAL_SPEED
        )
    if args.preflight_frames < MIN_PREFLIGHT_FRAMES:
        parser.error(
            '--preflight-frames must be at least %d' % MIN_PREFLIGHT_FRAMES
        )
    if args.drive_frames > MAX_DRIVE_FRAMES:
        parser.error(
            '--drive-frames cannot exceed %d in the first-drive trial'
            % MAX_DRIVE_FRAMES
        )
    if args.min_lane_rate < DEFAULT_MIN_LANE_RATE:
        parser.error(
            '--min-lane-rate cannot be below %.2f in the first-drive trial'
            % DEFAULT_MIN_LANE_RATE
        )

    camera_compat(__file__, sys.argv[1:] if argv is None else argv)
    try:
        return run_trial(
            args,
            session_runner=session_runner,
            calibration_loader=calibration_loader,
            input_fn=input_fn,
            sleep_fn=sleep_fn,
            print_fn=print_fn,
        )
    except KeyboardInterrupt:
        print_fn('\nSTOPPED: interrupted by operator.')
        return 130
    except (ImportError, OSError, RuntimeError) as error:
        print_fn('\nBLOCKED: %s' % error)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
