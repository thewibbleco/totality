import copy_reg
import datetime
import multiprocessing
from db import ReadGeodata, ReadLocations, ReadStoredData

_POOL_SIZE = multiprocessing.cpu_count()
_POOL = multiprocessing.Pool(_POOL_SIZE)

def getUTC():
	return (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds()

def getWindow():
	now = getUTC()
	window = ReadStoredData().readTimes(now)
	if window: msgs = ReadStoredData().readMsgs(window)

	#try:
                        #       if decoded['user']['location']:
                        #               city = decoded['user']['location'].split(',')[0].strip()
                        #               state = decoded['user']['location'].split(',')[1].strip()
                        #               locs = ReadGeodata().doSearch(city)
                        #except: pass
                        #try:
                        #       match = _POOL.map(ReadLocations().doSearch,locs)
                        #       if match:
                        #               self.update_db(decoded['id'],
                        #                               time,
                        #                               decoded['user']['location'].encode('utf-8'),
                        #                               message)
                        #               self.update_log(message)

def _reduce_method(m):
        if m.im_self is None:
                return getattr, (m.im_class, m.im_func.func_name)
        else:
                return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(type(ReadLocations.doSearch), _reduce_method)

