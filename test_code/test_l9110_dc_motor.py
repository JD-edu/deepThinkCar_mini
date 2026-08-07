"""Manual rear-motor test; importing this module never touches GPIO."""

import argparse
import time


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            'Run the physical L9110 rear motors through 10/20/30/37%. '
            'Lift the wheels clear of the floor before opting in.'
        )
    )
    parser.add_argument(
        '--run-hardware',
        action='store_true',
        help='required acknowledgement that real motors will move',
    )
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if not args.run_hardware:
        parser.error('refusing to move motors without --run-hardware')

    import RPi.GPIO as IO

    pwm_pin_1 = 19
    direction_pin_1 = 13
    pwm_pin_2 = 12
    direction_pin_2 = 16
    pwm_1 = None
    pwm_2 = None

    try:
        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(pwm_pin_1, IO.OUT)
        IO.setup(direction_pin_1, IO.OUT)
        IO.setup(pwm_pin_2, IO.OUT)
        IO.setup(direction_pin_2, IO.OUT)
        IO.output(direction_pin_1, False)
        IO.output(direction_pin_2, False)

        pwm_1 = IO.PWM(pwm_pin_1, 100)
        pwm_2 = IO.PWM(pwm_pin_2, 100)
        pwm_1.start(0)
        pwm_2.start(0)

        print('DC motor hardware test start...')
        for duty_cycle in (10, 20, 30, 37):
            print('DC motor power %d%%' % duty_cycle)
            pwm_1.ChangeDutyCycle(duty_cycle)
            pwm_2.ChangeDutyCycle(duty_cycle)
            time.sleep(2)
        print('DC motor hardware test completed')
        return 0
    except KeyboardInterrupt:
        print('\ninterrupted; stopping both motors')
        return 130
    finally:
        for pwm in (pwm_1, pwm_2):
            if pwm is None:
                continue
            try:
                pwm.ChangeDutyCycle(0)
            except Exception:
                pass
            try:
                pwm.stop()
            except Exception:
                pass
        for pin in (direction_pin_1, pwm_pin_1, direction_pin_2, pwm_pin_2):
            try:
                IO.output(pin, False)
            except Exception:
                pass
        try:
            IO.cleanup()
        except Exception:
            pass


if __name__ == '__main__':
    raise SystemExit(main())
