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
Configuration module for mate-menu.

Determines installation prefix at runtime to support non-/usr installations.
"""

import os
import sys

try:
    # Prefix recorded at install time by setup.py (mate_menu/_prefix.py).
    # Takes precedence, since it reflects where mate_menu was actually
    # installed rather than where the Python interpreter lives.
    from mate_menu._prefix import PREFIX as INSTALLED_PREFIX
except ImportError:
    INSTALLED_PREFIX = None

# Installation prefix - the one recorded at install time, or an explicit
# runtime override via the PREFIX environment variable, else fall back to
# sys.prefix (e.g. when running from the source tree without installing).
PREFIX = os.environ.get('PREFIX', INSTALLED_PREFIX or sys.prefix)

# Derived paths
LOCALE_DIR = os.path.join(PREFIX, 'share', 'locale')
DATA_DIR = os.path.join(PREFIX, 'share', 'mate-menu')
LIB_DIR = os.path.join(PREFIX, 'lib', 'mate-menu')
