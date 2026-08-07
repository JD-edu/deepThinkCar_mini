"""Shared fail-safe helpers for deepThinkCar driving entry points."""

import argparse
import math
import threading
import time

import cv2
import numpy as np


CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240


def speed_percentage(value):
    value = int(value)
    if not 1 <= value <= 100:
        raise argparse.ArgumentTypeError('speed must be a PWM percentage from 1 to 100')
    return value


def read_frame(capture):
    ok, frame = capture.read()
    if not ok or frame is None:
        return False, None
    if frame.ndim != 3 or frame.shape[2] != 3:
        return False, None
    frame = normalize_camera_frame(frame)
    return True, frame


def normalize_camera_frame(frame):
    """Return the 320x240 geometry used for recording and training.

    libcamerify has been observed to return 640x240 frames whose right half
    is uniform black padding.  Crop only that confirmed padding case.  A real
    higher-resolution frame is resized in full so the right side of the scene
    (including a possible hazard) is not discarded.
    """
    height, width = frame.shape[:2]
    if (height, width) == (CAMERA_HEIGHT, CAMERA_WIDTH):
        return frame
    if height == CAMERA_HEIGHT and width == CAMERA_WIDTH * 2:
        right_half = frame[:, CAMERA_WIDTH:]
        left_half = frame[:, :CAMERA_WIDTH]
        right_mean = float(np.mean(right_half))
        right_std = float(np.std(right_half))
        left_mean = float(np.mean(left_half))
        if right_mean <= 2.0 and right_std <= 2.0 and left_mean > right_mean + 3.0:
            return left_half
    return cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))


def frame_quality(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean = float(np.mean(gray))
    standard_deviation = float(np.std(gray))
    usable = 8.0 <= mean <= 247.0 and standard_deviation >= 8.0
    return usable, mean, standard_deviation


def safe_servo_angle(predicted_angle, servo_offset):
    predicted_angle = float(predicted_angle)
    servo_offset = float(servo_offset)
    if not math.isfinite(predicted_angle):
        raise ValueError('predicted steering angle must be finite')
    if not 30.0 <= predicted_angle <= 150.0:
        raise ValueError('predicted steering angle is outside the safety envelope')
    predicted_angle = min(135.0, max(45.0, predicted_angle))
    return min(140.0, max(40.0, predicted_angle + servo_offset))


class DryRunMotor:
    def __init__(self):
        self.is_moving = False
        self.start_count = 0
        self.stop_count = 0
        self.last_speed = None

    def motor_move_forward(self, speed):
        self.is_moving = True
        self.start_count += 1
        self.last_speed = speed

    def motor_stop(self):
        if self.is_moving:
            self.stop_count += 1
        self.is_moving = False


class DryRunServo:
    def __init__(self):
        self.angles = []
        self.closed = False

    def set_angle(self, angle):
        self.angles.append(float(angle))

    def shutdown(self):
        self.closed = True


class HardwareServo:
    def __init__(self, channel, center_angle):
        self.channel = channel
        self.center_angle = float(center_angle)

    def set_angle(self, angle):
        self.channel.angle = angle

    def shutdown(self):
        # Stop the wheels first (handled by shutdown_runtime), then center the
        # steering and release PCA9685 PWM so an exception cannot leave the
        # servo holding an extreme command indefinitely.
        self.channel.angle = self.center_angle
        time.sleep(0.2)
        self.channel.angle = None


class MotorWatchdog:
    """Stop a moving motor when the control loop stops sending heartbeats."""

    def __init__(
        self,
        motor,
        *,
        timeout_seconds=1.0,
        check_interval_seconds=0.05,
    ):
        if timeout_seconds <= 0 or check_interval_seconds <= 0:
            raise ValueError('watchdog intervals must be positive')
        self._motor = motor
        self.timeout_seconds = float(timeout_seconds)
        self.check_interval_seconds = float(check_interval_seconds)
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self._timeout_event = threading.Event()
        self._moving = False
        self._deadline = None
        self._thread = threading.Thread(
            target=self._monitor,
            name='deepthinkcar-motor-watchdog',
            daemon=True,
        )
        self._thread.start()

    @property
    def timed_out(self):
        return self._timeout_event.is_set()

    @property
    def is_moving(self):
        with self._lock:
            return self._moving

    def motor_move_forward(self, speed):
        with self._lock:
            if self.timed_out:
                raise RuntimeError('motor watchdog has timed out; restart is required')
            self._motor.motor_move_forward(speed)
            self._moving = True
            self._deadline = time.monotonic() + self.timeout_seconds

    def heartbeat(self):
        with self._lock:
            if self.timed_out:
                return False
            if self._moving:
                self._deadline = time.monotonic() + self.timeout_seconds
            return True

    def motor_stop(self):
        with self._lock:
            self._moving = False
            self._deadline = None
            self._motor.motor_stop()

    def wait_for_timeout(self, timeout_seconds):
        return self._timeout_event.wait(timeout_seconds)

    def shutdown(self):
        try:
            self.motor_stop()
        finally:
            self._shutdown_event.set()
            if threading.current_thread() is not self._thread:
                self._thread.join(timeout=max(0.2, self.check_interval_seconds * 3))

    def _monitor(self):
        while not self._shutdown_event.wait(self.check_interval_seconds):
            with self._lock:
                if (
                    not self._moving
                    or self._deadline is None
                    or time.monotonic() < self._deadline
                ):
                    continue
                self._moving = False
                self._deadline = None
                self._timeout_event.set()
                try:
                    self._motor.motor_stop()
                except Exception:
                    # The timeout remains latched. The main thread reports the
                    # timeout and performs another best-effort stop on exit.
                    pass


def shutdown_runtime(motor, servo, capture, *, preview):
    """Best-effort ordered cleanup; return errors so main exits non-zero."""
    errors = []

    def attempt(label, callback):
        try:
            callback()
        except Exception as error:
            errors.append('%s failed: %s' % (label, error))

    attempt('motor stop', motor.motor_stop)
    shutdown_servo = getattr(servo, 'shutdown', None)
    if shutdown_servo is not None:
        attempt('servo shutdown', shutdown_servo)
    shutdown_motor = getattr(motor, 'shutdown', None)
    if shutdown_motor is not None:
        attempt('motor watchdog shutdown', shutdown_motor)
    attempt('camera release', capture.release)
    if preview:
        attempt('window cleanup', cv2.destroyAllWindows)
    return errors


def create_actuators(drive, center_angle, watchdog_timeout_seconds=1.0):
    if not drive:
        return DryRunMotor(), DryRunServo()
    from adafruit_servokit import ServoKit
    from jd_car_motor_l9110 import JdCarMotorL9110

    hardware_motor = JdCarMotorL9110()
    hardware_motor.motor_stop()
    kit = ServoKit(channels=16)
    servo = HardwareServo(kit.servo[0], center_angle)
    servo.set_angle(center_angle)
    motor = MotorWatchdog(
        hardware_motor,
        timeout_seconds=watchdog_timeout_seconds,
    )
    return motor, servo
