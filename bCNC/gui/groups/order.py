""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

import Utils
from .. import utils
from .. import cncribbon

from globalVariables import N_

name = "OrderGroup"


# =============================================================================
# Order Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(
            self,
            master,
            N_("Order"),
            app,
            [
                (
                    _("Optimize"),
                    "optimize",
                    lambda a=app: a.insertCommand("OPTIMIZE", True),
                ),
            ],
        )
        self.grid2rows()

        # ===
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<Control-Key-Prior>",
            image=Utils.icons["up"],
            text=_("Up"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _("Move selected g-code up [Ctrl-Up, Ctrl-PgUp]")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self,
            "<Control-Key-Next>",
            image=Utils.icons["down"],
            text=_("Down"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _("Move selected g-code down [Ctrl-Down, Ctrl-PgDn]")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Invert>>",
            image=Utils.icons["swap"],
            text=_("Invert"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Invert cutting order of selected blocks"))
        self.addWidget(b)
