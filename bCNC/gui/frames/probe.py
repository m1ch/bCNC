""" This file was created due to the refactoring of
    ProbePage.py - ProbeFrame

    Authors:
             @m1ch
"""

import math
import sys

import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from .. import cncribbon
from .. import tkextra
import Utils
from .. import utils
from cnc import globCNC
from gcode import globGCode
from sender import globSender

from cnc import Block

from .probecommon import SideFrame as ProbeCommonFrame


# =============================================================================
# Probe Frame
# =============================================================================
class SideFrame(cncribbon.PageFrame):
    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, "Probe:Probe", app)

        # ----------------------------------------------------------------
        # Record point
        # ----------------------------------------------------------------

        # recframe = tkextra.ExLabelFrame(
        #     self, text=_("Record"), style='Panel.TLabelFrame.Label')
        f = utils.CollapsiblePageLabelFrame(
            self, app, name="Record", text=_("Record"))
        f.pack(side="top", expand=True, fill="x")
        recframe = f.frame

        self.recz = tk.IntVar()
        self.reczb = ttk.Checkbutton(
            recframe,
            text=_("Z"),
            variable=self.recz,  # onvalue=1, offvalue=0,
            style="Panel.TCheckbutton",
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        utils.ToolTip(self.reczb, _("Record Z coordinate?"))
        self.reczb.pack(side="left", expand=True, fill="x")
        self.addWidget(self.reczb)

        self.rr = ttk.Button(
            recframe,
            text=_("RAPID"),
            command=self.recordRapid,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.rr.pack(side="left", expand=True, fill="x")
        self.addWidget(self.rr)

        self.rr = ttk.Button(
            recframe,
            text=_("FEED"),
            command=self.recordFeed,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.rr.pack(side="left", expand=True, fill="x")
        self.addWidget(self.rr)

        self.rr = ttk.Button(
            recframe,
            text=_("POINT"),
            command=self.recordPoint,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.rr.pack(side="left", expand=True, fill="x")
        self.addWidget(self.rr)

        self.rr = ttk.Button(
            recframe,
            text=_("CIRCLE"),
            command=self.recordCircle,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.rr.pack(side="left", expand=True, fill="x")
        self.addWidget(self.rr)

        self.rr = ttk.Button(
            recframe,
            text=_("FINISH"),
            command=self.recordFinishAll,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.rr.pack(side="left", expand=True, fill="x")
        self.addWidget(self.rr)

        self.recsiz = tkextra.FloatEntry(
            recframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        utils.ToolTip(self.recsiz, _("Circle radius"))
        self.recsiz.set(10)
        self.recsiz.pack(side="bottom", expand=True, fill="x")
        self.addWidget(self.recsiz)

        # ----------------------------------------------------------------
        # Single probe
        # ----------------------------------------------------------------
        f = utils.CollapsiblePageLabelFrame(
            self, app, name="Probe", text=_("Probe"))
        f.pack(side="top", fill="x")
        lframe = f.frame
        # lframe = tkextra.ExLabelFrame(
        #     self, text=_("Probe"), style='Panel.TLabelFrame.Label'
        # )
        # lframe.pack(side="top", fill="x")

        row, col = 0, 0
        ttk.Label(lframe, text=_("Probe:")).grid(
            row=row, column=col, sticky="e")

        col += 1
        self._probeX = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90"
        )
        self._probeX.grid(row=row, column=col, padx=1, sticky="ews")

        col += 1
        self._probeY = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90"
        )
        self._probeY.grid(row=row, column=col, padx=1, sticky="ews")

        col += 1
        self._probeZ = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90"
        )
        self._probeZ.grid(row=row, column=col, padx=1, sticky="ews")

        # ---
        col += 1
        self.probeautogotonext = False
        self.probeautogoto = tk.BooleanVar(self, True)  # IntVar()
        self.autogoto = ttk.Checkbutton(
            lframe,
            text="",
            variable=self.probeautogoto,
            style="Panel.TCheckbutton",
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        # self.autogoto.select()
        utils.ToolTip(self.autogoto, _("Automatic GOTO after probing"))
        self.autogoto.grid(row=row, column=col, padx=1, sticky="ew")
        self.addWidget(self.autogoto)

        # ---
        col += 1
        b = ttk.Button(
            lframe,
            image=Utils.icons["rapid"],
            text=_("Goto"),
            compound="left",
            command=self.goto2Probe,
            # padx=5,
            # pady=0,
        )
        b.grid(row=row, column=col, padx=1, sticky="ew")
        self.addWidget(b)
        utils.ToolTip(b, _("Rapid goto to last probe location"))

        # ---
        row, col = row + 1, 0
        ttk.Label(lframe, text=_("Pos:")).grid(
            row=row, column=col, sticky="e")

        col += 1
        self.probeXdir = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.probeXdir.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeXdir, _("Probe along X direction"))
        self.addWidget(self.probeXdir)

        col += 1
        self.probeYdir = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.probeYdir.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeYdir, _("Probe along Y direction"))
        self.addWidget(self.probeYdir)

        col += 1
        self.probeZdir = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.probeZdir.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeZdir, _("Probe along Z direction"))
        self.addWidget(self.probeZdir)

        # ---
        col += 2
        b = ttk.Button(
            lframe,  # "<<Probe>>",
            image=Utils.icons["probe32"],
            text=_("Probe"),
            compound="left",
            command=self.probe,
            # padx=5,
            # pady=0,
        )
        b.grid(row=row, column=col, padx=1, sticky="ew")
        self.addWidget(b)
        utils.ToolTip(b, _("Perform a single probe cycle"))

        lframe.grid_columnconfigure(1, weight=1)
        lframe.grid_columnconfigure(2, weight=1)
        lframe.grid_columnconfigure(3, weight=1)

        # ----------------------------------------------------------------
        # Center probing
        # ----------------------------------------------------------------
        f = utils.CollapsiblePageLabelFrame(
            self, app, name="Center", text=_("Center"))
        f.pack(side="top", expand=True, fill="x")
        lframe = f.frame
        # lframe = tkextra.ExLabelFrame(
        #     self, text=_("Center"), style='Panel.TLabelFrame.Label'
        # )
        # lframe.pack(side="top", expand=True, fill="x")

        ttk.Label(lframe, text=_("Diameter:")).pack(side="left")
        self.diameter = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.diameter.pack(side="left", expand=True, fill="x")
        utils.ToolTip(
            self.diameter, _("Probing ring internal diameter"))
        self.addWidget(self.diameter)

        # ---
        b = ttk.Button(
            lframe,
            image=Utils.icons["target32"],
            text=_("Center"),
            compound="top",
            command=self.probeCenter,
            width=48,
            # padx=5,
            # pady=0,
        )
        b.pack(side="right")
        self.addWidget(b)
        utils.ToolTip(b, _("Center probing using a ring"))

        # ----------------------------------------------------------------
        # Align / Orient / Square ?
        # ----------------------------------------------------------------
        f = utils.CollapsiblePageLabelFrame(
            self, app, name="Orient", text=_("Orient"))
        f.pack(side="top", expand=True, fill="x")
        lframe = f.frame
        # lframe = tkextra.ExLabelFrame(
        #     self, text=_("Orient"), style='Panel.TLabelFrame.Label'
        # )
        # lframe.pack(side="top", expand=True, fill="x")

        # ---
        row, col = 0, 0

        ttk.Label(lframe, text=_("Markers:")).grid(
            row=row, column=col, sticky="e")
        col += 1

        self.scale_orient = ttk.Scale(
            lframe,
            from_=0,
            to_=0,
            orient="horizontal",
            # showvalue=1,
            state="disabled",
            command=self.changeMarker,
        )
        self.scale_orient.grid(row=row, column=col, columnspan=2, sticky="ew")
        utils.ToolTip(self.scale_orient, _("Select orientation marker"))

        # Add new point
        col += 2
        b = ttk.Button(
            lframe,
            text=_("Add"),
            image=Utils.icons["add"],
            compound="left",
            command=lambda s=self: s.event_generate("<<AddMarker>>"),
            # padx=1,
            # pady=1,
        )
        b.grid(row=row, column=col, sticky="nsew")
        self.addWidget(b)
        utils.ToolTip(
            b,
            _(
                "Add an orientation marker. "
                "Jog first the machine to the marker position "
                "and then click on canvas to add the marker."
            ),
        )

        # ----
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Gcode:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.x_orient = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.x_orient.grid(row=row, column=col, sticky="ew")
        self.x_orient.bind("<FocusOut>", self.orientUpdate)
        self.x_orient.bind("<Return>", self.orientUpdate)
        self.x_orient.bind("<KP_Enter>", self.orientUpdate)
        utils.ToolTip(
            self.x_orient, _("GCode X coordinate of orientation point"))

        col += 1
        self.y_orient = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.y_orient.grid(row=row, column=col, sticky="ew")
        self.y_orient.bind("<FocusOut>", self.orientUpdate)
        self.y_orient.bind("<Return>", self.orientUpdate)
        self.y_orient.bind("<KP_Enter>", self.orientUpdate)
        utils.ToolTip(
            self.y_orient, _("GCode Y coordinate of orientation point"))

        # Buttons
        col += 1
        b = ttk.Button(
            lframe,
            text=_("Delete"),
            image=Utils.icons["x"],
            compound="left",
            command=self.orientDelete,
            # padx=1,
            # pady=1,
        )
        b.grid(row=row, column=col, sticky="ew")
        self.addWidget(b)
        utils.ToolTip(b, _("Delete current marker"))

        # ---
        row += 1
        col = 0

        ttk.Label(lframe, text=_("WPos:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.xm_orient = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.xm_orient.grid(row=row, column=col, sticky="ew")
        self.xm_orient.bind("<FocusOut>", self.orientUpdate)
        self.xm_orient.bind("<Return>", self.orientUpdate)
        self.xm_orient.bind("<KP_Enter>", self.orientUpdate)
        utils.ToolTip(
            self.xm_orient, _("Machine X coordinate of orientation point")
        )

        col += 1
        self.ym_orient = tkextra.FloatEntry(
            lframe, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.ym_orient.grid(row=row, column=col, sticky="ew")
        self.ym_orient.bind("<FocusOut>", self.orientUpdate)
        self.ym_orient.bind("<Return>", self.orientUpdate)
        self.ym_orient.bind("<KP_Enter>", self.orientUpdate)
        utils.ToolTip(
            self.ym_orient, _("Machine Y coordinate of orientation point")
        )

        # Buttons
        col += 1
        b = ttk.Button(
            lframe,
            text=_("Clear"),
            image=Utils.icons["clear"],
            compound="left",
            command=self.orientClear,
            # padx=1,
            # pady=1,
        )
        b.grid(row=row, column=col, sticky="ew")
        self.addWidget(b)
        utils.ToolTip(b, _("Delete all markers"))

        # ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Angle:")).grid(
            row=row, column=col, sticky="e")

        col += 1
        self.angle_orient = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90", anchor="w"
        )
        self.angle_orient.grid(
            row=row, column=col, columnspan=2, sticky="ew", padx=1, pady=1
        )

        # Buttons
        col += 2
        b = ttk.Button(
            lframe,
            text=_("Orient"),
            image=Utils.icons["setsquare32"],
            compound="top",
            command=lambda a=app: a.insertCommand("ORIENT", True),
            # padx=1,
            # pady=1,
        )
        b.grid(row=row, rowspan=3, column=col, sticky="ew")
        self.addWidget(b)
        utils.ToolTip(b, _("Align GCode with the machine markers"))

        # ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Offset:")).grid(
            row=row, column=col, sticky="e")

        col += 1
        self.xo_orient = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90", anchor="w"
        )
        self.xo_orient.grid(row=row, column=col, sticky="ew", padx=1)

        col += 1
        self.yo_orient = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90", anchor="w"
        )
        self.yo_orient.grid(row=row, column=col, sticky="ew", padx=1)

        # ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Error:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.err_orient = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90", anchor="w"
        )
        self.err_orient.grid(
            row=row, column=col, columnspan=2, sticky="ew", padx=1, pady=1
        )

        lframe.grid_columnconfigure(1, weight=1)
        lframe.grid_columnconfigure(2, weight=1)

        # ----------------------------------------------------------------
        self.warn = True
        self.loadConfig()

    # -----------------------------------------------------------------------
    def loadConfig(self):
        self.probeXdir.set(gconfig.getstr("Probe", "x"))
        self.probeYdir.set(gconfig.getstr("Probe", "y"))
        self.probeZdir.set(gconfig.getstr("Probe", "z"))
        self.diameter.set(gconfig.getstr("Probe", "center"))
        self.warn = gconfig.getbool("Warning", "probe", self.warn)

    # -----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr("Probe", "x", self.probeXdir.get())
        gconfig.setstr("Probe", "y", self.probeYdir.get())
        gconfig.setstr("Probe", "z", self.probeZdir.get())
        gconfig.setstr("Probe", "center", self.diameter.get())
        gconfig.setbool("Warning", "probe", self.warn)

    # -----------------------------------------------------------------------
    def updateProbe(self):
        try:
            self._probeX["text"] = globCNC.vars.get("prbx")
            self._probeY["text"] = globCNC.vars.get("prby")
            self._probeZ["text"] = globCNC.vars.get("prbz")
        except Exception:
            return

        if self.probeautogotonext:
            self.probeautogotonext = False
            self.goto2Probe()

    # -----------------------------------------------------------------------
    def warnMessage(self):
        if self.warn:
            ans = tk.messagebox.askquestion(
                _("Probe connected?"),
                _(
                    "Please verify that the probe is connected.\n\n"
                    + "Show this message again?"
                ),
                icon="warning",
                parent=self.winfo_toplevel(),
            )
            if ans != "yes":
                self.warn = False

    # -----------------------------------------------------------------------
    # Probe one Point
    # -----------------------------------------------------------------------
    def probe(self, event=None):
        if self.probeautogoto.get():
            self.probeautogotonext = True

        if ProbeCommonFrame.probeUpdate():
            tk.messagebox.showerror(
                _("Probe Error"),
                _("Invalid probe feed rate"),
                parent=self.winfo_toplevel(),
            )
            return
        self.warnMessage()

        cmd = str(globCNC.vars["prbcmd"])
        ok = False

        v = self.probeXdir.get()
        if v != "":
            cmd += f"X{v}"
            ok = True

        v = self.probeYdir.get()
        if v != "":
            cmd += f"Y{v}"
            ok = True

        v = self.probeZdir.get()
        if v != "":
            cmd += f"Z{v}"
            ok = True

        v = ProbeCommonFrame.probeFeed.get()
        if v != "":
            cmd += f"F{v}"

        if ok:
            self.sendGCode(cmd)
        else:
            tk.messagebox.showerror(
                _("Probe Error"),
                _("At least one probe direction should be specified")
            )

    # -----------------------------------------------------------------------
    # Rapid move to the last probed location
    # -----------------------------------------------------------------------
    def goto2Probe(self, event=None):
        try:
            cmd = "G53 G0 X{:g} Y{:g} Z{:g}\n".format(
                globCNC.vars["prbx"],
                globCNC.vars["prby"],
                globCNC.vars["prbz"],
            )
        except Exception:
            return
        self.sendGCode(cmd)

    # -----------------------------------------------------------------------
    # Probe Center
    # -----------------------------------------------------------------------
    def probeCenter(self, event=None):
        self.warnMessage()

        cmd = f"G91 {globCNC.vars['prbcmd']} F{globCNC.vars['prbfeed']}"
        try:
            diameter = abs(float(self.diameter.get()))
        except Exception:
            diameter = 0.0

        if diameter < 0.001:
            tk.messagebox.showerror(
                _("Probe Center Error"),
                _("Invalid diameter entered"),
                parent=self.winfo_toplevel(),
            )
            return

        lines = []
        lines.append(f"{cmd} x-{diameter}")
        lines.append("%wait")
        lines.append("tmp=prbx")
        lines.append(f"g53 g0 x[prbx+{diameter / 10.0:g}]")
        lines.append("%wait")
        lines.append(f"{cmd} x{diameter}")
        lines.append("%wait")
        lines.append("g53 g0 x[0.5*(tmp+prbx)]")
        lines.append("%wait")
        lines.append(f"{cmd} y-{diameter}")
        lines.append("%wait")
        lines.append("tmp=prby")
        lines.append(f"g53 g0 y[prby+{diameter / 10.0:g}]")
        lines.append("%wait")
        lines.append(f"{cmd} y{diameter}")
        lines.append("%wait")
        lines.append("g53 g0 y[0.5*(tmp+prby)]")
        lines.append("%wait")
        lines.append("g90")
        self.app.run(lines=lines)

    # -----------------------------------------------------------------------
    # Solve the system and update fields
    # -----------------------------------------------------------------------
    def orientSolve(self, event=None):
        try:
            phi, xo, yo = globGCode.orient.solve()
            self.angle_orient["text"] = "%*f" % (
                globCNC.digits, math.degrees(phi))
            self.xo_orient["text"] = "%*f" % (globCNC.digits, xo)
            self.yo_orient["text"] = "%*f" % (globCNC.digits, yo)

            minerr, meanerr, maxerr = globGCode.orient.error()
            self.err_orient["text"] = "Avg:%*f  Max:%*f  Min:%*f" % (
                globCNC.digits,
                meanerr,
                globCNC.digits,
                maxerr,
                globCNC.digits,
                minerr,
            )

        except Exception:
            self.angle_orient["text"] = sys.exc_info()[1]
            self.xo_orient["text"] = ""
            self.yo_orient["text"] = ""
            self.err_orient["text"] = ""

    # -----------------------------------------------------------------------
    # Delete current orientation point
    # -----------------------------------------------------------------------
    def orientDelete(self, event=None):
        marker = self.scale_orient.get() - 1
        if marker < 0 or marker >= len(globGCode.orient):
            return
        globGCode.orient.clear(marker)
        self.orientUpdateScale()
        self.changeMarker(marker + 1)
        self.orientSolve()
        self.event_generate("<<DrawOrient>>")

    # -----------------------------------------------------------------------
    # Clear all markers
    # -----------------------------------------------------------------------
    def orientClear(self, event=None):
        if self.scale_orient.cget("to") == 0:
            return
        ans = tk.messagebox.askquestion(
            _("Delete all markers"),
            _("Do you want to delete all orientation markers?"),
            parent=self.winfo_toplevel(),
        )
        if ans != tk.messagebox.YES:
            return
        globGCode.orient.clear()
        self.orientUpdateScale()
        self.event_generate("<<DrawOrient>>")

    # -----------------------------------------------------------------------
    # Update orientation scale
    # -----------------------------------------------------------------------
    def orientUpdateScale(self):
        n = len(globGCode.orient)
        if n:
            self.scale_orient.config(state="normal", from_=1, to_=n)
        else:
            self.scale_orient.config(state="disabled", from_=0, to_=0)

    # -----------------------------------------------------------------------
    def orientClearFields(self):
        self.x_orient.delete(0, "end")
        self.y_orient.delete(0, "end")
        self.xm_orient.delete(0, "end")
        self.ym_orient.delete(0, "end")
        self.angle_orient["text"] = ""
        self.xo_orient["text"] = ""
        self.yo_orient["text"] = ""
        self.err_orient["text"] = ""

    # -----------------------------------------------------------------------
    # Update orient with the current marker
    # -----------------------------------------------------------------------
    def orientUpdate(self, event=None):
        marker = self.scale_orient.get() - 1
        if marker < 0 or marker >= len(globGCode.orient):
            self.orientClearFields()
            return
        xm, ym, x, y = globGCode.orient[marker]
        try:
            x = float(self.x_orient.get())
        except Exception:
            pass
        try:
            y = float(self.y_orient.get())
        except Exception:
            pass
        try:
            xm = float(self.xm_orient.get())
        except Exception:
            pass
        try:
            ym = float(self.ym_orient.get())
        except Exception:
            pass
        globGCode.orient.markers[marker] = xm, ym, x, y

        self.orientUpdateScale()
        self.changeMarker(marker + 1)
        self.orientSolve()
        self.event_generate("<<DrawOrient>>")

    # -----------------------------------------------------------------------
    # The index will be +1 to appear more human starting from 1
    # -----------------------------------------------------------------------
    def changeMarker(self, marker):
        marker = int(marker) - 1
        if marker < 0 or marker >= len(globGCode.orient):
            self.orientClearFields()
            self.event_generate("<<OrientChange>>", data=-1)
            return

        xm, ym, x, y = globGCode.orient[marker]
        d = globCNC.digits
        self.x_orient.set("%*f" % (d, x))
        self.y_orient.set("%*f" % (d, y))
        self.xm_orient.set("%*f" % (d, xm))
        self.ym_orient.set("%*f" % (d, ym))
        self.orientSolve()
        self.event_generate("<<OrientChange>>", data=marker)

    # -----------------------------------------------------------------------
    # Select marker
    # -----------------------------------------------------------------------
    def selectMarker(self, marker):
        self.orientUpdateScale()
        self.scale_orient.set(marker + 1)

    def recordAppend(self, line):
        hasblock = None
        for bid, block in enumerate(globGCode):
            if block._name == "recording":
                hasblock = bid
                eblock = block

        if hasblock is None:
            hasblock = -1
            eblock = Block("recording")
            globGCode.insBlocks(hasblock, [eblock], "Recorded point")

        eblock.append(line)
        self.app.refresh()
        self.app.setStatus(_("Pointrec"))

    def recordCoords(self, gcode="G0", point=False):
        x = globCNC.vars["wx"]
        y = globCNC.vars["wy"]
        z = globCNC.vars["wz"]

        coords = f"X{x} Y{y}"
        if self.recz.get() == 1:
            coords += f" Z{z}"

        if point:
            self.recordAppend(f"G0 Z{globCNC.vars['safe']}")
        self.recordAppend(f"{gcode} {coords}")
        if point:
            self.recordAppend("G1 Z0")

    def recordRapid(self):
        self.recordCoords()

    def recordFeed(self):
        self.recordCoords("G1")

    def recordPoint(self):
        self.recordCoords("G0", True)

    def recordCircle(self):
        r = float(self.recsiz.get())
        x = globCNC.vars["wx"] - r
        y = globCNC.vars["wy"]
        z = globCNC.vars["wz"]

        coords = f"X{x} Y{y}"
        if self.recz.get() == 1:
            coords += f" Z{z}"

        self.recordAppend(f"G0 {coords}")
        self.recordAppend(f"G02 {coords} I{r}")

    def recordFinishAll(self):
        for bid, block in enumerate(globGCode):
            if block._name == "recording":
                globGCode.setBlockNameUndo(bid, "recorded")
        self.app.refresh()
        self.app.setStatus(_("Finished recording"))
