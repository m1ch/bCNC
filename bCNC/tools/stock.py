""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from cnc import globCNC

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Stock material on worksurface
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Stock
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "Stock")
        self.variables = [
            ("name", "db", "", _("Name")),
            ("comment", "str", "", _("Comment")),
            ("material", "db", "", _("Material")),
            ("safe", "mm", 3.0, _("Safe Z")),
            ("surface", "mm", 0.0, _("Surface Z")),
            ("thickness", "mm", 5.0, _("Thickness")),
        ]

    # ----------------------------------------------------------------------
    # Update variables after edit command
    # ----------------------------------------------------------------------
    def update(self):
        globCNC["safe"] = self.fromMm("safe")
        globCNC["surface"] = self.fromMm("surface")
        globCNC["thickness"] = self.fromMm("thickness")
        if self["material"]:
            self.master["material"].makeCurrent(self["material"])
        return False
