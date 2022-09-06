""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

from .. import utils
from .. import cncribbon

from globalVariables import N_
from globalConfig import icon as gicon

name = "InfoGroup"


# =============================================================================
# Info Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Info"), app)
        self.grid2rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            image=gicon["stats"],
            text=_("Statistics"),
            compound="left",
            command=app.showStats,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Show statistics for enabled gcode"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            image=gicon["info"],
            text=_("Info"),
            compound="left",
            command=app.showInfo,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Show cutting information on selected blocks [Ctrl-n]")
        )
        self.addWidget(b)
