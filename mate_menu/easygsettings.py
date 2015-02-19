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

from gi.repository import Gio

class EasyGSettings:

    def __init__( self, schema = None ):
        self.schema = schema
        self.settings = Gio.Settings.new(self.schema)
        self.handlerIds = [ ]

    def get( self, type, key ):

        if type == "bool":
            return self.settings.get_boolean( key )
        if type == "string":
            return self.settings.get_string( key )
        if type == "int":
            return self.settings.get_int( key )
        if type == "color":
            color = self.settings.get_string( key )
            if not self.evalColor( color ):
                self.settings.set_string(key, "#ffffff")
                return "#ffffff"
            return color

        t = type.split("-")
        if len(t) == 2 and t[0] == "list":
            return self.settings.get_strv( key )

        return self.settings.get( key )

    def set( self, type, key, value ):

        if type == "bool":
            return self.settings.set_boolean( key, value )

        if type == "string":
            return self.settings.set_string( key, value )

        if type == "int":
            return self.settings.set_int( key, value )

        if type == "color":
            if self.evalColor( value ):
                return self.settings.set_string( key, value )
            else:
                return self.settings.set_string( key, "#ffffff" )

        t = type.split("-")
        if len(t) == 2 and t[0] == "list":
            return self.settings.set_strv( key, value )

        return self.settings.set( key, value )

    def notifyAdd( self, key, callback, args = None ):
        handlerId = self.settings.connect("changed::"+key, callback, args)
        self.handlerIds.append( handlerId )
        return handlerId

    def notifyRemove( self, handlerId ):
        return self.settings.disconnect(handlerId)

    def notifyRemoveAll( self ):
        for handlerId in self.handlerIds:
            self.settings.disconnect( handlerId )

    def evalColor(self, colorToTest ):
        if colorToTest[0] != '#' or len( colorToTest ) != 7:
            return False
        for i in colorToTest[1:]:
            if i not in ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return False
        return True
        
    def bindGSettingsEntryToVar( self, type, key, obj, varName ):
        return self.notifyAdd( key, self.setVar, ( type, obj, varName ) )
        
    def setVar( self, settings, key, args ):
        type, obj, varName = args

        if type == "string":
            setattr( obj, varName, settings.get_string(key) )
        elif type == "int":
            setattr( obj, varName, settings.get_int(key) )
        elif type == "float":
            setattr( obj, varName, settings.get_float(key) )
        elif type == "bool":
            setattr( obj, varName, settings.get_boolean(key) )
        else:
            setattr( obj, varName, settings.get_value(key) )


