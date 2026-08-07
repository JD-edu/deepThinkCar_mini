"""Persistent steering-servo calibration shared by driving scripts."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path


DEFAULT_CENTER_ANGLE = 90.0
MIN_CENTER_ANGLE = 60.0
MAX_CENTER_ANGLE = 130.0


def calibration_path():
    override = os.environ.get('DEEPTHINKCAR_SERVO_CONFIG')
    if override:
        return Path(override).expanduser()
    return Path.home() / '.config' / 'deepthinkcar' / 'servo_calibration.json'


def validate_center_angle(angle):
    if isinstance(angle, bool) or not isinstance(angle, (int, float)):
        raise ValueError('servo center angle must be numeric')
    angle = float(angle)
    if not MIN_CENTER_ANGLE <= angle <= MAX_CENTER_ANGLE:
        raise ValueError(
            'servo center angle must be between %.0f and %.0f degrees'
            % (MIN_CENTER_ANGLE, MAX_CENTER_ANGLE)
        )
    return angle


def load_center_angle(path=None, *, require_saved=False):
    path = calibration_path() if path is None else Path(path)
    try:
        with path.open(encoding='utf-8') as calibration_file:
            data = json.load(calibration_file)
        return validate_center_angle(data['center_angle'])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        if require_saved:
            raise RuntimeError(
                'a valid saved servo calibration is required for --drive; '
                'run python3 test_code/calibration.py and save the center angle'
            ) from error
        return DEFAULT_CENTER_ANGLE


def save_center_angle(angle, path=None):
    angle = validate_center_angle(angle)
    path = calibration_path() if path is None else Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + '.tmp')
    data = {
        'center_angle': angle,
        'offset_from_90': angle - 90.0,
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    with temporary_path.open('w', encoding='utf-8') as calibration_file:
        json.dump(data, calibration_file, indent=2)
        calibration_file.write('\n')
    temporary_path.replace(path)
    return path


def load_servo_offset(path=None):
    return load_center_angle(path) - 90.0
