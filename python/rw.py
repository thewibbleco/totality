import copy_reg
import datetime
import json
import multiprocessing
from db import ReadGeodata, ReadLocations, ReadStoredData

'''
Fair Warning: many of these routines aren't used. I planned to do something with them
at some point, but in the end, I didn't get around to many of them.
'''

'''
Setting up processor threading for resource-intensive MySQL calls.
'''

_POOL_SIZE = multiprocessing.cpu_count()
_POOL = multiprocessing.Pool(_POOL_SIZE)

'''
Date right now to seconds
'''
def getUTC():
	return (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds()

'''
Get the window happening at the current moment.
'''
def getWindow():
	now = getUTC()
	window = ReadStoredData().readTimes(now)
	return window

'''
Abstraction to read the tweets table. Probably used for debugging.
'''

def getMsgs(window):
	msgs = ReadStoredData().readMsgs(window)
	return msgs

'''
Retrieves zone ids for various coordinate locations. It appears that I didn't abstract
these calls in main, I just went right for 'em!
'''

def getZones(geo):
	match = _POOL.map(ReadLocations().doSearch,geo)
	return match

'''
Retrieve the location free text name for a given set of coordinates.
'''

def getReverse(geo):
	match = _POOL.map(ReadLocations().reverseSearch,geo)
	return match

'''
This is the loneliest function that you'll ever know.
'''

def saveJSON(message):
	pass

'''
Sets up blank JSON file with an empty array to be augmented.
'''

def initJSON(FILENAME):
	date = datetime.datetime.today().strftime('%Y%m%d%h%M%s')
	with open('/var/www/html/log/00-eclipse.txt','aw') as f:
        	json.dump([],f)


'''
Writes matching locations to the output log.
'''

def writeLog(logline):
	with open('/var/www/html/log/00-termlog.txt','aw') as f:
		f.write(str(logline)+"\r\n")

'''
This gets really big really fast. You should probably handle exceptions more gracefully than I.
'''

def errorLog(logline):
	with open('/var/www/html/log/00-errorlog.txt','aw') as f:
		f.write(logline+"\r\n")

'''
To call the db functions with multiprocessing, being that this is Python 2.7, we have to register
the custom methods. The methods have to be pickled to go from proc to proc. This thread is MVP:

https://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods

'''

def _reduce_method(m):
        if m.im_self is None:
                return getattr, (m.im_class, m.im_func.func_name)
        else:
                return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(type(ReadLocations().doSearch), _reduce_method)

if __name__ == '__main__':
	pass
