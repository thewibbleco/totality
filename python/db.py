import json
import MySQLdb
import re

'''
Setting up the passwords, tokens.
'''

with open('/var/www/html/python/api/mysql.keys','rb') as f:
        keys = json.loads(f.read())

USER = keys['USER']
PASS = keys['PASSWORD']

'''
Limit our queries to only those that matter, and for those users who put their states in in full text,
create a translation table.
'''

STATE_LIST = ['OR','MT','KS','IA','IL',
		'TN','KY','NC','SC','MO',
		'WY','GA','NE','ID']

TRANS_TABLE = {'Oregon':'OR','Montana':'MT','Kansas':'KS','Iowa':'IA', 'Illinois':'IL',
		'Tennessee':'TN','Kentucky':'KY','North Carolina':'NC','South Carolina':'SC','Missouri':'MO',
		'Wyoming':'WY','Georgia':'GA','Nebraska':'NB','Idaho':'ID'}

'''
The DB in total(ity).
'''

DB = 'totality'

class WriteMessages:

	'''
	Write to Twitter table. That re.escape is brutal, though.
	'''

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

	'''
	Do the lookup for zones and times in the path table. The SQL for this is in /sql.
	'''

	def doSearch(self,location):
		_delta = .75
		lat, lon = location
		db = MySQLdb.connect(host="localhost",
					user=USER,
                     			passwd=PASS,
                     			db=DB)
		cur = db.cursor()
		query = "SELECT zoneid, starttime, total FROM pathdata WHERE (nlat < %f AND %f < slat) AND (nlon > %f AND %f > slon)" % (lat+_delta, lat, lon-_delta, lon)
		cur.execute(query)
		match = [t for t in cur.fetchall() if len(t) > 0]
		db.close()
		return match

class ReadGeodata:

	'''
	Do the locomtion.
	'''

	@staticmethod
	def stateName(state):
		try:
			state = TRANS_TABLE[state]
		except KeyError:
			pass
		return state

	'''
	This is the beastly lookup table for locations from free text. pretty reliable, I have a fuller set of data, but
	query times slowed main down too much, so I removed all clearly-irrelevant data from states which wheren't in the path
	to arrive at this slimmer version.
	'''

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

	'''
	The previous method does a lookup on the label from free text; this does backward lookup for geodata. There's a small
	delta modifier which makes the query work, as it looks for something which actually returns values rather than looking for
	a dead-on value. This returns free text values for locations represented by the given coords.
	'''

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

	'''
	I confess that many of these are not used.
	'''

	'''
	This gets zone information for timings.
	'''

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

	'''
	A method only existing for debug/SQL queries to check data.
	'''

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
