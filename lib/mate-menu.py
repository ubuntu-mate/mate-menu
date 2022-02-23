#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Clement Lefebvre <root@linuxmint.com>
# Copyright (C) 2015-2017 Martin Wimpress <code@ubuntu-mate.org>
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

__VERSION__='22.04.1'

import gc
import gi
import gettext
import importlib
import os
import subprocess
import sys
import traceback
import signal
import setproctitle

gi.require_version("Gtk", "3.0")
gi.require_version('MatePanelApplet', '4.0')

from gi.repository import Gtk, GdkPixbuf, Gdk, GObject
from gi.repository import MatePanelApplet
from gi.repository import Gio

try:
    import xdg.Config
    import mate_menu.keybinding as keybinding
    import mate_menu.pointerMonitor as pointerMonitor
except Exception as e:
    print(e)
    sys.exit(1)

signal.signal(signal.SIGINT, signal.SIG_DFL)

# Rename the process
setproctitle.setproctitle('mate-menu')

# i18n
gettext.install("mate-menu", "/usr/share/locale")

NAME = _("Menu")

xdg.Config.setWindowManager('MATE')

from mate_menu.execute import *

class MainWindow( object ):
    """This is the main class for the application"""

    def __init__(self, toggleButton, settings):

        self.settings = settings
        self.data_path = os.path.join( '/', 'usr', 'share', 'mate-menu' )

        self.toggle = toggleButton
        # Load UI file and extract widgets
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join( self.data_path, "mate-menu.glade" ))
        self.window     = builder.get_object( "mainWindow" )
        self.paneholder = builder.get_object( "paneholder" )
        self.border     = builder.get_object( "border" )

        builder.connect_signals(self)

        self.panesToColor = [ ]
        self.headingsToColor = [ ]

        self.window.realize()
        self.window.get_window().set_decorations(Gdk.WMDecoration.BORDER)
        self.window.set_title('Advanced MATE Menu')
        self.window.set_app_paintable(True)

        self.window.connect("draw", self.onWindowDraw)
        self.window.connect("key-press-event", self.onWindowKeyPress)
        self.window.connect("focus-in-event", self.onWindowFocusIn)
        self.loseFocusId = self.window.connect("focus-out-event", self.onWindowFocusOut)
        self.loseFocusBlocked = False

        self.window.stick()

        plugindir = os.path.join( os.path.expanduser( "~" ), ".config/mate-menu/plugins" )
        sys.path.append( plugindir )

        self.panelSettings = Gio.Settings.new("org.mate.panel")
        self.panelSettings.connect( "changed::tooltips-enabled", self.toggleTooltipsEnabled )

        self.settings.connect( "changed::plugins-list", self.RegenPlugins )
        self.settings.connect( "changed::start-with-favorites", self.toggleStartWithFavorites )
        self.settings.connect( "changed::tooltips-enabled", self.toggleTooltipsEnabled )
        self.settings.connect( "changed::border-width", self.toggleBorderWidth )

        self.getSetGSettingEntries()

        self.tooltipsWidgets = []
        if self.globalEnableTooltips and self.enableTooltips:
            self.tooltipsEnable()
        else:
            self.tooltipsEnable( False )

        self.PopulatePlugins();
        self.firstTime = True;

    def on_window1_destroy (self, widget, data=None):
        Gtk.main_quit()
        sys.exit(0)

    def wakePlugins( self ):
        # Call each plugin and let them know we're showing up
        for plugin in self.plugins.values():
            if hasattr( plugin, "wake" ):
                plugin.wake()

    def toggleTooltipsEnabled( self, settings, key, args = None):
        if key == "tooltips-enabled":
            self.globalEnableTooltips = settings.get_boolean(key)
        else:
            self.enableTooltips = settings.get_boolean(key)

        if self.globalEnableTooltips and self.enableTooltips:
            self.tooltipsEnable()
        else:
            self.tooltipsEnable( False )

    def toggleStartWithFavorites( self, settings, key, args = None ):
        self.startWithFavorites = settings.get_boolean(key)

    def toggleBorderWidth( self, settings, key,  args = None ):
        self.borderwidth = settings.get_int(key)
        self.SetupMateMenuBorder()

    def getSetGSettingEntries( self ):
        self.pluginlist           = self.settings.get_strv( "plugins-list" )
        self.borderwidth          = self.settings.get_int( "border-width" )
        self.offset               = self.settings.get_int( "offset" )
        self.enableTooltips       = self.settings.get_boolean( "tooltips-enabled" )
        self.startWithFavorites   = self.settings.get_boolean( "start-with-favorites" )

        self.globalEnableTooltips = self.panelSettings.get_boolean( "tooltips-enabled" )

    def PopulatePlugins( self ):
        self.panesToColor = [ ]
        self.headingsToColor = [ ]
        PluginPane = Gtk.EventBox()
        PluginPane.show()
        PaneLadder = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
        PluginPane.add( PaneLadder )
        ImageBox = Gtk.EventBox()
        ImageBox.show()
        self.panesToColor.extend( [ PluginPane, ImageBox ] )

        self.plugins = {}

        for plugin in self.pluginlist:
            if plugin in self.plugins:
                print(u"Duplicate plugin in list: ", plugin)
                continue

            if plugin != "newpane":
                try:
                    plugin_module = 'mate_menu.plugins.{plugin}'.format(plugin=plugin)
                    MyPluginClass = importlib.import_module(plugin_module)
                    # If no parameter passed to plugin it is autonomous
                    if MyPluginClass.pluginclass.__init__.__code__.co_argcount == 1:
                        MyPlugin = MyPluginClass.pluginclass()
                    else:
                        # pass mateMenu and togglebutton instance so that the plugin can use it
                        MyPlugin = MyPluginClass.pluginclass(self, self.toggle)

                    #if hasattr( MyPlugin, "hideseparator" ) and not MyPlugin.hideseparator:
                    #    Image1 = Gtk.Image()
                    #    Image1.set_from_pixbuf( seperatorImage )
                    #    if not ImageBox.get_child():
                    #        ImageBox.add( Image1 )
                    #        Image1.show()

                    #print(u"Loading plugin '" + plugin + "' : sucessful")
                except Exception as e:
                    MyPlugin = Gtk.EventBox() #Fake class for MyPlugin
                    MyPlugin.heading = _("Couldn't load plugin:") + " " + plugin
                    MyPlugin.content_holder = Gtk.EventBox()

                    # create traceback
                    info = sys.exc_info()

                    errorLabel = Gtk.Label( "\n".join(traceback.format_exception( info[0], info[1], info[2] )).replace("\\n", "\n") )
                    errorLabel.set_selectable( True )
                    errorLabel.set_line_wrap( True )
                    errorLabel.set_alignment( 0.0, 0.0 )
                    errorLabel.set_padding( 5, 5 )
                    errorLabel.show()

                    MyPlugin.content_holder.add( errorLabel )
                    MyPlugin.add( MyPlugin.content_holder )
                    MyPlugin.width = 270
                    print(u"Unable to load " + plugin + " plugin :-(")


                self.panesToColor.append( MyPlugin.content_holder )
                MyPlugin.content_holder.show()

                VBox1 = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
                if MyPlugin.heading != "":
                    Label1 = Gtk.Label(label= MyPlugin.heading )
                    Label1.set_margin_start(10)
                    self.headingsToColor.append( Label1 )
                    Label1.show()

                    if not hasattr( MyPlugin, 'sticky' ) or MyPlugin.sticky == True:
                        heading = Gtk.EventBox()
                        heading.set_visible_window( False )
                        heading.set_size_request( MyPlugin.width, 30 )
                    else:
                        heading = Gtk.Box( orientation=Gtk.Orientation.HORIZONTAL )
                        Label1.set_margin_top(10)
                        Label1.set_margin_bottom(5)
                        heading.set_size_request( MyPlugin.width, -1 )

                    heading.add(Label1)
                    heading.show()
                    VBox1.pack_start( heading, False, False, 0 )
                VBox1.show()
                # Add plugin to Plugin Box under heading button
                MyPlugin.content_holder.get_parent().remove(MyPlugin.content_holder)
                VBox1.add( MyPlugin.content_holder )

                # Add plugin to main window
                PaneLadder.pack_start( VBox1 , True, True, 0)
                PaneLadder.show()

                try:
                    MyPlugin.get_window().destroy()
                except AttributeError:
                    pass

                try:
                    if hasattr( MyPlugin, 'do_plugin' ):
                        MyPlugin.do_plugin()
                    if hasattr( MyPlugin, 'height' ):
                        MyPlugin.content_holder.set_size_request( -1, MyPlugin.height )
                    if hasattr( MyPlugin, 'itemstocolor' ):
                        self.panesToColor.extend( MyPlugin.itemstocolor )
                    if hasattr( MyPlugin, 'headingstocolor' ):
                        self.headingsToColor.extend( MyPlugin.headingstocolor )
                except:
                    # create traceback
                    info = sys.exc_info()

                    error = _("Couldn't initialize plugin") + " " + plugin + " : " + "\n".join(traceback.format_exception( info[0], info[1], info[2] )).replace("\\n", "\n")
                    msgDlg = Gtk.MessageDialog( None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, error )
                    msgDlg.run();
                    msgDlg.destroy();

                self.plugins[plugin] = MyPlugin

            else:
                self.paneholder.pack_start( ImageBox, False, False, 0 )
                self.paneholder.pack_start( PluginPane, False, False, 0 )
                PluginPane = Gtk.EventBox()
                PaneLadder = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
                PluginPane.add( PaneLadder )
                ImageBox = Gtk.EventBox()
                self.panesToColor.extend( [ PluginPane, ImageBox ] )
                ImageBox.show()
                PluginPane.show_all()

                if self.plugins and hasattr( MyPlugin, 'hideseparator' ) and not MyPlugin.hideseparator:
                    Image1 = Gtk.Image()
                    Image1.set_from_pixbuf( seperatorImage )
                    Image1.set_margin_start(6)
                    Image1.set_margin_end(6)
                    Image1.show()

                    ImageBox.add(Image1)
                    ImageBox.show_all()


        self.paneholder.pack_start( ImageBox, False, False, 0 )
        self.paneholder.pack_start( PluginPane, False, False, 0 )
        self.tooltipsEnable( False )

    # A little bit hacky but works.
    def getDefaultColors( self ):
        widget = Gtk.EventBox()
        widget.show()

        context = widget.get_style_context()
        context.set_state( Gtk.StateFlags.NORMAL )
        context.add_class( Gtk.STYLE_CLASS_DEFAULT )
        context.add_class( Gtk.STYLE_CLASS_BACKGROUND )

        fgColor = context.get_color( context.get_state() )
        bgColor = context.get_background_color( context.get_state() )
        borderColor = context.get_border_color( context.get_state() )

        return { "fg": fgColor, "bg": bgColor, "border": borderColor }

    def loadTheme( self ):
        colors = self.getDefaultColors()
        self.SetupMateMenuBorder()
        self.SetPaneColors(self.panesToColor, colors["bg"])
        self.SetHeadingStyle( self.headingsToColor )

    def SetupMateMenuBorder(self):
        style = self.window.get_style_context()
        styleProvider = Gtk.CssProvider()
        styleProvider.load_from_data(b".background { border-width: %dpt; }" % self.borderwidth)
        style.add_provider(styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.border.set_margin_top(self.borderwidth)
        self.border.set_margin_bottom(self.borderwidth)
        self.border.set_margin_start(self.borderwidth)
        self.border.set_margin_end(self.borderwidth)

    def SetPaneColors( self, items, color = None ):
        for item in items:
            context = item.get_style_context()
            if color is not None:
                item.override_background_color( context.get_state(), color )

    def SetHeadingStyle( self, items ):
        for item in items:
            item.set_use_markup(True)
            text = item.get_text()
            markup = '<span size="12000" weight="bold">%s</span>' % (text)
            item.set_markup( markup )

    def tooltipsEnable( self, enable = True ):
        for widget in self.tooltipsWidgets:
            widget.set_has_tooltip( enable )

    def setTooltip( self, widget, tip ):
        self.tooltipsWidgets.append( widget )
        widget.set_tooltip_text( tip )

    def RegenPlugins( self, *args, **kargs ):
        #print("Reloading Plugins...")
        for item in self.paneholder:
            item.destroy()

        for plugin in self.plugins.values():
            if hasattr( plugin, "destroy" ):
                plugin.destroy()

        try:
            del plugin
        except:
            pass

        try:
            del self.plugins
        except:
            pass

        gc.collect()

        self.getSetGSettingEntries()
        self.PopulatePlugins()
        self.loadTheme()

        #print(NAME + " reloaded")

    def onWindowDraw(self, widget, cr):
        style = widget.get_style_context()
        req = widget.get_preferred_size()[0]
        Gtk.render_background(style, cr, 0, 0, req.width, req.height)
        Gtk.render_frame(style, cr, 0, 0, req.width, req.height)
        return False

    def onWindowKeyPress( self, widget, event ):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    def show( self ):
        self.window.present()

        # Hack for opacity not showing on first composited draw
        if self.firstTime:
            self.firstTime = False
            self.window.set_opacity(1.0)

        self.window.get_window().focus( Gdk.CURRENT_TIME )

        for plugin in self.plugins.values():
            if hasattr( plugin, "onShowMenu" ):
                plugin.onShowMenu()

        if ( "applications" in self.plugins ) and ( hasattr( self.plugins["applications"], "focusSearchEntry" ) ):
            if (self.startWithFavorites):
                self.plugins["applications"].changeTab(0)
            self.plugins["applications"].focusSearchEntry()

    def hide( self ):
        for plugin in self.plugins.values():
            if hasattr( plugin, "onHideMenu" ):
                plugin.onHideMenu()

        self.window.hide()

    def onWindowFocusIn(self, *args):
        if self.loseFocusBlocked:
            self.window.handler_unblock( self.loseFocusId )
            self.loseFocusBlocked = False

        return False

    def onWindowFocusOut(self, *args):
        if self.window.get_visible():
            self.hide()
        return False

    def stopHiding( self ):
        if not self.loseFocusBlocked:
            self.window.handler_block( self.loseFocusId )
            self.loseFocusBlocked = True

class MenuWin( object ):
    def __init__( self, applet, iid ):
        self.data_path = os.path.join('/','usr','share','mate-menu')
        self.applet = applet
        self.settings = Gio.Settings.new("org.mate.mate-menu")
        self.icon = "start-here"

        self.loadSettings()

        self.createPanelButton()

        self.mate_settings = Gio.Settings.new("org.mate.interface")
        self.mate_settings.connect( "changed::gtk-theme", self.changeTheme )
        self.mate_settings.connect( "changed::icon-theme", self.changeTheme )

        self.settings.connect( "changed::applet-text", self.reloadSettings )
        self.settings.connect( "changed::hot-key", self.reloadSettings )
        self.settings.connect( "changed::hide-applet-icon", self.reloadSettings )

        self.applet.set_flags( MatePanelApplet.AppletFlags.EXPAND_MINOR )
        self.applet.connect( "button-press-event", self.showMenu )
        self.applet.connect( "change-orient", self.changeOrientation )
        self.applet.connect( "change-size", self.reloadSettings )

        self.mainwin = MainWindow(self.button_box, self.settings)
        self.mainwin.window.connect( "map-event", self.onWindowMap )
        self.mainwin.window.connect( "unmap-event", self.onWindowUnmap )
        self.mainwin.window.connect( "size-allocate", lambda *args: self.positionMenu() )

        self.mainwin.window.set_name("mate-menu") # Name used in Gtk RC files
        self.applyTheme()
        self.mainwin.loadTheme()

        Gtk.Window.set_default_icon_name( self.icon )

        try:
            self.keybinder = keybinding.GlobalKeyBinding()
            if self.hotkeyText != "":
                self.keybinder.grab( self.hotkeyText )
            self.keybinder.connect("activate", self.onBindingPress)
            self.keybinder.start()
            self.settings.connect( "changed::hot-key", self.hotkeyChanged )
            print("Binding to Hot Key: " + self.hotkeyText)
        except Exception as cause:
            self.keybinder = None
            print("** WARNING ** - Keybinder Error")
            print("Error Report :\n", str(cause))

        self.applet.set_can_focus(False)

        try:
            self.pointerMonitor = pointerMonitor.PointerMonitor()
            self.pointerMonitor.connect("activate", self.onPointerOutside)
            self.mainwin.window.connect( "realize", self.onRealize )
        except Exception as cause:
            print("** WARNING ** - Pointer Monitor Error")
            print("Error Report :\n", str(cause))

    def onWindowMap( self, *args ):
        self.applet.get_style_context().set_state( Gtk.StateFlags.SELECTED )
        if self.keybinder is not None:
            self.keybinder.set_focus_window(self.mainwin.window.get_window())
        return False

    def onWindowUnmap( self, *args ):
        self.applet.get_style_context().set_state( Gtk.StateFlags.NORMAL )
        if self.keybinder is not None:
            self.keybinder.set_focus_window()
        return False

    def onRealize( self, *args):
        self.pointerMonitor.addWindowToMonitor( self.mainwin.window.get_window() )
        self.pointerMonitor.addWindowToMonitor( self.applet.get_window() )
        self.pointerMonitor.start()
        return False

    def onPointerOutside(self, *args):
        self.mainwin.hide()
        return True

    def onBindingPress(self, binder):
        self.toggleMenu()
        return True

    def do_load_icon(self, icon_name):
        icon_theme = Gtk.IconTheme.get_default()
        icon_size = self.applet.get_size() - 8
        scale_factor = self.button_icon.get_scale_factor()
        surface = icon_theme.load_surface(icon_name, icon_size, scale_factor, None, Gtk.IconLookupFlags.FORCE_SIZE)
        if surface is not None:
            self.button_icon.set_from_surface(surface)
        else:
            self.button_icon.set_from_icon_name(icon_name, Gtk.IconSize.MENU)

    def createPanelButton( self ):
        self.button_icon = Gtk.Image()
        self.do_load_icon(self.icon)
        self.systemlabel = Gtk.Label(label= "%s " % self.buttonText )
        try:
            process = subprocess.Popen(['lsb_release', '-d'], stdout=subprocess.PIPE, text=True)
            out, err = process.communicate()
            tooltip = str(out).replace('Description:', '').strip()
            self.systemlabel.set_tooltip_text(tooltip)
            self.button_icon.set_tooltip_text(tooltip)
        except OSError:
            pass

        if self.applet.get_orient() == MatePanelApplet.AppletOrient.UP or self.applet.get_orient() == MatePanelApplet.AppletOrient.DOWN:
            self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.button_box.pack_start(self.button_icon, False, False, 0)
            self.button_box.pack_start(self.systemlabel, False, False, 0)
            self.button_icon.set_margin_start(5)
            self.button_icon.set_margin_end(5)
        # if we have a vertical panel
        elif self.applet.get_orient() == MatePanelApplet.AppletOrient.LEFT:
            self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.systemlabel.set_angle(270)
            self.button_box.pack_start(self.button_icon , False, False, 0)
            self.button_box.pack_start(self.systemlabel , False, False, 0)
            self.button_icon.set_padding(0, 5)
        elif self.applet.get_orient() == MatePanelApplet.AppletOrient.RIGHT:
            self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.systemlabel.set_angle(90)
            self.button_box.pack_start(self.button_icon , False, False, 0)
            self.button_box.pack_start(self.systemlabel , False, False, 0)
            self.button_icon.set_margin_top(5)
            self.button_icon.set_margin_bottom(5)

        self.button_box.set_homogeneous( False )
        self.button_box.show_all()

        self.applet.add( self.button_box )
        self.applet.set_background_widget( self.applet )


    def loadSettings( self, *args, **kargs ):
        self.hideIcon   =  self.settings.get_boolean( "hide-applet-icon" )
        self.buttonText =  self.settings.get_string( "applet-text" )
        self.hotkeyText =  self.settings.get_string( "hot-key" )

    def changeTheme(self, *args):
        self.reloadSettings()
        self.applyTheme()
        self.mainwin.loadTheme()

    def applyTheme(self):
        style_settings = Gtk.Settings.get_default()

        desktop_theme = self.mate_settings.get_string('gtk-theme')
        style_settings.set_property("gtk-theme-name", desktop_theme)

        icon_theme = self.mate_settings.get_string('icon-theme')
        style_settings.set_property("gtk-icon-theme-name", icon_theme)

    def changeOrientation( self, *args, **kargs ):

        if self.applet.get_orient() == MatePanelApplet.AppletOrient.UP or self.applet.get_orient() == MatePanelApplet.AppletOrient.DOWN:
            tmpbox = Gtk.Box( orientation=Gtk.Orientation.HORIZONTAL )
            self.systemlabel.set_angle( 0 )
            self.button_box.reorder_child( self.button_icon, 0 )
            self.button_icon.set_padding( 5, 0 )
        elif self.applet.get_orient() == MatePanelApplet.AppletOrient.LEFT:
            tmpbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
            self.systemlabel.set_angle( 270 )
            self.button_box.reorder_child( self.button_icon, 0 )
            self.button_icon.set_padding( 0, 5 )
        elif self.applet.get_orient() == MatePanelApplet.AppletOrient.RIGHT:
            tmpbox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
            self.systemlabel.set_angle( 90 )
            self.button_box.reorder_child( self.button_icon, 1 )
            self.button_icon.set_padding( 0, 5 )

        tmpbox.set_homogeneous( False )

        # reparent all the hboxes to the new tmpbox
        for i in self.button_box:
            i.reparent( tmpbox )

        self.button_box.destroy()

        self.button_box = tmpbox
        self.button_box.show()

        # this call makes sure width stays intact
        self.updateButton()
        self.applet.add( self.button_box )


    def updateButton( self ):
        self.systemlabel.set_text( self.buttonText )
        self.button_icon.clear()
        self.do_load_icon(self.icon)

    def hotkeyChanged (self, schema, key):
        self.hotkeyText =  self.settings.get_string( "hot-key" )
        self.keybinder.rebind(self.hotkeyText)

    def reloadSettings( self, *args ):
        self.loadSettings()
        self.updateButton()

    def showAboutDialog( self, action, userdata = None ):
        about = Gtk.AboutDialog()
        about.set_program_name("Advanced MATE Menu")
        about.set_version(__VERSION__)
        about.set_comments( _("An Advanced Menu for the MATE Desktop") )
        icon_theme = Gtk.IconTheme.get_default ()
        pixbuf = icon_theme.load_icon ( self.icon, 256, 0 )
        if pixbuf:
            about.set_logo ( pixbuf )
        else:
            about.set_logo_icon_name ( self.icon )
        about.connect( "response", lambda dialog, r: dialog.destroy() )
        about.show()

    def showPreferences( self, action, userdata = None ):
        Execute( os.path.join( "/", "usr", "lib", "mate-menu", "mate-menu-config.py" ) )

    def showMenuEditor( self, action, userdata = None ):
        def pathExists(filename):
            if os.path.exists(filename):
                return True
            for path in os.environ["PATH"].split(os.pathsep):
                if os.path.exists(os.path.join(path, filename)):
                    return True

        if pathExists("menulibre"):
            Execute("menulibre")
        elif pathExists("mozo"):
            Execute("mozo")

    def showMenu( self, widget=None, event=None ):
        if event == None or event.button == 1:
            self.toggleMenu()
        # show right click menu
        elif event.button == 3:
            self.create_menu()
        # allow middle click and drag
        elif event.button == 2:
            self.mainwin.hide()

    def toggleMenu( self ):
        if self.applet.get_style_context().get_state() & Gtk.StateFlags.SELECTED:
            self.mainwin.hide()
        else:
            self.positionMenu()
            self.mainwin.show()
            self.wakePlugins()

    def wakePlugins( self ):
        self.mainwin.wakePlugins()

    def positionMenu( self ):
        # Get our own dimensions & position
        ourWidth  = self.mainwin.window.get_size()[0]
        ourHeight = self.mainwin.window.get_size()[1] + self.mainwin.offset

        # Get the dimensions/position of the widgetToAlignWith
        try:
            entryX = self.applet.get_window().get_origin().x
            entryY = self.applet.get_window().get_origin().y
        except AttributeError:
            # In older Gtk3 get_origin returns an unnamed tuple so the code above fails
            entryX = self.applet.get_window().get_origin()[1]
            entryY = self.applet.get_window().get_origin()[2]

        entryWidth, entryHeight =  self.applet.get_allocation().width, self.applet.get_allocation().height
        entryHeight = entryHeight + self.mainwin.offset

        # Get the monitor dimensions
        display = self.applet.get_display()
        if (Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION) >= (3, 22):
            monitor = display.get_monitor_at_window(self.applet.get_window())
            monitorGeometry = monitor.get_geometry()
        else:
            screen = display.get_default_screen()
            monitor = screen.get_monitor_at_window(self.applet.get_window())
            monitorGeometry = screen.get_monitor_geometry(monitor)

        applet_orient = self.applet.get_orient()
        if applet_orient == MatePanelApplet.AppletOrient.UP:
            newX = entryX
            newY = entryY - ourHeight
        elif applet_orient == MatePanelApplet.AppletOrient.DOWN:
            newX = entryX
            newY = entryY + entryHeight
        elif applet_orient == MatePanelApplet.AppletOrient.RIGHT:
            newX = entryX + entryWidth
            newY = entryY
        elif applet_orient == MatePanelApplet.AppletOrient.LEFT:
            newX = entryX - ourWidth
            newY = entryY

        # Adjust for offset if we reach the end of the screen
        # Bind to the right side
        if newX + ourWidth > (monitorGeometry.x + monitorGeometry.width):
            newX = (monitorGeometry.x + monitorGeometry.width) - ourWidth
            if applet_orient == MatePanelApplet.AppletOrient.LEFT:
                newX -= entryWidth

        # Bind to the left side
        if newX < monitorGeometry.x:
            newX = monitorGeometry.x
            if applet_orient == MatePanelApplet.AppletOrient.RIGHT:
                newX -= entryWidth;

        # Bind to the bottom
        if newY + ourHeight > (monitorGeometry.y + monitorGeometry.height):
            newY = (monitorGeometry.y + monitorGeometry.height) - ourHeight
            if applet_orient == MatePanelApplet.AppletOrient.UP:
                newY -= entryHeight

        # Bind to the top
        if newY < monitorGeometry.y:
            newY = monitorGeometry.y
            if applet_orient == MatePanelApplet.AppletOrient.DOWN:
                newY -= entryHeight

        # Move window
        self.mainwin.window.move( newX, newY )

    # this callback is to create a context menu
    def create_menu(self):
        action_group = Gtk.ActionGroup(name="context-menu")
        action = Gtk.Action(name="MateMenuPrefs", label=_("Preferences"), tooltip=None, icon_name="preferences-system")
        action.connect("activate", self.showPreferences)
        action_group.add_action(action)
        action = Gtk.Action(name="MateMenuEdit", label=_("Edit menu"), tooltip=None, stock_id=Gtk.STOCK_EDIT)
        action.connect("activate", self.showMenuEditor)
        action_group.add_action(action)
        action = Gtk.Action(name="MateMenuReload", label=_("Reload plugins"), tooltip=None, icon_name="view-refresh")
        action.connect("activate", self.mainwin.RegenPlugins)
        action_group.add_action(action)
        action = Gtk.Action(name="MateMenuAbout", label=_("About"), tooltip=None, icon_name="help-about")
        action.connect("activate", self.showAboutDialog)
        action_group.add_action(action)
        action_group.set_translation_domain ("mate-menu")

        xml = os.path.join( self.data_path, "popup.xml" )
        self.applet.setup_menu_from_file(xml, action_group)

def applet_factory( applet, iid, data ):
    MenuWin( applet, iid )
    applet.show()
    return True

def quit_all(widget):
    Gtk.main_quit()
    sys.exit(0)

MatePanelApplet.Applet.factory_main("MateMenuAppletFactory", True,
                                    MatePanelApplet.Applet.__gtype__,
                                    applet_factory, None)
