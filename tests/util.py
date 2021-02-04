import os
cwd = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cwd, 'data')

def datafile(s: str) -> str:
    return os.path.join(data_dir, s)