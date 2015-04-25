author__ = 'marc'

import cherrypy
import tenjin
import os
from tenjin.helpers import *
import json
import re
import pymongo

import requests
client = pymongo.MongoClient()
db = client.crunchbase
engine = tenjin.Engine(path=['templates'])

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

if __name__ == '__main__':

    cherrypy.config.update({
        'server.socket_port': 8095,
        'tools.proxy.on': True,
        'tools.proxy.base': 'localhost',
        'log.access_file': "cherrypy-filter-access.log",
        'log.error_file': "cherrypy-filter.log",
    })

    cherrypy.quickstart(Root(), '/crunchbase_search')


