#!/usr/bin/env python
#

import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
from modelo import Busqueda
import StringIO
import simplejson as json

from xml.dom import minidom
import sys, time, urllib2

logging.getLogger().setLevel(logging.DEBUG)

name = "Saludemos la Patria Orgullosos"
slogan = ""
myurl = "http://www.saludemoslapatria.com"

class MainHandler(webapp.RequestHandler):
    def get(self):
        #self.response.out.write('Hello world!')
        toMain(self)

class Gracias(webapp.RequestHandler):
	def get(self):
		gracias = self.get_gracias_cached()
		out = StringIO.StringIO()
		out.write("{ \"gracias\": ")
		out.write(gracias)
		out.write("}")
		self.response.out.write(out.getvalue())
	
	def get_gracias_cached(self):
		mas_gracias = memcache.get("mas_gracias")
		if mas_gracias is not None:
			return mas_gracias
		else:
			mas_gracias = self.get_gracias()
			if not memcache.add("mas_gracias", mas_gracias, 3600): ## cada 1 hora
				logging.error("Fallo memcache :(")
			return mas_gracias
	
	def get_gracias(self):
		q = db.GqlQuery("SELECT * FROM Busqueda ORDER BY pub DESC")
		buscados = q.fetch(404)
		lista = []
		for b in buscados:
			b1 = b.getJson()
			lista.append(b1)
		return json.dumps(lista)

class Fetch2(webapp.RequestHandler):  
	def get(self):
		page = self.request.get('page')
		url = "http://search.twitter.com/search.atom?rpp=200&q=Independencia%20El%20Salvador%20lang%3Aes%20include%3Aretweets&page=" + page
		xml = urllib2.urlopen(url)
		doc = minidom.parse(xml)
		
		eltitle = None
		elpub = None
		elid = None
		elname = None
		
		entries = doc.getElementsByTagName("entry")
		if len(entries) > 0:
			entries.reverse()
			for e in entries:
				elid = e.getElementsByTagName("id")[0].firstChild.data.split(":")[2]
				elname = e.getElementsByTagName("name")[0].firstChild.data.split(" ")[0]
				eltitle = e.getElementsByTagName("title")[0].firstChild.data
				elpub = e.getElementsByTagName("published")[0].firstChild.data
				elimage = e.getElementsByTagName("link")[1].getAttribute("href")
				busquedas = db.GqlQuery("SELECT * FROM Busqueda WHERE id = :1", elid)
				b = None
				if busquedas.count() == 0:
					b = Busqueda(id = elid, name = elname, title = eltitle, pub = elpub, image = elimage)
					b.put()
		self.response.out.write(url)
		
class Fetch(webapp.RequestHandler):  
	def get(self):
		#url = "http://search.twitter.com/search.atom?rpp=200&q=%s" % ('%22Indepdendencia%20El%20Salvador%22%20lang%3Aes')
		#url = "http://search.twitter.com/search.atom?rpp=200&q=%s" % ('%22Independencia%20El%20Salvador%22%20lang%3Aes')
		url = "http://search.twitter.com/search.atom?rpp=200&page=1&q=Independencia%20El%20Salvador%20lang%3Aes%20include%3Aretweets"
		xml = urllib2.urlopen(url)
		doc = minidom.parse(xml)
		
		eltitle = None
		elpub = None
		elid = None
		elname = None
		
		entries = doc.getElementsByTagName("entry")
		if len(entries) > 0:
			entries.reverse()
			for e in entries:
				elid = e.getElementsByTagName("id")[0].firstChild.data.split(":")[2]
				elname = e.getElementsByTagName("name")[0].firstChild.data.split(" ")[0]
				eltitle = e.getElementsByTagName("title")[0].firstChild.data
				elpub = e.getElementsByTagName("published")[0].firstChild.data
				elimage = e.getElementsByTagName("link")[1].getAttribute("href")
				busquedas = db.GqlQuery("SELECT * FROM Busqueda WHERE id = :1", elid)
				b = None
				if busquedas.count() == 0:
					b = Busqueda(id = elid, name = elname, title = eltitle, pub = elpub, image = elimage)
					b.put()
		self.response.out.write(url)

def toTemplate(self, template_values):
    template_file_name = 'maintemplate.html'
    path = os.path.join(os.path.dirname(__file__), template_file_name)
    logging.info(template_values)
    self.response.out.write(template.render(path, template_values))

def toMain(self):
    template_values = {
        'name' : name,
        'slogan': slogan,
		'myurl' : myurl
        }
    #logging.info("A MAIN!!!!")
    toTemplate(self, template_values)

def main():
    application = webapp.WSGIApplication([('/', MainHandler), ('/gracias', Gracias), ('/fetch', Fetch), ('/fetch2', Fetch2)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
