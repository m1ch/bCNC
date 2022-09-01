""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from cnc import globCNC

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# EndMill Bit database
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class EndMill
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "EndMill")
        self.variables = [
            ("name", "db", "", _("Name")),
            ("comment", "str", "", _("Comment")),
            ("type", "list", "", _("Type")),
            ("shape", "list", "", _("Shape")),
            ("material", "list", "", _("Material")),
            ("coating", "list", "", _("Coating")),
            ("diameter", "mm", 3.175, _("Diameter")),
            ("axis", "mm", 3.175, _("Mount Axis")),
            ("flutes", "int", 2, _("Flutes")),
            ("length", "mm", 20.0, _("Length")),
            ("angle", "float", "", _("Angle")),
            ("stepover", "float", 40.0, _("Stepover %")),
        ]

    # ----------------------------------------------------------------------
    # Update variables after edit command
    # ----------------------------------------------------------------------
    def update(self):
        globCNC["diameter"] = self.fromMm("diameter")
        globCNC["stepover"] = self["stepover"]
        return False
