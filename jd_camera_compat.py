"""Camera compatibility helpers for Raspberry Pi OS Bookworm."""

import os
import shutil
import sys


LIBCAMERA_PRELOAD_NAME = 'v4l2-compat.so'
LIBCAMERA_MARKER = 'DEEPTHINKCAR_LIBCAMERIFY_ACTIVE'


def is_libcamera_compat_active(environ=None):
    environ = os.environ if environ is None else environ
    preload = environ.get('LD_PRELOAD', '')
    return (
        environ.get(LIBCAMERA_MARKER) == '1'
        or LIBCAMERA_PRELOAD_NAME in preload
    )


def ensure_libcamerify(
    script_path,
    argv=None,
    environ=None,
    which_fn=shutil.which,
    exec_fn=os.execvpe,
    python_executable=None,
):
    """Re-exec a camera script through libcamerify when it is available."""
    environ = os.environ if environ is None else environ
    if is_libcamera_compat_active(environ):
        return False

    wrapper = which_fn('libcamerify')
    if wrapper is None:
        return False

    child_env = dict(environ)
    child_env[LIBCAMERA_MARKER] = '1'
    command = [
        wrapper,
        python_executable or sys.executable,
        os.path.abspath(script_path),
        *(sys.argv[1:] if argv is None else argv),
    ]
    exec_fn(wrapper, command, child_env)
    return True
