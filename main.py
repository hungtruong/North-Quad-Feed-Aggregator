from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import urllib2
from datetime import datetime
from datetime import date
from operator import itemgetter
import os
from google.appengine.ext.webapp import template
import xml.dom.minidom
from xml.dom.minidom import Node
import re
from google.appengine.api import memcache
import logging
from functions import *


class MainHandler(webapp.RequestHandler):
  def get(self):
	#Set up the various feeds and their "types"
	feeds = {
		'SI': {'type':'gcal', 'url':'http://www.google.com/calendar/feeds/si.umich.edu%40gmail.com/public/full?alt=json&ctz=America/Detroit&futureevents=true'},
		'COMM':{'type':'lsa', 'url':'http://www.lsa.umich.edu/vgn-ext-templating/resources/templates/events/xml.jsp?curSiteName=comm&department=comm&channelId=4a087b81da325210VgnVCM10000055b1d38dRCRD'},
		'SCW':{'type':'lsa', 'url':'http://www.lsa.umich.edu/vgn-ext-templating/resources/templates/events/xml.jsp?curSiteName=sweetland&department=sweetland&channelId=4a087b81da325210VgnVCM10000055b1d38dRCRD'},
		'MGW':{'type':'sharepoint', 'url':'https://sharepoint.umich.edu/univlib/northquad/_layouts/listfeed.aspx?List={9FB5EB42-3278-44E0-BCC4-7E964DFCAC9D}','defaultlocation':'Media Gateway'},
		'NQ':{'type':'sharepoint', 'url':'https://sharepoint.umich.edu/univlib/northquad/_layouts/listfeed.aspx?List={F008BBA6-E20A-470C-8C49-6E654A6F433E}','defaultlocation':'North Quad'},
		'GSP':{'type':'gcal', 'url':'http://www.google.com/calendar/feeds/dk38kh585r0lql859ol81oqrtc%40group.calendar.google.com/public/full?alt=json&ctz=America/Detroit&futureevents=true'}
		}
	
	defaultfeeds = 'SI,MGW,GSP,COMM,SCW'
	output = self.request.get("output")
	if output == '':
	  output = 'xml'
	requestedfeeds = self.request.get("feeds")
	if requestedfeeds == '':
	  requestedfeeds = defaultfeeds
	requestedfeeds = requestedfeeds.split(',')
	
	today = date.today()
	events = list()
	#do the stuff
	for feed in requestedfeeds:
		try:
			if feeds[feed] is not None:
				if feeds[feed]['type'] == 'gcal':
					events.extend(handle_google_cal(feeds[feed]['url']))
				elif feeds[feed]['type'] == 'sharepoint':
					events.extend(handle_sharepoint_cal(feeds[feed]['url'], feeds[feed]['defaultlocation']))
				elif feeds[feed]['type'] == 'lsa':
					events.extend(handle_lsa_feed(feeds[feed]['url']))
		except Exception, e:
			logging.error(e)
	
	sortedevents = sorted(events, key=itemgetter('start'))
	
	template_values = {
	'events': sortedevents
	}
	
	if output == 'xml':
	  self.response.headers['Content-Type'] = "application/xml"
  	path = os.path.join(os.path.dirname(__file__), 'templates/index.xml')
	if output == 'csv':
		path = os.path.join(os.path.dirname(__file__), 'templates/index.csv')
	self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
