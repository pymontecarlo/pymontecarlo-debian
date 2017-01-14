""""""

# Standard library modules.
import os
import subprocess

# Third party modules.

# Local modules.

# Globals and constants variables.

def extract_exe_info(filepath):
    """
    Runs the sigcheck.exe utility and returns a dictionary with the information.
    
    Sigcheck v2.03 - File version and signature viewer
    Copyright (C) 2004-2014 Mark Russinovich
    """
    cwd = os.path.dirname(__file__)
    command = ['wine', 'sigcheck.exe', '-a', '-q', filepath]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=cwd)
    proc.wait()

    exe_info = {}
    for line in proc.stdout.readlines():
        if not line.startswith(b'\t'):
            continue
        key, value = line.split(b':', 1)
        key = key.strip().decode('ascii', 'ignore')
        value = value.strip().decode('ascii', 'ignore')
        exe_info[key] = value

    proc.stdout.close()

    return exe_info