import sys
import pathlib

CWD = pathlib.Path(__file__).parent.absolute()

if CWD not in sys.path:
    sys.path.append(CWD)
