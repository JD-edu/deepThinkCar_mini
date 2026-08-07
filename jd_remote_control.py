"""Fail-safe pygame manual control and steering-data capture.

Hardware output is disabled unless ``--drive`` is explicitly supplied.  Each
run writes labeled frames to a new session directory and never deletes prior
recordings.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
import time

import cv2

from jd_camera_compat import ensure_libcamerify
from jd_drive_runtime import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    create_actuators,
    read_frame,
    safe_servo_angle,
    shutdown_runtime,
    speed_percentage,
)
from jd_servo_config import load_center_angle


DEFAULT_SPEED = 20
MAX_REMOTE_SPEED = 37
STEERING_STEP_DEGREES = 5.0
MIN_STEERING_ANGLE = 45.0
MAX_STEERING_ANGLE = 135.0


def remote_speed_percentage(value):
    """Parse a PWM percentage while enforcing the manual-driving cap."""
    value = speed_percentage(value)
    if value > MAX_REMOTE_SPEED:
        raise argparse.ArgumentTypeError(
            'manual-control speed must be between 1 and %d percent'
            % MAX_REMOTE_SPEED
        )
    return value


def create_session_directory(output_root, now_fn=datetime.now):
    """Create a new recording directory without touching previous data."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = now_fn().strftime('%Y%m%d_%H%M%S_%f')
    base_name = 'remote_control_' + timestamp
    for suffix in range(1000):
        name = base_name if suffix == 0 else '%s_%03d' % (base_name, suffix)
        session_directory = output_root / name
        try:
            session_directory.mkdir()
        except FileExistsError:
            continue
        return session_directory
    raise RuntimeError('could not create a unique remote-control session directory')


@dataclass(frozen=True)
class ManualCommand:
    quit: bool = False
    start: bool = False
    stop: bool = False
    left: bool = False
    right: bool = False


class PygameRemoteUi:
    """Small pygame adapter kept out of module-import and test paths."""

    def __init__(self, *, drive_enabled, speed, session_directory):
        import pygame

        self.pygame = pygame
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((720, 480))
            pygame.display.set_caption('deepThinkCar manual control')
            self.font = pygame.font.SysFont('arial', 26)
        except BaseException:
            pygame.quit()
            raise
        self.drive_enabled = bool(drive_enabled)
        self.speed = int(speed)
        self.session_name = Path(session_directory).name

    def poll(self):
        pygame = self.pygame
        quit_requested = any(
            event.type == pygame.QUIT for event in pygame.event.get()
        )
        keys = pygame.key.get_pressed()
        return ManualCommand(
            quit=quit_requested or bool(keys[pygame.K_q]),
            start=bool(keys[pygame.K_s]),
            stop=bool(keys[pygame.K_SPACE]),
            left=bool(keys[pygame.K_LEFT]),
            right=bool(keys[pygame.K_RIGHT]),
        )

    def draw(self, *, action, steering_angle, driving, saved_frames):
        mode = 'DRIVE' if self.drive_enabled else 'DRY-RUN'
        lines = (
            'Remote Control deepThinkCar (%s, speed %d%%)' % (mode, self.speed),
            's: start | SPACE: stop | q/window close: exit',
            'LEFT/RIGHT: steer continuously and save the current frame',
            'session: %s' % self.session_name,
            'state: %s | steering: %.0f | saved: %d' % (
                'moving' if driving else 'stopped',
                steering_angle,
                saved_frames,
            ),
            'last action: %s' % action,
        )
        self.screen.fill((0, 0, 0))
        for index, line in enumerate(lines):
            rendered = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(rendered, (30, 35 + index * 60))
        self.pygame.display.update()

    def close(self):
        self.pygame.quit()


def run_remote_control(
    capture,
    motor,
    servo,
    ui,
    session_directory,
    *,
    speed,
    center_angle,
    preview,
    camera_error_limit=30,
    max_frames=None,
    image_writer=cv2.imwrite,
    sleep_fn=time.sleep,
):
    """Run the manual loop with injected interfaces for hardware-free tests."""
    speed = int(speed)
    if not 1 <= speed <= MAX_REMOTE_SPEED:
        raise ValueError(
            'manual-control speed must be between 1 and %d percent'
            % MAX_REMOTE_SPEED
        )
    if camera_error_limit < 1:
        raise ValueError('camera_error_limit must be positive')
    if max_frames is not None and max_frames < 1:
        raise ValueError('max_frames must be positive')

    session_directory = Path(session_directory)
    steering_angle = 90.0
    servo_offset = float(center_angle) - 90.0
    valid_frames = 0
    camera_errors = 0
    saved_frames = 0
    motor_start_events = 0
    motor_stop_events = 0
    driving = False
    completed = False
    watchdog_timed_out = False
    cleanup_errors = []
    action = 'ready'

    try:
        while max_frames is None or valid_frames < max_frames:
            if getattr(motor, 'timed_out', False):
                watchdog_timed_out = True
                driving = False
                break

            command = ui.poll()
            if command.quit:
                action = 'quit'
                completed = True
                break

            # A command is never applied to an old or uninitialized frame.
            # jd_drive_runtime.read_frame also normalizes camera geometry.
            ok, frame = read_frame(capture)
            if not ok:
                camera_errors += 1
                action = 'camera error: stopped'
                motor.motor_stop()
                if driving:
                    motor_stop_events += 1
                driving = False
                ui.draw(
                    action=action,
                    steering_angle=steering_angle,
                    driving=driving,
                    saved_frames=saved_frames,
                )
                if camera_errors >= camera_error_limit:
                    break
                sleep_fn(0.05)
                continue

            camera_errors = 0
            valid_frames += 1
            steering_changed = False
            if command.left and not command.right:
                steering_angle = max(
                    MIN_STEERING_ANGLE,
                    steering_angle - STEERING_STEP_DEGREES,
                )
                steering_changed = True
                action = 'left'
            elif command.right and not command.left:
                steering_angle = min(
                    MAX_STEERING_ANGLE,
                    steering_angle + STEERING_STEP_DEGREES,
                )
                steering_changed = True
                action = 'right'

            servo.set_angle(safe_servo_angle(steering_angle, servo_offset))
            if steering_changed:
                image_path = session_directory / (
                    'RC_%06d_%03d.png'
                    % (saved_frames, int(round(steering_angle)))
                )
                if not image_writer(str(image_path), frame):
                    raise RuntimeError('failed to save steering frame: %s' % image_path)
                saved_frames += 1

            # Stop wins if start and stop are pressed together.  A start is
            # accepted only after a valid, normalized camera frame exists.
            if command.stop:
                action = 'stop'
                motor.motor_stop()
                if driving:
                    motor_stop_events += 1
                driving = False
            elif command.start and not driving:
                action = 'start'
                motor.motor_move_forward(speed)
                motor_start_events += 1
                driving = True

            heartbeat = getattr(motor, 'heartbeat', None)
            if driving and heartbeat is not None and not heartbeat():
                watchdog_timed_out = True
                driving = False
                break

            if preview:
                cv2.imshow('deepThinkCar camera', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    action = 'camera window quit'
                    completed = True
                    break

            ui.draw(
                action=action,
                steering_angle=steering_angle,
                driving=driving,
                saved_frames=saved_frames,
            )
        else:
            completed = True
    finally:
        if driving or getattr(motor, 'timed_out', False):
            motor_stop_events += 1
        cleanup_errors = shutdown_runtime(
            motor,
            servo,
            capture,
            preview=preview,
        )
        try:
            ui.close()
        except Exception as error:
            cleanup_errors.append('pygame cleanup failed: %s' % error)

    return {
        'complete': completed,
        'drive_enabled': not motor.__class__.__name__.startswith('DryRun'),
        'session_directory': str(session_directory),
        'speed_percent': speed,
        'valid_frames': valid_frames,
        'camera_errors_at_exit': camera_errors,
        'saved_frames': saved_frames,
        'steering_angle_at_exit': steering_angle,
        'motor_start_events': motor_start_events,
        'motor_stop_events': motor_stop_events,
        'watchdog_timed_out': watchdog_timed_out,
        'cleanup_errors': cleanup_errors,
    }


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description='Manual pygame steering and per-session data capture.'
    )
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument(
        '--drive',
        action='store_true',
        help='explicitly enable real motor and servo output',
    )
    parser.add_argument('--speed', type=remote_speed_percentage, default=DEFAULT_SPEED)
    parser.add_argument('--output-root', type=Path, default=Path('data'))
    parser.add_argument('--max-frames', type=int)
    parser.add_argument('--camera-error-limit', type=int, default=30)
    parser.add_argument('--watchdog-timeout', type=float, default=1.0)
    parser.add_argument('--no-preview', action='store_true')
    return parser


def load_runtime_center_angle(drive_enabled):
    return load_center_angle(require_saved=bool(drive_enabled))


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.max_frames is not None and args.max_frames < 1:
        parser.error('--max-frames must be positive')
    if args.camera_error_limit < 1:
        parser.error('--camera-error-limit must be positive')
    if not 0.2 <= args.watchdog_timeout <= 5.0:
        parser.error('--watchdog-timeout must be between 0.2 and 5.0 seconds')

    center_angle = load_runtime_center_angle(args.drive)
    ensure_libcamerify(
        __file__,
        sys.argv[1:] if argv is None else argv,
    )
    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        capture.release()
        raise SystemExit('could not open camera source: %s' % args.camera)
    ui = None
    motor = None
    servo = None
    runtime_owns_cleanup = False
    try:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(2)
        session_directory = create_session_directory(args.output_root)
        ui = PygameRemoteUi(
            drive_enabled=args.drive,
            speed=args.speed,
            session_directory=session_directory,
        )
        # create_actuators imports GPIO/ServoKit only when args.drive is true.
        motor, servo = create_actuators(
            args.drive,
            center_angle,
            watchdog_timeout_seconds=args.watchdog_timeout,
        )
        runtime_owns_cleanup = True
        summary = run_remote_control(
            capture,
            motor,
            servo,
            ui,
            session_directory,
            speed=args.speed,
            center_angle=center_angle,
            preview=not args.no_preview,
            camera_error_limit=args.camera_error_limit,
            max_frames=args.max_frames,
        )
    except BaseException:
        if not runtime_owns_cleanup:
            if motor is not None and servo is not None:
                shutdown_runtime(motor, servo, capture, preview=not args.no_preview)
            else:
                capture.release()
                if not args.no_preview:
                    cv2.destroyAllWindows()
            if ui is not None:
                try:
                    ui.close()
                except Exception:
                    pass
        raise

    summary['drive_enabled'] = args.drive
    summary['watchdog_timeout_seconds'] = (
        args.watchdog_timeout if args.drive else None
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if (
        not summary['complete']
        or summary['watchdog_timed_out']
        or bool(summary['cleanup_errors'])
        or summary['valid_frames'] == 0
    ):
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
