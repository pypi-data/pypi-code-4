import sqlite3
import cPickle

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

data = [ 0, 1, 2, 3]


cursor.execute("create table notes (id integer, file blob)")
cursor.execute("INSERT INTO notes (id, file) VALUES(0, ?)", [sqlite3.Binary(cPickle.dumps(data,cPickle.HIGHEST_PROTOCOL))])
conn.commit()

cursor.execute("SELECT file FROM notes WHERE id = 0")

stride = 4
row = str(cursor.fetchone()[0])
for i in range(0,4,stride):
    print row[i:i+stride]

cursor.close()
conn.close()