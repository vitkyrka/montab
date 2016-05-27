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

``Super + Shift + Tab``
  Like ``Super + Tab``, but cycle in reverse order.

``Super + [1-9]``
  Activate the most recent window on the specified monitor and move the mouse
  pointer to the window's center.  If there is no window on the specified
  monitor, just move the mouse pointer to the center of the monitor.

``Super + Ctrl + [1-9]``
  Cycle through a window list containing only windows on the specified monitor.
  When a window is selected, it is raised but not given focus.

``Super + Shift + Ctrl + [1-9]``
  Like ``Super + Ctrl + [1-9]``, but cycle in reverse order.

Installation
------------

::

    sudo apt-get install gir1.2-keybinder-3.0 python-gi python-xlib
    python setup.py install

Run ``montab`` after installation.  Note that if you're using XFCE, ``Super +
Tab`` has a default binding which you'll have to disable in the Window Manager
settings.
