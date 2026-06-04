import subprocess

def pre_build(**kwargs):
    subprocess.run(
        ["pip3", "install", "--upgrade", "cython>=3.0.0,<4"],
        check=True
    )
