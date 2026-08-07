"""Manual Pi-camera preview; importing this module never opens the camera."""

import argparse
import sys
import time

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_camera_compat import ensure_libcamerify


def build_argument_parser():
    parser = argparse.ArgumentParser(description='Preview the physical Pi camera.')
    parser.add_argument(
        '--run-hardware',
        action='store_true',
        help='required acknowledgement that the physical camera will be opened',
    )
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--camera-error-limit', type=int, default=30)
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if not args.run_hardware:
        parser.error('refusing to open the camera without --run-hardware')
    if args.camera_error_limit < 1:
        parser.error('--camera-error-limit must be positive')

    ensure_libcamerify(__file__, sys.argv[1:] if argv is None else argv)

    import cv2

    from jd_drive_runtime import CAMERA_HEIGHT, CAMERA_WIDTH, read_frame

    camera = cv2.VideoCapture(args.camera)
    consecutive_errors = 0
    try:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(2)

        if not camera.isOpened():
            print('camera could not be opened')
            return 1

        print("Camera preview started; press 'q' to quit.")
        while True:
            ok, frame = read_frame(camera)
            if not ok:
                consecutive_errors += 1
                if consecutive_errors == 1:
                    print('camera frame unavailable; retrying...')
                if consecutive_errors >= args.camera_error_limit:
                    print('camera did not recover; exiting')
                    return 1
                time.sleep(0.05)
                continue

            consecutive_errors = 0
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return 0
    except KeyboardInterrupt:
        print('\ninterrupted; closing the camera')
        return 130
    finally:
        try:
            camera.release()
        finally:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    raise SystemExit(main())
