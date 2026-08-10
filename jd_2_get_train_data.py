"""Convert a recorded lane-driving video into labeled training images.

The original script deleted every ``data/*.png`` file before conversion.
This version always writes to a new directory so existing recordings and
manually collected RC images remain untouched.
"""

import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import zipfile

import cv2
import numpy as np

from jd_drive_runtime import frame_quality
from jd_opencv_lane_detect import JdOpencvLaneDetect


MIN_LOOKAHEAD_WIDTH_RATIO = 0.15
MAX_LOOKAHEAD_WIDTH_RATIO = 0.75
MIN_BOTTOM_WIDTH_RATIO = 0.30
MAX_BOTTOM_WIDTH_RATIO = 1.50
MIN_TRAINING_ANGLE = 45
MAX_TRAINING_ANGLE = 135


def positive_integer(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError('value must be at least 1')
    return value


def default_output_directory(video_path):
    timestamp = datetime.fromtimestamp(video_path.stat().st_mtime)
    return video_path.parent / ('lane_dataset_' + timestamp.strftime('%Y%m%d_%H%M%S'))


def source_run_id(video_path, source_sha256):
    timestamp = datetime.fromtimestamp(video_path.stat().st_mtime)
    safe_stem = ''.join(
        character if character.isalnum() else '_'
        for character in video_path.stem
    ).strip('_')
    return '%s_%s_%s' % (
        safe_stem or 'lane_video',
        timestamp.strftime('%Y%m%d_%H%M%S'),
        source_sha256[:10],
    )


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _prepare_destination(output_directory, zip_path):
    if output_directory.exists():
        raise FileExistsError(
            'output directory already exists; choose a new --output-dir: %s'
            % output_directory
        )
    temporary_directory = output_directory.with_name(output_directory.name + '.tmp')
    if temporary_directory.exists():
        raise FileExistsError(
            'temporary output directory already exists: %s' % temporary_directory
        )
    if zip_path is not None:
        output_resolved = output_directory.resolve()
        zip_resolved = zip_path.resolve()
        if zip_resolved == output_resolved or output_resolved in zip_resolved.parents:
            raise ValueError('--zip must be outside --output-dir')
        if zip_path.exists():
            raise FileExistsError('ZIP already exists; choose a new --zip path: %s' % zip_path)
        temporary_zip = zip_path.with_name(zip_path.name + '.tmp')
        if temporary_zip.exists():
            raise FileExistsError('temporary ZIP already exists: %s' % temporary_zip)
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    if zip_path is not None:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
    return temporary_directory


def _write_training_zip(output_directory, zip_path):
    temporary_zip = zip_path.with_name(zip_path.name + '.tmp')
    try:
        with zipfile.ZipFile(temporary_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source_path in sorted(output_directory.iterdir()):
                archive.write(source_path, Path('data') / source_path.name)
        temporary_zip.replace(zip_path)
    except BaseException:
        temporary_zip.unlink(missing_ok=True)
        raise


def assess_lane_geometry(
    frame,
    lane_lines,
    *,
    require_two_lanes=True,
    min_lookahead_width_ratio=MIN_LOOKAHEAD_WIDTH_RATIO,
    max_lookahead_width_ratio=MAX_LOOKAHEAD_WIDTH_RATIO,
    min_bottom_width_ratio=MIN_BOTTOM_WIDTH_RATIO,
    max_bottom_width_ratio=MAX_BOTTOM_WIDTH_RATIO,
):
    """Check that detected tape components form a plausible lane corridor."""
    lane_count = 0 if lane_lines is None else len(lane_lines)
    metrics = {
        'lane_count': lane_count,
        'lookahead_width_ratio': None,
        'bottom_width_ratio': None,
    }
    if lane_count == 0:
        return False, 'lane_not_detected', metrics
    if require_two_lanes and lane_count != 2:
        return False, 'requires_two_lane_boundaries', metrics
    if lane_count == 1:
        return True, 'accepted_single_boundary', metrics

    _height, width = frame.shape[:2]
    try:
        endpoints = [np.asarray(line).reshape(-1)[:4] for line in lane_lines]
        if any(len(endpoint) != 4 for endpoint in endpoints):
            raise ValueError
        endpoints.sort(key=lambda endpoint: float(endpoint[2]))
        left, right = endpoints[:2]
        lookahead_width_ratio = float(right[2] - left[2]) / width
        bottom_width_ratio = float(right[0] - left[0]) / width
    except (TypeError, ValueError, IndexError):
        return False, 'invalid_lane_geometry', metrics

    metrics.update(
        {
            'lookahead_width_ratio': lookahead_width_ratio,
            'bottom_width_ratio': bottom_width_ratio,
        }
    )
    if bottom_width_ratio <= 0:
        return False, 'crossed_lane_boundaries', metrics
    if not min_lookahead_width_ratio <= lookahead_width_ratio <= max_lookahead_width_ratio:
        return False, 'implausible_lookahead_width', metrics
    if not min_bottom_width_ratio <= bottom_width_ratio <= max_bottom_width_ratio:
        return False, 'implausible_bottom_width', metrics
    return True, 'accepted_two_boundaries', metrics


def convert_video(
    video_path,
    output_directory,
    *,
    zip_path=None,
    sample_every=1,
    preview=False,
    detector=None,
    require_two_lanes=True,
):
    video_path = Path(video_path)
    output_directory = Path(output_directory)
    zip_path = None if zip_path is None else Path(zip_path)
    if sample_every < 1:
        raise ValueError('sample_every must be at least 1')
    if not video_path.is_file():
        raise FileNotFoundError('video does not exist: %s' % video_path)

    temporary_directory = _prepare_destination(output_directory, zip_path)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError('OpenCV could not open video: %s' % video_path)

    source_sha256 = sha256_file(video_path)
    detector = JdOpencvLaneDetect() if detector is None else detector
    reported_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    decoded_frames = 0
    sampled_frames = 0
    labeled_frames = 0
    angles = []
    lane_count_counts = Counter()
    rejection_counts = Counter()
    stopped_by_user = False
    run_id = source_run_id(video_path, source_sha256)

    temporary_directory.mkdir()
    manifest_path = temporary_directory / 'manifest.csv'
    try:
        with manifest_path.open('w', encoding='utf-8', newline='') as manifest_file:
            writer = csv.DictWriter(
                manifest_file,
                fieldnames=(
                    'image',
                    'source_frame',
                    'steering_angle',
                    'raw_steering_angle',
                    'status',
                    'lane_count',
                    'lookahead_width_ratio',
                    'bottom_width_ratio',
                    'frame_mean',
                    'frame_stddev',
                ),
            )
            writer.writeheader()

            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                source_frame = decoded_frames
                decoded_frames += 1
                if source_frame % sample_every != 0:
                    continue
                sampled_frames += 1

                usable, frame_mean, frame_stddev = frame_quality(frame)
                lanes, lane_image = detector.get_lane(frame)
                lane_count = 0 if lanes is None else len(lanes)
                lane_count_counts[lane_count] += 1
                geometry_ok, geometry_status, geometry = assess_lane_geometry(
                    frame,
                    lanes,
                    require_two_lanes=require_two_lanes,
                )
                raw_angle = None
                angle_image = None
                if lane_count:
                    raw_method = getattr(detector, 'get_raw_steering_angle', None)
                    if raw_method is None:
                        raw_angle, angle_image = detector.get_steering_angle(
                            lane_image,
                            lanes,
                        )
                    else:
                        raw_angle, angle_image = raw_method(lane_image, lanes)
                image_name = ''
                steering_angle = ''
                status = geometry_status
                if not usable:
                    status = 'unusable_frame_quality'
                elif geometry_ok and angle_image is not None:
                    angle = int(round(float(raw_angle)))
                    if not 0 <= angle <= 180:
                        raise RuntimeError(
                            'detector returned unsafe steering angle %d at frame %d'
                            % (angle, source_frame)
                        )
                    if not MIN_TRAINING_ANGLE <= angle <= MAX_TRAINING_ANGLE:
                        status = 'angle_outside_training_envelope'
                        rejection_counts[status] += 1
                    else:
                        image_name = '%s_f%06d_%03d.png' % (
                            run_id,
                            source_frame,
                            angle,
                        )
                        image_path = temporary_directory / image_name
                        if not cv2.imwrite(str(image_path), frame):
                            raise RuntimeError('failed to write image: %s' % image_path)
                        labeled_frames += 1
                        angles.append(angle)
                        steering_angle = angle
                        status = 'labeled'
                else:
                    rejection_counts[status] += 1

                writer.writerow(
                    {
                        'image': image_name,
                        'source_frame': source_frame,
                        'steering_angle': steering_angle,
                        'raw_steering_angle': (
                            '' if raw_angle is None else float(raw_angle)
                        ),
                        'status': status,
                        'lane_count': lane_count,
                        'lookahead_width_ratio': geometry['lookahead_width_ratio'],
                        'bottom_width_ratio': geometry['bottom_width_ratio'],
                        'frame_mean': frame_mean,
                        'frame_stddev': frame_stddev,
                    }
                )

                if preview:
                    preview_frame = angle_image if angle_image is not None else frame
                    cv2.imshow('lane training conversion', preview_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        stopped_by_user = True
                        break

        if stopped_by_user:
            raise RuntimeError('conversion was stopped before the end of the video')
        if reported_frames > 0 and decoded_frames != reported_frames:
            raise RuntimeError(
                'video decode ended early: decoded %d of %d reported frames'
                % (decoded_frames, reported_frames)
            )
        if labeled_frames == 0:
            raise RuntimeError('no frames contained a detectable lane; no dataset was created')

        angle_counts = Counter(angles)
        summary = {
            'complete': not stopped_by_user and (
                reported_frames <= 0 or decoded_frames == reported_frames
            ),
            'run_id': run_id,
            'source_video': str(video_path),
            'source_sha256': source_sha256,
            'source_size_bytes': video_path.stat().st_size,
            'reported_frames': reported_frames,
            'decoded_frames': decoded_frames,
            'sampled_frames': sampled_frames,
            'labeled_frames': labeled_frames,
            'unlabeled_sampled_frames': sampled_frames - labeled_frames,
            'label_rate': labeled_frames / sampled_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'sample_every': sample_every,
            'stopped_by_user': stopped_by_user,
            'angle_min': min(angles),
            'angle_max': max(angles),
            'angle_mean': statistics.fmean(angles),
            'angle_median': statistics.median(angles),
            'angle_counts': {str(key): angle_counts[key] for key in sorted(angle_counts)},
            'label_policy': (
                'raw OpenCV geometry, two plausible tape boundaries required'
                if require_two_lanes
                else 'raw OpenCV geometry, one or two tape boundaries allowed'
            ),
            'require_two_lanes': require_two_lanes,
            'lane_count_counts': {
                str(key): lane_count_counts[key] for key in sorted(lane_count_counts)
            },
            'rejection_counts': dict(sorted(rejection_counts.items())),
            'geometry_thresholds': {
                'lookahead_width_ratio': [
                    MIN_LOOKAHEAD_WIDTH_RATIO,
                    MAX_LOOKAHEAD_WIDTH_RATIO,
                ],
                'bottom_width_ratio': [
                    MIN_BOTTOM_WIDTH_RATIO,
                    MAX_BOTTOM_WIDTH_RATIO,
                ],
                'training_angle_degrees': [
                    MIN_TRAINING_ANGLE,
                    MAX_TRAINING_ANGLE,
                ],
            },
            'output_directory': str(output_directory),
            'zip_path': None if zip_path is None else str(zip_path),
        }
        with (temporary_directory / 'summary.json').open('w', encoding='utf-8') as summary_file:
            json.dump(summary, summary_file, indent=2, sort_keys=True)
            summary_file.write('\n')

        temporary_directory.replace(output_directory)
        if zip_path is not None:
            _write_training_zip(output_directory, zip_path)
        return summary
    except BaseException:
        if temporary_directory.exists():
            shutil.rmtree(temporary_directory)
        raise
    finally:
        capture.release()
        if preview:
            cv2.destroyAllWindows()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Create steering-angle PNG labels without deleting existing data.'
    )
    parser.add_argument('--video', type=Path, default=Path('data/car_video.avi'))
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument(
        '--zip',
        dest='zip_path',
        type=Path,
        help='optional training archive; it extracts as data/*.png',
    )
    parser.add_argument('--sample-every', type=positive_integer, default=1)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument(
        '--allow-single-lane',
        action='store_true',
        help='allow inferred labels from one boundary (not recommended)',
    )
    args = parser.parse_args(argv)

    output_directory = args.output_dir
    if output_directory is None:
        output_directory = default_output_directory(args.video)
    summary = convert_video(
        args.video,
        output_directory,
        zip_path=args.zip_path,
        sample_every=args.sample_every,
        preview=args.preview,
        require_two_lanes=not args.allow_single_lane,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
