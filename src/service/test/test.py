import sys
import pathlib

SERVICE_ROOT = pathlib.Path(__file__).parent.parent
print('\nservice root', SERVICE_ROOT)
sys.path.append(str(SERVICE_ROOT))

print(sys.path)

from database import news_db

db = news_db.NewsDb()
