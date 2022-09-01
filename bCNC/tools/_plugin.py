""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
class Plugin(DataBase):
    def __init__(self, master, name):
        DataBase.__init__(self, master, name)
        self.plugin = True
        self.group = "Macros"
        self.oneshot = False
        self.help = None
