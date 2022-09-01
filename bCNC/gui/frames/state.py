""" This file was created due to the refactoring of
    ControlPage.py - StateFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

import Utils
from .. import tkextra
from globalConfig import config as gconfig
from cnc import globCNC
from sender import globSender, NOT_CONNECTED, CONNECTED

from cnc import DISTANCE_MODE, FEED_MODE, PLANE, WCS

from .. import utils


OVERRIDES = ["Feed", "Rapid", "Spindle"]

# override for init
UNITS = {"G20": "inch", "G21": "mm"}


name = "StateFrame"


# =============================================================================
# StateFrame
# =============================================================================
class SideFrame(utils.CollapsiblePageLabelFrame):
    def __init__(self, master, app):
        # global wcsvar
        utils.CollapsiblePageLabelFrame.__init__(
            self, master, app, name="State", text=_("State"))
        self._gUpdate = False
        self._wcsvar = tk.IntVar(self, value=0)

        # State
        f = ttk.Frame(self.frame)
        f.pack(side="top", fill="x")

        # ===
        col, row = 0, 0
        f2 = ttk.Frame(f)
        f2.grid(row=row, column=col, columnspan=5, sticky="ew")
        for p, w in enumerate(WCS):
            col += 1
            b = ttk.Radiobutton(
                f2,
                text=w,
                variable=self._wcsvar,
                value=p,
                command=self.wcsChange,
                style="Workspaces.Panel.TButton",
                # foreground="DarkRed",
                # font="Helvetica,14",
                # padx=1,
                # pady=1,
                # # variable=wcsvar,
                # indicatoron=False,
                # activebackground="LightYellow",
            )
            b.pack(side="left", fill="x", expand=True)
            utils.ToolTip(b, _("Switch to workspace {}").format(w))
            self.addWidget(b)

        # Absolute or relative mode
        row += 1
        col = 0
        ttk.Label(f, text=_("Distance:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.distance = ttk.Combobox(f, width=5)
        self.distance['values'] = sorted(DISTANCE_MODE.values())
        self.distance['state'] = 'readonly'
        self.distance.bind('<<ComboboxSelected>>', self.distanceChange)

        # self.distance = tkextra.Combobox(
        #     f,
        #     True,
        #     command=self.distanceChange,
        #     width=5,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        # )
        # self.distance.fill(sorted(DISTANCE_MODE.values()))
        self.distance.grid(row=row, column=col, columnspan=2, sticky="ew")
        utils.ToolTip(self.distance, _("Distance Mode [G90,G91]"))
        self.addWidget(self.distance)

        # populate gstate dictionary
        self.gstate = {}  # $G state results widget dictionary
        for k, v in DISTANCE_MODE.items():
            self.gstate[k] = (self.distance, v)

        # Units mode
        col += 2
        ttk.Label(f, text=_("Units:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.units = ttk.Combobox(f, width=5)
        self.units['values'] = sorted(UNITS.values())
        self.units['state'] = 'readonly'
        self.units.bind('<<ComboboxSelected>>', self.unitsChange)
        # self.units = tkextra.Combobox(
        #     f,
        #     True,
        #     command=self.unitsChange,
        #     width=5,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        # )
        # self.units.fill(sorted(UNITS.values()))
        self.units.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.units, _("Units [G20, G21]"))
        for k, v in UNITS.items():
            self.gstate[k] = (self.units, v)
        self.addWidget(self.units)

        # Tool
        row += 1
        col = 0
        ttk.Label(f, text=_("Tool:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.toolEntry = tkextra.IntegerEntry(
            f,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.toolEntry.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.toolEntry, _("Tool number [T#]"))
        self.addWidget(self.toolEntry)

        col += 1
        b = ttk.Button(f, text=_("set"), command=self.setTool,
                       #    padx=1, pady=1
                       )
        b.grid(row=row, column=col, sticky="w")
        self.addWidget(b)

        # Plane
        col += 1
        ttk.Label(f, text=_("Plane:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.plane = ttk.Combobox(f, width=5)
        self.plane['values'] = sorted(PLANE.values())
        self.plane['state'] = 'readonly'
        self.plane.bind('<<ComboboxSelected>>', self.planeChange)
        # self.plane = tkextra.Combobox(
        #     f,
        #     True,
        #     command=self.planeChange,
        #     width=5,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        # )
        # self.plane.fill(sorted(PLANE.values()))
        self.plane.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.plane, _("Plane [G17,G18,G19]"))
        self.addWidget(self.plane)

        for k, v in PLANE.items():
            self.gstate[k] = (self.plane, v)

        # Feed speed
        row += 1
        col = 0
        ttk.Label(f, text=_("Feed:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.feedRate = tkextra.FloatEntry(
            f,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            # disabledforeground="Black",
            width=5,
        )
        self.feedRate.grid(row=row, column=col, sticky="ew")
        self.feedRate.bind("<Return>", self.setFeedRate)
        self.feedRate.bind("<KP_Enter>", self.setFeedRate)
        utils.ToolTip(self.feedRate, _("Feed Rate [F#]"))
        self.addWidget(self.feedRate)

        col += 1
        b = ttk.Button(f, text=_("set"),
                       command=self.setFeedRate,
                       #   padx=1, pady=1
                       )
        b.grid(row=row, column=col, columnspan=2, sticky="w")
        self.addWidget(b)

        # Feed mode
        col += 1
        ttk.Label(f, text=_("Mode:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.feedMode = ttk.Combobox(f, width=5)
        self.feedMode['values'] = sorted(FEED_MODE.values())
        self.feedMode['state'] = 'readonly'
        self.feedMode.bind('<<ComboboxSelected>>', self.feedModeChange)
        # self.feedMode = tkextra.Combobox(
        #     f,
        #     True,
        #     command=self.feedModeChange,
        #     width=5,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        # )
        # self.feedMode.fill(sorted(FEED_MODE.values()))
        self.feedMode.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.feedMode, _("Feed Mode [G93, G94, G95]"))
        for k, v in FEED_MODE.items():
            self.gstate[k] = (self.feedMode, v)
        self.addWidget(self.feedMode)

        # TLO
        row += 1
        col = 0
        ttk.Label(f, text=_("TLO:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.tlo = tkextra.FloatEntry(
            f,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            # disabledforeground="Black",
            width=5,
        )
        self.tlo.grid(row=row, column=col, sticky="ew")
        self.tlo.bind("<Return>", self.setTLO)
        self.tlo.bind("<KP_Enter>", self.setTLO)
        utils.ToolTip(self.tlo, _("Tool length offset [G43.1#]"))
        self.addWidget(self.tlo)

        col += 1
        b = ttk.Button(f, text=_("set"), command=self.setTLO,
                       #    padx=1, pady=1
                       )
        b.grid(row=row, column=col, columnspan=2, sticky="w")
        self.addWidget(b)

        # g92
        col += 1
        ttk.Label(f, text=_("G92:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.g92 = ttk.Label(f, text="")
        self.g92.grid(row=row, column=col, columnspan=3, sticky="ew")
        utils.ToolTip(self.g92, _("Set position [G92 X# Y# Z#]"))
        self.addWidget(self.g92)

        # ---
        f.grid_columnconfigure(1, weight=1)
        f.grid_columnconfigure(4, weight=1)

        # Spindle
        f = ttk.Frame(self.frame)
        f.pack(side="bottom", fill="x")

        self.override = tk.IntVar()
        self.override.set(100)
        self.spindle = tk.BooleanVar()
        self.spindleSpeed = tk.IntVar()

        col, row = 0, 0
        self.overrideCombo = ttk.Combobox(f, width=8)
        self.overrideCombo['values'] = OVERRIDES
        self.overrideCombo['state'] = 'readonly'
        self.overrideCombo.bind('<<ComboboxSelected>>',
                                self.overrideComboChange)
        # self.overrideCombo = tkextra.Combobox(
        #     f, width=8, command=self.overrideComboChange
        # )
        # self.overrideCombo.fill(OVERRIDES)
        self.overrideCombo.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(self.overrideCombo, _("Select override type."))

        b = ttk.Button(f, text=_("Reset"),
                       #    pady=0,
                       command=self.resetOverride)
        b.grid(row=row + 1, column=col, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Reset override to 100%"))

        col += 1
        self.overrideScale = ttk.Scale(
            f,
            command=self.overrideChange,
            variable=self.override,
            # showvalue=True,
            orient="horizontal",
            from_=25,
            to_=200,
            # resolution=1,
        )
        self.overrideScale.bind("<Double-1>", self.resetOverride)
        self.overrideScale.bind("<Button-3>", self.resetOverride)
        self.overrideScale.grid(
            row=row, column=col, rowspan=2, columnspan=4, sticky="ew")
        utils.ToolTip(
            self.overrideScale,
            _("Set Feed/Rapid/Spindle Override. "
              + "Right or Double click to reset."),
        )

        self.overrideCombo.set(OVERRIDES[0])

        # ---
        row += 2
        col = 0
        b = ttk.Checkbutton(
            f,
            text=_("Spindle"),
            image=Utils.icons["spinningtop"],
            command=self.spindleControl,
            variable=self.spindle,
            style="Panel.TCheckbutton",
            # compound="left",
            # indicatoron=False,
            # padx=1,
            # pady=0,
        )
        utils.ToolTip(b, _("Start/Stop spindle (M3/M5)"))
        b.grid(row=row, column=col, pady=0, sticky="nsew")
        self.addWidget(b)

        col += 1
        b = ttk.Scale(
            f,
            variable=self.spindleSpeed,
            command=self.spindleControl,
            # showvalue=True,
            orient="horizontal",
            from_=gconfig.get("CNC", "spindlemin"),
            to_=gconfig.get("CNC", "spindlemax"),
        )
        utils.ToolTip(b, _("Set spindle RPM"))
        b.grid(row=row, column=col, sticky="ew", columnspan=3)
        self.addWidget(b)

        f.grid_columnconfigure(1, weight=1)

        # Coolant control

        self.coolant = tk.BooleanVar()
        self.mist = tk.BooleanVar()
        self.flood = tk.BooleanVar()

        row += 1
        col = 0
        ttk.Label(f, text=_("Coolant:")).grid(row=row, column=col, sticky="e")
        col += 1

        coolantDisable = ttk.Checkbutton(
            f,
            text=_("OFF"),
            command=self.coolantOff,
            variable=self.coolant,
            style="Panel.TCheckbutton",
            # indicatoron=False,
            # padx=1,
            # pady=0,
        )
        utils.ToolTip(coolantDisable, _("Stop cooling (M9)"))
        coolantDisable.grid(row=row, column=col, pady=0, sticky="nsew")
        self.addWidget(coolantDisable)

        col += 1
        floodEnable = ttk.Checkbutton(
            f,
            text=_("Flood"),
            command=self.coolantFlood,
            # indicatoron=False,
            variable=self.flood,
            style="Panel.TCheckbutton",
            # padx=1,
            # pady=0,
        )
        utils.ToolTip(floodEnable, _("Start flood (M8)"))
        floodEnable.grid(row=row, column=col, pady=0, sticky="nsew")
        self.addWidget(floodEnable)

        col += 1
        mistEnable = ttk.Checkbutton(
            f,
            text=_("Mist"),
            command=self.coolantMist,
            # indicatoron=False,
            variable=self.mist,
            style="Panel.TCheckbutton",
            # padx=1,
            # pady=0,
        )
        utils.ToolTip(mistEnable, _("Start mist (M7)"))
        mistEnable.grid(row=row, column=col, pady=0, sticky="nsew")
        self.addWidget(mistEnable)
        f.grid_columnconfigure(1, weight=1)

    # ----------------------------------------------------------------------
    def overrideChange(self, event=None):
        n = self.overrideCombo.get()
        c = self.override.get()
        globCNC.vars["_Ov" + n] = c
        globCNC.vars["_OvChanged"] = True

    # ----------------------------------------------------------------------
    def resetOverride(self, event=None):
        self.override.set(100)
        self.overrideChange()

    # ----------------------------------------------------------------------
    def overrideComboChange(self, event=None):
        n = self.overrideCombo.get()
        if n == "Rapid":
            self.overrideScale.config(to_=100)  # , resolution=25)
        else:
            self.overrideScale.config(to_=200)  # , resolution=1)
        self.override.set(globCNC.vars["_Ov" + n])

    # ----------------------------------------------------------------------
    def _gChange(self, value, dictionary):
        for k, v in dictionary.items():
            if v == value:
                self.sendGCode(k)
                return

    # ----------------------------------------------------------------------
    def distanceChange(self, event=None):
        if self._gUpdate:
            return
        self._gChange(self.distance.get(), DISTANCE_MODE)

    # ----------------------------------------------------------------------
    def unitsChange(self, event=None):
        if self._gUpdate:
            return
        self._gChange(self.units.get(), UNITS)

    # ----------------------------------------------------------------------
    def feedModeChange(self, event=None):
        if self._gUpdate:
            return
        self._gChange(self.feedMode.get(), FEED_MODE)

    # ----------------------------------------------------------------------
    def planeChange(self, event=None):
        if self._gUpdate:
            return
        self._gChange(self.plane.get(), PLANE)

    # ----------------------------------------------------------------------
    def setFeedRate(self, event=None):
        if self._gUpdate:
            return
        try:
            feed = float(self.feedRate.get())
            self.sendGCode(f"F{feed:g}")
            self.event_generate("<<CanvasFocus>>")
        except ValueError:
            pass

    # ----------------------------------------------------------------------
    def setTLO(self, event=None):
        try:
            tlo = float(self.tlo.get())
            self.sendGCode(f"G43.1Z{tlo:g}")
            globSender.mcontrol.viewParameters()
            self.event_generate("<<CanvasFocus>>")
        except ValueError:
            pass

    # ----------------------------------------------------------------------
    def setTool(self, event=None):
        pass

    # ----------------------------------------------------------------------
    def spindleControl(self, event=None):
        if self._gUpdate:
            return
        # Avoid sending commands before unlocking
        if globCNC.vars["state"] in (CONNECTED,
                                     NOT_CONNECTED):
            return
        if self.spindle.get():
            self.sendGCode("M3 S%d" % (self.spindleSpeed.get()))
        else:
            self.sendGCode("M5")

    # ----------------------------------------------------------------------
    def coolantMist(self, event=None):
        if self._gUpdate:
            return
        # Avoid sending commands before unlocking
        if globCNC.vars["state"] in (CONNECTED,
                                     NOT_CONNECTED):
            self.mist.set(False)
            return
        self.coolant.set(False)
        self.mist.set(True)
        self.sendGCode("M7")

    # ----------------------------------------------------------------------
    def coolantFlood(self, event=None):
        if self._gUpdate:
            return
        # Avoid sending commands before unlocking
        if globCNC.vars["state"] in (CONNECTED,
                                     NOT_CONNECTED):
            self.flood.set(False)
            return
        self.coolant.set(False)
        self.flood.set(True)
        self.sendGCode("M8")

    # ----------------------------------------------------------------------
    def coolantOff(self, event=None):
        if self._gUpdate:
            return
        # Avoid sending commands before unlocking
        if globCNC.vars["state"] in (CONNECTED,
                                     NOT_CONNECTED):
            self.coolant.set(False)
            return
        self.flood.set(False)
        self.mist.set(False)
        self.coolant.set(True)
        self.sendGCode("M9")

    # ----------------------------------------------------------------------
    def updateG(self):
        # FIXME: Never called
        # global wcsvar
        self._gUpdate = True

        try:
            # wcsvar.set(WCS.index(globCNC.vars["WCS"]))
            self._wcsvar.set(WCS.index(globCNC.vars["WCS"]))
            self.feedRate.set(str(globCNC.vars["feed"]))
            self.feedMode.set(FEED_MODE[globCNC.vars["feedmode"]])
            self.spindle.set(globCNC.vars["spindle"] == "M3")
            self.spindleSpeed.set(int(globCNC.vars["rpm"]))
            self.toolEntry.set(globCNC.vars["tool"])
            self.units.set(UNITS[globCNC.vars["units"]])
            self.distance.set(DISTANCE_MODE[globCNC.vars["distance"]])
            self.plane.set(PLANE[globCNC.vars["plane"]])
            self.tlo.set(str(globCNC.vars["TLO"]))
            self.g92.config(text=str(globCNC.vars["G92"]))
        except KeyError:
            pass

        self._gUpdate = False

    # ----------------------------------------------------------------------
    def updateFeed(self):
        if self.feedRate.cget("state") == "disabled":
            self.feedRate.config(state="normal")
            self.feedRate.delete(0, "end")
            self.feedRate.insert(0, globCNC.vars["curfeed"])
            self.feedRate.config(state="disabled")

    # ----------------------------------------------------------------------
    def wcsChange(self):
        # global wcsvar
        self.sendGCode(WCS[self._wcsvar.get()])
        # self.sendGCode(WCS[wcsvar.get()])
        globSender.mcontrol.viewState()
