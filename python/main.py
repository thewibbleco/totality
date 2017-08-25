import datetime
import json
import traceback
import tweepy
import rw
import sys
from db import ReadGeodata, WriteMessages

'''
Ran the script as a Cron job, so absolute path was necessary. For your application it may not be.
'''

with open('/var/www/html/python/api/api.keys','rb') as f:
	keys = json.loads(f.read())

'''
Twitter authentication and a couple of setup steps, including writing the initial array in the JSON
file, hashtags and terms to search, initializing the JSON list object.
'''

auth = tweepy.OAuthHandler(keys['CONSUMER_KEY'],keys['CONSUMER_SECRET'])
auth.set_access_token(keys['ACCESS_KEY'], keys['ACCESS_SECRET'])
api = tweepy.API(auth)

HASHTAGS = ['#eclipse2017','#Eclipse2017','#ECLIPSE2017','eclipse',
		'Eclipse','ECLIPSE','Eclipse 2017','eclipse 2017',
		'totality','Totality','path of totality','sun','moon',
		'corona', 'Sun','Moon']

FILENAME = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')

jsons = list()
rw.initJSON(FILENAME)

'''
General class to initiate the stream, using the processTweets class to all the lifting, sorting,
stacking, and bottle-washing.
'''

class hashbot():

        def start(self):
                try:
                        tweepy.streamListener = processTweets()
                        twitterStream = tweepy.Stream(auth,listener=processTweets())
                        twitterStream.filter(track=HASHTAGS, async=True)
                except tweepy.TweepError as t:
                        print t

class processTweets(tweepy.StreamListener):

        def on_data(self,data):
		'''
		Setup markers for geodata (console logging), the current time, and the Twitter obeject (data)
		'''
		_geoflag = ''
		now = rw.getUTC()
                decoded = json.loads(data)
                '''
		Not the most elegant try/catch, but it returns mostly index errors, key errors, and the occasional unset
		variable. You can do much better, I imagine. The first part decodes all the stuff we're interested in.
		'''
		try:
			if decoded['user']['location'] and not decoded['retweeted'] and not decoded['text'].startswith('RT'):
				id = decoded['id_str']
				user = decoded['user']['screen_name']
				location = decoded['user']['location'].encode('utf-8')
				message = decoded['text'].encode('utf-8')
				time = int(decoded['timestamp_ms'])/1000
				'''
				Built to handle geodata, if set by the user. Surprisingly few users in our sample set use
				the feature, but it is helpful to have to supplement the data and get a more complete picture
				of who/what/where/when. As with all things Twitter, no one ever knows "why."
				'''
				try:
					if decoded['geo']['coordinates']:
						geo = ((decoded['geo']['coordinates'][0],
							decoded['geo']['coordinates'][1]),)
						_geoflag = '*'
						location = ReadGeodata().reverseSearch(geo)[0][0]
				except:
				'''
				Should geodata not be set, do a lookup of the plain text location field. The SQL for the table
				referenced in this method is included in /sql.
				'''
					geo = ReadGeodata().doSearch(location)
				'''
				Figure out where the associated coordinates live on the eclipse path. This table is also located
				in /sql.
				'''
				zone = rw.getZones(geo)
				zones = set([z[0] for z in zone])
				'''
				Helpful console logging; comment out if unhelpful.
				'''
				print location, zones
				'''
				If in a zone, when should the eclipse start (t1) and end (t2)?
				'''
				for item in zones: zid, t1, t2 = item
				if len(zones) > 0: rw.writeLog(location + "," + str(zones) + "," + _geoflag)
				if t1 < now < t2:
					'''
					These put the -fun- in -function-.
					'''
					#print location
					self.update_db(id,
						        time,
				       			location,
						        message)
					self.update_log(id,
							 user,
							 zid,
							 time,
							 location,
							 message)
		except Exception as e: rw.errorLog(str(sys.exc_info())) #print sys.exc_info()

        def on_error(self,status):
                print status

	def update_db(self,id,t,loc,msg):
		WriteMessages().doAdd([id,t,loc,msg])

        def update_log(self,id,user,zid,time,location,message):
                '''
		This is the site log used to construct the text body - typical JSON.
		'''
		try:
			item = {"t_id":id,"data":{"z_id":zid,"t":time,"loc":location,"msg":message,"user":user}}
			jsons.append(item)
			#date = datetime.datetime.today().strftime('%Y%m%d%h%M%s')
                        with open('/var/www/html/log/00-eclipse.txt','w') as f:
                                json.dump(jsons,f)
                except Exception as e: print str(e)

if __name__=='__main__':
	hashbot().start()
