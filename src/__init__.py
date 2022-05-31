import sys
import pathlib

CWD = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(CWD))
print(sys.path)