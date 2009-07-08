# -*- coding: utf-8 -*-

import cgi
import logging, os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from douban_db import *

def doRender(handler, tmpl='index.html', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tmpl)
    if not os.path.isfile(temp):
        return False

    newval = dict(values)
    newval['path'] = handler.request.path
    
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self)

class AddUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        books = ImportFromURL(user)
        doRender(self, 'userinfo.html', {'books': books});

class ShowUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        books = QueryUserBooks(user)
        doRender(self, 'showuser.html', {'books': books});

    def get(self):
        self.post()

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/addUser', AddUser),
                                      ('/showUser', ShowUser)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
