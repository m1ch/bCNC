""" This File was refactored from original File
    ProbePage.py - ProbePage

"""
# $Id$
#
# Author: Vasilis Vlachoudis
#  Email: vvlachoudis@gmail.com
#   Date: 18-Jun-2015
from . import _page
# from globalConstants import __author__, __email__


# =============================================================================
# Probe Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("Probe configuration and probing")
    _name_ = "Probe"
    _icon_ = "measure"

    # -----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # -----------------------------------------------------------------------
    def register(self):
        # self._register(
        #     groups=("ProbeTab", "Autolevel", "Camera", "Tool"),
        #     frames=("ProbeCommon", "Probe", "Autolevel",
        #             "Camera", "Tool"),
        # )
        # self._register(
        #     (ProbeTabGroup, AutolevelGroup, CameraGroup, ToolGroup),
        #     (ProbeCommonFrame, ProbeFrame, AutolevelFrame,
        #      CameraFrame, ToolFrame),
        # )

        # self.tabGroup = cncribbon.Page.groups["Probe"]
        self.tabGroup = self.app.groups["Probe"]
        self.tabGroup.tab.set("Probe")
        self.tabGroup.tab.trace("w", self.tabChange)

    # -----------------------------------------------------------------------
    def tabChange(self, a=None, b=None, c=None):
        tab = self.tabGroup.tab.get()
        self.master._forgetPage()

        # Remove all page tabs with ":" and add the new ones
        self.ribbons = [x for x in self.ribbons if ":" not in x[0].name]
        self.frames = [x for x in self.frames if ":" not in x[0].name]

        try:
            self.addRibbonGroup(f"Probe:{tab}")
        except KeyError:
            pass
        try:
            self.addPageFrame(f"Probe:{tab}")
        except KeyError:
            pass

        self.master.changePage(self)
