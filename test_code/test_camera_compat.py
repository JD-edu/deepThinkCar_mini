import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jd_camera_compat import ensure_libcamerify, is_libcamera_compat_active


class CameraCompatTest(unittest.TestCase):
    def test_detects_libcamera_preload(self):
        environ = {'LD_PRELOAD': '/usr/libexec/libcamera/v4l2-compat.so'}
        self.assertTrue(is_libcamera_compat_active(environ))

    def test_active_process_is_not_reexecuted(self):
        called = []
        result = ensure_libcamerify(
            'camera.py',
            environ={'DEEPTHINKCAR_LIBCAMERIFY_ACTIVE': '1'},
            which_fn=lambda _: '/usr/bin/libcamerify',
            exec_fn=lambda *args: called.append(args),
        )
        self.assertFalse(result)
        self.assertEqual([], called)

    def test_plain_process_is_reexecuted_with_original_arguments(self):
        called = []
        result = ensure_libcamerify(
            'camera.py',
            argv=['--headless', '--frames', '3'],
            environ={'PATH': '/usr/bin'},
            which_fn=lambda _: '/usr/bin/libcamerify',
            exec_fn=lambda *args: called.append(args),
            python_executable='/usr/bin/python3',
        )

        self.assertTrue(result)
        self.assertEqual('/usr/bin/libcamerify', called[0][0])
        self.assertEqual('/usr/bin/libcamerify', called[0][1][0])
        self.assertEqual('/usr/bin/python3', called[0][1][1])
        self.assertEqual(['--headless', '--frames', '3'], called[0][1][-3:])
        self.assertEqual('1', called[0][2]['DEEPTHINKCAR_LIBCAMERIFY_ACTIVE'])

    def test_missing_wrapper_leaves_process_unchanged(self):
        result = ensure_libcamerify(
            'camera.py',
            environ=os.environ,
            which_fn=lambda _: None,
            exec_fn=lambda *args: self.fail('exec should not be called'),
        )
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
