""" This file was created due to the refactoring of
    ProbePage.py - CameraFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from cnc import globCNC
from gcode import globGCode
from sender import globSender

from .. import cncribbon
from .. import tkextra
from .. import utils

CAMERA_LOCATION = {
    "Gantry": "none",
    "Top-Left": "nw",
    "Top": "n",
    "Top-Right": "ne",
    "Left": "w",
    "Center": "center",
    "Right": "e",
    "Bottom-Left": "sw",
    "Bottom": "s",
    "Bottom-Right": "se",
}
CAMERA_LOCATION_ORDER = [
    "Gantry",
    "Top-Left",
    "Top",
    "Top-Right",
    "Left",
    "Center",
    "Right",
    "Bottom-Left",
    "Bottom",
    "Bottom-Right",
]


# =============================================================================
# Camera Frame
# =============================================================================
class SideFrame(utils.PageLabelFrame):
    def __init__(self, master, app):
        utils.PageLabelFrame.__init__(
            self, master, app, "Probe:Camera", _("Camera"))

        # ---
        lframe = self.frame

        # ----
        row = 0
        ttk.Label(lframe, text=_("Location:")).grid(
            row=row, column=0, sticky="e")
        self.location = ttk.Combobox(lframe, width=16)
        self.location['state'] = 'readonly'
        self.location['values'] = CAMERA_LOCATION_ORDER
        self.location['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # self.location = tkextra.Combobox(
        #     lframe, True,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     width=16
        # )
        # self.location.fill(CAMERA_LOCATION_ORDER)
        self.location.set(CAMERA_LOCATION_ORDER[0])
        self.location.grid(row=row, column=1, columnspan=3, sticky="ew")
        utils.ToolTip(self.location, _("Camera location inside canvas"))

        # ----
        row += 1
        ttk.Label(lframe, text=_("Rotation:")).grid(
            row=row, column=0, sticky="e")
        self.rotation = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.rotation.grid(row=row, column=1, sticky="ew")
        self.rotation.bind("<Return>", self.updateValues)
        self.rotation.bind("<KP_Enter>", self.updateValues)
        self.rotation.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.rotation, _("Camera rotation [degrees]"))
        # ----
        row += 1
        ttk.Label(
            lframe,
            text=_("Haircross Offset:")
        ).grid(row=row, column=0, sticky="e")
        self.xcenter = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.xcenter.grid(row=row, column=1, sticky="ew")
        self.xcenter.bind("<Return>", self.updateValues)
        self.xcenter.bind("<KP_Enter>", self.updateValues)
        self.xcenter.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.xcenter, _("Haircross X offset [unit]"))

        self.ycenter = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.ycenter.grid(row=row, column=2, sticky="ew")
        self.ycenter.bind("<Return>", self.updateValues)
        self.ycenter.bind("<KP_Enter>", self.updateValues)
        self.ycenter.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.ycenter, _("Haircross Y offset [unit]"))
        # ----

        row += 1
        ttk.Label(lframe, text=_("Scale:")).grid(row=row, column=0, sticky="e")
        self.scale = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.scale.grid(row=row, column=1, sticky="ew")
        self.scale.bind("<Return>", self.updateValues)
        self.scale.bind("<KP_Enter>", self.updateValues)
        self.scale.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.scale, _("Camera scale [pixels / unit]"))

        # ----
        row += 1
        ttk.Label(lframe, text=_("Crosshair:")).grid(
            row=row, column=0, sticky="e")
        self.diameter = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.diameter.grid(row=row, column=1, sticky="ew")
        self.diameter.bind("<Return>", self.updateValues)
        self.diameter.bind("<KP_Enter>", self.updateValues)
        self.diameter.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(
            self.diameter, _("Camera cross hair diameter [units]"))

        b = ttk.Button(
            lframe, text=_("Get"), command=self.getDiameter,
            # padx=1, pady=1
            )
        b.grid(row=row, column=2, sticky="w")
        utils.ToolTip(b, _("Get diameter from active endmill"))

        # ----
        row += 1
        ttk.Label(lframe, text=_("Offset:")).grid(row=row, column=0, sticky="e")
        self.dx = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.dx.grid(row=row, column=1, sticky="ew")
        self.dx.bind("<Return>", self.updateValues)
        self.dx.bind("<KP_Enter>", self.updateValues)
        self.dx.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.dx, _("Camera offset from gantry"))

        self.dy = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.dy.grid(row=row, column=2, sticky="ew")
        self.dy.bind("<Return>", self.updateValues)
        self.dy.bind("<KP_Enter>", self.updateValues)
        self.dy.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(self.dy, _("Camera offset from gantry"))

        self.z = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.z.grid(row=row, column=3, sticky="ew")
        self.z.bind("<Return>", self.updateValues)
        self.z.bind("<KP_Enter>", self.updateValues)
        self.z.bind("<FocusOut>", self.updateValues)
        utils.ToolTip(
            self.z, _("Spindle Z position when camera was registered"))

        row += 1
        ttk.Label(lframe, text=_("Register:")).grid(
            row=row, column=0, sticky="e")
        b = ttk.Button(
            lframe,
            text=_("1. Spindle"),
            command=self.registerSpindle,
            # padx=1,
            # pady=1
        )
        utils.ToolTip(
            b, _("Mark spindle position for calculating offset"))
        b.grid(row=row, column=1, sticky="ew")
        b = ttk.Button(
            lframe, text=_("2. Camera"),
            command=self.registerCamera,
            # padx=1, pady=1
        )
        utils.ToolTip(
            b, _("Mark camera position for calculating offset"))
        b.grid(row=row, column=2, sticky="ew")

        lframe.grid_columnconfigure(1, weight=1)
        lframe.grid_columnconfigure(2, weight=1)
        lframe.grid_columnconfigure(3, weight=1)

        self.loadConfig()
        # self.location.config(command=self.updateValues)
        self.location.bind('<<ComboboxSelected>>', self.updateValues)
        self.spindleX = None
        self.spindleY = None

    # -----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr("Camera", "aligncam_anchor", self.location.get())
        gconfig.setstr("Camera", "aligncam_d", self.diameter.get())
        gconfig.setstr("Camera", "aligncam_scale", self.scale.get())
        gconfig.setstr("Camera", "aligncam_dx", self.dx.get())
        gconfig.setstr("Camera", "aligncam_dy", self.dy.get())
        gconfig.setstr("Camera", "aligncam_z", self.z.get())
        gconfig.setstr("Camera", "aligncam_rotation", self.rotation.get())
        gconfig.setstr("Camera", "aligncam_xcenter", self.xcenter.get())
        gconfig.setstr("Camera", "aligncam_ycenter", self.ycenter.get())

    # -----------------------------------------------------------------------
    def loadConfig(self):
        self.location.set(gconfig.getstr("Camera", "aligncam_anchor"))
        self.diameter.set(gconfig.getfloat("Camera", "aligncam_d"))
        self.scale.set(gconfig.getfloat("Camera", "aligncam_scale"))
        self.dx.set(gconfig.getfloat("Camera", "aligncam_dx"))
        self.dy.set(gconfig.getfloat("Camera", "aligncam_dy"))
        self.z.set(gconfig.getfloat("Camera", "aligncam_z", ""))
        self.rotation.set(gconfig.getfloat("Camera", "aligncam_rotation"))
        self.xcenter.set(gconfig.getfloat("Camera", "aligncam_xcenter"))
        self.ycenter.set(gconfig.getfloat("Camera", "aligncam_ycenter"))
        self.updateValues()

    # -----------------------------------------------------------------------
    # Return camera Anchor
    # -----------------------------------------------------------------------
    def cameraAnchor(self):
        return CAMERA_LOCATION.get(self.location.get(), "center")

    # -----------------------------------------------------------------------
    def getDiameter(self):
        self.diameter.set(globCNC.vars["diameter"])
        self.updateValues()

    # -----------------------------------------------------------------------
    # Update canvas with values
    # -----------------------------------------------------------------------
    def updateValues(self, *args):
        self.app.canvas.cameraAnchor = self.cameraAnchor()
        try:
            self.app.canvas.cameraRotation = float(self.rotation.get())
        except ValueError:
            pass
        try:
            self.app.canvas.cameraXCenter = float(self.xcenter.get())
        except ValueError:
            pass
        try:
            self.app.canvas.cameraYCenter = float(self.ycenter.get())
        except ValueError:
            pass
        try:
            self.app.canvas.cameraScale = max(0.0001, float(self.scale.get()))
        except ValueError:
            pass
        try:
            self.app.canvas.cameraR = float(self.diameter.get()) / 2.0
        except ValueError:
            pass
        try:
            self.app.canvas.cameraDx = float(self.dx.get())
        except ValueError:
            pass
        try:
            self.app.canvas.cameraDy = float(self.dy.get())
        except ValueError:
            pass
        try:
            self.app.canvas.cameraZ = float(self.z.get())
        except ValueError:
            self.app.canvas.cameraZ = None
        self.app.canvas.cameraUpdate()

    # -----------------------------------------------------------------------
    # Register spindle position
    # -----------------------------------------------------------------------
    def registerSpindle(self):
        self.spindleX = globCNC.vars["wx"]
        self.spindleY = globCNC.vars["wy"]
        self.event_generate(
            "<<Status>>", data=_("Spindle position is registered"))

    # -----------------------------------------------------------------------
    # Register camera position
    # -----------------------------------------------------------------------
    def registerCamera(self):
        if self.spindleX is None:
            tk.messagebox.showwarning(
                _("Spindle position is not registered"),
                _("Spindle position must be registered before camera"),
                parent=self,
            )
            return
        self.dx.set(str(self.spindleX - globCNC.vars["wx"]))
        self.dy.set(str(self.spindleY - globCNC.vars["wy"]))
        self.z.set(str(globCNC.vars["wz"]))
        self.event_generate("<<Status>>", data=_("Camera offset is updated"))
        self.updateValues()
