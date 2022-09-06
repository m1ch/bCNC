""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

from .. import cncribbon
from .. import utils

from globalVariables import N_
from globalConfig import icon as gicon

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
            image=gicon["paste32"],
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
            image=gicon["cut"],
            text=_("Cut"),
            compound="left",
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
            image=gicon["copy"],
            text=_("Copy"),
            compound="left",
            takefocus=False,
            style='RibbonGroup.Toolbutton',
        )
        utils.ToolTip(b, _("Copy [Ctrl-C]"))
        b.grid(row=1, column=1, padx=0, pady=1, sticky="nsew")
        self.addWidget(b)
