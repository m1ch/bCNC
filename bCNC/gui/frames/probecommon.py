""" This file was created due to the refactoring of
    ProbePage.py - ProbeCommonFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from .. import cncribbon
from .. import tkextra
from .. import utils
# from globalConstants import __author__, __email__
from cnc import globCNC
from gcode import globGCode
from sender import globSender


PROBE_CMD = [
    _("G38.2 stop on contact else error"),
    _("G38.3 stop on contact"),
    _("G38.4 stop on loss contact else error"),
    _("G38.5 stop on loss contact"),
]


# =============================================================================
# Probe Common Offset
# =============================================================================
class SideFrame(cncribbon.PageFrame):
    probeFeed = None
    tlo = None
    probeCmd = None

    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, "ProbeCommon", app)

        # lframe = tkextra.ExLabelFrame(
        #     self, text=_("Common"), style='Panel.TLabelFrame.Label'
        # )
        # lframe.pack(side="top", fill="x")
        # frame = lframe.frame
        lframe = utils.CollapsiblePageLabelFrame(
            self, app, name="Common", text=_("Common"))
        lframe.pack(side="top", expand=True, fill="x")
        frame = lframe.frame

        # ----
        row = 0
        col = 0

        # ----
        # Fast Probe Feed
        ttk.Label(
            frame,
            text=_("Fast Probe Feed:")
        ).grid(row=row, column=col, sticky="e")
        col += 1
        # FIXME: Add validate funktion from
        #        https://www.pythontutorial.net/tkinter/tkinter-validation/
        self.fastProbeFeed = tk.StringVar()
        self.fastProbeFeed.trace("w", self.probeUpdate)
        self.fastProbeFeedW = ttk.Entry(frame,
                                        width=5,
                                        textvariable=self.fastProbeFeed)
        # "w", lambda *_: SideFrame.probeUpdate())
        # SideFrame.fastProbeFeed = tkextra.FloatEntry(
        #     frame,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     width=5,
        #     textvariable=self.fastProbeFeed,
        # )
        # SideFrame.fastProbeFeed.grid(row=row, column=col, sticky="ew")
        self.fastProbeFeedW.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            self.fastProbeFeedW,
            _("Set initial probe feed rate for tool change and calibration"),
        )
        self.addWidget(self.fastProbeFeedW)

        # ----
        # Probe Feed
        row += 1
        col = 0
        ttk.Label(frame, text=_("Probe Feed:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.probeFeedVar = tk.StringVar()
        self.probeFeedVar.trace("w", self.probeUpdate)
        # self.probeFeedVar.trace("w", lambda *_: SideFrame.probeUpdate())
        SideFrame.probeFeed = tkextra.FloatEntry(
            frame,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5,
            textvariable=self.probeFeedVar,
        )
        SideFrame.probeFeed.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            SideFrame.probeFeed, _("Set probe feed rate"))
        self.addWidget(SideFrame.probeFeed)

        # ----
        # Tool offset
        row += 1
        col = 0
        ttk.Label(frame, text=_("TLO")).grid(row=row, column=col, sticky="e")
        col += 1
        SideFrame.tlo = tkextra.FloatEntry(
            frame, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        SideFrame.tlo.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(
            SideFrame.tlo, _("Set tool offset for probing"))
        self.addWidget(SideFrame.tlo)
        self.tlo.bind("<Return>", self.tloSet)
        self.tlo.bind("<KP_Enter>", self.tloSet)

        col += 1
        b = ttk.Button(frame, text=_("set"),
                       command=self.tloSet,
                       #   padx=2, pady=1
                       )
        b.grid(row=row, column=col, sticky="ew")
        self.addWidget(b)

        # ---
        # feed command
        row += 1
        col = 0
        ttk.Label(frame,
                  text=_("Probe Command")).grid(
                      row=row, column=col, sticky="e")
        col += 1
        self.probeCmd = ttk.Combobox(frame, width=16)
        self.probeCmd['state'] = 'readonly'
        self.probeCmd['values'] = PROBE_CMD
        self.probeCmd.bind('<<ComboboxSelected>>', self.probeUpdate)
        self.probeCmd['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # SideFrame.probeCmd = tkextra.Combobox(
        #     frame,
        #     True,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     width=16,
        #     command=SideFrame.probeUpdate,
        # )
        # SideFrame.probeCmd.fill(PROBE_CMD)
        self.probeCmd.grid(row=row, column=col, sticky="ew")
        self.addWidget(self.probeCmd)

        frame.grid_columnconfigure(1, weight=1)
        self.loadConfig()

    # ------------------------------------------------------------------------
    def tloSet(self, event=None):
        try:
            globCNC.vars["TLO"] = float(SideFrame.tlo.get())
            cmd = f"G43.1Z{SideFrame.tlo.get()}"
            self.sendGCode(cmd)
        except Exception:
            pass
        globSender.mcontrol.viewParameters()

    # ------------------------------------------------------------------------
    def probeUpdate(self, *args, **kw):
        try:
            globCNC.vars["fastprbfeed"] = float(
                self.fastProbeFeed.get())
            # SideFrame.fastProbeFeed.get())
            globCNC.vars["prbfeed"] = float(SideFrame.probeFeed.get())
            globCNC.vars["prbcmd"] = str(
                self.probeCmd.get().split()[0])
            return False
        except Exception:
            return True

    # ------------------------------------------------------------------------
    def updateTlo(self):
        try:
            if self.focus_get() is not SideFrame.tlo:
                state = SideFrame.tlo.cget("state")
                state = SideFrame.tlo["state"] = "normal"
                SideFrame.tlo.set(str(globCNC.vars.get("TLO", "")))
                state = SideFrame.tlo["state"] = state
        except Exception:
            pass

    # -----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr("Probe",
                       "fastfeed", self.fastProbeFeed.get())
        #    "fastfeed", SideFrame.fastProbeFeed.get())
        gconfig.setstr("Probe", "feed", SideFrame.probeFeed.get())
        gconfig.setstr("Probe", "tlo", SideFrame.tlo.get())
        gconfig.setstr("Probe", "cmd",
                       self.probeCmd.get().split()[0])

    # -----------------------------------------------------------------------
    def loadConfig(self):
        # SideFrame.fastProbeFeed.set(gconfig.getfloat("Probe",
        self.fastProbeFeed.set(gconfig.getfloat("Probe",
                                                "fastfeed"))
        SideFrame.probeFeed.set(gconfig.getfloat("Probe", "feed"))
        SideFrame.tlo.set(gconfig.getfloat("Probe", "tlo"))
        cmd = gconfig.getstr("Probe", "cmd")
        for p in PROBE_CMD:
            if p.split()[0] == cmd:
                self.probeCmd.set(p)
                break
