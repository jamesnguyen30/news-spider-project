import sys
import pathlib

SERVICE_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.append(str(SERVICE_ROOT))

print(sys.path)

from database import news_db

test = news_db.NewsDb()
