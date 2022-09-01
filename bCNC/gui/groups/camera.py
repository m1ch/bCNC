""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

import tkinter as tk

from cnc import globCNC
from gcode import globGCode
from sender import globSender

from .. import cncribbon
from .. import ribbon
import Utils
from .. import utils

name = "CameraGroup"


# =============================================================================
# Camera Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Probe:Camera", app)
        # self.label["background"] = ribbon._BACKGROUND_GROUP2
        self.grid3rows()

        self.switch = tk.BooleanVar()
        self.edge = tk.BooleanVar()
        self.freeze = tk.BooleanVar()

        # ---
        col, row = 0, 0
        self.switchButton = utils.LabelCheckbutton(
            self.frame,
            image=Utils.icons["camera32"],
            text=_("Switch To"),
            compound="top",
            variable=self.switch,
            command=self.switchCommand,
            # background=ribbon._BACKGROUND,
        )
        self.switchButton.grid(
            row=row, column=col, rowspan=3, padx=5, pady=0, sticky="nsew"
        )
        utils.ToolTip(self.switchButton,
                      _("Switch between camera and spindle"))

        # ---
        col, row = 1, 0
        b = utils.LabelCheckbutton(
            self.frame,
            image=Utils.icons["edge"],
            text=_("Edge Detection"),
            compound="left",
            variable=self.edge,
            anchor="w",
            command=self.edgeDetection,
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Turn on/off edge detection"))

        # ---
        row += 1
        b = utils.LabelCheckbutton(
            self.frame,
            image=Utils.icons["freeze"],
            text=_("Freeze"),
            compound="left",
            variable=self.freeze,
            anchor="w",
            command=self.freezeImage,
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Turn on/off freeze image"))

    # -----------------------------------------------------------------------
    # Move camera to spindle location and change coordinates to relative
    # to camera via g92
    # -----------------------------------------------------------------------
    def switchCommand(self, event=None):
        wx = globCNC.vars["wx"]
        wy = globCNC.vars["wy"]
        dx = self.app.canvas.cameraDx
        dy = self.app.canvas.cameraDy
        z = self.app.canvas.cameraZ
        if self.switch.get():
            self.switchButton.config(image=Utils.icons["endmill32"])
            self.sendGCode(f"G92X{dx + wx:g}Y{dy + wy:g}")
            self.app.canvas.cameraSwitch = True
        else:
            self.switchButton.config(image=Utils.icons["camera32"])
            self.sendGCode("G92.1")
            self.app.canvas.cameraSwitch = False
        if z is None:
            self.sendGCode(f"G0X{wx:g}Y{wy:g}")
        else:
            self.sendGCode(f"G0X{wx:g}Y{wy:g}Z{z:g}")

    # -----------------------------------------------------------------------
    def switchCamera(self, event=None):
        self.switch.set(not self.switch.get())
        self.switchCommand()

    # -----------------------------------------------------------------------
    def edgeDetection(self):
        self.app.canvas.cameraEdge = self.edge.get()

    # -----------------------------------------------------------------------
    def freezeImage(self):
        self.app.canvas.cameraFreeze(self.freeze.get())
