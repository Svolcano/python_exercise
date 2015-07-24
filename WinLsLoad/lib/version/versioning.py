#!/usr/bin/env python

""" Git Versioning Script

Will transform stdin to expand some keywords with git version/author/date information.

Specify --clean to remove this information before commit.

Setup:

1. Copy versioning.py into your git repository

2. Run:

 git config filter.versioning.smudge 'python versioning.py'
 git config filter.versioning.clean  'python versioning.py --clean'
 echo 'version.py filter=versioning' >> .gitattributes
 git add versioning.py


3. add a version.py file with this contents:

 __version__ = ""
 __author__ = ""
 __email__ = ""
 __date__ = ""

"""

import sys
import subprocess
import re


def main():
    clean = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '--clean':
            clean = True

    # initialise empty here. Otherwise: forkbomb through the git calls.
    subst_list = {
        "version": "",
        "date": "",
        "author": "",
        "email": ""
    }

    if not clean:
        p = subprocess.Popen(['git','describe','--always'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        version,err=p.communicate()
        p = subprocess.Popen(['git','log','--pretty=format:"%ad"','-1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        date,err=p.communicate()
        p = subprocess.Popen(['git','log','--pretty=format:"%an"','-1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        author,err=p.communicate()
        p = subprocess.Popen(['git','log','--pretty=format:"%ae"','-1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        email,err=p.communicate()

        subst_list = {
            "version": version.strip().strip('\"'),  
            "date": date.strip().strip('\"'),
            "author": author.strip().strip('\"'),
            "email": email.strip().strip('\"')
        }
        for k, v in subst_list.iteritems():
            #v = re.sub(r'[\n\r\t"\']', "", v)
            #rexp = "__%s__\s*=[\s'\"]+" % k
            #line = re.sub(rexp, "__%s__ = \"%s\"\n" % (k, v), line)
            #print line
            #sys.stdout.write(line)
            line = '__%s__=\"%s\"' % (k,v)
            print line


if __name__ == "__main__":
    main()
