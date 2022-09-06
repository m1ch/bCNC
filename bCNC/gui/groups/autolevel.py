""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

from .. import cncribbon
from .. import utils
from globalConfig import icon as gicon

name = "AutolevelGroup"


# =============================================================================
# Autolevel Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Probe:Autolevel", app)
        self.grid3rows()

        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<<AutolevelMargins>>",
            image=gicon["margins"],
            text=_("Margins"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Get margins from gcode file"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self,
            "<<AutolevelZero>>",
            image=gicon["origin"],
            text=_("Zero"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _(
                "Set current XY location as autoleveling Z-zero (recalculate "
                + "probed data to be relative to this XY origin point)"
            ),
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self,
            "<<AutolevelClear>>",
            image=gicon["clear"],
            text=_("Clear"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Clear probe data"))
        self.addWidget(b)

        # ---
        row = 0
        col += 1
        b = utils.LabelButton(
            self.frame,
            self,
            "<<AutolevelScanMargins>>",
            image=gicon["margins"],
            text=_("Scan"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Scan Autolevel Margins"))
        self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=gicon["level"],
            text=_("Autolevel"),
            compound="left",
            command=lambda a=app: a.insertCommand("AUTOLEVEL", True),
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Modify selected G-Code to match autolevel"))
        self.addWidget(b)

        # ---
        col, row = 2, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<<AutolevelScan>>",
            image=gicon["gear32"],
            text=_("Scan"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=3, sticky="nsew")
        self.addWidget(b)
        utils.ToolTip(
            b, _("Scan probed area for level information on Z plane"))
