#!/usr/bin/env python3
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
import subprocess
import signal

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GdkPixbuf
import mate_menu.keybinding as keybinding

signal.signal(signal.SIGINT, signal.SIG_DFL)

# i18n
gettext.install("mate-menu", "/usr/share/locale")

from mate_menu.easygsettings import EasyGSettings

class mateMenuConfig( object ):

    def __init__( self ):

        self.data_path =  os.path.join('/', 'usr', 'share', 'mate-menu' )

        # Load glade file and extract widgets
        self.builder = Gtk.Builder()

        self.builder.add_from_file (os.path.join(self.data_path, "mate-menu-config.glade" ))
        self.mainWindow=self.builder.get_object("mainWindow")

        #i18n
        self.mainWindow.set_title(_("Menu preferences"))
        self.mainWindow.set_icon_name("start-here")

        self.builder.get_object("startWithFavorites").set_label(_("Always start with favorites pane"))
        self.builder.get_object("showButtonIcon").set_label(_("Show button icon"))
        self.builder.get_object("showRecentPlugin").set_label(_("Show recent documents plugin"))
        self.builder.get_object("showApplicationsPlugin").set_label(_("Show applications plugin"))
        self.builder.get_object("showSystemPlugin").set_label(_("Show system plugin"))
        self.builder.get_object("showPlacesPlugin").set_label(_("Show places plugin"))

        self.builder.get_object("showAppComments").set_label(_("Show application comments"))
        self.builder.get_object("showCategoryIcons").set_label(_("Show category icons"))
        self.builder.get_object("hover").set_label(_("Hover"))
        self.builder.get_object("remember_filter").set_label(_("Remember the last category or search"))
        self.builder.get_object("swapGeneric").set_label(_("Swap name and generic name"))

        self.builder.get_object("label11").set_text(_("Border width:"))
        self.builder.get_object("label25").set_text(_("pixels"))

        self.builder.get_object("buttonTextLabel").set_text(_("Button text:"))
        self.builder.get_object("label1").set_text(_("Options"))
        self.builder.get_object("applicationsLabel").set_text(_("Applications"))

        self.builder.get_object("favLabel").set_text(_("Favorites"))
        self.builder.get_object("mainbuttonLabel").set_text(_("Main button"))
        self.builder.get_object("pluginsLabel").set_text(_("Plugins"))

        self.builder.get_object("always_show_search").set_label(_("Always show search suggestions"))
        self.builder.get_object("searchEngineTitleLabel").set_text(_("Search Engines:"))
        self.builder.get_object("enable_ddg").set_label(_("DuckDuckGo"))
        self.builder.get_object("enable_google").set_label(_("Google"))
        self.builder.get_object("enable_wikipedia").set_label(_("Wikipedia"))
        self.builder.get_object("enable_dictionary").set_label(_("Dictionary"))
        self.builder.get_object("enable_computer").set_label(_("Computer"))

        #self.builder.get_object("applicationsLabel").set_text(_("Applications"))
        #self.builder.get_object("favoritesLabel").set_text(_("Favorites"))
        self.builder.get_object("numberColumnsLabel").set_text(_("Number of columns:"))
        self.builder.get_object("iconSizeLabel").set_text(_("Icon size:"))
        self.builder.get_object("iconSizeLabel2").set_text(_("Icon size:"))
        self.builder.get_object("placesIconSizeLabel").set_text(_("Icon size:"))
        self.builder.get_object("systemIconSizeLabel").set_text(_("Icon size:"))
        self.builder.get_object("hoverLabel").set_text(_("Hover delay (ms):"))
        self.builder.get_object("label5").set_text(_("Search command:"))

        self.builder.get_object("placesLabel").set_text(_("Places"))
        self.builder.get_object("allowscrollbarcheckbutton").set_label(_("Allow Scrollbar"))
        self.builder.get_object("showgtkbookmarkscheckbutton").set_label(_("Show GTK+ Bookmarks"))
        self.builder.get_object("placesHeightEntryLabel").set_text(_("Height:"))
        self.builder.get_object("defaultPlacesFrameLabel").set_text(_("Toggle Default Places:"))
        self.builder.get_object("computercheckbutton").set_label(_("Computer"))
        self.builder.get_object("homecheckbutton").set_label(_("Home Folder"))
        self.builder.get_object("networkcheckbutton").set_label(_("Network"))
        self.builder.get_object("desktopcheckbutton").set_label(_("Desktop"))
        self.builder.get_object("trashcheckbutton").set_label(_("Trash"))
        self.builder.get_object("customPlacesFrameLabel").set_text(_("Custom Places:"))

        self.builder.get_object("systemLabel").set_text(_("System"))
        self.builder.get_object("allowscrollbarcheckbutton1").set_label(_("Allow Scrollbar"))
        self.builder.get_object("systemHeightEntryLabel").set_text(_("Height:"))
        self.builder.get_object("defaultItemsFrameLabel").set_text(_("Toggle Default Items:"))
        self.builder.get_object("packagemanagercheckbutton").set_label(_("Package Manager"))
        self.builder.get_object("controlcentercheckbutton").set_label(_("Control Center"))
        self.builder.get_object("terminalcheckbutton").set_label(_("Terminal"))
        self.builder.get_object("lockcheckbutton").set_label(_("Lock Screen"))
        self.builder.get_object("logoutcheckbutton").set_label(_("Log Out"))
        self.builder.get_object("quitcheckbutton").set_label(_("Quit"))

        self.editPlaceDialogTitle = (_("Edit Place"))
        self.newPlaceDialogTitle = (_("New Place"))
        self.folderChooserDialogTitle = (_("Select a folder"))

        self.startWithFavorites = self.builder.get_object( "startWithFavorites" )
        self.showAppComments = self.builder.get_object( "showAppComments" )
        self.showCategoryIcons = self.builder.get_object( "showCategoryIcons" )
        self.showRecentPlugin = self.builder.get_object( "showRecentPlugin" )
        self.showApplicationsPlugin = self.builder.get_object( "showApplicationsPlugin" )
        self.showSystemPlugin = self.builder.get_object( "showSystemPlugin" )
        self.showPlacesPlugin = self.builder.get_object( "showPlacesPlugin" )
        self.swapGeneric = self.builder.get_object("swapGeneric")
        self.hover = self.builder.get_object( "hover" )
        self.hoverDelay = self.builder.get_object( "hoverDelay" )
        self.rememberFilter = self.builder.get_object( "remember_filter" )
        self.alwaysShowSearch = self.builder.get_object( "always_show_search" )
        self.enableDdg = self.builder.get_object( "enable_ddg" )
        self.enableGoogle = self.builder.get_object( "enable_google" )
        self.enableWikipedia = self.builder.get_object( "enable_wikipedia" )
        self.enableDictionary = self.builder.get_object( "enable_dictionary" )
        self.enableComputer = self.builder.get_object( "enable_computer" )
        self.iconSize = self.builder.get_object( "iconSize" )
        self.favIconSize = self.builder.get_object( "favIconSize" )
        self.placesIconSize = self.builder.get_object( "placesIconSize" )
        self.systemIconSize = self.builder.get_object( "systemIconSize" )
        self.favCols = self.builder.get_object( "numFavCols" )
        self.borderWidth = self.builder.get_object( "borderWidth" )
        self.showButtonIcon = self.builder.get_object( "showButtonIcon" )
        self.buttonText = self.builder.get_object( "buttonText" )
        self.hotkeyWidget = keybinding.KeybindingWidget(_("Keyboard shortcut:") )
        grid = self.builder.get_object( "main_grid" )
        grid.attach(self.hotkeyWidget, 0, 2, 2, 1)
        self.image_filter = Gtk.FileFilter()
        self.image_filter.set_name(_("Images"))
        self.image_filter.add_pattern("*.png")
        self.image_filter.add_pattern("*.jpg")
        self.image_filter.add_pattern("*.jpeg")
        self.image_filter.add_pattern("*.bmp")
        self.image_filter.add_pattern("*.ico")
        self.image_filter.add_pattern("*.xpm")
        self.image_filter.add_pattern("*.svg")
        self.searchCommand = self.builder.get_object( "search_command" )
        self.computertoggle = self.builder.get_object( "computercheckbutton" )
        self.homefoldertoggle = self.builder.get_object( "homecheckbutton" )
        self.networktoggle = self.builder.get_object( "networkcheckbutton" )
        self.desktoptoggle = self.builder.get_object( "desktopcheckbutton" )
        self.trashtoggle = self.builder.get_object( "trashcheckbutton" )
        self.customplacestree = self.builder.get_object( "customplacestree" )
        self.allowPlacesScrollbarToggle = self.builder.get_object( "allowscrollbarcheckbutton" )
        self.showgtkbookmarksToggle = self.builder.get_object( "showgtkbookmarkscheckbutton" )
        self.placesHeightButton = self.builder.get_object( "placesHeightSpinButton" )
        if (self.allowPlacesScrollbarToggle.get_active() == False):
            self.placesHeightButton.set_sensitive(False)
        self.allowPlacesScrollbarToggle.connect("toggled", self.togglePlacesHeightEnabled )
        self.packageManagerToggle = self.builder.get_object( "packagemanagercheckbutton" )
        self.controlCenterToggle = self.builder.get_object( "controlcentercheckbutton" )
        self.terminalToggle = self.builder.get_object( "terminalcheckbutton" )
        self.lockToggle = self.builder.get_object( "lockcheckbutton" )
        self.logoutToggle = self.builder.get_object( "logoutcheckbutton" )
        self.quitToggle = self.builder.get_object( "quitcheckbutton" )
        self.allowSystemScrollbarToggle = self.builder.get_object( "allowscrollbarcheckbutton1" )
        self.systemHeightButton = self.builder.get_object( "systemHeightSpinButton" )
        if (self.allowSystemScrollbarToggle.get_active() == False): self.systemHeightButton.set_sensitive(False)
        self.allowSystemScrollbarToggle.connect("toggled", self.toggleSystemHeightEnabled )
        self.builder.get_object( "closeButton" ).connect("clicked", Gtk.main_quit )


        self.settings = EasyGSettings( "org.mate.mate-menu" )
        self.settingsApplications = EasyGSettings( "org.mate.mate-menu.plugins.applications" )
        self.settingsPlaces = EasyGSettings( "org.mate.mate-menu.plugins.places" )
        self.settingsSystem = EasyGSettings( "org.mate.mate-menu.plugins.system_management" )

        self.bindGSettingsValueToWidget( self.settings, "bool", "start-with-favorites", self.startWithFavorites, "toggled", self.startWithFavorites.set_active, self.startWithFavorites.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "show-application-comments", self.showAppComments, "toggled", self.showAppComments.set_active, self.showAppComments.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "show-category-icons", self.showCategoryIcons, "toggled", self.showCategoryIcons.set_active, self.showCategoryIcons.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "categories-mouse-over", self.hover, "toggled", self.hover.set_active, self.hover.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "swap-generic-name", self.swapGeneric, "toggled", self.swapGeneric.set_active, self.swapGeneric.get_active )

        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "category-hover-delay", self.hoverDelay, "value-changed", self.hoverDelay.set_value, self.hoverDelay.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "icon-size", self.iconSize, "value-changed", self.iconSize.set_value, self.iconSize.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "favicon-size", self.favIconSize, "value-changed", self.favIconSize.set_value, self.favIconSize.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "fav-cols", self.favCols, "value-changed", self.favCols.set_value, self.favCols.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "remember-filter", self.rememberFilter, "toggled", self.rememberFilter.set_active, self.rememberFilter.get_active)

        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "always-show-search", self.alwaysShowSearch, "toggled", self.alwaysShowSearch.set_active, self.alwaysShowSearch.get_active)
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "enable-ddg", self.enableDdg, "toggled", self.enableDdg.set_active, self.enableDdg.get_active)
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "enable-google", self.enableGoogle, "toggled", self.enableGoogle.set_active, self.enableGoogle.get_active)
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "enable-wikipedia", self.enableWikipedia, "toggled", self.enableWikipedia.set_active, self.enableWikipedia.get_active)
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "enable-dictionary", self.enableDictionary, "toggled", self.enableDictionary.set_active, self.enableDictionary.get_active)
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "enable-computer", self.enableComputer, "toggled", self.enableComputer.set_active, self.enableComputer.get_active)

        self.bindGSettingsValueToWidget( self.settingsPlaces, "int", "icon-size", self.placesIconSize, "value-changed", self.placesIconSize.set_value, self.placesIconSize.get_value )
        self.bindGSettingsValueToWidget( self.settingsSystem, "int", "icon-size", self.systemIconSize, "value-changed", self.systemIconSize.set_value, self.systemIconSize.get_value )

        self.bindGSettingsValueToWidget( self.settings, "int", "border-width", self.borderWidth, "value-changed", self.borderWidth.set_value, self.borderWidth.get_value_as_int )
        self.bindGSettingsValueToWidget( self.settings, "bool", "hide-applet-icon", self.showButtonIcon, "toggled", self.setShowButtonIcon, self.getShowButtonIcon )
        self.bindGSettingsValueToWidget( self.settings, "string", "applet-text", self.buttonText, "changed", self.buttonText.set_text, self.buttonText.get_text )
        self.bindGSettingsValueToWidget( self.settings, "string", "hot-key", self.hotkeyWidget, "accel-edited", self.hotkeyWidget.set_val, self.hotkeyWidget.get_val )
        self.bindGSettingsValueToWidget( self.settingsApplications, "string", "search-command", self.searchCommand, "changed", self.searchCommand.set_text, self.searchCommand.get_text )

        self.getPluginsToggle()
        self.showRecentPlugin.connect("toggled", self.setPluginsLayout )
        self.showApplicationsPlugin.connect("toggled", self.setPluginsLayout )
        self.showSystemPlugin.connect("toggled", self.setPluginsLayout )
        self.showPlacesPlugin.connect("toggled", self.setPluginsLayout )


        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-computer", self.computertoggle, "toggled", self.computertoggle.set_active, self.computertoggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-home-folder", self.homefoldertoggle, "toggled", self.homefoldertoggle.set_active, self.homefoldertoggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-network", self.networktoggle, "toggled", self.networktoggle.set_active, self.networktoggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-desktop", self.desktoptoggle, "toggled", self.desktoptoggle.set_active, self.desktoptoggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-trash", self.trashtoggle, "toggled", self.trashtoggle.set_active, self.trashtoggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "int", "height", self.placesHeightButton, "value-changed", self.placesHeightButton.set_value, self.placesHeightButton.get_value_as_int )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "allow-scrollbar", self.allowPlacesScrollbarToggle, "toggled", self.allowPlacesScrollbarToggle.set_active, self.allowPlacesScrollbarToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsPlaces, "bool", "show-gtk-bookmarks", self.showgtkbookmarksToggle, "toggled", self.showgtkbookmarksToggle.set_active, self.showgtkbookmarksToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-package-manager", self.packageManagerToggle, "toggled", self.packageManagerToggle.set_active, self.packageManagerToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-control-center", self.controlCenterToggle, "toggled", self.controlCenterToggle.set_active, self.controlCenterToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-terminal", self.terminalToggle, "toggled", self.terminalToggle.set_active, self.terminalToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-lock-screen", self.lockToggle, "toggled", self.lockToggle.set_active, self.lockToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-logout", self.logoutToggle, "toggled", self.logoutToggle.set_active, self.logoutToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "show-quit", self.quitToggle, "toggled", self.quitToggle.set_active, self.quitToggle.get_active )
        self.bindGSettingsValueToWidget( self.settingsSystem, "int", "height", self.systemHeightButton, "value-changed", self.systemHeightButton.set_value, self.systemHeightButton.get_value_as_int )
        self.bindGSettingsValueToWidget( self.settingsSystem, "bool", "allow-scrollbar", self.allowSystemScrollbarToggle, "toggled", self.allowSystemScrollbarToggle.set_active, self.allowSystemScrollbarToggle.get_active )

        self.customplacepaths = self.settingsPlaces.get( "list-string", "custom-paths" )
        self.customplacenames = self.settingsPlaces.get( "list-string", "custom-names" )

        self.customplacestreemodel = Gtk.ListStore( str, str)
        self.cell = Gtk.CellRendererText()

        for count in range( len(self.customplacepaths) ):
            self.customplacestreemodel.append( [ self.customplacenames[count], self.customplacepaths[count] ] )

        self.customplacestreemodel.connect("row-inserted", self.updatePlacesGSettings)
        self.customplacestreemodel.connect("row-deleted", self.updatePlacesGSettings)
        self.customplacestreemodel.connect("rows-reordered", self.updatePlacesGSettings)
        self.customplacestreemodel.connect("row-changed", self.updatePlacesGSettings)
        self.customplacestree.set_model( self.customplacestreemodel )
        self.namescolumn = Gtk.TreeViewColumn( _("Name"), self.cell, text = 0 )
        self.placescolumn = Gtk.TreeViewColumn( _("Path"), self.cell, text = 1 )
        self.customplacestree.append_column( self.namescolumn )
        self.customplacestree.append_column( self.placescolumn )
        self.builder.get_object("newButton").connect("clicked", self.newPlace)
        self.builder.get_object("editButton").connect("clicked", self.editPlace)
        self.builder.get_object("upButton").connect("clicked", self.moveUp)
        self.builder.get_object("downButton").connect("clicked", self.moveDown)
        self.builder.get_object("removeButton").connect("clicked", self.removePlace)

        self.mainWindow.present()

    def getPluginsToggle(self):
        array = self.settings.get ("list-string", "plugins-list")
        if "recent" in array:
            self.showRecentPlugin.set_active(True)
        else:
            self.showRecentPlugin.set_active(False)
        if "applications" in array:
            self.showApplicationsPlugin.set_active(True)
        else:
            self.showApplicationsPlugin.set_active(False)
        if "system_management" in array:
            self.showSystemPlugin.set_active(True)
        else:
            self.showSystemPlugin.set_active(False)
        if "places" in array:
            self.showPlacesPlugin.set_active(True)
        else:
            self.showPlacesPlugin.set_active(False)

    def setPluginsLayout (self, widget):
        visiblePlugins = []
        if self.showPlacesPlugin.get_active():
            visiblePlugins.append("places")
        if self.showSystemPlugin.get_active():
            visiblePlugins.append("system_management")
        if self.showApplicationsPlugin.get_active():
            if self.showPlacesPlugin.get_active() or self.showSystemPlugin.get_active():
                visiblePlugins.append("newpane")
            visiblePlugins.append("applications")
        if self.showRecentPlugin.get_active():
            if self.showApplicationsPlugin.get_active() or self.showPlacesPlugin.get_active() or self.showSystemPlugin.get_active():
                visiblePlugins.append("newpane")
            visiblePlugins.append("recent")
        self.settings.set ("list-string", "plugins-list", visiblePlugins)

    def setShowButtonIcon( self, value ):
        self.showButtonIcon.set_active(not value )

    def getShowButtonIcon( self ):
        return not self.showButtonIcon.get_active()

    def bindGSettingsValueToWidget( self, settings, setting_type, key, widget, changeEvent, setter, getter ):
        settings.notifyAdd( key, self.callSetter, args = [ setting_type, setter ] )
        setter( settings.get( setting_type, key ) )
        widget.connect( changeEvent, lambda *args: self.callGetter( settings, setting_type, key, getter ) )

    def callSetter( self, settings, key, args ):
        if args[0] == "bool":
            args[1]( settings.get_boolean(key) )
        elif args[0] == "string":
            args[1]( settings.get_string(key) )
        elif args[0] == "int":
            args[1]( settings.get_int(key) )

    def callGetter( self, settings, setting_type, key, getter ):
        if (setting_type == "int"):
            settings.set( setting_type, key, int(getter()))
        else:
            settings.set( setting_type, key, getter())

    def gdkRGBAToString( self, gdkRGBA ):
        return "#%.2X%.2X%.2X" % ( int(gdkRGBA.red * 256), int(gdkRGBA.green * 256), int(gdkRGBA.blue * 256) )

    def moveUp( self, upButton ):

        treeselection = self.customplacestree.get_selection()
        currentiter = (treeselection.get_selected())[1]

        if ( treeselection != None ):

            lagiter = self.customplacestreemodel.get_iter_first()
            nextiter = self.customplacestreemodel.get_iter_first()

            while ( (self.customplacestreemodel.get_path(nextiter) != self.customplacestreemodel.get_path(currentiter)) & (nextiter != None)):
                lagiter = nextiter
                nextiter = self.customplacestreemodel.iter_next(nextiter)

            if (nextiter != None):
                self.customplacestreemodel.swap(currentiter, lagiter)

        return

    def newPlace(self, newButton):
        self.builder.get_object("label2").set_text(_("Name:"))
        self.builder.get_object("label1").set_text(_("Path:"))
        newPlaceDialog = self.builder.get_object( "editPlaceDialog" )
        folderChooserDialog = self.builder.get_object( "fileChooserDialog" )
        newPlaceDialog.set_transient_for(self.mainWindow)
        newPlaceDialog.set_icon_name("start-here")
        newPlaceDialog.set_title(self.newPlaceDialogTitle)
        folderChooserDialog.set_title(self.folderChooserDialogTitle)
        newPlaceDialog.set_default_response(Gtk.ResponseType.OK)
        newPlaceName = self.builder.get_object( "nameEntryBox" )
        newPlacePath = self.builder.get_object( "pathEntryBox" )
        folderButton = self.builder.get_object( "folderButton" )
        def chooseFolder(folderButton):
            currentPath = newPlacePath.get_text()
            if (currentPath!=""):
                folderChooserDialog.select_filename(currentPath)
            response = folderChooserDialog.run()
            folderChooserDialog.hide()
            if (response == Gtk.ResponseType.OK):
                newPlacePath.set_text( folderChooserDialog.get_filenames()[0] )
        folderButton.connect("clicked", chooseFolder)

        response = newPlaceDialog.run()
        newPlaceDialog.hide()
        if (response == Gtk.ResponseType.OK ):
            name = newPlaceName.get_text()
            path = newPlacePath.get_text()
            if (name != "" and path !=""):
                self.customplacestreemodel.append( (name, path) )

    def editPlace(self, editButton):
        self.builder.get_object("label2").set_text(_("Name:"))
        self.builder.get_object("label1").set_text(_("Path:"))
        editPlaceDialog = self.builder.get_object( "editPlaceDialog" )
        folderChooserDialog = self.builder.get_object( "fileChooserDialog" )
        editPlaceDialog.set_transient_for(self.mainWindow)
        editPlaceDialog.set_icon_name("start-here")
        editPlaceDialog.set_title(self.editPlaceDialogTitle)
        folderChooserDialog.set_title(self.folderChooserDialogTitle)
        editPlaceDialog.set_default_response(Gtk.ResponseType.OK)
        editPlaceName = self.builder.get_object( "nameEntryBox" )
        editPlacePath = self.builder.get_object( "pathEntryBox" )
        folderButton = self.builder.get_object( "folderButton" )
        treeselection = self.customplacestree.get_selection()
        currentiter = (treeselection.get_selected())[1]

        if (currentiter != None):

            initName = self.customplacestreemodel.get_value(currentiter, 0)
            initPath = self.customplacestreemodel.get_value(currentiter, 1)

            editPlaceName.set_text(initName)
            editPlacePath.set_text(initPath)
            def chooseFolder(folderButton):
                currentPath = editPlacePath.get_text()
                if (currentPath!=""):
                    folderChooserDialog.select_filename(currentPath)
                response = folderChooserDialog.run()
                folderChooserDialog.hide()
                if (response == Gtk.ResponseType.OK):
                    editPlacePath.set_text( folderChooserDialog.get_filenames()[0] )
            folderButton.connect("clicked", chooseFolder)
            response = editPlaceDialog.run()
            editPlaceDialog.hide()
            if (response == Gtk.ResponseType.OK):
                name = editPlaceName.get_text()
                path = editPlacePath.get_text()
                if (name != "" and path != ""):
                    self.customplacestreemodel.set_value(currentiter, 0, name)
                    self.customplacestreemodel.set_value(currentiter, 1, path)

    def moveDown(self, downButton):

        treeselection = self.customplacestree.get_selection()
        currentiter = (treeselection.get_selected())[1]

        nextiter = self.customplacestreemodel.iter_next(currentiter)

        if (nextiter != None):
            self.customplacestreemodel.swap(currentiter, nextiter)

        return


    def removePlace(self, removeButton):

        treeselection = self.customplacestree.get_selection()
        currentiter = (treeselection.get_selected())[1]

        if (currentiter != None):
            self.customplacestreemodel.remove(currentiter)

        return

    def togglePlacesHeightEnabled(self, toggle):
        if (toggle.get_active() == True):
            self.placesHeightButton.set_sensitive(True)
        else:
            self.placesHeightButton.set_sensitive(False)

    def toggleSystemHeightEnabled(self, toggle):
        if (toggle.get_active() == True):
            self.systemHeightButton.set_sensitive(True)
        else:
            self.systemHeightButton.set_sensitive(False)

    def updatePlacesGSettings(self, treemodel, path, iter = None, new_order = None):

        # Do only if not partway though an append operation; Append = insert+change+change and each creates a signal
        if ((iter == None) or (self.customplacestreemodel.get_value(iter, 1) != None)):
            treeiter = self.customplacestreemodel.get_iter_first()
            customplacenames = [ ]
            customplacepaths = [ ]
            while( treeiter != None ):
                customplacenames = customplacenames + [ self.customplacestreemodel.get_value(treeiter, 0 ) ]
                customplacepaths = customplacepaths + [ self.customplacestreemodel.get_value(treeiter, 1 ) ]
                treeiter = self.customplacestreemodel.iter_next(treeiter)
            self.settingsPlaces.set( "list-string", "custom-paths", customplacepaths)
            self.settingsPlaces.set( "list-string", "custom-names", customplacenames)


window = mateMenuConfig()
Gtk.main()
