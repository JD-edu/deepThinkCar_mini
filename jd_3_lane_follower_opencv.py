"""OpenCV black-tape lane following without recording or deep learning."""

import argparse
import json
from pathlib import Path
import statistics
import sys
import time

import cv2

from jd_camera_compat import ensure_libcamerify
from jd_drive_runtime import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    create_actuators,
    frame_quality,
    read_frame,
    safe_servo_angle,
    shutdown_runtime,
    speed_percentage,
)
from jd_opencv_lane_detect import JdOpencvLaneDetect
from jd_servo_config import load_center_angle


def run_opencv_lane_follower(
    capture,
    lane_detector,
    motor,
    servo,
    *,
    speed,
    servo_offset,
    is_video,
    preview,
    warmup_frames=30,
    ready_lane_frames=5,
    lost_lane_limit=3,
    camera_error_limit=30,
    max_frames=None,
    max_seconds=None,
    recording_writer=None,
    required_lane_count=1,
    monotonic_fn=time.monotonic,
):
    if max_seconds is not None and max_seconds <= 0:
        raise ValueError('max_seconds must be positive')
    if required_lane_count not in (1, 2):
        raise ValueError('required_lane_count must be 1 or 2')

    valid_frames = 0
    lane_frames = 0
    no_lane_frames = 0
    partial_lane_frames = 0
    rejected_quality_frames = 0
    camera_errors = 0
    consecutive_ready = 0
    consecutive_lost = 0
    moving = False
    motor_start_events = 0
    motor_stop_events = 0
    recorded_frames = 0
    steering_angles = []
    completed = False
    time_limit_reached = False
    watchdog_timed_out = False
    cleanup_errors = []
    started_at = monotonic_fn()

    try:
        while max_frames is None or valid_frames < max_frames:
            if (
                max_seconds is not None
                and monotonic_fn() - started_at >= max_seconds
            ):
                time_limit_reached = True
                completed = True
                break
            ok, frame = read_frame(capture)
            if getattr(motor, 'timed_out', False):
                watchdog_timed_out = True
                moving = False
                break
            if not ok:
                if is_video:
                    completed = True
                    break
                camera_errors += 1
                consecutive_ready = 0
                if moving:
                    motor.motor_stop()
                    moving = False
                    motor_stop_events += 1
                if camera_errors >= camera_error_limit:
                    break
                time.sleep(0.05)
                continue

            camera_errors = 0
            valid_frames += 1
            if recording_writer is not None:
                recording_writer.write(frame)
                recorded_frames += 1
            usable, _brightness, _contrast = frame_quality(frame)
            lanes = []
            lane_frame = frame
            if usable:
                lanes, lane_frame = lane_detector.get_lane(frame)
            else:
                rejected_quality_frames += 1
                if moving:
                    motor.motor_stop()
                    moving = False
                    motor_stop_events += 1

            lane_count = 0 if lanes is None else len(lanes)
            lane_visible = lane_count >= required_lane_count
            if not lane_visible:
                no_lane_frames += 1
                if 0 < lane_count < required_lane_count:
                    partial_lane_frames += 1
                consecutive_ready = 0
                consecutive_lost += 1
                if moving and consecutive_lost >= lost_lane_limit:
                    motor.motor_stop()
                    moving = False
                    motor_stop_events += 1
                preview_frame = lane_frame
            else:
                lane_frames += 1
                consecutive_ready += 1
                consecutive_lost = 0
                steering_angle, preview_frame = lane_detector.get_steering_angle(
                    lane_frame,
                    lanes,
                )
                servo.set_angle(safe_servo_angle(steering_angle, servo_offset))
                steering_angles.append(float(steering_angle))
                if (
                    not moving
                    and valid_frames >= warmup_frames
                    and consecutive_ready >= ready_lane_frames
                ):
                    motor.motor_move_forward(speed)
                    moving = True
                    motor_start_events += 1

            if preview:
                cv2.imshow('OpenCV black-tape lane follower', preview_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            heartbeat = getattr(motor, 'heartbeat', None)
            if moving and heartbeat is not None and not heartbeat():
                watchdog_timed_out = True
                moving = False
                break
        else:
            completed = True
    finally:
        watchdog_timed_out = watchdog_timed_out or getattr(
            motor,
            'timed_out',
            False,
        )
        if moving or watchdog_timed_out:
            motor_stop_events += 1
        cleanup_errors = shutdown_runtime(
            motor,
            servo,
            capture,
            preview=preview,
        )
        if recording_writer is not None:
            try:
                recording_writer.release()
            except Exception as error:
                cleanup_errors.append('recording release failed: %s' % error)

    return {
        'complete': completed,
        'time_limit_reached': time_limit_reached,
        'valid_frames': valid_frames,
        'lane_frames': lane_frames,
        'no_lane_frames': no_lane_frames,
        'partial_lane_frames': partial_lane_frames,
        'required_lane_count': required_lane_count,
        'rejected_quality_frames': rejected_quality_frames,
        'lane_rate': lane_frames / valid_frames if valid_frames else 0.0,
        'camera_errors_at_exit': camera_errors,
        'steering_count': len(steering_angles),
        'steering_min': min(steering_angles) if steering_angles else None,
        'steering_max': max(steering_angles) if steering_angles else None,
        'steering_mean': (
            statistics.fmean(steering_angles) if steering_angles else None
        ),
        'motor_start_events': motor_start_events,
        'motor_stop_events': motor_stop_events,
        'watchdog_timed_out': watchdog_timed_out,
        'cleanup_errors': cleanup_errors,
        'speed_percent': speed,
        'recorded_frames': recorded_frames,
    }


def build_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video')
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--drive', action='store_true')
    parser.add_argument('--speed', type=speed_percentage, default=20)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--max-frames', type=int)
    parser.add_argument('--max-seconds', type=float)
    parser.add_argument(
        '--require-two-lanes',
        action='store_true',
        help='do not steer or drive unless both tape boundaries are visible',
    )
    parser.add_argument('--lost-lane-limit', type=int, default=3)
    parser.add_argument(
        '--record-video',
        type=Path,
        help='save every normalized camera frame to a new AVI file',
    )
    parser.add_argument('--warmup-frames', type=int, default=30)
    parser.add_argument('--watchdog-timeout', type=float, default=1.0)
    return parser


def run_opencv_session(
    *,
    video=None,
    camera=0,
    drive=False,
    speed=20,
    headless=False,
    max_frames=None,
    max_seconds=None,
    record_video=None,
    require_two_lanes=False,
    lost_lane_limit=3,
    warmup_frames=30,
    watchdog_timeout=1.0,
):
    """Open one source, run the follower, and return its safety summary."""
    source = camera if video is None else video
    center_angle = load_center_angle(require_saved=drive)
    lane_detector = JdOpencvLaneDetect()
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError('could not open camera/video source: %s' % source)
    if video is None:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(2)

    recording_writer = None
    if record_video is not None:
        record_video = Path(record_video)
        if record_video.exists():
            capture.release()
            raise RuntimeError('recording already exists: %s' % record_video)
        record_video.parent.mkdir(parents=True, exist_ok=True)
        recording_writer = cv2.VideoWriter(
            str(record_video),
            cv2.VideoWriter_fourcc(*'XVID'),
            20.0,
            (CAMERA_WIDTH, CAMERA_HEIGHT),
        )
        if not recording_writer.isOpened():
            recording_writer.release()
            capture.release()
            raise RuntimeError('could not create recording: %s' % record_video)

    try:
        motor, servo = create_actuators(
            drive,
            center_angle,
            watchdog_timeout_seconds=watchdog_timeout,
        )
    except Exception:
        if recording_writer is not None:
            recording_writer.release()
        capture.release()
        raise

    summary = run_opencv_lane_follower(
        capture,
        lane_detector,
        motor,
        servo,
        speed=speed,
        servo_offset=center_angle - 90.0,
        is_video=video is not None,
        preview=not headless,
        warmup_frames=warmup_frames,
        max_frames=max_frames,
        max_seconds=max_seconds,
        recording_writer=recording_writer,
        required_lane_count=2 if require_two_lanes else 1,
        lost_lane_limit=lost_lane_limit,
    )
    summary['drive_enabled'] = drive
    summary['source'] = str(source)
    summary['watchdog_timeout_seconds'] = watchdog_timeout if drive else None
    summary['recording'] = None if record_video is None else str(record_video)
    summary['require_two_lanes'] = require_two_lanes
    return summary


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.drive and args.video is not None:
        parser.error('--drive cannot be combined with --video')
    if args.video is not None and args.record_video is not None:
        parser.error('--record-video is only available with a live camera')
    if args.drive and args.max_frames is None and args.max_seconds is None:
        parser.error('--drive requires --max-frames or --max-seconds')
    if args.max_frames is not None and args.max_frames < 1:
        parser.error('--max-frames must be positive')
    if args.max_seconds is not None and args.max_seconds <= 0:
        parser.error('--max-seconds must be positive')
    if not 1 <= args.lost_lane_limit <= 30:
        parser.error('--lost-lane-limit must be from 1 to 30')
    if not 0.2 <= args.watchdog_timeout <= 5.0:
        parser.error('--watchdog-timeout must be between 0.2 and 5.0 seconds')
    if args.video is None:
        ensure_libcamerify(__file__, sys.argv[1:] if argv is None else argv)

    try:
        summary = run_opencv_session(
            video=args.video,
            camera=args.camera,
            drive=args.drive,
            speed=args.speed,
            headless=args.headless,
            max_frames=args.max_frames,
            max_seconds=args.max_seconds,
            record_video=args.record_video,
            require_two_lanes=args.require_two_lanes,
            lost_lane_limit=args.lost_lane_limit,
            warmup_frames=args.warmup_frames,
            watchdog_timeout=args.watchdog_timeout,
        )
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    print(json.dumps(summary, indent=2, sort_keys=True))
    if (
        not summary['complete']
        or summary['watchdog_timed_out']
        or bool(summary['cleanup_errors'])
        or summary['valid_frames'] == 0
        or summary['steering_count'] == 0
    ):
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
