import json
import MySQLdb
import re

with open('api/mysql.keys','rb') as f:
        keys = json.loads(f.read())

USER = keys['USER']
PASS = keys['PASSWORD']

DB = 'totality'

class WriteMessages:

	@staticmethod
	def doAdd(data):
		table = 'twitter'
		db = MySQLdb.connect(host="localhost",
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		query = "INSERT INTO twitter (id, time, location, tweet) VALUES (%s,%s,%s,%s)"
		try:
			cur.execute(query,(data[0], data[1], data[2], re.escape(data[3]) ) )
			db.commit()
		except Exception as e: print str(e)  #print "ERROR: AT QUERY"

class ReadLocations:

	def doSearch(self,location):
		lat, lon = location
		db = MySQLdb.connect(host="localhost",
					user=USER,
                     			passwd=PASS,
                     			db=DB)
		cur = db.cursor()
		query = "SELECT starttime,total FROM pathdata WHERE (%f BETWEEN slat AND nlat) AND (%f BETWEEN slon AND nlon)" % (lat, lon)
		cur.execute(query)
		match = [t for t in cur.fetchall()]
		db.close()
		return match

class ReadGeodata:

	@staticmethod
	def doSearch(place_name):
		results = list()
		db = MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		cur.execute("SELECT lat, lon FROM geodata WHERE asciiname LIKE '" + place_name + "' AND (lat BETWEEN 13.6 AND 44.5) AND (lon BETWEEN -164.6 AND -36.6)")
		for row in cur.fetchall():
			results.append(row)
		db.close()
		return results
