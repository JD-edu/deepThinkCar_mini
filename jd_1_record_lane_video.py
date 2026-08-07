'''
1. importing necessary modules
'''
import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

from jd_camera_compat import ensure_libcamerify

# Raspberry Pi OS Bookworm no longer exposes the Pi camera as a legacy V4L2
# camera.  Re-run through its compatibility layer when the user starts this
# file with a normal `python3 jd_1_record_lane_video.py` command.
def recording_speed(value):
    value = int(value)
    if not 1 <= value <= 37:
        raise argparse.ArgumentTypeError('recording speed must be from 1 to 37 percent')
    return value


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--camera-check', action='store_true')
argument_parser.add_argument(
    '--output',
    type=Path,
    help=(
        'recording path; defaults to a timestamped AVI under ./data '
        'and never overwrites an existing file'
    ),
)
argument_parser.add_argument(
    '--speed',
    type=recording_speed,
    default=37,
    help='rear-motor PWM duty percentage (default: 37)',
)
runtime_options = argument_parser.parse_args()
CAMERA_CHECK_ONLY = runtime_options.camera_check
RECORDING_SPEED = runtime_options.speed
RECORDING_OUTPUT = runtime_options.output or Path(
    'data/car_video_%s.avi' % datetime.now().strftime('%Y%m%d_%H%M%S')
)
if not CAMERA_CHECK_ONLY and RECORDING_OUTPUT.exists():
    argument_parser.error('output already exists: %s' % RECORDING_OUTPUT)
ensure_libcamerify(__file__, sys.argv[1:])

import cv2
from adafruit_servokit import ServoKit
from jd_drive_runtime import MotorWatchdog, read_frame, safe_servo_angle
from jd_opencv_lane_detect import JdOpencvLaneDetect
from jd_car_motor_l9110 import JdCarMotorL9110
from jd_servo_config import load_center_angle

try:
    servo_center_angle = load_center_angle(
        require_saved=not CAMERA_CHECK_ONLY,
    )
except RuntimeError as error:
    raise SystemExit(str(error))
servo_offset = servo_center_angle - 90.0

'''
2. Creating object from classes
  1) Servo handling object from ServoKit class 
  2) OpenCV lane detecting object from JdOpencvLaneDetect class 
  3) DC motor handling object form JdCarMotorL9110 class 
'''
# Servo object 
servo = ServoKit(channels=16)
# OpenCV line detector object
cv_detector = JdOpencvLaneDetect()
# DC motor object 
motor = JdCarMotorL9110()


def start_motor_with_watchdog(speed):
    global motor
    if not isinstance(motor, MotorWatchdog):
        motor = MotorWatchdog(motor, timeout_seconds=1.0)
    motor.motor_move_forward(speed)


def shutdown_motor():
    shutdown = getattr(motor, 'shutdown', None)
    if shutdown is not None:
        shutdown()
    else:
        motor.motor_stop()

'''
3. Creating camera object and setting resolution of camera image
cv2.VideoCapture() function create camera object.  
'''
# Camera object: reading image from camera
cap = cv2.VideoCapture(0)
# Setting camera resolution as 320x240
cap.set(3, 320)
cap.set(4, 240)
# libcamera needs a couple of seconds to stabilize exposure/AGC.
time.sleep(2)

'''
4. Creating data folder, if not exist
Video file that come from OpenCV driving is saved here. 
'''
# Create the selected output directory without touching existing recordings.
try:
    if not CAMERA_CHECK_ONLY:
        RECORDING_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
except OSError as error:
    raise SystemExit(
        'failed to create recording directory %s: %s'
        % (RECORDING_OUTPUT.parent, error)
    )
    
'''
5. Creating video recording object
In this first step, we record deepThinkCar driving as AVI video file.
To do this we have to use cv2.VideoWrite_forcc() and cv2.Video_writer()
For more info, refer OpenCV tutorial.
'''
# Create video codec object. We use 'XVID' format for Raspberry pi.
fourcc =  cv2.VideoWriter_fourcc(*'XVID')
#fourcc =  cv2.VideoWriter_fourcc('M','J','P','G')
# Video write object is created after the warm-up loop below, sized to
# match the normalized camera frame. The shared read_frame() helper keeps a
# real high-resolution view by resizing it, but removes the confirmed
# 640x240 black-padding case produced by libcamerify.
video_orig = None
camera_frame_size = None

'''
6. Preparing deepThinkCar starting.
Before start driving, we need to adjust servo offset(wheel calibraton)
and wheel control while motor stop.
It will prevents mis-driving of deepThinkCar.
'''
# Servo offset. You can get offset from calibration.py
print(
    "servo center: %.1f degrees (offset %+.1f)"
    % (servo_center_angle, servo_offset)
)
if not CAMERA_CHECK_ONLY:
    servo.servo[0].angle = servo_center_angle

# Prepare real starting
CAMERA_WARMUP_FRAMES = 30
CAMERA_START_TIMEOUT_SECONDS = 10.0
READY_LANE_FRAMES = 5
valid_camera_frames = 0
lane_ready = False
consecutive_lane_ready = 0
waiting_message_printed = False
warmup_deadline = time.monotonic() + CAMERA_START_TIMEOUT_SECONDS
while (
    valid_camera_frames < CAMERA_WARMUP_FRAMES
    and time.monotonic() < warmup_deadline
):
    ret, img_org = read_frame(cap)
    if not ret:
        if not waiting_message_printed:
            print("waiting for camera frames...")
            waiting_message_printed = True
        time.sleep(0.05)
        continue

    valid_camera_frames += 1
    if camera_frame_size is None:
        h, w = img_org.shape[:2]
        camera_frame_size = (w, h)
        print("actual camera frame size: %dx%d" % (w, h))
        if not CAMERA_CHECK_ONLY:
            # Re-check immediately before VideoWriter, so a second recorder
            # cannot silently replace a file created during camera warm-up.
            if RECORDING_OUTPUT.exists():
                motor.motor_stop()
                cap.release()
                raise SystemExit(
                    'output already exists: %s' % RECORDING_OUTPUT
                )
            video_orig = cv2.VideoWriter(
                str(RECORDING_OUTPUT), fourcc, 20.0, (w, h)
            )

    lanes, img_lane = cv_detector.get_lane(img_org)
    angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
    if img_angle is None:
        print("can't find lane...")
        consecutive_lane_ready = 0
    else:
        print(angle)
        if not CAMERA_CHECK_ONLY:
            servo.servo[0].angle = safe_servo_angle(angle, servo_offset)
        consecutive_lane_ready += 1
    lane_ready = consecutive_lane_ready >= READY_LANE_FRAMES

# Never start the motor when the camera pipeline did not produce a frame.
if valid_camera_frames == 0:
    motor.motor_stop()
    cap.release()
    cv2.destroyAllWindows()
    raise SystemExit(
        "camera returned no frames; check the ribbon cable or run "
        "`libcamerify python3 jd_1_record_lane_video.py`"
    )
if CAMERA_CHECK_ONLY:
    motor.motor_stop()
    cap.release()
    cv2.destroyAllWindows()
    print(
        "camera_check=ok valid_frames=%d lane_frames_seen=%s"
        % (valid_camera_frames, lane_ready)
    )
    raise SystemExit(0)
if video_orig is None or not video_orig.isOpened():
    motor.motor_stop()
    cap.release()
    raise SystemExit("failed to open %s for recording" % RECORDING_OUTPUT)
print("recording output: %s" % RECORDING_OUTPUT)

'''
7. Starting motor before real driving 
'''
# Start only after consecutive lane detections at the end of warm-up.
# Otherwise the main loop waits with the motor stopped until the same gate
# succeeds; one stale or false-positive frame can never start the car.
is_moving = False
if lane_ready:
    print("recording speed: %d" % RECORDING_SPEED)
    try:
        start_motor_with_watchdog(RECORDING_SPEED)
    except BaseException:
        shutdown_motor()
        cap.release()
        video_orig.release()
        cv2.destroyAllWindows()
        raise
    is_moving = True
else:
    motor.motor_stop()
    print("lane not found during warm-up; motor remains stopped")

'''
8. Perform real driving
In this part, we perform real OpenCV lane detecting driving.
When you press 'q' key, it stp deepThinkCar.
While on driving, driving is recorded. 
'''
# real driving routine
# If the lane goes undetected for too many frames in a row, the car was
# just holding its last steering angle and driving blind - which is how
# it ended up circling off the track. Stop the motor instead once that
# happens, and resume once the lane is found again.
LOST_LANE_LIMIT = 15
CAMERA_ERROR_LIMIT = 30
lost_lane_count = 0
camera_error_count = 0
try:
    while True:
        ret, img_org = read_frame(cap)
        if ret:
            camera_error_count = 0
            # camera image writing
            video_orig.write(img_org)
            # Find lane angle
            lanes, img_lane = cv_detector.get_lane(img_org)
            angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
            if img_angle is None:
                print("can't find lane...")
                lost_lane_count += 1
                consecutive_lane_ready = 0
                if lost_lane_count >= LOST_LANE_LIMIT and is_moving:
                    print("lane lost for too long, stopping until it's found again")
                    motor.motor_stop()
                    is_moving = False
            else:
                cv2.imshow('lane', img_angle)
                print(angle)
                servo.servo[0].angle = safe_servo_angle(angle, servo_offset)
                lost_lane_count = 0
                consecutive_lane_ready += 1
                if (
                    not is_moving
                    and consecutive_lane_ready >= READY_LANE_FRAMES
                ):
                    start_motor_with_watchdog(RECORDING_SPEED)
                    is_moving = True
            heartbeat = getattr(motor, 'heartbeat', None)
            if is_moving and heartbeat is not None and not heartbeat():
                print('motor watchdog timed out; exiting safely')
                is_moving = False
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            camera_error_count += 1
            consecutive_lane_ready = 0
            if is_moving:
                motor.motor_stop()
                is_moving = False
            if camera_error_count == 1:
                print("camera frame lost; motor stopped, retrying...")
            if camera_error_count >= CAMERA_ERROR_LIMIT:
                print("camera did not recover; exiting safely")
                break
except KeyboardInterrupt:
    print("interrupted; stopping safely")
finally:
    try:
        shutdown_motor()
    finally:
        try:
            servo.servo[0].angle = servo_center_angle
            time.sleep(0.2)
            servo.servo[0].angle = None
        finally:
            cap.release()
            video_orig.release()
            cv2.destroyAllWindows()
