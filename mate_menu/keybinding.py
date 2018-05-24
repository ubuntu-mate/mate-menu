# -*- coding: utf-8 -*-

# Copyright (C) 2013  Ozcan Esen <ozcanesen@gmail.com>
# Copyright (C) 2008  Luca Bruno <lethalman88@gmail.com>
#
# This a slightly modified version of the globalkeybinding.py file which is part of FreeSpeak.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import gi
import threading
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GdkX11, GObject, GLib
from Xlib.display import Display
from Xlib import X, error

SPECIAL_MODS = (["Super_L",    "<Super>"],
                ["Super_R",    "<Super>"],
                ["Alt_L",      "<Alt>"],
                ["Alt_R",      "<Alt>"],
                ["Control_L",  "<Primary>"],
                ["Control_R",  "<Primary>"],
                ["Shift_L",    "<Shift>"],
                ["Shift_R",    "<Shift>"])

class GlobalKeyBinding(GObject.GObject, threading.Thread):
    __gsignals__ = {
        'activate': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self):
        GObject.GObject.__init__ (self)
        threading.Thread.__init__ (self)
        self.setDaemon (True)

        self.keymap = Gdk.Keymap().get_default()
        self.display = Display()
        self.screen = self.display.screen()
        self.window = self.screen.root
        self.ignored_masks = self.get_mask_combinations(X.LockMask | X.Mod2Mask | X.Mod5Mask)
        self.map_modifiers()
        self.raw_keyval = None
        self.keytext = ""

    def map_modifiers(self):
        gdk_modifiers =(Gdk.ModifierType.CONTROL_MASK, Gdk.ModifierType.SHIFT_MASK, Gdk.ModifierType.MOD1_MASK,
                         Gdk.ModifierType.MOD2_MASK, Gdk.ModifierType.MOD3_MASK, Gdk.ModifierType.MOD4_MASK, Gdk.ModifierType.MOD5_MASK,
                         Gdk.ModifierType.SUPER_MASK, Gdk.ModifierType.HYPER_MASK)
        self.known_modifiers_mask = 0
        for modifier in gdk_modifiers:
            if "Mod" not in Gtk.accelerator_name(0, modifier) or "Mod4" in Gtk.accelerator_name(0, modifier):
                self.known_modifiers_mask |= modifier

    def grab(self, key):
        accelerator = key
        accelerator = accelerator.replace("<Super>", "<Mod4>")
        keyval, modifiers = Gtk.accelerator_parse(accelerator)
        if not accelerator or (not keyval and not modifiers):
            self.keycode = None
            self.modifiers = None
            return False

        self.keytext = key
        try:
            self.keycode = self.keymap.get_entries_for_keyval(keyval).keys[0].keycode
        except AttributeError:
            # In older Gtk3 the get_entries_for_keyval() returns an unnamed tuple...
            self.keycode = self.keymap.get_entries_for_keyval(keyval)[1][0].keycode
        self.modifiers = int(modifiers)

        # Request to receive key press/release reports from other windows that may not be using modifiers
        catch = error.CatchError(error.BadWindow)
        if self.modifiers:
            self.window.change_attributes(onerror=catch, event_mask = X.KeyPressMask | X.KeyReleaseMask)
        else:
            self.window.change_attributes(onerror=catch, event_mask = X.NoEventMask)
        if catch.get_error():
            return False

        catch = error.CatchError(error.BadAccess)
        for ignored_mask in self.ignored_masks:
            mod = modifiers | ignored_mask
            result = self.window.grab_key(self.keycode, mod, True, X.GrabModeAsync, X.GrabModeAsync, onerror=catch)
        self.display.flush()
        if catch.get_error():
            return False

        catch = error.CatchError(error.BadCursor)
        if not self.modifiers:
           # We grab Super+click so that we can forward it to the window manager and allow Super+click bindings (window move, resize, etc.)
           self.window.grab_button(X.AnyButton, X.Mod4Mask, True, X.ButtonPressMask, X.GrabModeSync, X.GrabModeAsync, X.NONE, X.NONE)
        self.display.flush()
        if catch.get_error():
            return False

        return True

    def ungrab(self):
        if self.keycode:
            self.window.ungrab_key(self.keycode, X.AnyModifier, self.window)

    def rebind(self, key):
        self.ungrab()
        if key != "":
            self.grab(key)
        else:
            self.keytext = ""

    def set_focus_window(self, window = None):
        self.ungrab()
        if window is None:
            self.window = self.screen.root
        else:
            self.window = self.display.create_resource_object("window", window.get_xid())
        self.grab(self.keytext)

    def get_mask_combinations(self, mask):
        return [x for x in range(mask+1) if not (x & ~mask)]

    def idle(self):
        self.emit("activate")
        return False

    def activate(self):
        GLib.idle_add(self.run)

    # Get which window manager we're currently using (Marco, Compiz, Metacity, etc...)
    def get_wm(self):
        name = ''
        wm_check = self.display.get_atom('_NET_SUPPORTING_WM_CHECK')
        win_id = self.window.get_full_property(wm_check, X.AnyPropertyType)
        if win_id:
            w = self.display.create_resource_object("window", win_id.value[0])
            wm_name = self.display.get_atom('_NET_WM_NAME')
            prop = w.get_full_property(wm_name, X.AnyPropertyType)
            if prop:
                name = prop.value
        return name.lower()

    def run(self):
        self.running = True
        wait_for_release = False
        while self.running:
            event = self.display.next_event()

            if self.modifiers:
                # Use simpler logic when using traditional combined keybindings
                modifiers = event.state & self.known_modifiers_mask
                if event.type == X.KeyPress and event.detail == self.keycode and modifiers == self.modifiers:
                    GLib.idle_add(self.idle)

            else:
                try:
                    # KeyPress
                    if event.type == X.KeyPress and event.detail == self.keycode and not wait_for_release:
                        modifiers = event.state & self.known_modifiers_mask
                        if modifiers == self.modifiers:
                            wait_for_release = True

                    # KeyRelease
                    elif event.type == X.KeyRelease and event.detail == self.keycode and wait_for_release:
                        GLib.idle_add(self.idle)
                        wait_for_release = False

                    # Modifiers are often used with mouse events - don't let the system swallow those
                    elif event.type == X.ButtonPress:
                        self.display.allow_events(X.ReplayPointer, X.CurrentTime)
                        # Compiz would rather not have the event sent to it and just read it from the replayed queue
                        wm = self.get_wm()
                        if wm != "compiz":
                            self.display.ungrab_keyboard(X.CurrentTime)
                            self.display.ungrab_pointer(X.CurrentTime)
                            query_pointer = self.window.query_pointer()
                            self.display.send_event(query_pointer.child, event, X.ButtonPressMask, True)
                        wait_for_release = False

                    # If the user presses another key in between the KeyPress and the KeyRelease, they
                    # meant to use a different shortcut
                    else:
                        self.display.ungrab_keyboard(X.CurrentTime)
                        # Send the event up in case another window is listening to it
                        self.display.send_event(event.window, event, X.KeyPressMask | X.KeyReleaseMask, True)
                        wait_for_release = False
                except AttributeError:
                    continue

    def stop(self):
        self.running = False
        self.ungrab()
        self.display.close()

class KeybindingWidget(Gtk.Box):
    __gsignals__ = {
        'accel-edited': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    def __init__(self, desc):
        super(KeybindingWidget, self).__init__()
        self.desc = desc
        self.label = Gtk.Label(label=desc)
        if self.desc != "":
            self.pack_start(self.label, False, False, 0)
        self.button = Gtk.Button()
        self.button.set_tooltip_text(_("Click to set a new accelerator key for opening and closing the menu.  ") +
                                     _("Press Escape or click again to cancel the operation.  ") +
                                     _("Press Backspace to clear the existing keybinding."))
        self.button.connect("clicked", self.clicked)
        self.button.set_size_request(200, -1)
        self.pack_start(self.button, False, False, 4)

        self.show_all()
        self.event_id = None
        self.teaching = False

    def clicked(self, widget):
        display = widget.get_display()
        if not self.teaching:
            if (Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION) >= (3, 20):
                seat = display.get_default_seat()
                seat.grab(widget.get_window(), Gdk.SeatCapabilities.KEYBOARD, False,
                          None, None, None, None)
            else:
                Gdk.keyboard_grab(self.get_window(), False, Gdk.CURRENT_TIME)

            self.button.set_label(_("Pick an accelerator"))
            self.event_id = self.connect( "key-release-event", self.on_key_release )
            self.teaching = True
        else:
            if self.event_id:
                self.disconnect(self.event_id)
            self.ungrab(display)
            self.set_button_text()
            self.teaching = False

    def on_key_release(self, widget, event):
        self.disconnect(self.event_id)
        self.ungrab(widget.get_display())
        self.event_id = None
        if event.keyval == Gdk.KEY_Escape:
            self.set_button_text()
            self.teaching = False
            return True
        if event.keyval == Gdk.KEY_BackSpace:
            self.teaching = False
            self.value = ""
            self.set_button_text()
            self.emit("accel-edited")
            return True
        accel_string = Gtk.accelerator_name( event.keyval, event.state )
        accel_string = self.sanitize(accel_string)
        self.value = accel_string
        self.set_button_text()
        self.teaching = False
        self.emit("accel-edited")
        return True

    def sanitize(self, string):
        accel_string = string.replace("<Mod2>", "")
        accel_string = accel_string.replace("<Mod4>", "")
        for single, mod in SPECIAL_MODS:
            if single in accel_string and mod in accel_string:
                accel_string = accel_string.replace(mod, "")
        return accel_string

    def get_val(self):
        return self.value

    def set_val(self, value):
        self.value = value
        self.set_button_text()

    def ungrab(self, display):
        if (Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION) >= (3, 20):
            seat = display.get_default_seat()
            seat.ungrab()
        else:
            Gdk.keyboard_ungrab(Gdk.CURRENT_TIME)

    def set_button_text(self):
        if self.value == "":
            self.button.set_label(_("<not set>"))
        else:
            self.button.set_label(self.value)
