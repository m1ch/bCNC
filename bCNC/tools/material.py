""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from cnc import globCNC

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Material database
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Material
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "Material")
        self.variables = [
            ("name", "db", "", _("Name")),
            ("comment", "str", "", _("Comment")),
            ("feed", "mm", 10.0, _("Feed")),
            ("feedz", "mm", 1.0, _("Plunge Feed")),
            ("stepz", "mm", 1.0, _("Depth Increment")),
        ]

    # ----------------------------------------------------------------------
    # Update variables after edit command
    # ----------------------------------------------------------------------
    def update(self):
        # update ONLY if stock material is empty:
        stockmat = self.master["stock"]["material"]
        if stockmat == "" or stockmat == self["name"]:
            globCNC["cutfeed"] = self.fromMm("feed")
            globCNC["cutfeedz"] = self.fromMm("feedz")
            globCNC["stepz"] = self.fromMm("stepz")
        return False
