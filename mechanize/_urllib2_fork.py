"""Fork of urllib2.

When reading this, don't assume that all code in here is reachable.  Code in
the rest of mechanize may be used instead.

Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009 Python
Software Foundation; All Rights Reserved

Copyright 2002-2009 John J Lee <jjl@pobox.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD or ZPL 2.1 licenses (see the file
COPYING.txt included with the distribution).

"""

# XXX issues:
# If an authentication error handler that tries to perform
# authentication for some reason but fails, how should the error be
# signalled?  The client needs to know the HTTP error code.  But if
# the handler knows that the problem was, e.g., that it didn't know
# that hash algo that requested in the challenge, it would be good to
# pass that information along to the client, too.
# ftp errors aren't handled cleanly
# check digest against correct (i.e. non-apache) implementation

# Possible extensions:
# complex proxies  XXX not sure what exactly was meant by this
# abstract factory for opener

import logging
import urllib.request
from socket import _GLOBAL_DEFAULT_TIMEOUT
from ._rfc3986 import is_clean_uri


warn = logging.getLogger("mechanize").warning


class Request(urllib.request.Request):
    def __init__(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False, visit=None,
                 timeout=_GLOBAL_DEFAULT_TIMEOUT):
        # In mechanize 0.2, the interpretation of a unicode url argument will
        # change: A unicode url argument will be interpreted as an IRI, and a
        # bytestring as a URI. For now, we accept unicode or bytestring.  We
        # don't insist that the value is always a URI (specifically, must only
        # contain characters which are legal), because that might break working
        # code (who knows what bytes some servers want to see, especially with
        # browser plugins for internationalised URIs).
        if not is_clean_uri(url):
            warn("url argument is not a URI "
                 "(contains illegal characters) %r" % url)
        super().__init__(self, url, data, headers)
        self.selector = None
        self.visit = visit
        self.timeout = timeout

    def __str__(self):
        return "<Request for %s>" % self.get_full_url()
