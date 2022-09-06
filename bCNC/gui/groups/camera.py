""" This file was created due to the refactoring of
    ProbePage.py

    Authors:
             @m1ch
"""

import tkinter as tk

from cnc import globCNC

from .. import cncribbon
from .. import utils
from globalConfig import icon as gicon

name = "CameraGroup"


# =============================================================================
# Camera Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, "Probe:Camera", app)
        self.grid3rows()

        self.switch = tk.BooleanVar()
        self.edge = tk.BooleanVar()
        self.freeze = tk.BooleanVar()

        # ---
        col, row = 0, 0
        self.switchButton = utils.LabelCheckbutton(
            self.frame,
            image=gicon["camera32"],
            text=_("Switch To"),
            compound="top",
            variable=self.switch,
            command=self.switchCommand,
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
            image=gicon["edge"],
            text=_("Edge Detection"),
            compound="left",
            variable=self.edge,
            command=self.edgeDetection,
        )
        b.grid(row=row, column=col, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Turn on/off edge detection"))

        # ---
        row += 1
        b = utils.LabelCheckbutton(
            self.frame,
            image=gicon["freeze"],
            text=_("Freeze"),
            compound="left",
            variable=self.freeze,
            command=self.freezeImage,
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
            self.switchButton.config(image=gicon["endmill32"])
            self.sendGCode(f"G92X{dx + wx:g}Y{dy + wy:g}")
            self.app.canvas.cameraSwitch = True
        else:
            self.switchButton.config(image=gicon["camera32"])
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
