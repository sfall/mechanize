import logging
from optparse import OptionParser
from os import getcwd
from sys import argv
from sys import stdout
from time import sleep
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer


def parse_options(args):
    parser = OptionParser()
    parser.add_option("--log", action="store_true")
    parser.add_option("--port", type="int", default=2121)
    options, remaining_args = parser.parse_args(args)
    try:
        options.root_path = remaining_args[0]
    except:
        options.root_path = None
    return options


options = parse_options(argv[1:])
path = options.root_path if options.root_path else '.'
authorizer = DummyAuthorizer()
authorizer.add_user('john', 'john', path, perm='elradfmwM')
authorizer.add_anonymous(path)

handler = FTPHandler
handler.authorizer = authorizer
handler.banner = "pyftpdlib based ftpd ready."

logging.basicConfig(stream=stdout)
address = ('127.0.0.1', options.port)
server = ThreadedFTPServer(address, handler)
server.max_cons = 256
server.max_cons_per_ip = 5


def start_server():
    global server
    server.serve_forever()

def main():
    global server
    t = Thread(target=start_server)
    t.start()
    sleep(3)
    server.close_all()

if __name__ == "__main__":
    main()
        ## Root path is a variable
        ## Add user
        ## Add root path
        ## Add anon user
        ## Start log
