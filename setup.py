#!/usr/bin/env python2
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
  ("share/man/man1",
   glob("data/*.1")
  ),
  ("share/glib-2.0/schemas",
   [
    "data/org.mate.mate-menu.gschema.xml",
   ] +
   glob("data/plugins/org.mate.mate-menu.plugins.*.gschema.xml"),
  ),
  ("share/mate-panel/applets",
   [
    "data/org.mate.panel.MateMenuApplet.mate-panel-applet",
   ]),
  ("share/dbus-1/services",
   [
    "data/org.mate.panel.applet.MateMenuAppletFactory.service",
   ]),
  ("share/mate-menu",
   [
    "data/mate-menu.glade",
    "data/mate-menu-config.glade",
    "data/popup.xml",
    "data/applications.list",
   ]),
  ("share/mate-menu/plugins",
   [
    "data/plugins/applications.glade",
    "data/plugins/system_management.glade",
    "data/plugins/places.glade",
    "data/plugins/recent.glade",
    "mate_menu/plugins/applications.py",
    "mate_menu/plugins/system_management.py",
    "mate_menu/plugins/places.py",
    "mate_menu/plugins/recent.py",
   ]),
  ("share/mate-menu/icons",
   [
    "data/icons/mate-logo.svg",
    "data/icons/dictionary.png",
   ]),
  ("share/mate-menu/icons/search_engines",
   [
    "data/icons/google.ico",
    "data/icons/wikipedia.ico",
   ]),
  ("lib/mate-menu",
   glob("lib/*.py*"),
  ),
]
data_files.extend(datafilelist("share/locale", 'build/mo'))

if sys.argv[1] == "build":
    import compileall
    compileall.compile_dir("lib")
elif sys.argv[1] in ("install", "uninstall"):
    # Enforce "/usr" prefix.
    sys.argv += ["--prefix", "/usr"]

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
