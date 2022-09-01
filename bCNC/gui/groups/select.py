""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

from globalConfig import config as gconfig
from .. import cncribbon
from .. import tkextra
import Utils
from .. import utils

from globalVariables import N_

name = "SelectGroup"


# =============================================================================
# Select Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Select"), app)
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            app,
            "<<SelectAll>>",
            image=Utils.icons["select_all"],
            text=_("All"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Select all blocks [Ctrl-A]"))
        self.addWidget(b)

        # ---
        col += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<SelectNone>>",
            image=Utils.icons["select_none"],
            text=_("None"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Unselect all blocks [Ctrl-Shift-A]"))
        self.addWidget(b)

        # ---
        col, row = 0, 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<SelectInvert>>",
            image=Utils.icons["select_invert"],
            text=_("Invert"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Invert selection [Ctrl-I]"))
        self.addWidget(b)

        # ---
        col += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<SelectLayer>>",
            image=Utils.icons["select_layer"],
            text=_("Layer"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Select all blocks from current layer"))
        self.addWidget(b)

        # ---
        col, row = 0, 2
        self.filterString = tkextra.LabelEntry(
            self.frame,
            _("Filter"),
            "DarkGray",
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=16,
        )
        self.filterString.grid(
            row=row, column=col, columnspan=2, padx=0, pady=0, sticky="nsew"
        )
        utils.ToolTip(self.filterString, _("Filter blocks"))
        self.addWidget(self.filterString)
        self.filterString.bind("<Return>", self.filter)
        self.filterString.bind("<KP_Enter>", self.filter)

    # -----------------------------------------------------------------------
    def filter(self, event=None):
        txt = self.filterString.get()
        self.app.insertCommand(f"FILTER {txt}", True)
