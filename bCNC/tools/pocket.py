""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Pocket
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Pocket
    """
    def __init__(self, master):
        DataBase.__init__(self, master, "Pocket")
        self.icon = "pocket"
        self.variables = [
            ("name", "db", "", _("Name")),
            ("endmill", "db", "", _("End Mill")),
        ]
        self.buttons.append("exe")
        self.help = """Remove all material inside selected shape
"""

    # ----------------------------------------------------------------------
    def execute(self, app):
        if self["endmill"]:
            self.master["endmill"].makeCurrent(self["endmill"])
        name = self["name"]
        if name == "default" or name == "":
            name = None
        app.pocket(name)
        app.setStatus(_("Generate pocket path"))
