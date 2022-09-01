""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

import Utils

from .. import cncribbon
from .. import utils

from globalVariables import N_

name = "ClipboardGroup"


# =============================================================================
# Clipboard Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Clipboard"), app)
        self.grid2rows()

        # ---
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Paste>>",
            image=Utils.icons["paste32"],
            text=_("Paste"),
            compound="top",
            takefocus=False,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Paste [Ctrl-V]"))
        self.addWidget(b)

        # ---
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Cut>>",
            image=Utils.icons["cut"],
            text=_("Cut"),
            compound="left",
            anchor="w",
            takefocus=False,
            style='RibbonGroup.Toolbutton',
        )
        utils.ToolTip(b, _("Cut [Ctrl-X]"))
        b.grid(row=0, column=1, padx=0, pady=1, sticky="nsew")
        self.addWidget(b)

        # ---
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Copy>>",
            image=Utils.icons["copy"],
            text=_("Copy"),
            compound="left",
            anchor="w",
            takefocus=False,
            style='RibbonGroup.Toolbutton',
        )
        utils.ToolTip(b, _("Copy [Ctrl-C]"))
        b.grid(row=1, column=1, padx=0, pady=1, sticky="nsew")
        self.addWidget(b)
