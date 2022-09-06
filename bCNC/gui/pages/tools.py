""" This File was refactored from original File
    ToolsPage.py - ToolsPage

"""
# $Id$
#
# Author:       vvlachoudis@gmail.com
# Date: 24-Aug-2014

from . import _page

from globalVariables import N_

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Tools Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("GCode manipulation tools and user plugins")
    _name_ = N_("CAM")
    _icon_ = "tools"

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    # def register(self):
    #     self._register(
    #         # GeneratorGroup,
    #         # ArtisticGroup,
    #         # MacrosGroup,
    #         groups=("Config", "DataBase", "CAM"),
    #         frames=("cam",),
    #     )

    #     self._register(
    #         (
    #             ConfigGroup,
    #             DataBaseGroup,
    #             CAMGroup,
    #             # GeneratorGroup,
    #             # ArtisticGroup,
    #             # MacrosGroup,
    #         ),
    #         (ToolsFrame,),
    #     )

    # ----------------------------------------------------------------------
    def edit(self, event=None):
        self.app.leftpanels["CAM"].edit()

    # ----------------------------------------------------------------------
    def add(self, event=None):
        self.app.leftpanels["CAM"].add()

    # ----------------------------------------------------------------------
    def clone(self, event=None):
        self.app.leftpanels["CAM"].clone()

    # ----------------------------------------------------------------------
    def delete(self, event=None):
        self.app.leftpanels["CAM"].delete()

    # ----------------------------------------------------------------------
    def rename(self, event=None):
        self.app.leftpanels["CAM"].rename()
