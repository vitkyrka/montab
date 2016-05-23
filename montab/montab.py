#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import signal

import Xlib.display
import Xlib.protocol
import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')

from gi.repository import GLib, Gdk, GdkX11, Gtk, Keybinder
from Xlib import X

# GdkX11 is not an unused import but a workaround for this bug:
# https://bugzilla.gnome.org/show_bug.cgi?id=673396
GdkX11


class MonTab:
    def __init__(self):
        self.screen = Gdk.Screen.get_default()
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root
        self.windows = []

    def get_windows(self, desk=None, monitor=None):
        if desk is None:
            desk = self.screen.get_current_desktop()
        if monitor is None:
            monitor = self.get_current_monitor()

        clients = self.screen.get_window_stack()
        wins = []

        for w in reversed(clients):
            if w.get_desktop() != desk:
                continue

            if self.screen.get_monitor_at_window(w) != monitor:
                continue

            wins.append(w)

        return wins

    def win2xwin(self, win):
        xwin = self.display.create_resource_object('window', win.get_xid())
        return xwin

    def get_xproperty(self, win, typ):
        xwin = self.win2xwin(win)
        prop = xwin.get_full_property(self.display.get_atom(typ),
                                      X.AnyPropertyType)
        return prop.value

    def set_xproperty(self, win, typ, data):
        xwin = self.win2xwin(win)
        atom = self.display.get_atom(typ)
        ev = Xlib.protocol.event.ClientMessage(window=xwin, client_type=atom,
                                               data=(32, data))

        mask = X.SubstructureRedirectMask | X.SubstructureNotifyMask
        self.root.send_event(ev, event_mask=mask)
        self.display.flush()

    def get_window_name(self, win):
        return self.get_xproperty(win, '_NET_WM_NAME')

    def get_current_monitor(self):
        win = self.screen.get_active_window()
        return self.screen.get_monitor_at_window(win)

    def activate_window(self, win):
        # The source of 2 is to indicate that we're a pager, xfwm4 doesn't give
        # the window focus otherwise.  The time is passed in instead of
        # X.CurrentTimestamp because that seems to be always zero, and xfwm4
        # forces source=1 on _NET_ACTIVE_WINDOW events with zero timestamps.
        #
        # See clientHandleNetActiveWindow() and clientActivate() in xfwm4 for
        # details.
        data = [2, int(time.time()), 0, 0, 0]
        self.set_xproperty(win, '_NET_ACTIVE_WINDOW', data)

    def move_mouse(self, x, y):
        self.root.warp_pointer(x, y)
        self.display.flush()

    def goto_monitor(self, monitor):
        windows = self.get_windows(monitor=monitor)

        if windows:
            win = windows[0]
            origin = win.get_origin()
            self.move_mouse(origin.x + win.get_width() / 2,
                            origin.y + win.get_height() / 2)
            self.activate_window(win)
        else:
            geo = self.screen.get_monitor_geometry(monitor)
            self.move_mouse(geo.x + geo.width / 2,
                            geo.y + geo.height / 2)


class Switcher(Gtk.Window):
    def __init__(self, windows, names, activate):
        Gtk.Window.__init__(self, title='Switcher', decorated=False,
                            modal=True, type_hint=Gdk.WindowTypeHint.DOCK)

        self.set_position(Gtk.WindowPosition.CENTER)

        grid = Gtk.Grid(margin=10)
        self.add(grid)

        self.windows = windows
        self.buttons = []
        self.position = 1
        self.handlers = []

        self.connect('draw', self.on_draw)
        self.connect('focus-out-event', self.focus_out)
        self.connect('key-press-event', self.key_press)
        self.connect('key-release-event', self.key_release)

        self.activate = activate

        for i, win in enumerate(windows):
            active = i == self.position
            button = Gtk.ToggleButton(label=names[win], active=active)
            handler = button.connect('clicked',
                                     lambda w, i=i: self.activate_and_die(i))

            grid.attach(button, 0, i, 1, 1)

            self.handlers.append(handler)
            self.buttons.append(button)

    def on_draw(self, widget, cr):
        keymap = Gdk.Keymap.get_default()
        state = keymap.get_modifier_state()

        # This is for the case when the key is released so quickly that we
        # never get a release event for it in this window
        if not state & Gdk.ModifierType.MOD4_MASK:
            self.activate_and_die()

    def key_press(self, widget, event):
        name = Gdk.keyval_name(event.keyval)
        if name == 'Tab':
            self.choose_next()

    def key_release(self, widget, event):
        name = Gdk.keyval_name(event.keyval)
        if name.startswith('Super'):
            self.activate_and_die()

    def choose_next(self):
        button = self.buttons[self.position]
        with button.handler_block(self.handlers[self.position]):
            button.set_active(False)

        self.position += 1
        self.position %= len(self.buttons)

        button = self.buttons[self.position]
        with button.handler_block(self.handlers[self.position]):
            button.set_active(True)

    def activate_and_die(self, position=None):
        if position is None:
            position = self.position
        self.activate(self.windows[position])
        self.destroy()

    def focus_out(self, widget, event):
        self.activate(None)
        self.destroy()


class Listener:
    def __init__(self, superkey='<Super>', monkeys='qwerty'):
        self.montab = MonTab()
        self.monkeys = monkeys
        self.super = superkey
        Keybinder.init()

    def install(self):
        n_monitors = self.montab.screen.get_n_monitors()
        for i in range(min(len(self.monkeys), n_monitors)):
            Keybinder.bind(self.super + self.monkeys[i], self.monitor_key, i)

        self.bind_tab(True)

    def bind_tab(self, bind=True):
        tabkey = self.super + 'Tab'
        if bind:
            Keybinder.bind(tabkey, self.tab_key)
        else:
            Keybinder.unbind(tabkey)

    def activate_window(self, win):
        if win:
            self.montab.activate_window(win)
        self.bind_tab(True)

    def show_switcher(self):
        windows = self.montab.get_windows()
        if len(windows) < 2:
            return

        # If we don't unbind, the window loses focus on further Super-Tabs
        self.bind_tab(False)

        names = dict([(w, self.montab.get_window_name(w)) for w in windows])
        win = Switcher(windows, names, activate=self.activate_window)
        win.show_all()

    def tab_key(self, keystring):
        # If the unbind is done here, we segfault
        GLib.idle_add(self.show_switcher)

    def monitor_key(self, keystring, monitor):
        self.montab.goto_monitor(monitor)


def main():
    Listener().install()

    # Make Ctrl-C kill loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()


if __name__ == '__main__':
    main()
