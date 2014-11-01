#!/usr/bin/env python2

import apt
import sys

try:
	cache = apt.Cache()	
	pkg = cache[sys.argv[1]]
	if pkg.installed is not None:
		print pkg.installed.version
	else:
		print ""
except:
	print ""
