# -*- coding: utf-8 -*-

import cgi
import logging, os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from douban_db import *
from test import *
from renderer import *

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self)

class AddUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        UserRegister(self, user)

class ShowUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        QueryUserBooks(self, user)

    def get(self):
        self.post()

class TestRandomProgress(webapp.RequestHandler):
    def post(self):
        book = self.request.get('book')
        randomProgress(self, book)

    def get(self):
        self.post()
        
application = webapp.WSGIApplication(
    [('/', MainPage),
     ('/addUser', AddUser),
     ('/showUser', ShowUser),
     ('/randomProgress', TestRandomProgress),
     ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
