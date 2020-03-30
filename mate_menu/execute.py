# -*- coding: utf-8 -*-

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

import os

from gi.repository import Gdk, Gtk, Gio

def RemoveArgs(Execline):
	NewExecline = []
	Specials=["\"%c\"", "%f","%F","%u","%U","%d","%D","%n","%N","%i","%c","%k","%v","%m","%M", "-caption", "/bin/sh", "sh", "-c", "STARTED_FROM_MENU=yes"]
	for elem in Execline:
		elem = elem.replace("'","")
		elem = elem.replace("\"", "")
		if elem not in Specials:
			print(elem)
			NewExecline.append(elem)
	return NewExecline

# Actually launch the application
def Launch(cmd, cwd=None):
	if cwd:
		os.chdir(cwd)

	app_info = Gio.AppInfo.create_from_commandline(cmd,
						       None,
						       Gio.AppInfoCreateFlags.SUPPORTS_STARTUP_NOTIFICATION)

	display = Gdk.Display.get_default()
	context = display.get_app_launch_context()
	context.set_desktop(-1) # use default screen & desktop
	context.set_timestamp(Gtk.get_current_event_time())

	app_info.launch(None, context)

def Execute(cmd , commandCwd=None):
	if commandCwd:
		tmpCwd = os.path.expanduser( commandCwd );
		if (os.path.exists(tmpCwd)):
			cwd = tmpCwd
	else:
		cwd = None

	if isinstance( cmd, str ):
		if (cmd.find("/home/") >= 0) or (cmd.find("xdg-su") >= 0) or (cmd.find("\"") >= 0):
			try:
				Launch(cmd, cwd)
				return True
			except Exception as detail:
				print(detail)
				return False
	cmd = cmd.split()
	cmd = RemoveArgs(cmd)

	try:
		string = ' '.join(cmd)
		Launch(string, cwd)
		return True
	except Exception as detail:
		print(detail)
		return False
