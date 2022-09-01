""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

import tkinter as tk

import Utils
from .. import utils
from ..cnccanvas import ACTION_MOVE, ACTION_ORIGIN
from .. import cncribbon
from .. import ribbon

from globalVariables import N_

name = "MoveGroup"


# =============================================================================
# Move Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(self, master, N_("Move"), app)
        self.grid3rows()

        self.add_menu((
            (_("Top-Left"), "tl", lambda a=app: a.insertCommand(
                "MOVE TL", True)),
            (_("Left"), "lc", lambda a=app: a.insertCommand(
                "MOVE LC", True)),
            (_("Bottom-Left"), "bl", lambda a=app: a.insertCommand(
                "MOVE BL", True)),
            (_("Top"), "tc", lambda a=app: a.insertCommand(
                "MOVE TC", True)),
            (_("Center"), "center", lambda a=app: a.insertCommand(
                "MOVE CENTER", True)),
            (_("Bottom"), "bc", lambda a=app: a.insertCommand(
                "MOVE BC", True)),
            (_("Top-Right"), "tr", lambda a=app: a.insertCommand(
                "MOVE TR", True)),
            (_("Right"), "rc", lambda a=app: a.insertCommand(
                "MOVE RC", True)),
            (_("Bottom-Right"), "br", lambda a=app: a.insertCommand(
                "MOVE BR", True)),
        ))

        # ===
        col, row = 0, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["move32"],
            text=_("Move"),
            compound="top",
            anchor="w",
            variable=app.canvas.actionVar,
            value=ACTION_MOVE,
            command=app.canvas.setActionMove,
            # background=ribbon._BACKGROUND,
            style="RibbonGroup.Toolbutton"
        )
        b.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Move objects [M]"))
        self.addWidget(b)

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["origin32"],
            text=_("Origin"),
            compound="top",
            anchor="w",
            variable=app.canvas.actionVar,
            value=ACTION_ORIGIN,
            command=app.canvas.setActionOrigin,
            # background=ribbon._BACKGROUND,
            style="RibbonGroup.Toolbutton"
        )
        b.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Move all gcode such as origin is on mouse location [O]")
        )
        self.addWidget(b)

    # ----------------------------------------------------------------------
    def createMenu(self):
        menu = tk.Menu(self, tearoff=0)
        for i, n, c in (
            (_("Top-Left"), "tl", "MOVE TL"),
            (_("Left"), "lc", "MOVE LC"),
            (_("Bottom-Left"), "bl", "MOVE BL"),
            (_("Top"), "tc", "MOVE TC"),
            (_("Center"), "center", "MOVE CENTER"),
            (_("Bottom"), "bc", "MOVE BC"),
            (_("Top-Right"), "tr", "MOVE TR"),
            (_("Right"), "rc", "MOVE RC"),
            (_("Bottom-Right"), "br", "MOVE BR"),
        ):
            menu.add_command(
                label=n,
                image=Utils.icons[i],
                compound="left",
                command=lambda a=self.app, c=c: a.insertCommand(c, True),
            )
        return menu

