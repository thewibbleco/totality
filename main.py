import datetime
import json
import traceback
import tweepy
import rw
import sys
from db import ReadGeodata, WriteMessages

with open('api/api.keys','rb') as f:
	keys = json.loads(f.read())

auth = tweepy.OAuthHandler(keys['CONSUMER_KEY'],keys['CONSUMER_SECRET'])
auth.set_access_token(keys['ACCESS_KEY'], keys['ACCESS_SECRET'])
api = tweepy.API(auth)

HASHTAGS = ['#eclipse2017','#Eclipse2017','#ECLIPSE2017']

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
		now = rw.getUTC()
                decoded = json.loads(data)
                try:
			if decoded['user']['location'] and not decoded['retweeted']:
				id = decoded['id']
				location = decoded['user']['location'].encode('utf-8')
				message = decoded['text'].encode('utf-8')
				time = int(decoded['timestamp_ms'])/1000
				geo = ReadGeodata().doSearch(location)
				zone = rw.getZones(geo)
				zones = set([z[0] for z in zone])
				for item in zones: zid, t1, t2 = item
				if zid: print t1, t2, now, zid
				if t1 < now < t2:
					self.update_db(id,
						        time,
				       			location,
						        message)
					self.update_log(message)
		except Exception as e: pass

        def on_error(self,status):
                return True

	def update_db(self,id,t,loc,msg):
		WriteMessages().doAdd([id,t,loc,msg])

        def update_log(self,row):
                try:
			date = datetime.datetime.today().strftime('%Y%m%d')
                        with open('/root/totality/logs/'+str(date)+'log.txt','aw') as f:
                                f.write(row+"\n")
                except Exception as e: pass

if __name__=='__main__':
	hashbot().start()
