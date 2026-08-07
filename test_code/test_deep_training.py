import importlib.util
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_SCRIPT = PROJECT_ROOT / 'PC_run_code' / 'jd_deep_learning.py'
SPEC = importlib.util.spec_from_file_location('jd_deep_learning', TRAINING_SCRIPT)
training = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(training)


class DeepTrainingTest(unittest.TestCase):
    def test_label_parser_accepts_course_filename_format(self):
        self.assertEqual(0, training.parse_steering_angle('run_f000001_000.png'))
        self.assertEqual(90, training.parse_steering_angle('run_f000002_090.png'))
        self.assertEqual(180, training.parse_steering_angle('run_f000003_180.png'))

    def test_label_parser_rejects_invalid_filename(self):
        with self.assertRaises(ValueError):
            training.parse_steering_angle('frame.png')
        with self.assertRaises(ValueError):
            training.parse_steering_angle('frame_181.png')

    def test_preprocess_shape_type_and_range(self):
        image = np.zeros((240, 320, 3), dtype=np.uint8)
        image[:, :, 1] = 200
        processed = training.img_preprocess(image)
        self.assertEqual((66, 200, 3), processed.shape)
        self.assertEqual(np.float32, processed.dtype)
        self.assertGreaterEqual(float(processed.min()), 0.0)
        self.assertLessEqual(float(processed.max()), 1.0)

    def test_dataset_discovery_uses_only_compatible_png_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = np.zeros((24, 32, 3), dtype=np.uint8)
            for index in range(10):
                cv2.imwrite(str(root / ('run_%03d_090.png' % index)), image)
            (root / 'manifest.csv').write_text('ignored')
            paths, angles = training.discover_dataset(root)
            self.assertEqual(10, len(paths))
            self.assertTrue(np.all(angles == 90))

    def test_model_has_expected_input_and_scalar_output(self):
        model = training.build_nvidia_model()
        self.assertEqual((None, 66, 200, 3), model.input_shape)
        self.assertEqual((None, 1), model.output_shape)
        deployment_model = training.build_deployment_model(model)
        inputs = np.zeros((1, 66, 200, 3), dtype=np.float32)
        normalized = model.predict(inputs, verbose=0)
        degrees = deployment_model.predict(inputs, verbose=0)
        np.testing.assert_allclose(
            degrees,
            normalized * 90.0 + 90.0,
            rtol=1e-5,
            atol=1e-5,
        )

    def test_temporal_split_does_not_share_frame_groups(self):
        paths = [Path('run_f%06d_090.png' % index) for index in range(100)]
        train, validation, groups = training.split_dataset_indices(
            paths,
            validation_fraction=0.2,
            seed=7,
            temporal_group_size=10,
        )
        self.assertTrue(set(groups[train]).isdisjoint(set(groups[validation])))


if __name__ == '__main__':
    unittest.main()
