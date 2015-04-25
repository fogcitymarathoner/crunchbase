author__ = 'marc'

import cherrypy
import tenjin
import os
from tenjin.helpers import *
import json
import re
import pymongo

import requests
import urllib
from settings import PAGE_SIZE
client = pymongo.MongoClient()
db = client.crunchbase
engine = tenjin.Engine(path=['templates'])

def scrub_name(synced):
    synced_scrubbed = []
    for s in synced:

        try:
            encoded_name = urllib.urlencode({'q': s['name']})
        except:
            encoded_name = 'NON ASCII'
        s['encoded_name'] = encoded_name
        synced_scrubbed.append(s)
    return synced_scrubbed
class Root(object):

    @cherrypy.expose
    def index(self, q=None):
        """
        Show search form with basic measurements like unsynced count and overall count
        """
        count = db.crunchbase.count()
        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        if q is None or q == '':
            context = {
                'results': [],
                'count': count,
                'unsynced_count': unsynced_count,
                'q': q,
                'results_count': 0
            }
        else:
            res = db.crunchbase.find({"name": {'$regex':'%s'%q}})
            context = {
                'results': res,
                'count': count,
                'unsynced_count': unsynced_count,
                'q': q,
                'results_count': res.count()
            }
        ## render template with context data
        html = engine.render('search.pyhtml', context)
        return html

    @cherrypy.expose
    def show(self, q=None):

        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        count = db.crunchbase.count()
        if q is None or q == '':
            context = {
                'results': [],
                'count': count,
                'unsynced_count': unsynced_count,
                'q': q
            }
            ## render template with context data
            html = engine.render('search.pyhtml', context)

            return html
        else:

            res = db.crunchbase.find({"name": {'$regex':'%s'%q}})
            url = 'https://api.crunchbase.com/v/2/%s?user_key=4c8d0795c93056f45eb38d1a16ddd71f'%res[0]['path']

            r = requests.get(url)
            company_info = json.loads(r.text)
            context = {
                'company_info': company_info,
                'company_info_pp': json.dumps(company_info, sort_keys=True, indent=4, separators=(',', ': ')),
                'count': count,
                'unsynced_count': unsynced_count,
                'q': q
            }
        ## render template with context data
        html = engine.render('show.pyhtml', context)

        return html

    @cherrypy.expose
    def synced(self, page=0):

        synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        synced = db.crunchbase.find({ "synced" : { "$exists" : True } } )

        context = {
            'synced_count': synced_count,
            'synced': scrub_name(synced)[page*PAGE_SIZE, page*PAGE_SIZE+PAGE_SIZE]
        }
        ## render template with context data
        html = engine.render('synced.pyhtml', context)

        return html

    @cherrypy.expose
    def unsynced(self, page=0):

        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        unsynced = db.crunchbase.find({ "synced" : { "$exists" : False } } )
        context = {
            'unsynced_count': unsynced_count,
            'unsynced': scrub_name(unsynced)[page*PAGE_SIZE, page*PAGE_SIZE+PAGE_SIZE]
        }
        ## render template with context data
        html = engine.render('unsynced.pyhtml', context)

        return html
if __name__ == '__main__':

    cherrypy.config.update({
        'server.socket_port': 8095,
        'tools.proxy.on': True,
        'tools.proxy.base': 'localhost',
        'log.access_file': "cherrypy-filter-access.log",
        'log.error_file': "cherrypy-filter.log",
    })

    cherrypy.quickstart(Root(), '/crunchbase_search')


