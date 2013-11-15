"""
create empty database for MyTrip
"""

import sqlite3 as lite
import os

dbname = 'mytrip.db'
if os.path.exists(dbname):
    print 'Databasefile existing already! Please delete manually!'
    raise ValueError, 'STOPPED'

#/// connect ///
con = lite.connect(dbname)
cur = con.cursor()

#--- CATEGORY ---
cur.execute('CREATE TABLE Category(id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(64) UNIQUE );')
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'Unknown'])
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'FrancePassion'])
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'Camping Municipal'])
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'Camping Commercial'])
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'AireCampingCars'])
cur.execute('INSERT INTO Category VALUES (?,?)',[None,'Others'])

#--- WEEKDAYS ---
cur.execute('CREATE TABLE WeekDays(id INTEGER PRIMARY KEY AUTOINCREMENT, day INTEGER UNIQUE, name varchar(16) );')
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'1','Monday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'2','Tuesday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'3','Wednsday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'4','Thursday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'5','Friday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'6','Saturday'])
cur.execute('INSERT INTO WeekDays VALUES (?,?,?)',[None,'7','Sunday'])


#--- LOCATION ---
cur.execute('CREATE TABLE Location(id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, lon REAL, name varchar(255), status INTEGER DEFAULT 0, stars INTEGER DEFAULT 0, Adress varchar(255));') #status: visited/not visited

#--- Place (sleeping location for camping car) ---
cur.execute('CREATE TABLE Place(id INTEGER PRIMARY KEY AUTOINCREMENT, loc_id INTEGER , cat_id INTEGER DEFAULT 1, FOREIGN KEY(loc_id) REFERENCES Location(id), FOREIGN KEY(cat_id) REFERENCES Category(id) );')

#--- MARKET (n:m mapping of locations and market-days) ---
cur.execute('CREATE TABLE Market(id INTEGER PRIMARY KEY AUTOINCREMENT, loc_id INTEGER, day INTEGER, FOREIGN KEY(loc_id) REFERENCES Location(id) , FOREIGN KEY(day) REFERENCES WeekDays(day));')

#--- MAPS ---
cur.execute('CREATE TABLE Map(id INTEGER PRIMARY KEY AUTOINCREMENT, map BLOB );')

#--- MAP2LOC ---
cur.execute('CREATE TABLE Map2Location(id INTEGER PRIMARY KEY AUTOINCREMENT, loc_id INTEGER, map_id INTEGER, FOREIGN KEY(loc_id) REFERENCES Location(id), FOREIGN KEY(map_id) REFERENCES Maps(id) );')





#--- Details ---
cur.execute('CREATE TABLE Details(id INTEGER PRIMARY KEY AUTOINCREMENT, loc_id INTEGER UNIQUE, description TEXT, FOREIGN KEY(loc_id) REFERENCES Location(id) );')



#--- commit results to database ---
con.commit() #this is important as otherwise table remains empty





#~ cur.execute("SELECT * FROM Location")
#~ rows=cur.fetchall()


#~ for row in rows:
    #~ print row

#~ print len(rows)
