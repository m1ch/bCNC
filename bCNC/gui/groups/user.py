""" This file was created due to the refactoring of
    ControlPage.py

    Authors:
             @m1ch
"""

from globalConfig import config as gconfig

from .. import utils
from .. import cncribbon

name = "UserGroup"


# =============================================================================
# User Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "User", app)
        self.grid3rows()

        n = gconfig.getint("Buttons", "n", 6)
        for i in range(1, n):
            b = utils.UserButton(
                self.frame,
                self.app,
                i,
                style='RibbonGroup.Toolbutton',
            )
            col, row = divmod(i - 1, 3)
            b.grid(row=row, column=col, sticky="nsew")
            self.addWidget(b)
