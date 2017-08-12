import datetime
import json
import traceback
import tweepy
import sys
from db import WriteMessages

with open('api/api.keys','rb') as f:
	keys = json.loads(f.read())

auth = tweepy.OAuthHandler(keys['CONSUMER_KEY'],keys['CONSUMER_SECRET'])
auth.set_access_token(keys['ACCESS_KEY'], keys['ACCESS_SECRET'])
api = tweepy.API(auth)

HASHTAGS = ['#SongsWithLowSelfEsteem']
#HASHTAGS = ['#eclipse2017','#Eclipse2017','#ECLIPSE2017']

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
                decoded = json.loads(data)
                if decoded['text']:
			message = decoded['text'].encode('utf-8')
			time = decoded['timestamp_ms']
			try:
				self.update_db(decoded['id'],
						time,
						decoded['user']['location'].encode('utf-8'),
						message)
				self.update_log(message)
			except UnicodeDecodeError as e: print traceback.print_tb(sys.exc_info()[2])
			except Exception as e: pass #print traceback.print_tb(sys.exc_info()[2])
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

if __name__=='__main__':
	hashbot().start()
