""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

import Utils
from .. import utils
from .. import cncribbon

from globalVariables import N_

name = "RouteGroup"


# =============================================================================
# Route Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Route"), app)
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["conventional"],
            text=_("Conventional"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand(
                "DIRECTION CONVENTIONAL", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _("Change cut direction to conventional for selected gcode blocks")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["climb"],
            text=_("Climb"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand("DIRECTION CLIMB", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Change cut direction to climb for selected gcode blocks")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["reverse"],
            text=_("Reverse"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand("REVERSE", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Reverse cut direction for selected gcode blocks"))
        self.addWidget(b)

        # ---
        col, row = 1, 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["rotate_90"],
            text=_("Cut CW"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand("DIRECTION CW", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Change cut direction to CW for selected gcode blocks")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["rotate_270"],
            text=_("Cut CCW"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand("DIRECTION CCW", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Change cut direction to CCW for selected gcode blocks")
        )
        self.addWidget(b)
