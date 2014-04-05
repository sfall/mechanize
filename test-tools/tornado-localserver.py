import re
import threading
import tornado.httpserver
import tornado.ioloop
import tornado.web
import time
from authhandler import BasicAuthHandler
from authhandler import DigestAuthHandler

RELOAD_TEST_HTML = """\
<html>
<head><title>Title</title></head>
<body>

<a href="/mechanize">near the start</a>

<p>Now some data to prevent HEAD parsing from reading the link near
the end.

<pre>
%s</pre>

<a href="/mechanize">near the end</a>

</body>

</html>""" % (("0123456789ABCDEF"*4+"\n")*61)

REFERER_TEST_HTML = """\
<html>
<head>
<title>mechanize Referer (sic) test page</title>
</head>
<body>
<p>This page exists to test the Referer functionality of <a href="/mechanize">mechanize</a>.
<p><a href="/cgi-bin/cookietest.cgi">Here</a> is a link to a page that displays the Referer header.
</body>
</html>"""

def html(title=None, extra_content=""):
    html = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
    <title>mechanize</title>
  </head>
  <body><a href="http://sourceforge.net/">
%s</a>
</body>
</html>
""" % extra_content
    if title is not None:
        html = re.sub("<title>(.*)</title>", "<title>%s</title>" % title, html)
    return html


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        HTML = html('mechanize')
        self.write(HTML)


class RobotHandler(tornado.web.RequestHandler):
    def get(self, page):
        self.set_header('Content-Type', 'text/plain')
        if page == 'robots.txt':
            self.write("User-Agent: *\nDisallow: /norobots")
        elif page == 'robots':
            self.write("Hello, robots.")
        elif page == 'norobots':
            self.write("Hello, non-robots.")
        else:
            self.write(page+": I don't understand!")


class MechanizeHandler(tornado.web.RequestHandler):
    def get(self, page):
        if page == '':
            HTML = html()
        elif page == 'example.html':
            import os.path
            HTML = open(os.path.join("..", "examples", "forms", "example.html")).read()
        else:
            HTML = 'Wrong!'
        self.write(HTML)


class TestFixturesHandler(tornado.web.RequestHandler):
    def get(self, page):
        if page == '':
            HTML = html("Python bits", extra_content="GeneralFAQ.html")
        elif page == 'cctest2.txt':
            self.set_header('Content-Type', 'text/plain')
            HTML = "Hello ClientCookie functional test suite."
        elif page == 'referertest.html':
            HTML = REFERER_TEST_HTML
        elif page == 'mechanize_reload_test.html':
            HTML = RELOAD_TEST_HTML
        else:
            HTML = "Wrong!"
        self.write(HTML)


class CGIHandler(tornado.web.RequestHandler):
    # TODO(Samba): Move this code into Tornado Templates
    # There's a time for intelligence, and that's later.
    # ...I need a better motto.
    def post(self, page):
        if page == 'cookietest':
            import os
            import urllib.parse
            from html import escape
            from time import time, localtime
            from xml.sax import saxutils

            year_plus_one = localtime(time())[0] + 1
            expires = "expires=09-Nov-%d 23:12:40 GMT" % (year_plus_one,)
            cookies = self.cookies

            self.set_header("Content-Type", "text/html")
            self.add_header("Set-Cookie", "foo=bar; {}".format(expires))
            self.add_header("Set-Cookie", "sessioncookie=spam")
            HTML = """\
            <html><head><title>Cookies and form submission parameters</title>
            """

            refresh_value = self.get_argument("refresh")
            if refresh_value:
                HTML += '<meta http-equiv="refresh" content=%s>' % (
                    saxutils.quoteattr(urllib.parse.unquote_plus(refresh_value)))
            elif "foo" not in cookies:
                HTML += '<meta http-equiv="refresh" content="5">'

            HTML += """</head>
            <p>Received cookies:</p>
            <pre>
            """
            HTML += ', '.join(c for c in cookies)
            HTML += "\n</pre>\n"

            if "foo" in cookies:
                HTML += "<p>Your browser supports cookies!</p>\n"
            if "sessioncookie" in cookies:
                HTML += "<p>Received session cookie</p>\n"
            HTML += """<p>Referer:</p>
            <pre>
            """
            HTML += self.request.get_header('Referer')
            HTML += """\n</pre>
            <p>Received parameters:</p>
            <pre>
            """
            form = {k: self.get_arguments(k) for k in self.request.arguments if self.get_arguments(k)}
            for k in form:
                v = form.get(k)
                if isinstance(v, list):
                    vs = []
                    for item in v:
                        vs.append(item)
                    text = ', '.join(vs)
                elif not v:
                    text = "None"
                else:
                    text = v
                HTML += "%s: %s\n" % (escape(k), escape(text))
            HTML += "</pre></html>"
        elif page == 'echo':
            from html import escape
            self.set_header("Content-Type", "text/html")
            HTML = "<html><head><title>Form submission parameters</title></head>\n"

            form = {k: self.get_arguments(k) for k in self.request.arguments if self.get_arguments(k)}
            HTML += "<p>Received parameters:</p>\n"
            HTML += "<pre>\n"
            for k in form:
                v = form.get(k)
                if isinstance(v, list):
                    vs = []
                    for item in v:
                        vs.append(item)
                    text = ', '.join(vs)
                else:
                    text = v
                HTML += "%s: %s\n" % (escape(k), text)
            HTML += "</pre></html>"
        else:
            HTML = "Wrong!"
        self.write(HTML)


def start_tornado(*args, **kwargs):
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/mechanize/?([\w.]*)", MechanizeHandler),
        (r"/(.*robot.*)", RobotHandler),
        (r"/test_fixtures/?([\w.]*)", TestFixturesHandler),
        (r"/redirected", tornado.web.RedirectHandler, {"url": "/"}),
        (r"/cgi-bin/(.*)\.cgi", CGIHandler),
        (r"/basic_auth", BasicAuthHandler),
        (r"/digest_auth", DigestAuthHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8878)
    print("Starting Tornado")
    tornado.ioloop.IOLoop.instance().start()
    print("Tornado finished")


def stop_tornado():
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(lambda x: x.stop(), ioloop)
    print("Asked Tornado to exit")


def main():
    t = threading.Thread(target=start_tornado)  
    t.start()

    time.sleep(60)

    stop_tornado()
    t.join()

if __name__ == "__main__":
    main()