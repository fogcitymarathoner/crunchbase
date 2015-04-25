import requests
import pymongo
import json

import daemon # install python-daemon from pypi
import os
import sys
import sched
import time
from datetime import datetime as dt
import datetime
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from settings import CRUNCHBASE_KEY

def get_page_record_page(x, db):
    """
    scheduled (deferred) task that pulls down summary page number x
    and records data into database
    :param x:
    :return:
    """
    r = requests.get('https://api.crunchbase.com/v/2/organizations?user_key=%s&page=%s'%(CRUNCHBASE_KEY, x))

    data = json.loads(r.text)

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


def now_str():
    """Return hh:mm:ss string representation of the current time."""
    t = dt.now().time()
    return t.strftime("%H:%M:%S")


def main():

    client = pymongo.MongoClient()
    db = client.crunchbase

    # Build a scheduler object that will look at absolute times
    scheduler = sched.scheduler(time.time, time.sleep)
    print 'START:', now_str()
    # Put task for today at 7am on queue. Executes immediately if past 7am
    daily_time = datetime.time(8)
    first_time = dt.combine(dt.now(), daily_time)
    # time, priority, callable, *args

    scheduler.enterabs(time.mktime(t.timetuple()), 1, get_page_record_page, (1, db))
    scheduler.run()

if __name__ == '__main__':
    if "-f" in sys.argv:
        main()
    else:
        with daemon.DaemonContext():
            main()
