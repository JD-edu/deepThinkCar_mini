"""Manual steering-servo sweep; importing this module never moves a servo."""

import argparse
import time


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            'Sweep the physical steering servo 10 degrees around its saved center. '
            'Keep hands and cables clear before opting in.'
        )
    )
    parser.add_argument(
        '--run-hardware',
        action='store_true',
        help='required acknowledgement that the real steering servo will move',
    )
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if not args.run_hardware:
        parser.error('refusing to move the servo without --run-hardware')

    from adafruit_servokit import ServoKit
    from jd_servo_config import load_center_angle

    servo_channel = None
    center_angle = load_center_angle(require_saved=True)
    try:
        kit = ServoKit(channels=16)
        servo_channel = kit.servo[0]
        print('Servo hardware test start...')
        angles = (
            center_angle - 10,
            center_angle,
            center_angle + 10,
            center_angle,
        )
        for angle in angles:
            print('Servo angle %.1f' % angle)
            servo_channel.angle = angle
            time.sleep(1)
        print('Servo hardware test completed')
        return 0
    except KeyboardInterrupt:
        print('\ninterrupted; centering and releasing the servo')
        return 130
    finally:
        if servo_channel is not None:
            try:
                servo_channel.angle = center_angle
                time.sleep(0.2)
            except BaseException:
                pass
            try:
                servo_channel.angle = None
            except BaseException:
                pass


if __name__ == '__main__':
    raise SystemExit(main())
