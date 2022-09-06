# $Id$
#
# Author: Vasilis Vlachoudis
#  Email: Vasilis.Vlachoudis@cern.ch
#   Date: 16-Apr-2015

import os
import sys
import traceback

import tkinter.font as tkfont

from lib.log import say

try:
    import serial
except Exception:
    serial = None

icons = {}
images = {}

language = ""

errors = []


# -----------------------------------------------------------------------------
# Create a font string
# -----------------------------------------------------------------------------
def fontString(font):
    name = str(font[0])
    size = str(font[1])
    if name.find(" ") >= 0:
        s = f"\"{name}\" {size}"
    else:
        s = f"{name} {size}"

    try:
        if font[2] == tkfont.BOLD:
            s += " bold"
    except Exception:
        pass
    try:
        if font[3] == tkfont.ITALIC:
            s += " italic"
    except Exception:
        pass
    return s


# -----------------------------------------------------------------------------
# Return all comports when serial.tools.list_ports is not available!
# -----------------------------------------------------------------------------
def comports(include_links=True):
    locations = ["/dev/ttyACM", "/dev/ttyUSB", "/dev/ttyS", "com"]

    comports = []
    for prefix in locations:
        for i in range(32):
            device = f"{prefix}{i}"
            try:
                os.stat(device)
                comports.append((device, None, None))
            except OSError:
                pass

            # Detects windows XP serial ports
            try:
                s = serial.Serial(device)
                s.close()
                comports.append((device, None, None))
            except Exception:
                pass
    return comports


# =============================================================================
def getDictKeyByValue(dict, value):
    try:
        index = list(dict.values()).index(value)
    except ValueError:
        return None
    return list(dict.keys())[index]


# =============================================================================
def addException():
    from globalVariables import glob_errors
    from gui import tkdialogs

    # global errors
    try:
        typ, val, tb = sys.exc_info()
        traceback.print_exception(typ, val, tb)
        if glob_errors:
            glob_errors.append("")
        exception = traceback.format_exception(typ, val, tb)
        glob_errors.extend(exception)
        if len(glob_errors) > 100:
            # If too many errors are found send the error report
            # FIXME: self outside of Class
            tkdialogs.ReportDialog(self.widget)  # noqa: F821 - see fixme
    except Exception:
        say(str(sys.exc_info()))


# =============================================================================
class CallWrapper:
    """Replaces the tkinter.CallWrapper with extra functionality"""

    def __init__(self, func, subst, widget):
        """Store FUNC, SUBST and WIDGET as members."""
        self.func = func
        self.subst = subst
        self.widget = widget

    # ----------------------------------------------------------------------
    def __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit:  # both
            raise SystemExit(sys.exc_info()[1])
        except KeyboardInterrupt:
            pass
        except Exception:
            addException()
