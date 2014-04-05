# TODO(Samba): Ask "renjie" what he thinks of me using his code.
# I found this code on a Chinese blog; I only made a few modifications.
# I'm guessing it's OK to use, but I didn't find any licensing info.
#
# Copied from the following site:
# "tornado http basic and digest auth handler"
# http://www.renjie.me/?p=54
from base64 import b64decode
from tornado.web import RequestHandler
from tornado.escape import utf8
from hashlib import md5

class BasicAuthHandler(RequestHandler):
    def get(self):
        realm = 'renjie'
        username = 'foo'
        password = 'bar'
        # Authorization: Basic base64("user:passwd")
        auth_header = self.request.headers.get('Authorization', None)
        if auth_header:
            # Basic Zm9vOmJhcg==
            auth_mode, auth_base64 = auth_header.split(' ', 1)
            assert auth_mode == 'Basic'
            # 'Zm9vOmJhcg==' == base64("foo:bar")
            auth_bytes = b64decode(auth_base64.encode('utf-8'))
            auth_username, auth_password = auth_bytes.decode().split(':', 1)
            if auth_username == username or auth_password == password:
                self.write('ok')
            else:
                self.set_status(401)
                self.set_header('WWW-Authenticate', 'Basic realm="%s"' % realm)
                self.write('fail')
        else:
            # HTTP/1.1 401 Unauthorized
            # WWW-Authenticate: Basic realm="renjie"
            self.set_status(401)
            self.set_header('WWW-Authenticate', 'Basic realm="%s"' % realm)

class DigestAuthHandler(RequestHandler):
    def get(self):
        realm = 'test'
        opaque = 'asdf'
        # Real implementations would use a random nonce.
        nonce = '1234'
        username = 'foo'
        password = 'bar'
        # Authorization: Digest username="foo",
        #                       realm="test",
        #                       nonce="1234",
        #                       uri="/digest_auth",
        #                       response="e839337ef079c93238a4bf4f1ae712b3",
        #                       opaque="asdf"
        auth_header = self.request.headers.get('Authorization', None)
        print(auth_header)
        if auth_header:
            auth_bytes = auth_header.encode('utf-8')
            auth_mode, params = auth_bytes.decode().split(' ', 1)
            assert auth_mode == 'Digest'
            param_dict = {}
            for pair in params.split(','):
                k, v = pair.strip().split('=', 1)
                v = v.strip('"')
                param_dict[k] = v
                print(k, '=', v)
            assert param_dict['realm'] == realm
            assert param_dict['opaque'] == opaque
            assert param_dict['nonce'] == nonce
            assert param_dict['username'] == username
            assert param_dict['uri'] == self.request.path
            h1 = md5(utf8('%s:%s:%s' % (username, realm, password))).hexdigest()
            h2 = md5(utf8('%s:%s' % (self.request.method,
                                     self.request.path))).hexdigest()
            digest = md5(utf8('%s:%s:%s' % (h1, nonce, h2))).hexdigest()
            print(digest)
            print(param_dict['response'])
            if digest == param_dict['response']:
                self.write('ok')
            else:
                self.write('fail')
        else:
            self.set_status(401)
            # WWW-Authenticate: Digest realm="test", nonce="1234", opaque="asdf"
            self.set_header('WWW-Authenticate',
                            'Digest realm="%s", nonce="%s", opaque="%s"' %
                            (realm, nonce, opaque))