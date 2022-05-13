import sys
import pathlib

CWD = pathlib.Path(__file__).parent.aboslute()

if CWD not in sys.path:
    sys.path.append(CWD)
