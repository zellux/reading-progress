# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache

import douban, douban.service
import pickle, re
import logging
import datetime, simplejson as json, timeit, time

from renderer import *
from chart import ShowChart, ShowEmptyChart


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
    if owner == None:
	doRender(handler, 'error.html', {'errormsg': '用户不存在'});
        return

    books = owner.bookstate_set

    logging.info("Query books of user %s\n"%name)
    if books.count() == 0:
        logging.info("Query result: Empty\n")
	
        
    doRender(handler, 'showuser.html', {'books': books.fetch(1000), 'user': owner});

def QueryProgress(handler, bkey):
    book = db.get(bkey)
    
    doRender(handler, 'progress.html', {
            'book': book,
            'dataurl': '/getOFCData?key='+bkey,
            'method': 'OFC'})
    
def FetchOFCData(handler, bkey):
    bkey = bkey.strip()

    # TODO: refresh memcache when update progress
    datajson = memcache.get('ofc.' + bkey)
    datajson = None
    if datajson:
        logging.info('ofc cache hits.')
        handler.response.out.write(json.dumps(datajson))
        return

    book = db.get(bkey)
    q = book.updatepoint_set

    if q.count() <= 1:
        datajson = ShowEmptyChart(handler, book)
        return
    q.order('date')
    ups = q.fetch(1000)

    data = [ups[0].page]
    for (i, up) in enumerate(ups):
        if i == 0: continue
        days = (up.date - ups[i-1].date).days
        pages = up.page - ups[i-1].page
        
        ppd = pages / (days + 0.0)
        for j in range(days):
            if j != days - 1:
                # data.append(int(j*ppd + ups[i-1].page))
                data.append(-1)
            else:
                data.append(up.page)
                
    datajson = ShowChart(handler, data, book, ups)
    memcache.add('ofc.' + bkey, datajson)
    
def QueryUser(name):
    user = db.GqlQuery("SELECT * FROM UserInfo where uid='%s'"%name)

    logging.info("Query user %s\n"%name)
    if user.count() == 0:
        logging.info("Query result: Empty\n")

    return user.get()

def UpdateRecord(handler, bkey, datestr, pagestr):
    logging.info("Update: %s %s %s"%(bkey, datestr, pagestr))
    try:
	book = db.get(bkey)
    except Exception, e:
	handler.response.out.write('无法获得图书信息')
	logging.info(e)
	return

    try:
	t = time.strptime(datestr, '%Y-%m-%d')
	date = datetime.date.fromtimestamp(time.mktime(t))
    except:
	handler.response.out.write('日期格式错误')
	return

    try:
	page = int(pagestr)
	# TODO: page > book.pages
    except:
	handler.response.out.write('页码错误')
	return

    try:
	q = UpdatePoint.all()
	q.filter('date =', date)
	q.filter('book =', book)
	if q.count() == 0:
	    up = UpdatePoint(book=book, date=date, page=page)
	else:
	    up = q.fetch(1)[0]
	    up.page = page
	if page > book.done:
	    book.done = page
	    db.put(book)
	db.put(up)
	handler.response.out.write('更新成功')
    except Exception, e:
	handler.response.out.write('更新出错')
	logging.info(e)
    
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
