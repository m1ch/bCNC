""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

import tkinter as tk

import Camera
from .. import cncribbon
from .. import utils

from globalVariables import N_
from globalConfig import icon as gicon

name = "ProbeTabGroup"

required_groups = ["Autolevel", "Camera", "Tool"]
required_frames = ["Probe", "Autolevel", "Camera", "Tool"]


# =============================================================================
# Probe Tab Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Probe"), app)

        self.tab = tk.StringVar()
        # ---
        col, row = 0, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["probe32"],
            text=_("Probe"),
            compound="top",
            variable=self.tab,
            value="Probe",
        )
        b.grid(row=row, column=col, padx=5, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Simple probing along a direction"))

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["level32"],
            text=_("Autolevel"),
            compound="top",
            variable=self.tab,
            value="Autolevel",
        )
        b.grid(row=row, column=col, padx=5, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Autolevel Z surface"))

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["camera32"],
            text=_("Camera"),
            compound="top",
            variable=self.tab,
            value="Camera",
        )
        b.grid(row=row, column=col, padx=5, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Work surface camera view and alignment"))
        if Camera.cv is None:
            b.config(state="disabled")

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["endmill32"],
            text=_("Tool"),
            compound="top",
            variable=self.tab,
            value="Tool",
        )
        b.grid(row=row, column=col, padx=5, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Setup probing for manual tool change"))

        self.frame.grid_rowconfigure(0, weight=1)
