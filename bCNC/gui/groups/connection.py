""" This file was created due to the refactoring of
    ControlPage.py

    Authors:
             @m1ch
"""

import Utils
from globalVariables import N_

from .. import utils
from .. import cncribbon
from .. import commands as cmd

name = "ConnectionGroup"


# =============================================================================
# Connection Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(
            self,
            master,
            N_("Connection"),
            app,
            [(_("Hard Reset"), "reset", cmd.hardReset)],
        )
        self.grid2rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["home32"],
            text=_("Home"),
            compound="top",
            anchor="w",
            command=cmd.home,
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Perform a homing cycle [$H] now"))
        self.addWidget(b)

        # ---
        col, row = 1, 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["unlock"],
            text=_("Unlock"),
            compound="left",
            anchor="w",
            command=cmd.unlock,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Unlock controller [$X]"))
        self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["serial"],
            text=_("Connection"),
            compound="left",
            anchor="w",
            command=lambda s=self: s.event_generate("<<Connect>>"),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Open/Close connection"))
        self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["reset"],
            text=_("Reset"),
            compound="left",
            anchor="w",
            command=cmd.softReset,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Software reset of controller [ctrl-x]"))
        self.addWidget(b)
