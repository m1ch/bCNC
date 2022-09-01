""" This File was refactored from original File
    TerminalPage.py - TerminalPage

"""
# $Id$
#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015


from . import _page

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


# =============================================================================
# Terminal Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("Serial Terminal")
    _name_ = "Terminal"
    _icon_ = "terminal"

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    def register(self):
        self._register(groups=("Commands", "Terminal"), frames=("Terminal",))
        # self._register((CommandsGroup, TerminalGroup), (TerminalFrame,))
