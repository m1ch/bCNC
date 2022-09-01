""" This file was created due to the refactoring of
    FilePage.py

    Authors:
             @m1ch
"""

import Utils

from .. import utils

from .. import cncribbon


from globalVariables import N_

name = "CloseGroup"


# =============================================================================
# Close Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Close"), app)

        # ---
        b = utils.LabelButton(
            self.frame,
            text=_("Exit"),
            image=Utils.icons["exit32"],
            compound="top",
            command=app.quit,
            anchor="w",
            style='RibbonGroup.TButton',
        )
        b.pack(fill="both", expand=True)
        utils.ToolTip(b, _("Close program [Ctrl-Q]"))
