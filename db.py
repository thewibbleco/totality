import json
import MySQLdb
import re

with open('api/mysql.keys','rb') as f:
        keys = json.loads(f.read())

USER = keys['USER']
PASS = keys['PASSWORD']

STATE_LIST = ['OR','MT','KS','IA','IL',
		'TN','KY','NC','SC','MO',
		'WY','GA','NE','ID']

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
		query = "SELECT zoneid, starttime, total FROM pathdata WHERE (nlat < %f AND %f < slat) AND (nlon > %f AND %f > slon)" % (lat, lat, lon, lon)
		cur.execute(query)
		match = [t for t in cur.fetchall() if len(t) > 0]
		db.close()
		return match

class ReadGeodata:

	@staticmethod
	def doSearch(place):
		place_name = place.split(',')[0]
		state_name = place.split(',')[1].strip()
		if state_name not in STATE_LIST: return []
		results = list()
		db = MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		cur.execute("SELECT lat, lon FROM slim_geodata WHERE asciiname = '" + place_name + "' AND admin1code = '" + state_name + "'")
		matches = cur.fetchall()
		db.close()
		return matches

class ReadStoredData:

	@staticmethod
	def getZone(t):
		db =MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		query = "SELECT zone FROM pathdata WHERE %d BETWEEN starttime AND total" % t
		cur.execute(query)
		zones = cur.fetchall()
		db.close()
		if len(times) > 0: return zones[0]
		else: return 0

	@staticmethod
	def getWindow(zone):
                db = MySQLdb.connect(host='localhost',
                                        user=USER,
                                        passwd=PASS,
                                        db=DB)
                cur = db.cursor()
                query = "SELECT starttime,total FROM pathdata WHERE zone = " % (zone)
                cur.execute(query)
                matches = cur.fetchall()
                db.close()


	@staticmethod
	def readMsgs((t1,t2)):
		print t1,t2
		results = list()
		db = MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		query = "SELECT id,location,tweet FROM twitter WHERE time BETWEEN %d AND %d" % (t1,t2)
		cur.execute(query)
		matches = [r for r in cur.fetchall()]
		db.close()
		return matches
