import os
import sqlite3

path = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(path, 'library.db')

db = sqlite3.connect(file)
db.close()