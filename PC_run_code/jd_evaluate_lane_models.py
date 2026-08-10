"""Compare deepThinkCar steering models on one saved validation split.

The training command writes ``validation_predictions.csv`` so later model
comparisons can reuse exactly the same images and expected steering angles.
Model specifications use ``LABEL=PATH`` to keep the JSON output stable even
when several files share the same basename.
"""

import argparse
import csv
import json
import math
from pathlib import Path

import cv2
import keras
import numpy as np

from jd_deep_learning import img_preprocess, sha256_file


def parse_model_spec(value):
    label, separator, path = value.partition('=')
    if not separator or not label or not path:
        raise argparse.ArgumentTypeError('model must use LABEL=PATH')
    return label, Path(path)


def load_validation_data(data_directory, validation_csv):
    data_directory = Path(data_directory)
    image_names = []
    expected_angles = []
    images = []

    with Path(validation_csv).open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        required_fields = {'image', 'expected_angle'}
        if not required_fields.issubset(reader.fieldnames or []):
            raise ValueError(
                'validation CSV must contain image and expected_angle columns'
            )
        for row in reader:
            image_name = row['image']
            image_path = data_directory / image_name
            image = cv2.imread(str(image_path))
            if image is None:
                raise RuntimeError('OpenCV could not read image: %s' % image_path)
            image_names.append(image_name)
            expected_angles.append(float(row['expected_angle']))
            images.append(img_preprocess(image))

    if not images:
        raise RuntimeError('validation CSV contains no rows')
    if len(image_names) != len(set(image_names)):
        raise ValueError('validation CSV contains duplicate image names')
    return (
        image_names,
        np.asarray(images, dtype=np.float32),
        np.asarray(expected_angles, dtype=np.float32),
    )


def regression_metrics(expected, predicted):
    expected = np.asarray(expected, dtype=np.float32).reshape(-1)
    predicted = np.asarray(predicted, dtype=np.float32).reshape(-1)
    if expected.shape != predicted.shape:
        raise ValueError('expected and predicted values must have the same shape')
    if not np.isfinite(predicted).all():
        raise ValueError('model returned a non-finite prediction')
    errors = predicted - expected
    mse = float(np.mean(np.square(errors)))
    return {
        'validation_images': len(expected),
        'validation_mse': mse,
        'validation_rmse': float(math.sqrt(mse)),
        'validation_mae': float(np.mean(np.abs(errors))),
        'validation_bias': float(np.mean(errors)),
        'validation_max_absolute_error': float(np.max(np.abs(errors))),
        'prediction_min': float(predicted.min()),
        'prediction_max': float(predicted.max()),
    }


def evaluate_model(model_path, images, expected_angles):
    model_path = Path(model_path)
    model = keras.models.load_model(model_path, compile=False)
    if tuple(model.input_shape[-3:]) != (66, 200, 3):
        raise ValueError('%s input must be (66, 200, 3)' % model_path)
    if tuple(model.output_shape[-1:]) != (1,):
        raise ValueError('%s must return one steering angle' % model_path)
    predictions = model.predict(images, batch_size=1, verbose=0).reshape(-1)
    result = regression_metrics(expected_angles, predictions)
    result.update(
        {
            'model_path': str(model_path),
            'model_sha256': sha256_file(model_path),
        }
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Compare steering models on a saved validation manifest.'
    )
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--validation-csv', type=Path, required=True)
    parser.add_argument(
        '--model',
        action='append',
        type=parse_model_spec,
        required=True,
        metavar='LABEL=PATH',
    )
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)

    image_names, images, expected_angles = load_validation_data(
        args.data_dir,
        args.validation_csv,
    )
    results = {
        'validation_csv': str(args.validation_csv),
        'validation_images': len(image_names),
        'validation_angle_min': float(expected_angles.min()),
        'validation_angle_max': float(expected_angles.max()),
        'models': {
            label: evaluate_model(path, images, expected_angles)
            for label, path in args.model
        },
    }
    rendered = json.dumps(results, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
