import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PC_RUN_CODE = PROJECT_ROOT / 'PC_run_code'
sys.path.insert(0, str(PC_RUN_CODE))
EVALUATION_SCRIPT = PC_RUN_CODE / 'jd_evaluate_lane_models.py'
SPEC = importlib.util.spec_from_file_location(
    'jd_evaluate_lane_models',
    EVALUATION_SCRIPT,
)
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class LaneModelEvaluationTest(unittest.TestCase):
    def test_model_spec_requires_label_and_path(self):
        label, path = evaluation.parse_model_spec('candidate=models/model.h5')
        self.assertEqual('candidate', label)
        self.assertEqual(Path('models/model.h5'), path)
        with self.assertRaises(evaluation.argparse.ArgumentTypeError):
            evaluation.parse_model_spec('models/model.h5')

    def test_regression_metrics(self):
        metrics = evaluation.regression_metrics(
            np.asarray([80.0, 90.0, 100.0]),
            np.asarray([82.0, 89.0, 97.0]),
        )
        self.assertAlmostEqual(14.0 / 3.0, metrics['validation_mse'], places=6)
        self.assertAlmostEqual(2.0, metrics['validation_mae'])
        self.assertAlmostEqual(-2.0 / 3.0, metrics['validation_bias'])
        self.assertEqual(3.0, metrics['validation_max_absolute_error'])

    def test_regression_metrics_rejects_non_finite_values(self):
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            evaluation.regression_metrics([90.0], [float('nan')])


if __name__ == '__main__':
    unittest.main()
