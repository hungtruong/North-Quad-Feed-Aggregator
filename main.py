#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
		'SI': {'type':'gcal', 'url':'http://www.google.com/calendar/feeds/si.umich.edu%40gmail.com/public/full?alt=json&ctz=America/Detroit'},
		'MGW':{'type':'sharepoint', 'url':'https://sharepoint.umich.edu/univlib/northquad/_layouts/listfeed.aspx?List={9FB5EB42-3278-44E0-BCC4-7E964DFCAC9D}'},
		'GSP':{'type':'gcal', 'url':'http://www.google.com/calendar/feeds/dk38kh585r0lql859ol81oqrtc%40group.calendar.google.com/public/full?alt=json&ctz=America/Detroit'}}
	
	defaultfeeds = 'SI,MGW,GSP'
	
	requestedfeeds = self.request.get("feeds")
	if requestedfeeds == '':
	  requestedfeeds = defaultfeeds
	requestedfeeds = requestedfeeds.split(',')
	
	today = date.today()
	events = list()
	#do the stuff
	for feed in requestedfeeds:
	  if feeds[feed] is not None:
		if feeds[feed]['type'] == 'gcal':
		  events.extend(handle_google_cal(feeds[feed]['url']))
		elif feeds[feed]['type'] == 'sharepoint':
		  events.extend(handle_sharepoint_cal(feeds[feed]['url']))

	sortedevents = sorted(events, key=itemgetter('start'))

	template_values = {
	'events': sortedevents
	}
	self.response.headers['Content-Type'] = "application/xml"
	path = os.path.join(os.path.dirname(__file__), 'templates/index.xml')
	self.response.out.write(template.render(path, template_values))
	
	#self.response.out.write(sortedevents)
	#self.response.out.write(json.dumps(b, indent=2))

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
