
""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

from .. import utils
from .. import cncribbon

from globalVariables import N_
from globalConfig import icon as gicon

name = "TransformGroup"


# =============================================================================
# Transform Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Transform"), app)
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            image=gicon["rotate_90"],
            text=_("CW"),
            compound="left",
            command=lambda s=app: s.insertCommand("ROTATE CW", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Rotate selected gcode clock-wise (-90deg)"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=gicon["rotate_180"],
            text=_("Flip"),
            compound="left",
            command=lambda s=app: s.insertCommand("ROTATE FLIP", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Rotate selected gcode by 180deg"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=gicon["rotate_270"],
            text=_("CCW"),
            compound="left",
            command=lambda s=app: s.insertCommand("ROTATE CCW", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Rotate selected gcode counter-clock-wise (90deg)"))
        self.addWidget(b)

        # ---
        col, row = 1, 0
        b = utils.LabelButton(
            self.frame,
            image=gicon["flip_horizontal"],
            text=_("Horizontal"),
            compound="left",
            command=lambda s=app: s.insertCommand("MIRROR horizontal", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Mirror horizontally X=-X selected gcode"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=gicon["flip_vertical"],
            text=_("Vertical"),
            compound="left",
            command=lambda s=app: s.insertCommand("MIRROR vertical", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Mirror vertically Y=-Y selected gcode"))
        self.addWidget(b)
