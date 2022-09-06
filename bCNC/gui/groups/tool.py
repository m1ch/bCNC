""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

from .. import cncribbon
from .. import utils
from globalConfig import icon as gicon

name = "ToolGroup"


# =============================================================================
# Tool Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Probe:Tool", app)

        b = utils.LabelButton(
            self.frame,
            self,
            "<<ToolCalibrate>>",
            image=gicon["calibrate32"],
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
            image=gicon["endmill32"],
            text=_("Change"),
            compound="top",
            # width=48,
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both", expand=True)
        self.addWidget(b)
        utils.ToolTip(b, _("Perform a tool change cycle"))
