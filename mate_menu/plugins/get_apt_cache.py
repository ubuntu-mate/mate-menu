#!/usr/bin/env python

# Copyright (C) 2007-2014 Clement Lefebvre <root@linuxmint.com>
# Copyright (C) 2015 Martin Wimpress <code@ubuntu-mate.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

import apt, sys

try:
    cache = apt.Cache()    
    for pkg in cache:
        if not pkg.is_installed:
            name = pkg.name
            summary = pkg.candidate.summary.capitalize()
            description = pkg.candidate.description.replace("\n", "~~~")
            print "CACHE" + "###" + str(name) + "###" + str(summary) + "###" + str(description)
except Exception, detail:
    print "ERROR###ERROR###ERROR###ERROR"
    print detail
    sys.exit(1)
