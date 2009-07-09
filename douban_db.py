# -*- coding: utf-8 -*-

from google.appengine.ext import db
import douban, douban.service
import pickle, re

import logging
from renderer import *

from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis

import datetime

SERVER = 'api.douban.com'
API_KEY = '08ddb388b20b31581a991a9a16219408'
SECRET = 'a3ef59aefaa9b85e'

client = douban.service.DoubanService(server=SERVER, api_key=API_KEY,secret=SECRET)

class UserInfo(db.Model):
    uid = db.StringProperty(required=True)
    uname = db.StringProperty()

class BookState(db.Model):
    owner = db.ReferenceProperty(UserInfo)
    isbn  = db.StringProperty()
    title = db.StringProperty(required=True)
    pages = db.IntegerProperty(required=True)
    done  = db.IntegerProperty(required=True)
    img   = db.StringProperty()

class UpdatePoint(db.Model):
    book = db.ReferenceProperty(BookState)
    date = db.DateProperty(required=True)
    page = db.IntegerProperty(required=True)
    
def UserRegister(handler, name):
    name = name.strip()
    q = db.Query(UserInfo)
    q = q.filter('uid = ', name)
    results = q.fetch(limit=1)
    if len(results) > 0:
        logging.info('Duplicated user: uid=%s'%name)
        doRender(handler, 'error.html', {'errormsg': '该用户已被注册'});
        return
    
    user = UserInfo(uid=name)
    
    books = client.GetMyCollection(
        url='/people/%s/collection'%name,
        cat='book',
        tag='',
        status='reading',
        max_results=50)

    uname = re.search('(.*) 的收藏', books.title.text)
    if uname:
        user.uname = unicode(uname.group(1), 'utf-8')
    db.put(user)
    
    logging.info(books.title.text)
    for b in books.entry:
        bs = BookState(
            owner=user,
            title=unicode(b.subject.title.text.strip(), 'utf-8'),
            pages=0,
            done=0
            )
        book = client.GetBook(b.subject.id.text)
        for attr in book.attribute:
            if attr.name == 'pages':
                try:
                    bs.pages = int(attr.text.split()[0])
                except:
                    logging.error('Error when fetching page number of book %s'%b.subject.id.text)

        # for author in b.subject.author:
        #     print author.name.text
        for link in b.subject.link:
            if link.rel == 'image':
                bs.img = link.href
        # for attr in b.subject.attribute:
        #     print attr.name, attr.text
        # print dir(b.subject.summary)
        db.put(bs)

    doRender(handler, 'userinfo.html', {'books': books});

def QueryUserBooks(handler, name):
    owner = QueryUser(name)
    books = owner.bookstate_set

    logging.info("Query books of user %s\n"%name)
    if books.count() == 0:
        logging.info("Query result: Empty\n")
        
    doRender(handler, 'showuser.html', {'books': books, 'user': owner});

def QueryProgress(handler, bkey):
    book = db.get(bkey)
    ups = book.updatepoint_set
    ups.order('date')

    date = ups[0].date
    oneday = datetime.timedelta(days=1)
    data = [ups[0].page]
    label = [str(date.day)]
    for (i, up) in enumerate(ups):
        if i == 0: continue
        days = (up.date - ups[i-1].date).days
        pages = up.page - ups[i-1].page
        ppd = pages / (days + 0.0)
        for j in range(days):
            date += oneday
            if date.weekday() == 0: # only records sunday
                if date.day < 7:
                    label.append(str(date.month))
                else:
                    label.append('.')
            if j != days - 1:
                data.append(int(j*ppd + ups[i-1].page))
            else:
                data.append(up.page)
        logging.info('%s(%d): %s' % (up.date, days, data))

    max_y = book.pages

    chart = SimpleLineChart(600, 320, y_range=[0, max_y])

    # data = [
    #     32, 34, 34, 32, 34, 34, 32, 32, 32, 34, 34, 32, 29, 29, 34, 34, 34, 37,
    #     37, 39, 42, 47, 50, 54, 57, 60, 60, 60, 60, 60, 60, 60, 62, 62, 60, 55,
    #     55, 52, 47, 44, 44, 40, 40, 37, 34, 34, 32, 32, 32, 31, 32
    #     ]
    chart.add_data(data)
    
    # Set the line colour to blue
    chart.set_colours(['0000FF'])
    
    # Set the vertical stripes
    chart.fill_linear_stripes(Chart.CHART, 0, 'CCCCCC', 0.2, 'FFFFFF', 0.2)
    
    # Set the horizontal dotted lines
    chart.set_grid(0, 25, 5, 5)

    # The Y axis labels contains 0 to 100 skipping every 25, but remove the
    # first number because it's obvious and gets in the way of the first X
    # label.
    left_axis = range(0, max_y + 1, ((max_y / 8) / 50 + 1) * 50)
    left_axis[0] = ''
    chart.set_axis_labels(Axis.LEFT, left_axis)
    
    # X axis labels
    chart.set_axis_labels(Axis.BOTTOM, label)

    doRender(handler, 'progress.html', {'book': book, 'imgurl': chart.get_url()})
        
    
def QueryUser(name):
    user = db.GqlQuery("SELECT * FROM UserInfo where uid='%s'"%name)

    logging.info("Query user %s\n"%name)
    if user.count() == 0:
        logging.info("Query result: Empty\n")

    return user.get()

if __name__ == '__main__':
    books = client.GetMyCollection(url='/people/zellux/collection', cat='book', tag='', status='reading', max_results=50)
    # pickle.dump(books, open('mybooks.pickle', 'w'))
    books = pickle.load(open('mybooks.pickle', 'r'))
    for b in books.entry:
        print b.subject.title.text
        for author in b.subject.author:
            print author.name.text
        for link in b.subject.link:
            print link.rel, link.href
        for attr in b.subject.attribute:
            print attr.name, attr.text
        print dir(b.subject.summary)
        break
