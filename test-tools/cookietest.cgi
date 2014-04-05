#!/usr/bin/python
# -*-python-*-

# This is used by functional_tests.py

#import cgitb; cgitb.enable()

from time import time, localtime
import os, html, http.cookies, urllib.parse
from xml.sax import saxutils

year_plus_one = localtime(time())[0] + 1
expires = "expires=09-Nov-%d 23:12:40 GMT" % (year_plus_one,)
cookie = http.cookies.SimpleCookie()
cookieHdr = os.environ.get("HTTP_COOKIE", "")
cookie.load(cookieHdr)

response = """\
Content-Type: text/html
Set-Cookie: foo=bar; {}
Set-Cookie: sessioncookie=spam\n
<html><head><title>Cookies and form submission parameters</title>
""".format(expires)

refresh_value = self.get_argument("refresh")
if refresh_value:
    response += '<meta http-equiv="refresh" content=%s>' % (
        saxutils.quoteattr(urllib.parse.unquote_plus(refresh_value)))
elif "foo" not in cookie:
    response += '<meta http-equiv="refresh" content="5">'

response += """</head>
<p>Received cookies:</p>
<pre>
"""
response += html.escape(os.environ.get("HTTP_COOKIE", ""))
response += "\n</pre>\n"

if "foo" in cookie:
    response += "<p>Your browser supports cookies!</p>\n"
if "sessioncookie" in cookie:
    response += "<p>Received session cookie</p>\n"
response += """<p>Referer:</p>
<pre>
"""
response += html.escape(os.environ.get("HTTP_REFERER", ""))
response += """\n</pre>
<p>Received parameters:</p>
<pre>
"""
form = {k: self.get_arguments(k) for k in self.request.arguments if self.get_arguments(k)}
for k in form:
    v = form.get(k)
    if isinstance(v, list):
        vs = []
        for item in v:
            vs.append(item.value)
        text = ', '.join(vs)
    else:
        text = v
    response += "%s: %s" % (html.escape(k), text)
response += "</pre></html>"
