author__ = 'marc'
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

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
    def show(self, permalink=None, format='html'):

        #unsynced_count = db.crunchbase.find({ "synced" : { "$exists" : False } } ).count()
        #synced_count = db.crunchbase.find({ "synced" : { "$exists" : True } } ).count()
        #count = db.crunchbase.count()
        if permalink is None or permalink == '':
            context = {
                'results': [],
                #'count': count,
                #'unsynced_count': unsynced_count,
                #'synced_count': synced_count,
                'q': name
            }
            ## render template with context data
            if format == 'html':
                html = engine.render('search.pyhtml', context)
                return html
            else:
                json = json.dumps({'error': 1, 'message': 'You did not specify a permalink'})
                return json
        else:
            print 'Permalink %s'%permalink
            """
            link = 'https://api.crunchbase.com/v/3/organizations/:%s?user_key=%s'%(urllib.quote_plus(permalink),
                                                                                   CRUNCHBASE_KEY)
                                                                                   """
            driver = webdriver.Firefox()
            link = 'https://www.crunchbase.com/organization/%s'%(urllib.quote_plus(permalink))

            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print (link)

            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            print ('###################################################################')
            #r = requests.get(link)

            # go to the google home page
            driver.get(link)
            print driver.page_source
            try:
                element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, "profile_header_heading"))
                )
            except TimeoutException:
                return '<h1>That Company does not have a proper CrunchBase profile</h1>'
            finally:
                pass
            # the page is ajaxy so the title is originally this:
            print driver.title
            print driver.page_source
            doc = bs(driver.page_source)
            dic_div = doc.find('div', { "class" : "definition-list container" })

            dic_item = dic_div.find('dt', text='Headquarters:')
            desc_item = dic_div.find('dt', text='Descripton:')
            cat_item = dic_div.find('dt', text='Categories:')
            website_item = dic_div.find('dt', text='Website:')
            if dic_item:
                location = dic_item.find_next_sibling('dd').text
            else:
                location = ''
            if desc_item:
                description = desc_item.find_next_sibling('dd').text
            else:
                description = ''
            if cat_item:
                categories = cat_item.find_next_sibling('dd').text
            else:
                categories = ''
            if website_item:
                website = website_item.find_next_sibling('dd').text
            else:
                website = ''
            imgs = driver.find_elements_by_class_name('entity-info-card-primary-image')
            if imgs[0]:
                img_url = imgs[0].get_attribute("src")
            else:
                image_url = ''
            results = {
                'img_url': img_url,
                'title': driver.title,
                'location': location,
                'description': description,
                'categories': categories,
                'website': website,
            }

            #count = 1
            #
            # keeps details render from choking
            #
            results_count = 1
            context = {
                'img_src': img_url,
                'results': results,
                #'count': count,
                #'unsynced_count': unsynced_count,
                #'synced_count': synced_count,
                'q': permalink,
                'results_count': results_count,
            }
        driver.quit()
        ## render template with context data
        if format == 'html':
            html = engine.render('search.pyhtml', context)
            return html
        else:
            import json #????
            json_context = json.dumps(context)
            return json_context
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


