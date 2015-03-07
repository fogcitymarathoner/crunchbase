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
def main():

    client = pymongo.MongoClient()
    db = client.crunchbase
    s = sched.scheduler(time.time, time.sleep)
    i = 1
    for x in range(0, 300):
        print time.time()
        s.enter(5*i, 1, get_page_record_page, (x, db))
        s.run()
        i += 1
        print time.time()

    print 'done!'

if __name__ == "__main__":
    sys.exit(main())

