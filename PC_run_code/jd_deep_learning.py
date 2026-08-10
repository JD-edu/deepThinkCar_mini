"""Train the deepThinkCar steering model with current TensorFlow/Keras.

The image filename must end in ``_<three digit angle>.png``.  This keeps the
dataset produced by ``jd_2_get_train_data.py`` compatible with the original
course workflow while allowing each run to live in its own directory.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

import cv2
import keras
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import tensorflow as tf


ANGLE_PATTERN = re.compile(r'_(\d{3})\.png$')
SOURCE_FRAME_PATTERN = re.compile(r'(?:_f|_)(\d+)_(\d{3})\.png$')
TARGET_CENTER_DEGREES = 90.0
TARGET_SCALE_DEGREES = 90.0


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_sha256(image_paths):
    """Hash ordered file names and bytes without exposing local paths."""
    digest = hashlib.sha256()
    for path in image_paths:
        path = Path(path)
        digest.update(path.name.encode('utf-8'))
        digest.update(b'\0')
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def parse_steering_angle(path):
    match = ANGLE_PATTERN.search(Path(path).name)
    if match is None:
        raise ValueError('filename does not end in _<three digit angle>.png: %s' % path)
    angle = int(match.group(1))
    if not 0 <= angle <= 180:
        raise ValueError('steering angle must be from 000 to 180: %s' % path)
    return angle


def discover_dataset(data_directory):
    data_directory = Path(data_directory)
    image_paths = sorted(
        (
            path
            for path in data_directory.rglob('*.png')
            if ANGLE_PATTERN.search(path.name)
        ),
        key=lambda path: path.relative_to(data_directory).as_posix(),
    )
    if len(image_paths) < 10:
        raise RuntimeError(
            'at least 10 labeled PNG files are required in %s; found %d'
            % (data_directory, len(image_paths))
        )
    angles = np.asarray(
        [parse_steering_angle(path) for path in image_paths],
        dtype=np.float32,
    )
    return image_paths, angles


def img_preprocess(image):
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('expected a BGR image with three channels')
    height = image.shape[0]
    image = image[height // 2 :, :, :]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    return image.astype(np.float32) / 255.0


def load_images(image_paths):
    images = []
    for image_path in image_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError('OpenCV could not read image: %s' % image_path)
        images.append(img_preprocess(image))
    return np.asarray(images, dtype=np.float32)


def temporal_group_key(path, group_size):
    match = SOURCE_FRAME_PATTERN.search(Path(path).name)
    if match is None:
        raise ValueError('filename does not contain a source frame index: %s' % path)
    source_frame = int(match.group(1))
    run_prefix = Path(path).name[: match.start()]
    return '%s:%06d' % (run_prefix, source_frame // group_size)


def source_run_key(path):
    match = SOURCE_FRAME_PATTERN.search(Path(path).name)
    if match is None:
        raise ValueError('filename does not contain a source frame index: %s' % path)
    return Path(path).name[: match.start()]


def split_dataset_indices(image_paths, validation_fraction, seed, temporal_group_size):
    groups = np.asarray(
        [temporal_group_key(path, temporal_group_size) for path in image_paths]
    )
    if len(np.unique(groups)) < 2:
        raise RuntimeError('dataset needs at least two temporal groups')
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=validation_fraction,
        random_state=seed,
    )
    indices = np.arange(len(image_paths))
    train_indices, validation_indices = next(splitter.split(indices, groups=groups))
    return train_indices, validation_indices, groups


def split_dataset_by_run_indices(image_paths, validation_fraction, seed):
    groups = np.asarray([source_run_key(path) for path in image_paths])
    if len(np.unique(groups)) < 3:
        raise RuntimeError(
            'run-level validation requires at least three independent recordings'
        )
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=validation_fraction,
        random_state=seed,
    )
    indices = np.arange(len(image_paths))
    train_indices, validation_indices = next(splitter.split(indices, groups=groups))
    return train_indices, validation_indices, groups


def steering_region_counts(angles):
    angles = np.asarray(angles)
    return {
        'left_below_85': int(np.sum(angles < 85.0)),
        'center_85_to_95': int(np.sum((angles >= 85.0) & (angles <= 95.0))),
        'right_above_95': int(np.sum(angles > 95.0)),
    }


def augment_with_horizontal_flip(images, angles):
    flipped_images = images[:, :, ::-1, :]
    flipped_angles = 180.0 - angles
    return (
        np.concatenate((images, flipped_images), axis=0),
        np.concatenate((angles, flipped_angles), axis=0),
    )


def normalize_angles(angles):
    return (np.asarray(angles, dtype=np.float32) - TARGET_CENTER_DEGREES) / (
        TARGET_SCALE_DEGREES
    )


def angles_from_normalized(values):
    return (
        np.asarray(values, dtype=np.float32) * TARGET_SCALE_DEGREES
        + TARGET_CENTER_DEGREES
    )


def build_nvidia_model():
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(66, 200, 3)),
            keras.layers.Conv2D(24, (5, 5), strides=(2, 2), activation='elu'),
            keras.layers.Conv2D(36, (5, 5), strides=(2, 2), activation='elu'),
            keras.layers.Conv2D(48, (5, 5), strides=(2, 2), activation='elu'),
            keras.layers.Conv2D(64, (3, 3), activation='elu'),
            keras.layers.Dropout(0.2),
            keras.layers.Conv2D(64, (3, 3), activation='elu'),
            keras.layers.Flatten(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(100, activation='elu'),
            keras.layers.Dense(50, activation='elu'),
            keras.layers.Dense(10, activation='elu'),
            keras.layers.Dense(1),
        ],
        name='Nvidia_Model',
    )
    model.compile(
        loss='mse',
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        metrics=['mae'],
    )
    return model


def build_deployment_model(normalized_model):
    degree_output = keras.layers.Rescaling(
        scale=TARGET_SCALE_DEGREES,
        offset=TARGET_CENTER_DEGREES,
        name='steering_angle_degrees',
    )(normalized_model.outputs[0])
    return keras.Model(
        inputs=normalized_model.inputs[0],
        outputs=degree_output,
        name='Nvidia_Steering_Degrees',
    )


def prepare_output_directory(output_directory):
    output_directory = Path(output_directory)
    if output_directory.exists() and any(output_directory.iterdir()):
        raise FileExistsError(
            'output directory is not empty; choose a new path: %s' % output_directory
        )
    output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory


def train_model(
    data_directory,
    output_directory,
    *,
    epochs=50,
    batch_size=32,
    validation_fraction=0.2,
    seed=20260807,
    flip_augmentation=True,
    temporal_group_size=20,
    split_strategy='temporal',
):
    if epochs < 1 or batch_size < 1:
        raise ValueError('epochs and batch_size must be positive')
    if not 0.1 <= validation_fraction <= 0.4:
        raise ValueError('validation_fraction must be between 0.1 and 0.4')
    if temporal_group_size < 2:
        raise ValueError('temporal_group_size must be at least 2')
    if split_strategy not in ('temporal', 'run'):
        raise ValueError('split_strategy must be temporal or run')

    keras.utils.set_random_seed(seed)
    image_paths, angles = discover_dataset(data_directory)
    if split_strategy == 'run':
        train_indices, validation_indices, split_groups = (
            split_dataset_by_run_indices(
                image_paths,
                validation_fraction,
                seed,
            )
        )
    else:
        train_indices, validation_indices, split_groups = split_dataset_indices(
            image_paths,
            validation_fraction,
            seed,
            temporal_group_size,
        )
    train_paths = [image_paths[index] for index in train_indices]
    validation_paths = [image_paths[index] for index in validation_indices]
    train_angles = angles[train_indices]
    validation_angles = angles[validation_indices]
    original_train_angles = train_angles.copy()
    if split_strategy == 'run':
        for split_name, split_angles in (
            ('training', train_angles),
            ('validation', validation_angles),
        ):
            region_counts = steering_region_counts(split_angles)
            if min(region_counts.values()) < 5:
                raise RuntimeError(
                    '%s run split lacks steering coverage: %s; collect another '
                    'complete run with left, center, and right examples'
                    % (split_name, region_counts)
                )
    train_images = load_images(train_paths)
    validation_images = load_images(validation_paths)

    original_train_count = len(train_images)
    if flip_augmentation:
        train_images, train_angles = augment_with_horizontal_flip(
            train_images,
            train_angles,
        )
    train_targets = normalize_angles(train_angles)
    validation_targets = normalize_angles(validation_angles)

    output_directory = prepare_output_directory(output_directory)
    best_model_path = (
        output_directory / 'lane_navigation_best_normalized_do_not_deploy.keras'
    )
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            best_model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-5,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1,
        ),
    ]

    model = build_nvidia_model()
    history = model.fit(
        train_images,
        train_targets,
        validation_data=(validation_images, validation_targets),
        epochs=epochs,
        batch_size=batch_size,
        shuffle=True,
        callbacks=callbacks,
        verbose=2,
    )

    deployment_model = build_deployment_model(model)
    candidate_keras_path = output_directory / 'lane_navigation_candidate.keras'
    candidate_h5_path = output_directory / 'lane_navigation_candidate.h5'
    deployment_model.save(candidate_keras_path)
    deployment_model.save(candidate_h5_path, include_optimizer=False)

    # Batch size 1 matches runtime inference.  Export parity is checked over
    # every validation image rather than a single convenient sample.
    predictions = deployment_model.predict(
        validation_images,
        batch_size=1,
        verbose=0,
    ).reshape(-1)
    errors = predictions - validation_angles
    validation_loss = float(np.mean(np.square(errors)))
    validation_mae = float(np.mean(np.abs(errors)))
    reloaded_model = keras.models.load_model(candidate_h5_path, compile=False)
    reloaded_predictions = reloaded_model.predict(
        validation_images,
        batch_size=1,
        verbose=0,
    )
    export_max_abs_difference = float(
        np.max(np.abs(reloaded_predictions.reshape(-1) - predictions))
    )

    history_data = {
        key: [float(value) for value in values]
        for key, values in history.history.items()
    }
    with (output_directory / 'history.json').open('w', encoding='utf-8') as history_file:
        json.dump(history_data, history_file, indent=2, sort_keys=True)
        history_file.write('\n')

    with (output_directory / 'validation_predictions.csv').open(
        'w', encoding='utf-8', newline=''
    ) as prediction_file:
        writer = csv.DictWriter(
            prediction_file,
            fieldnames=('image', 'expected_angle', 'predicted_angle', 'error'),
        )
        writer.writeheader()
        for path, expected, predicted, error in zip(
            validation_paths,
            validation_angles,
            predictions,
            errors,
        ):
            writer.writerow(
                {
                    'image': path.name,
                    'expected_angle': float(expected),
                    'predicted_angle': float(predicted),
                    'error': float(error),
                }
            )

    summary = {
        'dataset_id': Path(data_directory).name,
        'dataset_sha256': dataset_sha256(image_paths),
        'dataset_images': len(image_paths),
        'train_images_before_augmentation': original_train_count,
        'train_images_after_augmentation': len(train_images),
        'validation_images': len(validation_images),
        'flip_augmentation': flip_augmentation,
        'target_normalization': '(angle - 90) / 90',
        'split_strategy': (
            'held-out source recording runs'
            if split_strategy == 'run'
            else 'source-frame temporal groups'
        ),
        'validation_fraction_requested': validation_fraction,
        'validation_fraction_actual': len(validation_images) / len(image_paths),
        'temporal_group_size': temporal_group_size,
        'train_split_groups': len(np.unique(split_groups[train_indices])),
        'validation_split_groups': len(np.unique(split_groups[validation_indices])),
        'dataset_source_runs': len(
            {source_run_key(path) for path in image_paths}
        ),
        'train_source_runs': sorted(
            {source_run_key(path) for path in train_paths}
        ),
        'validation_source_runs': sorted(
            {source_run_key(path) for path in validation_paths}
        ),
        'dataset_steering_regions': steering_region_counts(angles),
        'train_steering_regions_before_augmentation': steering_region_counts(
            original_train_angles
        ),
        'validation_steering_regions': steering_region_counts(validation_angles),
        'seed': seed,
        'epochs_requested': epochs,
        'epochs_completed': len(history.history['loss']),
        'batch_size': batch_size,
        'validation_mse': validation_loss,
        'validation_rmse': float(math.sqrt(validation_loss)),
        'validation_mae': validation_mae,
        'validation_bias': float(np.mean(errors)),
        'validation_max_absolute_error': float(np.max(np.abs(errors))),
        'validation_angle_min': float(validation_angles.min()),
        'validation_angle_max': float(validation_angles.max()),
        'prediction_min': float(predictions.min()),
        'prediction_max': float(predictions.max()),
        'export_max_abs_difference': export_max_abs_difference,
        'candidate_h5': candidate_h5_path.name,
        'candidate_h5_sha256': sha256_file(candidate_h5_path),
        'candidate_keras': candidate_keras_path.name,
        'normalized_checkpoint': best_model_path.name,
        'normalized_checkpoint_deployable': False,
        'input_contract': 'BGR lower half -> YUV -> blur -> 200x66 -> /255',
        'output_contract': 'one steering angle in degrees',
        'promotion_status': 'candidate_requires_independent_drive_test',
        'validation_limitation': (
            'held-out recordings still require a held-out track layout for '
            'strong generalization evidence'
            if split_strategy == 'run'
            else 'same-session temporal split is not independent'
        ),
        'python_version': sys.version.split()[0],
        'opencv_version': cv2.__version__,
        'numpy_version': np.__version__,
        'keras_version': keras.__version__,
        'tensorflow_version': tf.__version__,
    }
    with (output_directory / 'training_summary.json').open(
        'w', encoding='utf-8'
    ) as summary_file:
        json.dump(summary, summary_file, indent=2, sort_keys=True)
        summary_file.write('\n')
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Train the NVIDIA-style steering-angle regression model.'
    )
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--validation-fraction', type=float, default=0.2)
    parser.add_argument('--temporal-group-size', type=int, default=20)
    parser.add_argument(
        '--split-strategy',
        choices=('temporal', 'run'),
        default='temporal',
        help='use run to keep complete recordings out of training',
    )
    parser.add_argument('--seed', type=int, default=20260807)
    parser.add_argument('--no-flip-augmentation', action='store_true')
    args = parser.parse_args(argv)
    summary = train_model(
        args.data_dir,
        args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
        flip_augmentation=not args.no_flip_augmentation,
        temporal_group_size=args.temporal_group_size,
        split_strategy=args.split_strategy,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
