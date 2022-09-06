""" This file was created due to the refactoring of
    FilePage.py

    Authors:
             @m1ch
"""

from .. import tkdialogs

from .. import utils

from .. import cncribbon

from globalVariables import N_
from globalConfig import icon as gicon

name = "OptionsGroup"


# =============================================================================
# Options Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Options"), app)
        self.grid3rows()

        # ===
        col, row = 1, 0
        b = utils.LabelButton(
            self.frame,
            text=_("Report"),
            image=gicon["debug"],
            compound="left",
            command=tkdialogs.ReportDialog.sendErrorReport,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="ew")
        utils.ToolTip(b, _("Send Error Report"))

        # ---
        col, row = 1, 1
        b = utils.LabelButton(
            self.frame,
            text=_("Updates"),
            image=gicon["global"],
            compound="left",
            command=self.app.checkUpdates,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="ew")
        utils.ToolTip(b, _("Check Updates"))

        col, row = 1, 2
        b = utils.LabelButton(
            self.frame,
            text=_("About"),
            image=gicon["about"],
            compound="left",
            command=self.app.about,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="ew")
        utils.ToolTip(b, _("About the program"))
