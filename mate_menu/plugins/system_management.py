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

import gettext
import gi
import os

gi.require_version("Gtk", "2.0")

from gi.repository import Gtk
from mate_menu.easybuttons import *
from mate_menu.execute import Execute
from mate_menu.easygsettings import EasyGSettings

# i18n
gettext.install("mate-menu", "/usr/share/locale")

class pluginclass( object ):

    def __init__(self, mateMenuWin, toggleButton):

        self.mateMenuWin = mateMenuWin
        self.toggleButton = toggleButton

        self.builder = Gtk.Builder()
        self.builder.add_from_file( os.path.join( '/', 'usr', 'share', 'mate-menu',  'plugins', 'system_management.glade' ))

        self.systemBtnHolder    = self.builder.get_object( "system_button_holder" )
        self.editableBtnHolder  = self.builder.get_object( "editable_button_holder" )
        self.scrolledWindow = self.builder.get_object( "scrolledwindow2" )

        # These properties are NECESSARY to maintain consistency

        # Set 'window' property for the plugin (Must be the root widget)
        self.window = self.builder.get_object( "mainWindow" )

        # Set 'heading' property for plugin
        self.heading = _("System")

        # This should be the first item added to the window in glade
        self.content_holder = self.builder.get_object( "System" )

        # Items to get custom colors
        self.itemstocolor = [ self.builder.get_object( "viewport2" ) ]

        # Gconf stuff
        self.settings = EasyGSettings( "org.mate.mate-menu.plugins.system_management" )

        self.settings.notifyAdd( "icon-size", self.RegenPlugin )
        self.settings.notifyAdd( "show-control-center", self.RegenPlugin )
        self.settings.notifyAdd( "show-lock-screen", self.RegenPlugin )
        self.settings.notifyAdd( "show-logout", self.RegenPlugin )
        self.settings.notifyAdd( "show-package-manager", self.RegenPlugin )
        self.settings.notifyAdd( "show-terminal", self.RegenPlugin )
        self.settings.notifyAdd( "show-quit", self.RegenPlugin )
        self.settings.notifyAdd( "allow-scrollbar", self.RegenPlugin )
        self.settings.notifyAdd( "height", self.changePluginSize )
        self.settings.notifyAdd( "width", self.changePluginSize )
        self.settings.bindGSettingsEntryToVar( "bool", "sticky", self, "sticky" )

        self.GetGSettingsEntries()

        self.content_holder.set_size_request( self.width, self.height )

    def destroy( self ):
        self.settings.notifyRemoveAll()

    def wake (self) :
        pass

    def changePluginSize( self, settings, key, args ):
        self.allowScrollbar = self.settings.get( "bool", "allow-scrollbar")
        if key == "width":
            self.width = settings.get_int(key)
        elif key == "height":
            if (self.allowScrollbar == False):
                self.height = -1
                self.scrolledWindow.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER )
            else:
                self.scrolledWindow.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC )
                self.height = settings.get_int(key)

        self.content_holder.set_size_request( self.width, self.height )


    def RegenPlugin( self, *args, **kargs ):
        self.GetGSettingsEntries()
        self.ClearAll()
        self.do_standard_items()

    def GetGSettingsEntries( self ):

        self.width = self.settings.get( "int", "width")
        self.allowScrollbar = self.settings.get( "bool", "allow-scrollbar")
        self.scrolledWindow.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC )
        self.height = self.settings.get( "int", "height")
        self.content_holder.set_size_request( self.width, self.height )
        if (self.allowScrollbar == False):
            self.height = -1
            self.scrolledWindow.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER )
        self.content_holder.set_size_request( self.width, self.height )
        self.iconsize = self.settings.get( "int","icon-size")

        # Check toggles
        self.showPackageManager = self.settings.get( "bool", "show-package-manager")
        self.showControlCenter = self.settings.get( "bool", "show-control-center")
        self.showTerminal = self.settings.get( "bool", "show-terminal")
        self.showLockScreen = self.settings.get( "bool", "show-lock-screen")
        self.showLogout = self.settings.get( "bool", "show-logout")
        self.showQuit = self.settings.get( "bool", "show-quit")

        # Plugin icon
        self.icon = self.settings.get( "string", "icon" )
        # Allow plugin to be minimized to the left plugin pane
        self.sticky = self.settings.get( "bool", "sticky")
        self.minimized = self.settings.get( "bool", "minimized")

    def ClearAll(self):
        for child in self.systemBtnHolder.get_children():
            child.destroy()
        for child in self.editableBtnHolder.get_children():
            child.destroy()

    #Add standard items
    def do_standard_items( self ):

        if ( self.showPackageManager == True ):           
            if os.path.exists("/usr/bin/software-center") or os.path.exists("/usr/bin/synaptic-pkexec"):
                if os.path.exists("/usr/bin/synaptic-pkexec"):
                    Button2 = easyButton("synaptic", self.iconsize, [_("Package Manager")], -1, -1 )
                    Button2.connect( "clicked", self.ButtonClicked, "/usr/bin/synaptic-pkexec" )
                elif os.path.exists("/usr/bin/software-center"):
                    Button2 = easyButton("softwarecenter", self.iconsize, [_("Package Manager")], -1, -1 )
                    Button2.connect( "clicked", self.ButtonClicked, "/usr/bin/software-center" )
                Button2.show()
                self.systemBtnHolder.pack_start( Button2, False, False, 0 )
                self.mateMenuWin.setTooltip( Button2, _("Install, remove and upgrade software packages") )

        if ( self.showControlCenter == True ):
            Button3 = easyButton( "gtk-preferences", self.iconsize, [_("Control Center")], -1, -1 )
            Button3.connect( "clicked", self.ButtonClicked, "mate-control-center" )
            Button3.show()
            self.systemBtnHolder.pack_start( Button3, False, False, 0 )
            self.mateMenuWin.setTooltip( Button3, _("Configure your system") )

        if ( self.showTerminal == True ):
            Button4 = easyButton( "terminal", self.iconsize, [_("Terminal")], -1, -1 )
            if os.path.exists("/usr/bin/mate-terminal"):
                Button4.connect( "clicked", self.ButtonClicked, "mate-terminal" )
            else:
                Button4.connect( "clicked", self.ButtonClicked, "x-terminal-emulator" )
            Button4.show()
            self.systemBtnHolder.pack_start( Button4, False, False, 0 )
            self.mateMenuWin.setTooltip( Button4, _("Use the command line") )

        if ( self.showLockScreen == True ):
            Button5 = easyButton( "system-lock-screen", self.iconsize, [_("Lock Screen")], -1, -1 )
            if os.path.exists("/usr/bin/mate-screensaver-command"):
                Button5.connect( "clicked", self.ButtonClicked, "mate-screensaver-command -l" )
            else:
                Button5.connect( "clicked", self.ButtonClicked, "xdg-screensaver lock" )

            Button5.show()
            self.systemBtnHolder.pack_start( Button5, False, False, 0 )
            self.mateMenuWin.setTooltip( Button5, _("Requires password to unlock") )

        if ( self.showLogout == True ):
            Button6 = easyButton( "system-log-out", self.iconsize, [_("Logout")], -1, -1 )
            Button6.connect( "clicked", self.ButtonClicked, "mate-session-save --logout-dialog" )
            Button6.show()
            self.systemBtnHolder.pack_start( Button6, False, False, 0 )
            self.mateMenuWin.setTooltip( Button6, _("Log out or switch user") )

        if ( self.showQuit == True ):
            Button7 = easyButton( "system-shutdown", self.iconsize, [_("Quit")], -1, -1 )
            Button7.connect( "clicked", self.ButtonClicked, "mate-session-save --shutdown-dialog" )
            Button7.show()
            self.systemBtnHolder.pack_start( Button7, False, False, 0 )
            self.mateMenuWin.setTooltip( Button7, _("Shutdown, restart, suspend or hibernate") )

    def ButtonClicked( self, widget, Exec ):
        self.mateMenuWin.hide()
        if Exec:
            Execute( Exec )

    def do_plugin( self ):
        self.do_standard_items()
