""" This file was created due to the refactoring of
    FilePage.py

    Authors:
             @m1ch
"""

from .. import utils

from ..cncribbon import ButtonGroup

from globalVariables import N_
from globalConfig import icon as gicon

name = "CloseGroup"


# =============================================================================
# Close Group
# =============================================================================
class RibbonGroup(ButtonGroup):
    def __init__(self, master, app):
        ButtonGroup.__init__(self, master, N_("Close"), app)

        # ---
        b = utils.LabelButton(
            self.frame,
            text=_("Exit"),
            image=gicon["exit32"],
            compound="top",
            command=app.quit,
            style='RibbonGroup.TButton',
        )
        b.pack(fill="both", expand=True)
        utils.ToolTip(b, _("Close program [Ctrl-Q]"))
