#!/usr/bin/python
# -*-python-*-

from html import escape

HTML = """Content-Type: text/html\n
<html><head><title>Form submission parameters</title></head>
"""

form = {k: self.get_arguments(k) for k in self.request.arguments if self.get_arguments(k)}
HTML += "<p>Received parameters:</p>\n"
HTML += "<pre>\n"
for k in form:
    v = form.get(k)
    if isinstance(v, list):
        vs = []
        for item in v:
            vs.append(item.value)
        text = ', '.join(vs)
    else:
        text = v
    HTML += "%s: %s\n" % (escape(k), text)
print("</pre></html>")
