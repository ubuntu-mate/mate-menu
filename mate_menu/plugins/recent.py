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
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango
from mate_menu.easygsettings import EasyGSettings
from mate_menu.execute import Execute
from mate_menu.easyfiles import *
from mate_menu.easybuttons import *

class pluginclass:
    """This is the main class for the plugin"""
    """It MUST be named pluginclass"""

    def __init__(self, mateMenuWin, toggleButton):

        self.Win = mateMenuWin
        self.toggleButton = toggleButton

        self.builder = Gtk.Builder()
        #The Glade file for the plugin
        self.builder.add_from_file (os.path.join( '/', 'usr', 'share', 'mate-menu',  'plugins', 'recent.glade' ))

        #Set 'window' property for the plugin (Must be the root widget)
        self.window = self.builder.get_object( "window1" )

        #Set 'heading' property for plugin
        self.heading = _("Recent documents")

        #This should be the first item added to the window in glade
        self.content_holder = self.builder.get_object( "eventbox1" )

        self.recentBox = self.builder.get_object("RecentBox")
        self.recentVBox = self.builder.get_object( "vbox1" )

        #Specify plugin width
        self.width = 250

        #Plugin icon
        self.icon = 'folder.png'

        self.settings = EasyGSettings ("org.mate.mate-menu.plugins.recent")

        self.settings.notifyAdd( 'height', self.RegenPlugin )
        self.settings.notifyAdd( 'width', self.RegenPlugin )
        self.settings.notifyAdd( 'num-recent-docs', self.RegenPlugin )
        self.settings.notifyAdd( 'recent-font-size', self.RegenPlugin )

        self.FileList=[]
        self.RecManagerInstance = Gtk.RecentManager.get_default()
        self.recentManagerId = self.RecManagerInstance.connect("changed", self.DoRecent)

        self.RegenPlugin()
        self.builder.get_object( "RecentTabs" ).set_current_page(1)

        #Connect event handlers
        clr_btn = self.builder.get_object("ClrBtn")
        clr_btn.connect("clicked", self.clrmenu)
        clr_btn.connect("motion-notify-event", self.onMotion)
        clr_btn.connect("enter-notify-event", self.onEnter)
        clr_btn.connect("focus-in-event", self.onFocusIn)
        clr_btn.connect("focus-out-event", self.onFocusOut)

    def wake (self) :
        pass

    def destroy( self ):
        self.recentBox.destroy()
        self.recentVBox.destroy()
        self.builder.get_object( "RecentTabs" ).destroy()
        self.builder.get_object("ClrBtn").destroy()
        self.content_holder.destroy()
        self.settings.notifyRemoveAll()
        if self.recentManagerId:
            self.RecManagerInstance.disconnect(self.recentManagerId)

    def RegenPlugin( self, *args, **kargs ):
        self.GetGSettingsEntries()

    def GetGSettingsEntries( self ):
        self.recenth = self.settings.get( 'int', 'height' )
        self.recentw = self.settings.get( 'int', 'width' )
        self.numentries = self.settings.get( 'int', 'num-recent-docs' )
        self.recentfontsize = self.settings.get( 'int', 'recent-font-size' )

        # Plugin icon
        self.icon = self.settings.get( "string", 'icon' )
        # Allow plugin to be minimized to the left plugin pane
        self.sticky = self.settings.get( "bool", "sticky" )
        self.minimized = self.settings.get( "bool", "minimized" )
        self.RebuildPlugin()

    def SetHidden( self, state ):
        if state == True:
            self.settings.set( "bool", "minimized", True )
        else:
            self.settings.set( "bool", "minimized", False )


    def RebuildPlugin(self):
        self.content_holder.set_size_request(self.recentw, self.recenth )
        self.DoRecent()


    def DoRecent( self, *args, **kargs ):
        for i in self.recentBox.get_children():
            i.destroy()

        self.recentVBox.set_size_request( self.recentw, self.recenth )
        if len( self.recentBox.get_children() ) < self.numentries:
            n=len( self.recentBox.get_children() )-1
        else:
            n=self.numentries-1
        while n >= 0:
            self.recentBox.remove( self.recentBox.get_children()[n] )
            n-=1

        self.FileList, self.IconList = self.GetRecent()
        loc = 0
        for Name in self.FileList:
            if Name != None:
                self.AddRecentBtn( Name, self.IconList[loc] )
            loc = loc + 1
        return True

    def clrmenu(self, *args, **kargs):
        self.RecManagerInstance.purge_items()
        self.DoRecent()
        return

    def AddRecentBtn( self, Name, RecentImage ):
        DispName=os.path.basename( Name )

        AButton = Gtk.Button( "", "ok", True )
        AButton.remove( AButton.get_children()[0] )
        AButton.set_size_request( 200, -1 )
        AButton.set_relief( Gtk.ReliefStyle.NONE )
        AButton.set_events( Gdk.EventMask.POINTER_MOTION_MASK )
        AButton.connect( "motion-notify-event", self.onMotion )
        AButton.connect( "enter-notify-event", self.onEnter )
        AButton.connect( "focus-in-event", self.onFocusIn )
        AButton.connect( "focus-out-event", self.onFocusOut )
        AButton.connect( "clicked", self.callback, Name )
        AButton.show()

        Box1 = Gtk.Box( orientation=Gtk.Orientation.HORIZONTAL, spacing=5 )

        ButtonIcon = Gtk.Image()
        ButtonIcon.set_size_request( 20, -1 )
        ButtonIcon.set_from_pixbuf(RecentImage)
        Box1.add( ButtonIcon )

        Label1 = Gtk.Label( DispName )
        Label1.set_ellipsize( Pango.EllipsizeMode.END )
        Box1.add( Label1 )

        AButton.add( Box1 )
        AButton.show_all()

        self.recentBox.pack_start( AButton, False, True, 0 )

    def onMotion(self, widget, event):
        # Only grab if mouse is actually hovering
        if self.mouse_entered:
            widget.grab_focus()
            self.mouse_entered = False

    def onEnter(self, widget, event):
        # Prevent false "enter" notifications by determining
        # whether the mouse is actually hovering on the button.
        self.mouse_entered = True

    def onFocusIn(self, widget, event):
        widget.set_state_flags( Gtk.StateFlags.PRELIGHT, False )

    def onFocusOut(self, widget, event):
        widget.unset_state_flags( Gtk.StateFlags.PRELIGHT )

    def callback(self, widget, filename=None):
        self.Win.hide()

        x = os.system("gio open \""+filename+"\"")
        if x == 256:
            dia = Gtk.Dialog('File not found!',
                             None,  #the toplevel wgt of your app
                             Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,  #binary flags or'ed together
                             ("Ok", 77))
            dia.vbox.pack_start(Gtk.Label('The location or file could not be found!'), False, False, 0)
            dia.vbox.show_all()
            dia.show()
            result = dia.run()
            if result == 77:
                dia.destroy()



    def GetRecent(self, *args, **kargs):
        FileString=[]
        IconString=[]
        RecentInfo=self.RecManagerInstance.get_items()
        # print(RecentInfo[0].get_icon(Gtk.IconSize.MENU))
        count=0
        MaxEntries=self.numentries
        if self.numentries == -1:
            MaxEntries=len(RecentInfo)
        for items in RecentInfo:
            FileString.append(items.get_uri_display())
            IconString.append(items.get_icon(Gtk.IconSize.MENU))
            count+=1
            if count >= MaxEntries:
                break
        return FileString,  IconString


    def ButtonClicked( self, widget, event, Exec ):
        self.press_x = event.x
        self.press_y = event.y
        self.Exec = Exec

    def ButtonReleased( self, w, ev, ev2 ):
        if ev.button == 1:
            if not hasattr( self, "press_x" ) or \
                    not w.drag_check_threshold( int( self.press_x ),
                                                                             int( self.press_y ),
                                                                             int( ev.x ),
                                                                             int( ev.y ) ):
                if self.Win.pinmenu == False:
                    self.Win.wTree.get_widget( "window1" ).hide()
                if "applications" in self.Win.plugins:
                    self.Win.plugins["applications"].wTree.get_widget( "entry1" ).grab_focus()
                Execute( w, self.Exec )

    def do_plugin(self):
        self.DoRecent()
