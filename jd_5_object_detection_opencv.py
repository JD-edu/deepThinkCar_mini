"""Step 5: deep lane following plus fail-safe hazard detection."""

import argparse
from collections import Counter
from functools import partial
import json
from pathlib import Path
import statistics
import sys
import time

import cv2

from jd_camera_compat import ensure_libcamerify
from jd_deep_lane_detect import JdDeepLaneDetect
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
from jd_opencv_dnn_objectdetect_v3 import default_detection_model, detect_hazards
from jd_opencv_lane_detect import JdOpencvLaneDetect
from jd_servo_config import load_center_angle


def run_object_aware_follower(
    capture,
    deep_detector,
    lane_guard,
    hazard_detector,
    motor,
    servo,
    *,
    speed,
    servo_offset,
    is_video,
    preview,
    warmup_frames=30,
    ready_lane_frames=5,
    clear_frames_to_resume=5,
    lost_lane_limit=3,
    camera_error_limit=30,
    max_frames=None,
):
    valid_frames = 0
    lane_frames = 0
    hazard_frames = 0
    no_lane_frames = 0
    rejected_quality_frames = 0
    camera_errors = 0
    consecutive_lane = 0
    consecutive_lost = 0
    consecutive_clear = 0
    moving = False
    motor_start_events = 0
    motor_stop_events = 0
    predictions = []
    detected_classes = Counter()
    triggered_classes = Counter()
    completed = False
    watchdog_timed_out = False
    cleanup_errors = []

    try:
        while max_frames is None or valid_frames < max_frames:
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
                consecutive_lane = 0
                consecutive_clear = 0
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
            usable, _brightness, _contrast = frame_quality(frame)
            if usable:
                should_stop, object_frame, detections = hazard_detector(frame)
            else:
                rejected_quality_frames += 1
                should_stop, object_frame, detections = True, frame, []

            for detection in detections:
                if detection.get('is_hazard_class', True):
                    detected_classes[detection['class_name']] += 1
                if detection.get('triggers_stop', False):
                    triggered_classes[detection['class_name']] += 1
            if should_stop:
                hazard_frames += 1
                consecutive_clear = 0
                if moving:
                    motor.motor_stop()
                    moving = False
                    motor_stop_events += 1
            else:
                consecutive_clear += 1

            lanes = []
            if usable:
                lanes, _lane_image = lane_guard.get_lane(frame)
            lane_visible = lanes is not None and len(lanes) > 0
            if not lane_visible:
                no_lane_frames += 1
                consecutive_lane = 0
                consecutive_lost += 1
                if moving and consecutive_lost >= lost_lane_limit:
                    motor.motor_stop()
                    moving = False
                    motor_stop_events += 1
            else:
                lane_frames += 1
                consecutive_lane += 1
                consecutive_lost = 0
                predicted_angle, _lane_preview = deep_detector.follow_lane(frame)
                servo.set_angle(safe_servo_angle(predicted_angle, servo_offset))
                predictions.append(float(predicted_angle))

            if (
                not moving
                and not should_stop
                and valid_frames >= warmup_frames
                and consecutive_lane >= ready_lane_frames
                and consecutive_clear >= clear_frames_to_resume
            ):
                motor.motor_move_forward(speed)
                moving = True
                motor_start_events += 1

            if preview:
                cv2.imshow('object-aware lane follower', object_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    completed = False
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

    return {
        'complete': completed,
        'valid_frames': valid_frames,
        'lane_frames': lane_frames,
        'no_lane_frames': no_lane_frames,
        'hazard_frames': hazard_frames,
        'rejected_quality_frames': rejected_quality_frames,
        'lane_rate': lane_frames / valid_frames if valid_frames else 0.0,
        'camera_errors_at_exit': camera_errors,
        'prediction_count': len(predictions),
        'prediction_min': min(predictions) if predictions else None,
        'prediction_max': max(predictions) if predictions else None,
        'prediction_mean': statistics.fmean(predictions) if predictions else None,
        'detected_classes': dict(sorted(detected_classes.items())),
        'triggered_classes': dict(sorted(triggered_classes.items())),
        'motor_start_events': motor_start_events,
        'motor_stop_events': motor_stop_events,
        'watchdog_timed_out': watchdog_timed_out,
        'cleanup_errors': cleanup_errors,
        'speed_percent': speed,
    }


def build_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, default=Path('models/lane_navigation_final.h5'))
    parser.add_argument('--video', type=Path)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--drive', action='store_true', help='enable real motor and servo output')
    parser.add_argument('--speed', type=speed_percentage, default=25)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--max-frames', type=int)
    parser.add_argument('--warmup-frames', type=int, default=30)
    parser.add_argument('--watchdog-timeout', type=float, default=1.0)
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.drive and args.video is not None:
        parser.error('--drive cannot be combined with --video')
    if args.max_frames is not None and args.max_frames < 1:
        parser.error('--max-frames must be positive')
    if not 0.2 <= args.watchdog_timeout <= 5.0:
        parser.error('--watchdog-timeout must be between 0.2 and 5.0 seconds')
    if args.video is None:
        ensure_libcamerify(__file__, sys.argv[1:] if argv is None else argv)

    deep_detector = JdDeepLaneDetect(args.model)
    lane_guard = JdOpencvLaneDetect()
    # Load and validate both neural-network artifacts before creating real
    # actuators.  A missing/corrupt object model must never be discovered only
    # after GPIO and the steering servo have been initialized.
    hazard_detector = partial(
        detect_hazards,
        model=default_detection_model(),
    )
    source = args.camera if args.video is None else str(args.video)
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        capture.release()
        raise SystemExit('could not open camera/video source: %s' % source)
    if args.video is None:
        capture.set(3, CAMERA_WIDTH)
        capture.set(4, CAMERA_HEIGHT)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(2)

    center_angle = load_center_angle(require_saved=args.drive)
    motor, servo = create_actuators(
        args.drive,
        center_angle,
        watchdog_timeout_seconds=args.watchdog_timeout,
    )
    summary = run_object_aware_follower(
        capture,
        deep_detector,
        lane_guard,
        hazard_detector,
        motor,
        servo,
        speed=args.speed,
        servo_offset=center_angle - 90.0,
        is_video=args.video is not None,
        preview=not args.headless,
        warmup_frames=args.warmup_frames,
        max_frames=args.max_frames,
    )
    summary['drive_enabled'] = args.drive
    summary['source'] = str(source)
    summary['model'] = str(args.model)
    summary['watchdog_timeout_seconds'] = (
        args.watchdog_timeout if args.drive else None
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if (
        not summary['complete']
        or summary['watchdog_timed_out']
        or bool(summary['cleanup_errors'])
        or summary['valid_frames'] == 0
        or summary['prediction_count'] == 0
    ):
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
