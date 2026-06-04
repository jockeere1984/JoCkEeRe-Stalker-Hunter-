import subprocess
import os

def pre_build(**kwargs):
    # Force Cython 3.x
    subprocess.run(
        ["python3.10", "-m", "pip", "install", "--upgrade", "cython>=3.0.0,<4"],
        check=False
    )
    # Force python-for-android to use Python 3.10
    os.environ['PYTHON'] = '/usr/bin/python3.10'
    os.environ['PYTHONPATH'] = ''
