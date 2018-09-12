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
import shlex
import subprocess

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

# Actually execute the command
def ExecuteCommand(cmd , commandCwd=None):
	if not commandCwd:
		cwd = os.path.expanduser( "~" );
	else:
		tmpCwd = os.path.expanduser( commandCwd );
		if (os.path.exists(tmpCwd)):
			cwd = tmpCwd

	if isinstance( cmd, str ):
		if (cmd.find("/home/") >= 0) or (cmd.find("xdg-su") >= 0) or (cmd.find("\"") >= 0):
			print("running manually...")
			try:
				os.chdir(cwd)
				subprocess.Popen(shlex.split(cmd))
				return True
			except Exception as detail:
				print(detail)
				return False
	cmd = cmd.split()
	cmd = RemoveArgs(cmd)

	try:
		os.chdir( cwd )
		string = ' '.join(cmd)
		subprocess.Popen(shlex.split(string))
		return True
	except Exception as detail:
		print(detail)
		return False

# Execute cmd using the double fork method
def Execute(cmd, commandCwd=None):
	child_pid = os.fork()
	if child_pid == 0:
		ExecuteCommand(cmd, commandCwd)
		os._exit(0)
	else:
		os.wait()
