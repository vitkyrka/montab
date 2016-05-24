.. -*- rst -*-

Mon-Tab
=======

This provides behaviour similar to Alt-Tab, but for switching between monitors
or cycling through windows on a specific monitor.  It has only been tested with
XFCE (with focus follows mouse), but should work with any window manager which
supports EWMH.

The trigger key is currently hard coded to ``Super_L`` / ``Mod4``.  The
following shortcuts are available:

``Super + Tab``
  Cycle through a window list containing only windows on the same monitor as
  the currently active window.

``Super + [qwerty]``
  Activate the most recent window on the specified monitor (first = ``q``,
  second = ``w``, and so on) and move the mouse pointer to the window's center.
  If there is no window on the specified monitor, just move the mouse pointer
  to the center of the monitor.

Installation
------------

::

    sudo apt-get install gir1.2-keybinder-3.0 python-gi python-xlib
    python setup.py install

Run ``montab`` after installation.  Note that if you're using XFCE, ``Super +
Tab`` has a default binding which you'll have to disable in the Window Manager
settings.
