from google.appengine.api import memcache
from google.appengine.api import urlfetch
import urllib2
import xml.dom.minidom
from xml.dom.minidom import Node
from datetime import datetime
from datetime import date
from datetime import timedelta
import logging
from django.utils import simplejson as json
import hashlib
import re


def handle_google_cal(url):
	events = memcache.get(url)
	if events is None:
	  	today = date.today()
		events = list()
		#url = "http://www.google.com/calendar/feeds/si.umich.edu%40gmail.com/public/full?alt=json"
		try:
		  body = urlfetch.fetch(url).content
		except:
		  logging.error('Error downloading thing')
		  return list()
		else:
			a = json.loads(body)
			b = a["feed"]["entry"]
			for feedevents in b:
			  start = feedevents["gd$when"][0]["startTime"]
			  start = start[0:-6]
			  start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.000")
			  
			  end = feedevents["gd$when"][0]["endTime"]
			  end = end[0:-6]
			  end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.000")
			  
			  title = feedevents["title"]["$t"]
			  where = feedevents["gd$where"][0]["valueString"]
			  description = feedevents["content"]["$t"]
			  description = description.strip()
			  description = remove_html_tags(description)
			  link = feedevents["link"][0]["href"]
			  author = feedevents["author"][0]["name"]["$t"]
			  
			  if ((start >= datetime(today.year, today.month, today.day, 0)) and (start <= (datetime(today.year, today.month, today.day, 0) + timedelta(30)))):
					guid = start.isoformat() + title.encode("utf-8")
					guid = hashlib.md5(guid).hexdigest()
					events.append(dict(start=start, end=end, title=title, description=description,
					where=where, link=link, author=author, guid=guid))
			#add the events we just compiled to the memcache
			memcache.add(url, events, 60*10)
	return events

def handle_sharepoint_cal(url,defaultlocation):
	events = memcache.get(url)
	if events is None:
		today = date.today()
		events = list()
		try:
	  	  content = urlfetch.fetch(url).content
		except:
		  logging.error('Error downloading thing')
		  return events
		else:
			doc = xml.dom.minidom.parseString(content)
			for node in doc.getElementsByTagName("item"):
			  title = node.getElementsByTagName("title")[0].firstChild.data
			  link = node.getElementsByTagName("link")[0].firstChild.data
			  #author = node.getElementsByTagName("author")[0].firstChild.data
			  author = ""
			  description = node.getElementsByTagName("description")[0].firstChild.data
			  parts = description.split('<div>')
		  	  description = remove_html_tags(description)
			  for part in parts:
				part = remove_html_tags(part).strip()
				pieces = part.partition(': ')
				if pieces[0] == 'Start Time':
				  start = datetime.strptime(pieces[2], "%m/%d/%Y %I:%M %p")
				elif pieces[0] == 'End Time':
				  end = datetime.strptime(pieces[2], "%m/%d/%Y %I:%M %p")
				elif pieces[0] == 'Description':
				  description = pieces[2]
			  if (start >= datetime(today.year, today.month, today.day, 0)) and (start <= (datetime(today.year, today.month, today.day, 0) + timedelta(30))):
					guid = start.isoformat() + title.encode("utf-8")
					guid = hashlib.md5(guid).hexdigest()
					events.append(dict(start=start, end=end, title=title, description=description,
						where=defaultlocation, link=link, author=author, guid=guid))
			memcache.add(url, events, 60*10)
	return events

def handle_lsa_feed(url):
  events = memcache.get(url)
  if events is None:
    today = date.today()
    events = list()
  else:
    return events
  try:
    content = urlfetch.fetch(url).content
  except:
    logging.error('Error downloading thing')
    return events
  else:
    doc = xml.dom.minidom.parseString(content)
    for node in doc.getElementsByTagName("event"):
      title = node.getElementsByTagName("title")[0].firstChild.data
      link = node.getElementsByTagName("link")[0].firstChild.data
      author = node.getElementsByTagName("author")[0].firstChild.data
      location = node.getElementsByTagName("location")[0].firstChild.data
      description = node.getElementsByTagName("description")[0].firstChild.data
      startstring = node.getElementsByTagName("startDateEvent")[0].firstChild.data + " " + node.getElementsByTagName("startTime")[0].firstChild.data
      endstring = node.getElementsByTagName("endDateEvent")[0].firstChild.data + " " + node.getElementsByTagName("endTime")[0].firstChild.data
      start = datetime.strptime(startstring, "%Y-%m-%d %I:%M %p")
      end = datetime.strptime(endstring, "%Y-%m-%d %I:%M %p")
      if (start >= datetime(today.year, today.month, today.day, 0)) and (start <= (datetime(today.year, today.month, today.day, 0) + timedelta(30))):
				guid = start.isoformat() + title.encode("utf-8")
				guid = hashlib.md5(guid).hexdigest()
				events.append(dict(start=start, end=end, title=title, description=description, where=location, link=link, author=author, guid=guid))
    memcache.add(url, events, 60*10)
  return events

def remove_html_tags(data):
  p = re.compile(r'<.*?>')
  return p.sub('', data)
