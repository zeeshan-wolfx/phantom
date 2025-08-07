import subprocess



def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise Exception(result.stderr or result.stdout)
    return result.stdout