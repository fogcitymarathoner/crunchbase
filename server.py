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
from settings import CRUNCHBASE_KEY
client = pymongo.MongoClient()
db = client.crunchbase
engine = tenjin.Engine(path=['templates'])

def scrub_name(synced, page):
    synced_scrubbed = []
    for s in synced:

        try:
            encoded_name = urllib.urlencode({'q': s['name']})
        except:
            encoded_name = 'NON ASCII'
        s['encoded_name'] = encoded_name
        synced_scrubbed.append(s)
    return synced_scrubbed[page*PAGE_SIZE: page*PAGE_SIZE+PAGE_SIZE]
class Root(object):

    @cherrypy.expose
    def index(self, q=None, reset_btn=None):
        """
        Show search form for fuzzy search
        """
        count = db.crunchbase.count()
        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        if q is None or q == '':
            context = {
                'results': [],
                'count': count,
                'unsynced_count': unsynced_count,
                'synced_count': synced_count,
                'q': q,
                'results_count': 0
            }
        else:
            #res = db.crunchbase.find({"name": {'$regex':'%s'%q}})

            link = 'https://api.crunchbase.com/v/3/organizations?query=*%s*&user_key=%s'%(q, CRUNCHBASE_KEY)
            print link

            r = requests.get(link)
            returned_json = r.text
            #print returned_json
            results = json.loads(returned_json)
            results_count = len(results['data']['items'])
            context = {
                'results': results,
                'count': count,
                'unsynced_count': unsynced_count,
                'synced_count': synced_count,
                'q': q,
                'results_count': results_count,
            }
        ## render template with context data
        html = engine.render('search.pyhtml', context)
        return html

    @cherrypy.expose
    def show(self, name=None):

        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        count = db.crunchbase.count()
        if name is None or name == '':
            context = {
                'results': [],
                'count': count,
                'unsynced_count': unsynced_count,
                'synced_count': synced_count,
                'q': name
            }
            ## render template with context data
            html = engine.render('search.pyhtml', context)

            return html
        else:
            print 'Company %s'%name
            link = 'https://api.crunchbase.com/v/3/organizations?name=%s&user_key=%s'%(name, CRUNCHBASE_KEY)
            print link
            r = requests.get(link)
            returned_json = r.text
            print returned_json
            response = json.loads(returned_json)
            if len(response['data']['items']) > 0:
                """
                show all found and ask for more selection
                """
                context = {
                        'results': response,
                        'count': count,
                        'unsynced_count': unsynced_count,
                        'synced_count': synced_count,
                        'q': name,
                        'results_count': len(response['data']['items'])
                    }
                ## render template with context data
                html = engine.render('search.pyhtml', context)
                return html

        # Shouldn't be hit

    @cherrypy.expose
    def synced(self, page=0):

        count = db.crunchbase.count()
        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        synced = db.crunchbase.find({ "synced" : { "$exists" : True } } )

        context = {
            'synced_count': synced_count,
            'unsynced_count': unsynced_count,
            'count': count,
            'q':'',
            'synced': scrub_name(synced, page)
        }
        ## render template with context data
        html = engine.render('synced.pyhtml', context)

        return html

    @cherrypy.expose
    def unsynced(self, page=0):

        count = db.crunchbase.count()
        unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        unsynced = db.crunchbase.find({ "synced" : { "$exists" : False } } )
        context = {
            'unsynced_count': unsynced_count,
            'synced_count': synced_count,
            'count': count,
            'q':'',
            'unsynced': scrub_name(unsynced, page)
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


