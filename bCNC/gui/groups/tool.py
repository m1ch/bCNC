""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

from .. import cncribbon
from .. import ribbon
import Utils
from .. import utils

name = "ToolGroup"


# =============================================================================
# Tool Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Probe:Tool", app)
        # self.label["background"] = ribbon._BACKGROUND_GROUP2

        b = utils.LabelButton(
            self.frame,
            self,
            "<<ToolCalibrate>>",
            image=Utils.icons["calibrate32"],
            text=_("Calibrate"),
            compound="top",
            # width=48,
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both", expand=True)
        self.addWidget(b)
        utils.ToolTip(
            b,
            _("Perform a single a tool change cycle to set the "
              + "calibration field")
        )

        b = utils.LabelButton(
            self.frame,
            self,
            "<<ToolChange>>",
            image=Utils.icons["endmill32"],
            text=_("Change"),
            compound="top",
            # width=48,
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both", expand=True)
        self.addWidget(b)
        utils.ToolTip(b, _("Perform a tool change cycle"))
