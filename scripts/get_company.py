__author__ = 'marc'
import requests
import pymongo
import json
import sys

import sched, time
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from settings import CRUNCHBASE_KEY

"""
get_company.py - loops through company gotten with get_companies.py that have not been mined for
details

API Rate Limits

We limit usage to 50 calls per minute, 2,500 calls per day and a total lifetime limit of 25k.
To increase your rate limit, just email us at licensing@crunchbase.com.
Technical questions and suggestions should be sent to api@crunchbase.com.
"""
def fetch_update_company(company, db):
    print 'Company %s'%company['name']
    link = 'https://api.crunchbase.com/v/2/%s?user_key=%s'%(company['path'], CRUNCHBASE_KEY)
    print link
    r = requests.get(link)
    returned_json = r.text
    print returned_json
    response = json.loads(returned_json)
    if 'error' in response['data']:
        if response['data']['error']['message'] == "Organization not found":
            print 'Removing Company %s'%company['name']
            db.crunchbase.remove( {"_id": company['_id']})
            return
        if response['data']['error']['message'].find('not found') != -1:
            print 'Removing Company %s'%company['name']
            db.crunchbase.remove( {"_id": company['_id']})
            return

    if returned_json.find('Rate Limit Error') == -1:
        try:
            response = json.loads(returned_json)
        except ValueError:
            pass
        if 'response' in response['data']:
            pass
        data =  response['data']
        #print data
        if 'response' in data:
            print data['error']['code']
            print 'bad co'
            #db.crunchbase.remove(company)
        else:
            print 'got it'
            #print data
            #quit()
            print company['_id']
            if 'description' in data['properties']:
                print data['properties']
                db.crunchbase.update(
                    {'_id': company['_id']},
                    {
                        '$set':
                            {'synced': True,
                             'description': data['properties']['description'],
                             }
                    },
                    upsert=False
                )
            elif 'short_description' in data['properties']:
                print data['properties']
                db.crunchbase.update(
                    {'_id': company['_id']},
                    {
                        '$set':
                            {'synced': True,
                             'description': data['properties']['short_description'],
                             }
                    },
                    upsert=False
                )
            if 'headquarters' in data['relationships']:
                if 'items' in data['relationships']['headquarters']:
                    print 'has hq'
                    print data['relationships']['headquarters']
                    location = {
                                         'city': data['relationships']['headquarters']['items'][0]['city'] if 'city' in data['relationships']['headquarters']['items'][0] else '',
                                         'state': data['relationships']['headquarters']['items'][0]['state'] if 'state' in data['relationships']['headquarters']['items'][0] else '',
                                         'postal_code': data['relationships']['headquarters']['items'][0]['postal_code'] if 'postal_code' in data['relationships']['headquarters']['items'][0] else '',
                                         'country': data['relationships']['headquarters']['items'][0]['country'] if 'country' in data['relationships']['headquarters']['items'][0] else '',
                                }

                    db.crunchbase.update(
                        {'_id': company['_id']},
                        {
                            '$set':
                                {'synced': True,
                                 'location': location
                                 }
                        },
                        upsert=False
                    )
            print db.crunchbase.find(
                    {'_id': company['_id']}
            )[0]
    else:
        print 'daily call limit exceeded'


s = sched.scheduler(time.time, time.sleep)

client = pymongo.MongoClient()
db = client.crunchbase

i = 1
for company in db.crunchbase.find({ "synced" : { "$exists" : False } } )[0:2400]:


    print time.time()
    s.enter(5*i, 1, fetch_update_company, (company, db))
    s.run()
    i += 1
    print time.time()

print 'done!'