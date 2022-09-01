""" This File was refactored from original File
    FilePage.py - FilePage

"""
# $Id$
#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015


from . import _page

from globalVariables import N_

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


# =============================================================================
# File Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("File I/O and configuration")
    _name_ = N_("File")
    _icon_ = "new"

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    def register(self):
        self._register(
            groups=("File", "Pendant", "Options", "Close"),
            frames=("Serial"),
        )
        # self._register(
        #     (FileGroup, PendantGroup, OptionsGroup, CloseGroup),
        # (SerialFrame,)
        # )
