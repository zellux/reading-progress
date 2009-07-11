# -*- coding: utf-8 -*-

from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis

import logging
import datetime, time
import os
import simplejson as json
from renderer import *

TimeToInt = lambda x: int(time.mktime(x.timetuple()))

def ShowChartByGoogle(handler, data, book, ups):
    oneday = datetime.timedelta(days=1)
    date = ups[0].date
    xlabel = [str(date.day)]
    ylabel = range(0, book.pages + 1, ((book.pages / 8) / 50 + 1) * 50)
    
    for (i, up) in enumerate(ups):
        if i == 0: continue
        days = (up.date - ups[i-1].date).days
        for j in range(days):
            date += oneday
            if date.weekday() == 0: # only records sunday
                if date.day < 7:
                    xlabel.append(str(date.month))
                else:
                    xlabel.append('.')

    chart = SimpleLineChart(600, 320, y_range=[0, ylabel[-1]])

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
    left_axis = ylabel
    left_axis[0] = ''
    chart.set_axis_labels(Axis.LEFT, left_axis)
    
    # X axis labels
    chart.set_axis_labels(Axis.BOTTOM, xlabel)

    doRender(handler, 'progress.html', {
            'book': book,
            'imgurl': chart.get_url(),
            'method': 'google'})

def ShowChartByOFC(handler, data, book, ups):
    datajson = json.loads(JsonSample())
    values = datajson['elements'][0]['values']

    oneday = datetime.timedelta(days=1)
    date = ups[0].date
    # for i, y in enumerate(data):
    #     if i % 7 == 0:
    #         values.append({'x': TimeToInt(date), 'y': y})
    #     date += oneday

    for y in data:
        if y >= 0:
            values.append({'x': TimeToInt(date), 'y': y})
        else:
            values.append(None)

        date += oneday
        
    steps = 86400 * 7
    datajson['title']['text'] = book.title
    datajson['x_axis']['min'] = TimeToInt(ups[0].date)
    datajson['x_axis']['max'] = TimeToInt(ups[len(ups)-1].date)
    datajson['x_axis']['steps'] = datajson['x_axis']['labels']['steps'] = steps
    datajson['x_axis']['labels']['visible-steps'] = 1,

    slice = ((book.pages - 1) / 8 / 50 + 1) * 50
    datajson['y_axis']['min'] = 0
    datajson['y_axis']['max'] = (book.pages / slice + 1) * slice
    datajson['y_axis']['steps'] = slice
    handler.response.out.write(json.dumps(datajson, indent=4))
    return datajson

ShowChart = ShowChartByOFC

def JsonSample():
    return """
{
  "elements": [
    {
      "type": "scatter_line",
      "colour": "#DB1750",
      "width": 1,
      "values": [
      ],
      "dot-style": {
        "type": "bow",
        "dot-size": 4,
        "halo-size": 0,
        "tip": "#date:d M y#<br>Value: #val#",
        "rotation": 90
      }
    }
  ],
  "title": {
    "text": 31
  },
  "x_axis": {
    "min": 1230768000,
    "max": 1233360000,
    "steps": 86400,
    "labels": {
      "text": "#date:jS M#",
      "steps": 86400,
      "visible-steps": 2,
      "rotate": 90
    }
  },
  "y_axis": {
    "min": 0,
    "max": 15,
    "steps": 5
  }
}
"""
