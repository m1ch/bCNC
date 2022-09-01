""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Profile
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Profile
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "Profile")
        self.icon = "profile"
        self.variables = [
            ("name", "db", "", _("Name")),
            (
                "endmill",
                "db",
                "",
                _("End Mill"),
                _("Size of this endmill will be used as offset distance"),
            ),
            (
                "direction",
                "inside,outside",
                "outside",
                _("Direction"),
                _("Should we machine on inside or outside of the shape?"),
            ),
            ("offset", "float", 0.0, _("Additional offset distance")),
            (
                "overcut",
                "bool",
                1,
                _("Overcut"),
                _("Sets if we want to overcut or not."),
            ),
            (
                "pocket",
                "bool",
                0,
                _("Pocket"),
                _(
                    "Generate pocket after profiling? Useful for making "
                    + "pockets with overcuts."
                ),
            ),
        ]
        self.buttons.append("exe")
        self.help = "\n".join([
            "This plugin offsets shapes to create toolpaths for profiling "
            + "operation.",
            "Shape needs to be offset by the radius of endmill to get cut "
            + "correctly.",
            "",
            "Currently we have two modes.",
            "",
            "Without overcut:",
            "#overcut-without",
            "",
            "And with overcut:",
            "#overcut-with",
            "",
            "Blue is the original shape from CAD",
            "Turquoise is the generated toolpath",
            "Grey is simulation of how part will look after machining",
        ])

    # ----------------------------------------------------------------------
    def execute(self, app):
        if self["endmill"]:
            self.master["endmill"].makeCurrent(self["endmill"])
        direction = self["direction"]
        name = self["name"]
        pocket = self["pocket"]
        if name == "default" or name == "":
            name = None
        app.profile(direction, self["offset"], self["overcut"], name, pocket)
        app.setStatus(_("Generate profile path"))
