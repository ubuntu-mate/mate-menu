# -*- coding: utf-8 -*-

# Copyright (C) 2026
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

"""
Icon helpers for mate-menu.
"""

# Imports are deferred to call time so this module stays lightweight,
# and so icon loading only happens once the default screen exists.

def resolvedIconName(name):
    """
    Return the first icon that's actually present in the theme, walking
    the automatic GIcon fallback chain (start-here-mate -> start-here ->
    start). The input name is returned if nothing matches.
    """
    from gi.repository import Gtk, Gio
    theme = Gtk.IconTheme.get_default()
    for candidate in Gio.ThemedIcon.new_with_default_fallbacks(name).get_names():
        if theme.has_icon(candidate):
            return candidate
    return name
