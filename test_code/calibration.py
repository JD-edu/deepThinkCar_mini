"""Safely calibrate the front steering servo without driving the car."""

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from adafruit_servokit import ServoKit

from jd_car_motor_l9110 import JdCarMotorL9110
from jd_servo_config import (
    MAX_CENTER_ANGLE,
    MIN_CENTER_ANGLE,
    load_center_angle,
    save_center_angle,
    validate_center_angle,
)


def apply_angle(servo_channel, angle):
    angle = validate_center_angle(angle)
    servo_channel.angle = angle
    print('center angle: %.1f degrees (offset %+.1f)' % (angle, angle - 90.0))
    return angle


def main():
    parser = argparse.ArgumentParser(
        description='Calibrate only the steering servo; rear motors stay stopped.'
    )
    parser.add_argument('--angle', type=float)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()

    motor = JdCarMotorL9110()
    motor.motor_stop()
    servo = ServoKit(channels=16)
    original_angle = load_center_angle()
    current_angle = original_angle if args.angle is None else args.angle

    try:
        current_angle = apply_angle(servo.servo[0], current_angle)

        if args.angle is not None:
            if args.save:
                path = save_center_angle(current_angle)
                print('saved:', path)
            else:
                print('applied temporarily; add --save to persist it')
            return 0

        print('Rear motors are stopped.')
        print('a: -1 degree | d: +1 degree | aa/dd: -5/+5 | s: save | q: cancel')
        print('You may also enter a direct angle from %.0f to %.0f.' % (
            MIN_CENTER_ANGLE, MAX_CENTER_ANGLE
        ))

        while True:
            command = input('calibration> ').strip().lower()
            if command == 'a':
                current_angle -= 1
            elif command == 'd':
                current_angle += 1
            elif command == 'aa':
                current_angle -= 5
            elif command == 'dd':
                current_angle += 5
            elif command == 's':
                path = save_center_angle(current_angle)
                print('saved:', path)
                return 0
            elif command == 'q':
                apply_angle(servo.servo[0], original_angle)
                print('cancelled; restored the previous center')
                return 0
            else:
                try:
                    current_angle = float(command)
                except ValueError:
                    print('unknown command')
                    continue

            try:
                current_angle = apply_angle(servo.servo[0], current_angle)
            except ValueError as error:
                print(error)
                current_angle = max(
                    MIN_CENTER_ANGLE,
                    min(MAX_CENTER_ANGLE, current_angle),
                )
    except KeyboardInterrupt:
        apply_angle(servo.servo[0], original_angle)
        print('\ninterrupted; restored the previous center')
        return 130
    finally:
        motor.motor_stop()


if __name__ == '__main__':
    raise SystemExit(main())
