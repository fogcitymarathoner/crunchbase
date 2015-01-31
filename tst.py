import requests
import pymongo
import json
import sys
def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

client = pymongo.MongoClient()
db = client.crunchbase

for x in range(315, 318):
  r = requests.get('https://api.crunchbase.com/v/2/organizations?user_key=4c8d0795c93056f45eb38d1a16ddd71f&page=%s'%x)
  #print strip_non_ascii(r.text)
  data = json.loads(r.text)
  #print r.text
  #quit()
  for y in data['data']['items']:
    #print y['name']
    #print y['path']
    o = {
      'name': y['name'],
      'path': y['path'],
    }
    db.crunchbase.update( o, o, True)
    sys.stdout.write('.')
    sys.stdout.flush()


print 'done!'
