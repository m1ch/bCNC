""" This File was refactored from original File
    ControlPage.py - ControlPage

"""

# $Id$
#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015

from . import _page

from globalVariables import N_

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


OVERRIDES = ["Feed", "Rapid", "Spindle"]

# override for init
UNITS = {"G20": "inch", "G21": "mm"}


# =============================================================================
# Control Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("CNC communication and control")
    _name_ = N_("Control")
    _icon_ = "control"

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    # def register(self):
    #     # global wcsvar
    #     # wcsvar = tk.IntVar()
    #     # wcsvar.set(0)

    #     self._register(
    #         groups=("Connection", "User", "Run"),
    #         frames=("DRO", "abcDRO", "Control", "abcControl", "State"),
    #     )

    # self._register(
    #     (ConnectionGroup, UserGroup, RunGroup),
    #     (DROFrame, abcDROFrame, ControlFrame, abcControlFrame,
    # StateFrame),
    # )
