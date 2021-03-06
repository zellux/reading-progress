# -*- coding: utf-8 -*-

import cgi
import logging, os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from douban_db import *
from test_db import RandomProgress
from renderer import *

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self)

class AddUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        UserRegister(self, user)

    def get(self):
	self.post()

class ShowUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        QueryUserBooks(self, user)

    def get(self):
        self.post()

class UpdateUser(webapp.RequestHandler):
    def post(self):
        user = self.request.get('user')
        UserRefresh(self, user)

    def get(self):
        self.post()

class TestRandomProgress(webapp.RequestHandler):
    def post(self):
        book = self.request.get('book')
        RandomProgress(self, book)

    def get(self):
        self.post()
        
class ShowProgress(webapp.RequestHandler):
    def post(self):
        book = self.request.get('book')
        QueryProgress(self, book)

    def get(self):
        self.post()
        
class ShowOFCData(webapp.RequestHandler):
    def post(self):
        book = self.request.get('key')
        FetchOFCData(self, book)

    def get(self):
        self.post()

class AjaxUpdateRecord(webapp.RequestHandler):
    def pose(self):
	date = self.request.get('date')
	bkey = self.request.get('key')
	page = self.request.get('page')
	UpdateRecord(self, bkey, date, page)

    def get(self):
	self.pose()

class AjaxGetPage(webapp.RequestHandler):
    def pose(self):
	bkey = self.request.get('key')
	GetPage(self, bkey)

    def get(self):
	self.pose()

class AdminControl(webapp.RequestHandler):
    def pose(self):
	func = self.request.get('do')
	globals()[func](self)

    def get(self):
	self.pose()
	
application = webapp.WSGIApplication(
    [('/', MainPage),
     ('/addUser', AddUser),
     ('/showUser', ShowUser),
     ('/updateUser', UpdateUser),
     ('/randomProgress', TestRandomProgress),
     ('/showProgress', ShowProgress),
     ('/getOFCData', ShowOFCData),
     ('/updateRecord', AjaxUpdateRecord),
     ('/ajaxGetPage', AjaxGetPage),
     ('/admin', AdminControl)
     ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
