""" This file was created due to the refactoring of
    ProbePage.py - ToolFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from .. import tkextra
from .. import utils
from cnc import globCNC
from gcode import globGCode
from sender import globSender


TOOL_POLICY = [
    _("Send M6 commands"),  # 0
    _("Ignore M6 commands"),  # 1
    _("Manual Tool Change (WCS)"),  # 2
    _("Manual Tool Change (TLO)"),  # 3
    _("Manual Tool Change (NoProbe)"),  # 4
]

TOOL_WAIT = [_("ONLY before probing"), _("BEFORE & AFTER probing")]


# =============================================================================
# Tool Frame
# =============================================================================
class SideFrame(utils.PageLabelFrame):
    def __init__(self, master, app):
        utils.PageLabelFrame.__init__(
            self, master, app, "Probe:Tool", _("Manual Tool Change"))

        # ---
        lframe = self.frame

        # --- Tool policy ---
        row, col = 0, 0
        ttk.Label(lframe, text=_("Policy:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.toolPolicy = ttk.Combobox(lframe, width=16)
        self.toolPolicy['state'] = 'readonly'
        self.toolPolicy['values'] = TOOL_POLICY
        self.toolPolicy.bind('<<ComboboxSelected>>', self.policyChange)
        self.toolPolicy['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # self.toolPolicy = tkextra.Combobox(
        #     lframe,
        #     True,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     command=self.policyChange,
        #     width=16,
        # )
        # self.toolPolicy.fill(TOOL_POLICY)
        self.toolPolicy.grid(row=row, column=col, columnspan=3, sticky="ew")
        self.toolPolicy.set(TOOL_POLICY[0])
        utils.ToolTip(self.toolPolicy, _("Tool change policy"))
        self.addWidget(self.toolPolicy)

        # ----
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Pause:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.toolWait = ttk.Combobox(lframe, width=16)
        self.toolWait['state'] = 'readonly'
        self.toolWait['values'] = TOOL_WAIT
        self.toolWait.bind('<<ComboboxSelected>>', self.waitChange)
        self.toolWait['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # self.toolWait = tkextra.Combobox(
        #     lframe,
        #     True,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     command=self.waitChange,
        #     width=16,
        # )
        # self.toolWait.fill(TOOL_WAIT)
        self.toolWait.grid(row=row, column=col, columnspan=3, sticky="ew")
        self.toolWait.set(TOOL_WAIT[1])
        self.addWidget(self.toolWait)

        # ----
        row += 1
        col = 1
        ttk.Label(lframe, text=_("MX")).grid(row=row, column=col, sticky="ew")
        col += 1
        ttk.Label(lframe, text=_("MY")).grid(row=row, column=col, sticky="ew")
        col += 1
        ttk.Label(lframe, text=_("MZ")).grid(row=row, column=col, sticky="ew")

        # --- Tool Change position ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Change:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.changeX = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.changeX.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.changeX, _("Manual tool change Machine X location"))
        self.addWidget(self.changeX)
        self.changeX.bind("<KeyRelease>", self.setProbeParams)
        self.changeX.bind("<FocusOut>", self.setProbeParams)

        col += 1
        self.changeY = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.changeY.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.changeY, _("Manual tool change Machine Y location"))
        self.addWidget(self.changeY)
        self.changeY.bind("<KeyRelease>", self.setProbeParams)
        self.changeY.bind("<FocusOut>", self.setProbeParams)

        col += 1
        self.changeZ = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.changeZ.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.changeZ, _("Manual tool change Machine Z location"))
        self.addWidget(self.changeZ)
        self.changeZ.bind("<KeyRelease>", self.setProbeParams)
        self.changeZ.bind("<FocusOut>", self.setProbeParams)

        col += 1
        b = ttk.Button(
            lframe, text=_("get"), command=self.getChange,
            # padx=2, pady=1
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            b, _("Get current gantry position as machine tool change location")
        )
        self.addWidget(b)

        # --- Tool Probe position ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Probe:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.probeX = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.probeX.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.probeX, _("Manual tool change Probing MX location"))
        self.addWidget(self.probeX)
        self.probeX.bind("<KeyRelease>", self.setProbeParams)
        self.probeX.bind("<FocusOut>", self.setProbeParams)

        col += 1
        self.probeY = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.probeY.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.probeY, _("Manual tool change Probing MY location"))
        self.addWidget(self.probeY)
        self.probeY.bind("<KeyRelease>", self.setProbeParams)
        self.probeY.bind("<FocusOut>", self.setProbeParams)

        col += 1
        self.probeZ = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.probeZ.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.probeZ, _("Manual tool change Probing MZ location"))
        self.addWidget(self.probeZ)
        self.probeZ.bind("<KeyRelease>", self.setProbeParams)
        self.probeZ.bind("<FocusOut>", self.setProbeParams)

        col += 1
        b = ttk.Button(lframe, text=_("get"),
                       command=self.getProbe,
                       #   padx=2, pady=1
                       )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            b, _("Get current gantry position as machine tool probe location")
        )
        self.addWidget(b)

        # --- Probe Distance ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Distance:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.probeDistance = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.probeDistance.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.probeDistance,
            _("After a tool change distance to scan starting from ProbeZ"),
        )
        self.addWidget(self.probeDistance)
        self.probeDistance.bind("<KeyRelease>", self.setProbeParams)
        self.probeDistance.bind("<FocusOut>", self.setProbeParams)

        # --- Calibration ---
        row += 1
        col = 0
        ttk.Label(lframe,
                  text=_("Calibration:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.toolHeight = tkextra.FloatEntry(
            lframe, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"), width=5
        )
        self.toolHeight.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.toolHeight, _("Tool probe height"))
        self.addWidget(self.toolHeight)

        col += 1
        b = ttk.Button(lframe,
                       text=_("Calibrate"),
                       command=self.calibrate,
                       #   padx=2,
                       #   pady=1
                       )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            b, _("Perform a calibration probing to determine the height")
        )
        self.addWidget(b)

        lframe.grid_columnconfigure(1, weight=1)
        lframe.grid_columnconfigure(2, weight=1)
        lframe.grid_columnconfigure(3, weight=1)

        self.loadConfig()

    # -----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr(
            "Probe", "toolpolicy",
            TOOL_POLICY.index(self.toolPolicy.get())
        )
        gconfig.setstr(
            "Probe", "toolwait",
            TOOL_WAIT.index(self.toolWait.get())
        )

        gconfig.setstr("Probe", "toolchangex", self.changeX.get())
        gconfig.setstr("Probe", "toolchangey", self.changeY.get())
        gconfig.setstr("Probe", "toolchangez", self.changeZ.get())

        gconfig.setstr("Probe", "toolprobex", self.probeX.get())
        gconfig.setstr("Probe", "toolprobey", self.probeY.get())
        gconfig.setstr("Probe", "toolprobez", self.probeZ.get())

        gconfig.setstr("Probe", "tooldistance", self.probeDistance.get())
        gconfig.setstr("Probe", "toolheight", self.toolHeight.get())
        gconfig.setstr("Probe", "toolmz", globCNC.vars.get("toolmz", 0.0))

    # -----------------------------------------------------------------------
    def loadConfig(self):
        self.changeX.set(gconfig.getfloat("Probe", "toolchangex"))
        self.changeY.set(gconfig.getfloat("Probe", "toolchangey"))
        self.changeZ.set(gconfig.getfloat("Probe", "toolchangez"))

        self.probeX.set(gconfig.getfloat("Probe", "toolprobex"))
        self.probeY.set(gconfig.getfloat("Probe", "toolprobey"))
        self.probeZ.set(gconfig.getfloat("Probe", "toolprobez"))

        self.probeDistance.set(gconfig.getfloat("Probe", "tooldistance"))
        self.toolHeight.set(gconfig.getfloat("Probe", "toolheight"))
        self.toolPolicy.set(
            TOOL_POLICY[gconfig.getint("Probe", "toolpolicy", 0)])
        self.toolWait.set(TOOL_WAIT[gconfig.getint("Probe", "toolwait", 1)])
        globCNC.vars["toolmz"] = gconfig.getfloat("Probe", "toolmz")
        self.set()

    # -----------------------------------------------------------------------
    def set(self):
        self.policyChange()
        self.waitChange()
        try:
            globCNC.vars["toolchangex"] = float(self.changeX.get())
            globCNC.vars["toolchangey"] = float(self.changeY.get())
            globCNC.vars["toolchangez"] = float(self.changeZ.get())
        except Exception:
            tk.messagebox.showerror(
                _("Probe Tool Change Error"),
                _("Invalid tool change position"),
                parent=self.winfo_toplevel(),
            )
            return

        try:
            globCNC.vars["toolprobex"] = float(self.probeX.get())
            globCNC.vars["toolprobey"] = float(self.probeY.get())
            globCNC.vars["toolprobez"] = float(self.probeZ.get())
        except Exception:
            tk.messagebox.showerror(
                _("Probe Tool Change Error"),
                _("Invalid tool probe location"),
                parent=self.winfo_toplevel(),
            )
            return

        try:
            globCNC.vars["tooldistance"] = abs(float(self.probeDistance.get()))
        except Exception:
            tk.messagebox.showerror(
                _("Probe Tool Change Error"),
                _("Invalid tool scanning distance entered"),
                parent=self.winfo_toplevel(),
            )
            return

        try:
            globCNC.vars["toolheight"] = float(self.toolHeight.get())
        except Exception:
            tk.messagebox.showerror(
                _("Probe Tool Change Error"),
                _("Invalid tool height or not calibrated"),
                parent=self.winfo_toplevel(),
            )
            return

    # -----------------------------------------------------------------------
    def check4Errors(self):
        if globCNC.vars["tooldistance"] <= 0.0:
            tk.messagebox.showerror(
                _("Probe Tool Change Error"),
                _("Invalid tool scanning distance entered"),
                parent=self.winfo_toplevel(),
            )
            return True
        return False

    # -----------------------------------------------------------------------
    def policyChange(self):
        b = self.toolPolicy.get()
        globCNC.toolPolicy = int(TOOL_POLICY.index(b))

    # -----------------------------------------------------------------------
    def waitChange(self):
        b = self.toolWait.get()
        globCNC.toolWaitAfterProbe = int(TOOL_WAIT.index(b))

    # -----------------------------------------------------------------------
    def setProbeParams(self, dummy=None):
        print("probe chg handler")
        globCNC.vars["toolchangex"] = float(self.changeX.get())
        globCNC.vars["toolchangey"] = float(self.changeY.get())
        globCNC.vars["toolchangez"] = float(self.changeZ.get())
        globCNC.vars["toolprobex"] = float(self.probeX.get())
        globCNC.vars["toolprobey"] = float(self.probeY.get())
        globCNC.vars["toolprobez"] = float(self.probeZ.get())
        globCNC.vars["tooldistance"] = float(self.probeDistance.get())

    # -----------------------------------------------------------------------
    def getChange(self):
        self.changeX.set(globCNC.vars["mx"])
        self.changeY.set(globCNC.vars["my"])
        self.changeZ.set(globCNC.vars["mz"])
        self.setProbeParams()

    # -----------------------------------------------------------------------
    def getProbe(self):
        self.probeX.set(globCNC.vars["mx"])
        self.probeY.set(globCNC.vars["my"])
        self.probeZ.set(globCNC.vars["mz"])
        self.setProbeParams()

    # -----------------------------------------------------------------------
    def updateTool(self):
        state = self.toolHeight.cget("state")
        self.toolHeight.config(state="normal")
        self.toolHeight.set(globCNC.vars["toolheight"])
        self.toolHeight.config(state=state)

    # -----------------------------------------------------------------------
    def calibrate(self, event=None):
        self.set()
        if self.check4Errors():
            return
        lines = []
        lines.append("g53 g0 z[toolchangez]")
        lines.append("g53 g0 x[toolchangex] y[toolchangey]")
        lines.append("g53 g0 x[toolprobex] y[toolprobey]")
        lines.append("g53 g0 z[toolprobez]")
        if globCNC.vars["fastprbfeed"]:
            prb_reverse = {"2": "4", "3": "5", "4": "2", "5": "3"}
            globCNC.vars["prbcmdreverse"] = (
                globCNC.vars["prbcmd"][:-1] + prb_reverse[globCNC.vars["prbcmd"][-1]]
            )
            currentFeedrate = globCNC.vars["fastprbfeed"]
            while currentFeedrate > globCNC.vars["prbfeed"]:
                lines.append("%wait")
                lines.append(
                    f"g91 [prbcmd] {globCNC.fmt('f', currentFeedrate)} "
                    + "z[toolprobez-mz-tooldistance]"
                )
                lines.append("%wait")
                lines.append(
                    f"[prbcmdreverse] {globCNC.fmt('f', currentFeedrate)} "
                    + "z[toolprobez-mz]"
                )
                currentFeedrate /= 10
        lines.append("%wait")
        lines.append("g91 [prbcmd] f[prbfeed] z[toolprobez-mz-tooldistance]")
        lines.append("g4 p1")  # wait a sec
        lines.append("%wait")
        lines.append("%global toolheight; toolheight=wz")
        lines.append("%global toolmz; toolmz=prbz")
        lines.append("%update toolheight")
        lines.append("g53 g0 z[toolchangez]")
        lines.append("g53 g0 x[toolchangex] y[toolchangey]")
        lines.append("g90")
        self.app.run(lines=lines)

    # -----------------------------------------------------------------------
    # FIXME: Should be replaced with globCNC.toolChange()
    # -----------------------------------------------------------------------
    def change(self, event=None):
        self.set()
        if self.check4Errors():
            return
        lines = self.app.cnc.toolChange(0)
        self.app.run(lines=lines)
