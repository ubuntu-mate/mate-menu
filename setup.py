#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 by Mike Gabriel <mike.gabriel@das-netzwerkteam.de>
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

import os
import sys

from glob import glob

from setuptools import setup

import DistUtilsExtra.command.build_extra
import DistUtilsExtra.command.build_i18n
import DistUtilsExtra.command.clean_i18n

# to update i18n .mo files (and merge .pot file into .po files) run on Linux:
# ,,python setup.py build_i18n -m''

# silence pyflakes, __VERSION__ is properly assigned below...
__VERSION__ = '0.0.0.0'
for line in file('lib/mate-menu.py').readlines():
    if (line.startswith('__VERSION__')):
        exec(line.strip())
        break

PROGRAM_VERSION = __VERSION__

def datafilelist(installbase, sourcebase):
    datafileList = []
    for root, subFolders, files in os.walk(sourcebase):
        fileList = []
        for f in files:
            fileList.append(os.path.join(root, f))
        datafileList.append((root.replace(sourcebase, installbase), fileList))
    return datafileList

data_files = [
    ('{prefix}/share/man/man1'.format(prefix=sys.prefix), glob('data/*.1')),
    ('{prefix}/share/glib-2.0/schemas'.format(prefix=sys.prefix), ['data/org.mate.mate-menu.gschema.xml',
                                                                  ] +
                                                                  glob('data/plugins/org.mate.mate-menu.plugins.*.gschema.xml'),
    ),
    ('{prefix}/share/mate-panel/applets'.format(prefix=sys.prefix), ['data/org.mate.panel.MateMenuApplet.mate-panel-applet']),
    ('{prefix}/share/dbus-1/services'.format(prefix=sys.prefix), ['data/org.mate.panel.applet.MateMenuAppletFactory.service']),
    ('{prefix}/share/mate-menu'.format(prefix=sys.prefix), ['data/mate-menu-config.glade',
                                                            'data/mate-menu.glade',
                                                            'data/popup.xml',
                                                            'data/applications.list',
                                                           ],
    ),
    ('{prefix}/share/mate-menu/plugins'.format(prefix=sys.prefix), ['data/plugins/applications.glade',
                                                                    'data/plugins/system_management.glade',
                                                                    'data/plugins/places.glade',
                                                                    'data/plugins/recent.glade',
                                                                    'mate_menu/plugins/applications.py',
                                                                    'mate_menu/plugins/system_management.py',
                                                                    'mate_menu/plugins/places.py',
                                                                    'mate_menu/plugins/recent.py',
                                                                   ],
    ),
    ('{prefix}/share/mate-menu/icons'.format(prefix=sys.prefix), ['data/icons/mate-logo.svg',
                                                                  'data/icons/dictionary.png',
                                                                 ],
    ),
    ('{prefix}/share/mate-menu/icons/search_engines'.format(prefix=sys.prefix), ['data/icons/google.ico','data/icons/wikipedia.ico']),
    ('{prefix}/lib/mate-menu'.format(prefix=sys.prefix), glob('lib/*.py')),
]
data_files.extend(datafilelist('{prefix}/share/locale'.format(prefix=sys.prefix), 'build/mo'))

cmdclass ={
            "build" : DistUtilsExtra.command.build_extra.build_extra,
            "build_i18n" :  DistUtilsExtra.command.build_i18n.build_i18n,
            "clean": DistUtilsExtra.command.clean_i18n.clean_i18n,
}

setup(
    name = "mate-menu",
    version = PROGRAM_VERSION,
    description = "An advanced menu for MATE. Supports filtering, favorites, autosession, and many other features.",
    license = 'GPLv2+',
    author = 'Martin Wimpress',
    url = 'https://bitbucket.org/ubuntu-mate/mate-menu/',
    packages = [ 'mate_menu', 'mate_menu.plugins', ],
    package_dir = {
        '': '.',
    },
    data_files = data_files,
    install_requires = [ 'setuptools', ],
    scripts = ['mate-menu'],
    cmdclass = cmdclass,
)
