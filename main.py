import copy_reg
import datetime
import HTMLParser
import json
import multiprocessing
import traceback
import tweepy
import sys
from db import ReadLocations, ReadGeodata, WriteMessages
from subprocess import call

with open('api/api.keys','rb') as f:
	keys = json.loads(f.read())

auth = tweepy.OAuthHandler(keys['CONSUMER_KEY'],keys['CONSUMER_SECRET'])
auth.set_access_token(keys['ACCESS_KEY'], keys['ACCESS_SECRET'])
api = tweepy.API(auth)

#HASHTAGS = ['#FridayFeeling']
HASHTAGS = ['#eclipse2017','#Eclipse2017','#ECLIPSE2017']

_POOL_SIZE = multiprocessing.cpu_count()
_POOL = multiprocessing.Pool(_POOL_SIZE)

class hashbot():

        def start(self):
                try:
                        tweepy.streamListener = processTweets()
                        twitterStream = tweepy.Stream(auth,listener=processTweets())
                        twitterStream.filter(track=HASHTAGS)
                except tweepy.TweepError as t:
                        print t

class processTweets(tweepy.StreamListener):

        def on_data(self,data):
		locs, city, state = list(), '', ''
                decoded = json.loads(data)
                html = HTMLParser.HTMLParser()
                if decoded['text']:
			message = decoded['text'].encode('utf-8')
			try:
				if decoded['user']['location']:
					city = decoded['user']['location'].split(',')[0].strip()
					state = decoded['user']['location'].split(',')[1].strip()
					locs = ReadGeodata().doSearch(city)
			except: pass
			try:
				time = decoded['timestamp_ms']
			 	match = _POOL.map(ReadLocations().doSearch,locs)
				if match:
					self.update_db(decoded['id'],
							time,
							decoded['user']['location'].encode('utf-8'),
							message)
					self.update_log(message)
			except UnicodeDecodeError as e: print traceback.print_tb(sys.exc_info()[2])
			finally: pass

        def on_error(self,status):
                return false

	def update_db(self,id,t,loc,msg):
		WriteMessages().doAdd([id,t,loc,msg])

        def update_log(self,row):
                try:
			date = datetime.datetime.today().strftime('%Y%m%d')
                        with open('/root/totality/logs/'+str(date)+'log.txt','aw') as f:
                                f.write(row+"\n")
                except Exception as e:
			print "ERROR WRITING TO LOG: %s" % str(e)

def _reduce_method(m):
	if m.im_self is None:
		return getattr, (m.im_class, m.im_func.func_name)
	else:
		return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(type(ReadLocations.doSearch), _reduce_method)

if __name__=='__main__':
	hashbot().start()
