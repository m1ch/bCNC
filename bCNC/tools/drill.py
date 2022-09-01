""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Drill material
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Drill
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "Drill")
        self.icon = "drill"
        self.variables = [
            ("name", "db", "", _("Name")),
            ("center", "bool", True, _("Drill in center only")),
            ("depth", "mm", "", _("Target Depth")),
            ("peck", "mm", "", _("Peck depth")),
            ("dwell", "float", "", _("Dwell (s)")),
            ("distance", "mm", "", _("Distance (mm)")),
            ("number", "int", "", _("Number")),
        ]
        self.help = "\n".join([
            "Drill a hole in the center of the selected path or drill many "
            + "holes along the selected path.",
            "",
            "MODULE PARAMETERS:",
            "",
            "* center : if checked, there is only one drill in the center of "
            + "the selected path. (Otherwise drill along path)",
            "",
            "* depth : Depth of the drill. If not provided, stock material "
            + "thickness is used. (usually negative value)",
            "",
            "* peck: Peck step depth. If provided, drill with peck depth "
            + "step, raising the drill to z travel value. If not provided, "
            + "one pass drill is generated.",
            "",
            "* dwell: Dwell time at the bottom. If pecking is defined, dwell "
            + "also at lifted height.",
            "",
            "* distance: Distance between drills if drilling along path. "
            + "(Number of drills will superceed this parameter))",
            "",
            "* number: Number of drills if drilling along path. If nonzero, "
            + "Parameter 'distance' has no effect.",
        ])
        self.buttons.append("exe")

    # ----------------------------------------------------------------------
    def execute(self, app):
        h = self.fromMm("depth", None)
        p = self.fromMm("peck", None)
        e = self.fromMm("distance", None)
        c = self["center"]
        try:
            d = self["dwell"]
        except Exception:
            d = None
        try:
            n = int(self["number"])
        except Exception:
            n = 0
        app.executeOnSelection("DRILL", True, h, p, d, e, n, c)
        app.setStatus(_("DRILL selected points"))

