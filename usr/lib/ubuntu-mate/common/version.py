#!/usr/bin/env python

import sys

try:
    import apt
    cache = apt.Cache()
    pkg = cache[sys.argv[1]]
    if pkg.installed is not None:
        print pkg.installed.version
    else:
        print ""
except:
    print ""
