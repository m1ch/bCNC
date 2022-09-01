""" This file was created due to the refactoring of
    ControlPage.py

    Authors:
             @m1ch
"""

import Utils

from .. import utils
from .. import cncribbon

name = "RunGroup"


# =============================================================================
# Run Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Run", app)

        b = utils.LabelButton(
            self.frame,
            self,
            "<<Run>>",
            image=Utils.icons["start32"],
            text=_("Start"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both")
        utils.ToolTip(
            b, _("Run g-code commands from editor to controller"))
        self.addWidget(b)

        b = utils.LabelButton(
            self.frame,
            self,
            "<<Pause>>",
            image=Utils.icons["pause32"],
            text=_("Pause"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both")
        utils.ToolTip(
            b,
            _("Pause running program. Sends either FEED_HOLD ! "
              + "or CYCLE_START ~")
        )

        b = utils.LabelButton(
            self.frame,
            self,
            "<<Stop>>",
            image=Utils.icons["stop32"],
            text=_("Stop"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.pack(side="left", fill="both")
        utils.ToolTip(
            b, _("Pause running program and soft reset controller to "
                 + "empty the buffer.")
        )
