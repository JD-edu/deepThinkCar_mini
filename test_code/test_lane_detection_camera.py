import argparse
from pathlib import Path
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jd_camera_compat import ensure_libcamerify
from jd_opencv_lane_detect import JdOpencvLaneDetect, detect_black_mask


CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240


def read_frame(camera):
    ok, frame = camera.read()
    if ok and frame is not None and frame.shape[1] > CAMERA_WIDTH:
        frame = frame[:, :CAMERA_WIDTH]
    return ok, frame


def make_diagnostic_view(frame, mask, lane_image, lane_count):
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    cv2.putText(
        lane_image,
        'lane boundaries: %d' % lane_count,
        (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0) if lane_count else (0, 0, 255),
        2,
    )
    return np.hstack((frame, mask_bgr, lane_image))


def main():
    parser = argparse.ArgumentParser(
        description='Preview lane detection without importing or driving motors.'
    )
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--frames', type=int, default=0,
                        help='Stop after N valid frames; 0 runs until q is pressed.')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()

    ensure_libcamerify(__file__, sys.argv[1:])

    camera = cv2.VideoCapture(args.camera)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    time.sleep(2)

    detector = JdOpencvLaneDetect()
    valid_frames = 0
    detected_frames = 0
    startup_deadline = time.monotonic() + 10.0
    last_frame_time = None

    try:
        while args.frames == 0 or valid_frames < args.frames:
            ok, frame = read_frame(camera)
            if not ok or frame is None:
                now = time.monotonic()
                if valid_frames == 0 and now >= startup_deadline:
                    break
                if last_frame_time is not None and now - last_frame_time >= 2.0:
                    break
                time.sleep(0.05)
                continue

            last_frame_time = time.monotonic()
            lanes, lane_image = detector.get_lane(frame)
            mask = detect_black_mask(frame)
            valid_frames += 1
            detected_frames += bool(lanes)

            if not args.headless:
                view = make_diagnostic_view(frame, mask, lane_image, len(lanes))
                cv2.imshow('raw | black mask | detected lanes (q: quit)', view)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()

    print('valid_frames=%d detected_frames=%d' % (valid_frames, detected_frames))
    if not valid_frames:
        print('camera returned no frames; check the ribbon cable and libcamera')
    return 0 if valid_frames else 1


if __name__ == '__main__':
    raise SystemExit(main())
