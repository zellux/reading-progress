from google.appengine.ext.webapp import template
import os

def doRender(handler, tmpl='index.html', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tmpl)
    if not os.path.isfile(temp):
        return False

    newval = dict(values)
    newval['path'] = handler.request.path
    
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

