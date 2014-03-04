__author__ = 'sfall_000'

# I was having problems with relative import statements that look like this:
#       from . import <package>
# Unfortunately, this style of importing was everywhere after I ran 2to3.
# So, I thought up this script to change those statements into something that worked for me:
#       from .<package> import <package member>
# The script also replaces all mentions of
#       <package>.<package member>
# with
#       <package member>
# If necessary, the script will rename the member to something unique.
#
# As is, it's set to run on all .py files in the mechanize subdirectory
# when called from the dev-tools folder.

import re
from os import chdir, listdir

path = "_urllib2.py"
chdir(r'C:\Users\sfall_000\Documents\GitHub\mechanize\mechanize')
#files = listdir('.')

import_prog = re.compile("from . import ([_A-Za-z0-9]+)")
# for path in files:
with open(path, 'r+') as f:
    contents = f.read()
    contents_minus = re.sub("#.+\n", "", contents)
    for match in import_prog.finditer(contents):
        pkg = match.group(1)
        uses = re.finditer(''.join([pkg, '.', '([_A-Za-z0-9]+)']), contents_minus)
        members = set([use.group(1) for use in uses])
        for m in members:
            if len(re.findall(m, contents_minus)) > len(members):
                members.remove(m)
                print('Look into ', m, ' in the "', path, '" file.')
                continue
            contents = re.sub(''.join([pkg, '.', m]), m, contents)
        pattern = ''.join(['from . import ', pkg])
        replacement = ''.join(['from .', pkg, ' import ']+[', '.join(members)])
        contents = re.sub(pattern, replacement, contents)
    f.seek(0)
    f.write(contents)
    f.truncate()
