# -*- coding: utf-8 -*-

from google.appengine.ext import db
import douban, douban.service

from douban_db import BookState, UpdatePoint
from renderer import *

import logging
import datetime

def randomProgress(handler, bkey):
    try:
        book = db.get(bkey)
    except:
        logging.error('Cannot find book: book key=%s'%bkey)
        doRender(handler, 'error.html', {'errormsg': '找不到这本书的信息'});
        return

    import random as r
    date = datetime.date(2008, r.randint(1, 12), r.randint(1,28))
    delta = datetime.timedelta(days=1)
    page = 0
    for i in range(r.randint(10, 30)):
        date = date + delta
        if r.randint(0, 1) == 0:
            pass
        else:
            up = UpdatePoint(book=book, date=date, page=page)
            db.put(up)
            page += r.randint(0, 10)
            
