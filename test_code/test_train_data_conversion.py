from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from jd_2_get_train_data import assess_lane_geometry, convert_video


class FakeLaneDetector:
    def __init__(self):
        self.calls = 0

    def get_lane(self, frame):
        height, width = frame.shape[:2]
        return [
            [[5, height, 18, height // 2]],
            [[width - 5, height, width - 18, height // 2]],
        ], frame

    def get_steering_angle(self, frame, _lanes):
        self.calls += 1
        if self.calls % 3 == 0:
            return 90, None
        return 80 + self.calls, frame


class UnsafeAngleDetector(FakeLaneDetector):
    def get_steering_angle(self, frame, _lanes):
        return 181, frame


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_test_video(path, frame_count=6):
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*'MJPG'),
        10.0,
        (64, 48),
    )
    if not writer.isOpened():
        raise unittest.SkipTest('MJPG VideoWriter is unavailable')
    for index in range(frame_count):
        frame = np.full((48, 64, 3), 60 + index, dtype=np.uint8)
        frame[:, ::4, :] = 180
        writer.write(frame)
    writer.release()


class TrainDataConversionTest(unittest.TestCase):
    def test_geometry_gate_requires_two_ordered_plausible_boundaries(self):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        plausible = [
            [[20, 240, 90, 120]],
            [[300, 240, 230, 120]],
        ]
        accepted, status, metrics = assess_lane_geometry(frame, plausible)
        self.assertTrue(accepted)
        self.assertEqual('accepted_two_boundaries', status)
        self.assertGreater(metrics['lookahead_width_ratio'], 0)

        accepted, status, _metrics = assess_lane_geometry(frame, plausible[:1])
        self.assertFalse(accepted)
        self.assertEqual('requires_two_lane_boundaries', status)

        crossed = [
            [[250, 240, 90, 120]],
            [[70, 240, 230, 120]],
        ]
        accepted, status, _metrics = assess_lane_geometry(frame, crossed)
        self.assertFalse(accepted)
        self.assertEqual('crossed_lane_boundaries', status)

    def test_conversion_preserves_existing_png_and_builds_training_zip(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video_path = root / 'car_video.avi'
            old_png = root / 'RC_000_090.png'
            old_png.write_bytes(b'keep me')
            create_test_video(video_path)
            source_hash = file_sha256(video_path)
            output_directory = root / 'lane_run'
            zip_path = root / 'lane_run.zip'

            with patch(
                'jd_2_get_train_data.cv2.imshow',
                side_effect=AssertionError('headless conversion called imshow'),
            ), patch(
                'jd_2_get_train_data.cv2.waitKey',
                side_effect=AssertionError('headless conversion called waitKey'),
            ):
                summary = convert_video(
                    video_path,
                    output_directory,
                    zip_path=zip_path,
                    detector=FakeLaneDetector(),
                )

            self.assertEqual(b'keep me', old_png.read_bytes())
            self.assertEqual(source_hash, file_sha256(video_path))
            self.assertEqual(6, summary['decoded_frames'])
            self.assertEqual(4, summary['labeled_frames'])
            self.assertEqual(2, summary['unlabeled_sampled_frames'])
            self.assertTrue(summary['require_two_lanes'])
            self.assertEqual({'2': 6}, summary['lane_count_counts'])
            images = sorted(output_directory.glob('*.png'))
            self.assertEqual(4, len(images))
            self.assertTrue(all(image.name[-7:-4].isdigit() for image in images))
            manifest_lines = (output_directory / 'manifest.csv').read_text().splitlines()
            self.assertEqual(7, len(manifest_lines))
            saved_summary = json.loads((output_directory / 'summary.json').read_text())
            self.assertEqual(4, saved_summary['labeled_frames'])
            with zipfile.ZipFile(zip_path) as archive:
                names = archive.namelist()
            self.assertIn('data/manifest.csv', names)
            self.assertIn('data/summary.json', names)
            self.assertEqual(4, sum(name.endswith('.png') for name in names))

    def test_existing_output_is_rejected_without_modification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video_path = root / 'car_video.avi'
            create_test_video(video_path, frame_count=1)
            output_directory = root / 'lane_run'
            output_directory.mkdir()
            marker = output_directory / 'marker.txt'
            marker.write_text('keep')

            with self.assertRaises(FileExistsError):
                convert_video(
                    video_path,
                    output_directory,
                    detector=FakeLaneDetector(),
                )

            self.assertEqual('keep', marker.read_text())

    def test_unsafe_angle_is_rejected_and_partial_output_is_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video_path = root / 'car_video.avi'
            create_test_video(video_path, frame_count=1)
            output_directory = root / 'lane_run'

            with self.assertRaisesRegex(RuntimeError, 'unsafe steering angle'):
                convert_video(
                    video_path,
                    output_directory,
                    detector=UnsafeAngleDetector(),
                )

            self.assertFalse(output_directory.exists())
            self.assertFalse((root / 'lane_run.tmp').exists())

    def test_zip_cannot_be_inside_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video_path = root / 'car_video.avi'
            create_test_video(video_path, frame_count=1)
            output_directory = root / 'lane_run'

            with self.assertRaisesRegex(ValueError, 'outside'):
                convert_video(
                    video_path,
                    output_directory,
                    zip_path=output_directory / 'lane.zip',
                    detector=FakeLaneDetector(),
                )

            self.assertFalse(output_directory.exists())


if __name__ == '__main__':
    unittest.main()
