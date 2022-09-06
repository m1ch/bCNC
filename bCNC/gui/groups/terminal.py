""" This file was created due to the refactoring of
    TerminalPage.py

    Authors:
             @m1ch
"""

from globalVariables import N_
from .. import utils
from .. import cncribbon
from globalConfig import icon as gicon

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
            image=gicon["clean32"],
            text=_("Clear"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.pack(fill="both", expand=True)
        utils.ToolTip(b, _("Clear terminal"))
