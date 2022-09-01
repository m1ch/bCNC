""" This file was created due to the refactoring of
    TerminalPage.py

    Authors:
             @m1ch
"""

import Utils
from globalVariables import N_
from .. import utils
from .. import cncribbon

name = "TerminalGroup"


# =============================================================================
# Terminal Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Terminal"), app)

        b = utils.LabelButton(
            self.frame,
            self,
            "<<TerminalClear>>",
            image=Utils.icons["clean32"],
            text=_("Clear"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.pack(fill="both", expand=True)
        utils.ToolTip(b, _("Clear terminal"))
