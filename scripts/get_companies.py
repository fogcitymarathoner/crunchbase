import requests
import pymongo
import json
import sys
import sched, time

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def get_page_record_page(x, db):
    """
    scheduled (deferred) task that pulls down summary page number x
    and records data into database
    :param x:
    :return:
    """
    r = requests.get('https://api.crunchbase.com/v/2/organizations?user_key=4c8d0795c93056f45eb38d1a16ddd71f&page=%s'%x)
    #print strip_non_ascii(r.text)
    data = json.loads(r.text)
    #print r.text
    #quit()
    for y in data['data']['items']:
        o = {
          'name': y['name'],
          'path': y['path'],
        }
        db.crunchbase.update(o, o, True)
        sys.stdout.write('.')
        sys.stdout.flush()
    if x < 400:

        print time.time()
        new_date = dt.now() + datetime.timedelta(minutes=5)
        daily_time = new_date.time()
        print daily_time
        #quit()
        t = dt.combine(dt.now() + datetime.timedelta(days=0), daily_time)
        logging.debug('RUNNING: again')
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(time.mktime(t.timetuple()), 1, get_page_record_page, (x+1, db))
        scheduler.run()

import daemon # install python-daemon from pypi
import os
import sys
import sched
import time
from datetime import datetime as dt
import datetime
import logging

def now_str():
    """Return hh:mm:ss string representation of the current time."""
    t = dt.now().time()
    return t.strftime("%H:%M:%S")


def main():
    def do_something_again(message):
        print 'RUNNING:', now_str(), message
        logging.debug('RUNNING:', now_str(), message)


        client = pymongo.MongoClient()
        db = client.crunchbase
        os.system('echo hi')
        # Do whatever you need to do here
        # then re-register task for same time tomorrow
        # Put task for today at 7am on queue. Executes immediately if past 7am
        """
        new_date = dt.now() + datetime.timedelta(minutes=5)
        daily_time = new_date.time()
        print daily_time
        #quit()
        t = dt.combine(dt.now() + datetime.timedelta(days=0), daily_time)
        logging.debug('RUNNING: again')
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(time.mktime(t.timetuple()), 1, do_something_again, ('Running again',))
        scheduler.run()
        """

        #i = 1
        #for x in range(0, 300):
        print time.time()
        new_date = dt.now() + datetime.timedelta(minutes=5)
        daily_time = new_date.time()
        print daily_time
        #quit()
        t = dt.combine(dt.now() + datetime.timedelta(days=0), daily_time)
        logging.debug('RUNNING: again')
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(time.mktime(t.timetuple()), 1, get_page_record_page, (1, db))
        scheduler.run()



    # Build a scheduler object that will look at absolute times
    scheduler = sched.scheduler(time.time, time.sleep)
    print 'START:', now_str()
    # Put task for today at 7am on queue. Executes immediately if past 7am
    daily_time = datetime.time(8)
    first_time = dt.combine(dt.now(), daily_time)
    # time, priority, callable, *args
    logging.debug('RUN the first time')
    scheduler.enterabs(time.mktime(first_time.timetuple()), 1,
                       do_something_again, ('Run the first time',))
    scheduler.run()

if __name__ == '__main__':
    if "-f" in sys.argv:
        main()
    else:
        with daemon.DaemonContext():
            main()

"""

def main():

    client = pymongo.MongoClient()
    db = client.crunchbase
    s = sched.scheduler(time.time, time.sleep)
    i = 1
    for x in range(0, 300):
        print time.time()
        s.enter(5*i, 1, b))get_page_record_page, (x, d
        s.run()
        i += 1
        print time.time()

    print 'done!'

if __name__ == "__main__":
    sys.exit(main())

"""