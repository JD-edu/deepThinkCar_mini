import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jd_servo_config import (
    DEFAULT_CENTER_ANGLE,
    load_center_angle,
    load_servo_offset,
    save_center_angle,
    validate_center_angle,
)


class ServoConfigTest(unittest.TestCase):
    def test_missing_config_uses_current_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'missing.json'
            self.assertEqual(DEFAULT_CENTER_ANGLE, load_center_angle(path))

    def test_saved_center_is_loaded_as_shared_offset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'servo.json'
            save_center_angle(97.0, path)
            self.assertEqual(97.0, load_center_angle(path))
            self.assertEqual(7.0, load_servo_offset(path))
            data = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(97.0, data['center_angle'])

    def test_invalid_file_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'servo.json'
            path.write_text('{broken', encoding='utf-8')
            self.assertEqual(DEFAULT_CENTER_ANGLE, load_center_angle(path))

    def test_drive_requires_a_saved_valid_calibration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'missing.json'
            with self.assertRaisesRegex(RuntimeError, 'required for --drive'):
                load_center_angle(path, require_saved=True)

    def test_unsafe_center_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_center_angle(140)


if __name__ == '__main__':
    unittest.main()
