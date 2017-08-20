import json
import MySQLdb
import re

# TO-DO: TRANSLATION TABLE

with open('/var/www/html/python/api/mysql.keys','rb') as f:
        keys = json.loads(f.read())

USER = keys['USER']
PASS = keys['PASSWORD']

STATE_LIST = ['OR','MT','KS','IA','IL',
		'TN','KY','NC','SC','MO',
		'WY','GA','NE','ID']

TRANS_TABLE = {'Oregon':'OR','Montana':'MT','Kansas':'KS','Iowa':'IA', 'Illinois':'IL',
		'Tennessee':'TN','Kentucky':'KY','North Carolina':'NC','South Carolina':'SC','Missouri':'MO',
		'Wyoming':'WY','Georgia':'GA','Nebraska':'NB','Idaho':'ID'}

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
		_delta = .75
		lat, lon = location
		db = MySQLdb.connect(host="localhost",
					user=USER,
                     			passwd=PASS,
                     			db=DB)
		cur = db.cursor()
		query = "SELECT zoneid, starttime, total FROM pathdata_test WHERE (nlat < %f AND %f < slat) AND (nlon > %f AND %f > slon)" % (lat, lat, lon-_delta, lon)
		cur.execute(query)
		match = [t for t in cur.fetchall() if len(t) > 0]
		db.close()
		return match

class ReadGeodata:

	@staticmethod
	def stateName(state):
		try:
			state = TRANS_TABLE[state]
		except KeyError:
			pass
		return state

	@staticmethod
	def doSearch(place):
		place_name = place.split(',')[0]
		state_name = place.split(',')[1].strip()
		if len(state_name) > 2: state_name = ReadGeodata.stateName(state_name)
		if state_name not in STATE_LIST: return []
		results = list()
		db = MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		query = "SELECT lat, lon FROM geodata WHERE asciiname = %s AND admin1code = %s"
		cur.execute(query,(place_name,state_name))
		matches = cur.fetchall()
		db.close()
		return matches

	@staticmethod
	def reverseSearch(geo):
		_delta = .0001
		lat,lon = geo
		db = MySQLdb.connect(host="localhost",
                                        user=USER,
                                        passwd=PASS,
                                        db=DB)
                cur = db.cursor()
                query = "SELECT asciiname FROM geodata WHERE (lat >= %f AND lat <= %f) AND (lon >= %f AND lon <= %f)" % (lat-_delta,lat+_delta,lon-_delta,lon+_delta)
                cur.execute(query)
                match = [t for t in cur.fetchall() if len(t) > 0]
                db.close()
                return match

class ReadStoredData:

	@staticmethod
	def getZone(t):
		db =MySQLdb.connect(host='localhost',
					user=USER,
					passwd=PASS,
					db=DB)
		cur = db.cursor()
		query = "SELECT zone FROM pathdata_test WHERE %d BETWEEN starttime AND total" % t
		cur.execute(query)
		zones = cur.fetchall()
		db.close()
		if len(times) > 0: return zones[0]
		else: return 0

	@staticmethod
	def readMsgs((t1,t2)):
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
