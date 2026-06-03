
def pre_build(**kwargs):
    import subprocess
    subprocess.run([
        "pip", "install", "--upgrade",
        "cython>=3.0.0,<4"
    ], check=True)
