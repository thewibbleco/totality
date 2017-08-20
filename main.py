import datetime
import json
import traceback
import tweepy
import rw
import sys
from db import ReadGeodata, WriteMessages

#TO-DO IPHONE GEODATA

with open('/var/www/html/python/api/api.keys','rb') as f:
	keys = json.loads(f.read())

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
		_geoflag = ''
		now = rw.getUTC()
                decoded = json.loads(data)
                try:
			if decoded['user']['location'] and not decoded['retweeted'] and not decoded['text'].startswith('RT'):
				id = decoded['id']
				location = decoded['user']['location'].encode('utf-8')
				message = decoded['text'].encode('utf-8')
				time = int(decoded['timestamp_ms'])/1000
				try:
					if decoded['geo']['coordinates']:
						geo = ((decoded['geo']['coordinates'][0],
							decoded['geo']['coordinates'][1]),)
						_geoflag = '*'
						location = ReadGeodata().reverseSearch(geo)[0][0]
				except:
					geo = ReadGeodata().doSearch(location)
				zone = rw.getZones(geo)
				zones = set([z[0] for z in zone])
				print location, zones
				for item in zones: zid, t1, t2 = item
				if len(zones) > 0: rw.writeLog(location + "," + str(zones) + "," + _geoflag)
				if t1 < now < t2:
					#print location
					self.update_db(id,
						        time,
				       			location,
						        message)
					self.update_log(id,
							 zid,
							 time,
							 location,
							 message)
		except Exception as e: rw.errorLog(str(sys.exc_info())) #print sys.exc_info()

        def on_error(self,status):
                print status

	def update_db(self,id,t,loc,msg):
		WriteMessages().doAdd([id,t,loc,msg])

        def update_log(self,id,zid,time,location,message):
                try:
			item = {"t_id":id,"data":{"z_id":zid,"t":time,"loc":location,"msg":message}}
			jsons.append(item)
			#date = datetime.datetime.today().strftime('%Y%m%d%h%M%s')
                        with open('/var/www/html/log/00-eclipse.txt','w') as f:
                                json.dump(jsons,f)
                except Exception as e: print str(e)

if __name__=='__main__':
	hashbot().start()
