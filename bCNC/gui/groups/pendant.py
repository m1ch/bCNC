""" This file was created due to the refactoring of
    FilePage.py

    Authors:
             @m1ch
"""

import Utils

from .. import utils

from .. import cncribbon


from globalVariables import N_

name = "PendantGroup"


# =============================================================================
# Pendant Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Pendant"), app)
        self.grid3rows()

        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            text=_("Start"),
            image=Utils.icons["start_pendant"],
            compound="left",
            anchor="w",
            command=app.startPendant,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Start pendant"))

        row += 1
        b = utils.LabelButton(
            self.frame,
            text=_("Stop"),
            image=Utils.icons["stop_pendant"],
            compound="left",
            anchor="w",
            command=app.stopPendant,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Stop pendant"))
