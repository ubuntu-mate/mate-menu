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

from gi.repository import Gio, GLib


class FileMonitor ( object ):
    """ Watches files for changes without spawning threads or background
        pollers: each monitored file gets a standard Gio file monitor, and
        the change callback is dispatched on the GTK main loop
    """
    def __init__ ( self ):
        self.monitorId = 0
        self.monitors = { }

    def addMonitor ( self, filename, callback, args = None ):
        self.monitorId += 1
        monitorId = self.monitorId

        gio_file = Gio.File.new_for_path( filename )
        monitor = gio_file.monitor_file( Gio.FileMonitorFlags.NONE, None )
        changedId = monitor.connect( "changed", self.fileChanged, callback, args )
        self.monitors[ monitorId ] = ( monitor, changedId )

        return monitorId

    def removeMonitor ( self, monitorId ):
        if monitorId in self.monitors:
            monitor, changedId = self.monitors.pop( monitorId )
            monitor.disconnect( changedId )
            monitor.cancel()

    def fileChanged ( self, monitor, file, other_file, event, callback, args ):
        if args:
            GLib.idle_add( callback, args )
        else:
            GLib.idle_add( callback )


monitor = FileMonitor()
