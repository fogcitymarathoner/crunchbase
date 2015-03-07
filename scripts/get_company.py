__author__ = 'marc'
import requests
import pymongo
import json
import sys
client = pymongo.MongoClient()
db = client.crunchbase

#first = db.crunchbase.find_one()

#link = 'https://api.crunchbase.com/v/2/%s?user_key=4c8d0795c93056f45eb38d1a16ddd71f'%(first['path'])
for company in db.crunchbase.find()[0:2400]:
    link = 'https://api.crunchbase.com/v/2/%s?user_key=4c8d0795c93056f45eb38d1a16ddd71f'%(company['path'])
    print link
    r = requests.get(link)
    returned_json = r.text
    print returned_json
    print type(returned_json)
    print returned_json.find('Rate Limit Error')
    if returned_json.find('Rate Limit Error') == -1:
        try:
            response = json.loads(returned_json)
        except ValueError:
            continue
        if 'response' in response['data']:
            continue
        data =  response['data']
        #print data
        if 'response' in data:
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