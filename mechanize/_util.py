"""Utility functions and date/time routines.

 Copyright 2002-2006 John J Lee <jjl@pobox.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD or ZPL 2.1 licenses (see the file
COPYING.txt included with the distribution).
"""

import warnings


class ExperimentalWarning(UserWarning):
    pass

def experimental(message):
    warnings.warn(message, ExperimentalWarning, stacklevel=3)
def hide_experimental_warnings():
    warnings.filterwarnings("ignore", category=ExperimentalWarning)
def reset_experimental_warnings():
    warnings.filterwarnings("default", category=ExperimentalWarning)

def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=3)
def hide_deprecations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
def reset_deprecations():
    warnings.filterwarnings("default", category=DeprecationWarning)


def isstringlike(x):
    try: x+""
    except: return False
    else: return True

## def caller():
##     try:
##         raise SyntaxError
##     except:
##         import sys
##     return sys.exc_traceback.tb_frame.f_back.f_back.f_code.co_name
