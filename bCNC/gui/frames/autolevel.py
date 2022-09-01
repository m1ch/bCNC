""" This file was created due to the refactoring of
    ProbePage.py - AutolevelFrame

    Authors:
             @m1ch
"""

import tkinter as tk

from globalConfig import config as gconfig
from cnc import globCNC
from gcode import globGCode
# from sender import globSender

from .. import tkextra
from tkinter import ttk
# from .. import cncribbon
from .. import utils

from .probecommon import SideFrame as ProbeCommonFrame


# =============================================================================
# Autolevel Frame
# =============================================================================
class SideFrame(utils.PageLabelFrame):
    def __init__(self, master, app):
        utils.PageLabelFrame.__init__(
            self, master, app, "Probe:Autolevel", _("Autolevel"))

        # ---
        lframe = self.frame

        row, col = 0, 0
        # Empty
        col += 1
        ttk.Label(lframe, text=_("Min")).grid(row=row, column=col, sticky="ew")
        col += 1
        ttk.Label(lframe, text=_("Max")).grid(row=row, column=col, sticky="ew")
        col += 1
        ttk.Label(lframe, text=_("Step")).grid(
            row=row, column=col, sticky="ew")
        col += 1
        ttk.Label(lframe, text=_("N")).grid(row=row, column=col, sticky="ew")

        # --- X ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("X:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.probeXmin = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeXmin.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeXmin, _("X minimum"))
        self.addWidget(self.probeXmin)

        col += 1
        self.probeXmax = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeXmax.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeXmax, _("X maximum"))
        self.addWidget(self.probeXmax)

        col += 1
        self.probeXstep = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90",
            width=5
        )
        self.probeXstep.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeXstep, _("X step"))

        col += 1
        self.probeXbins = ttk.Spinbox(
            lframe,
            from_=2,
            to_=1000,
            command=self.draw,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=3,
        )
        self.probeXbins.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeXbins, _("X bins"))
        self.addWidget(self.probeXbins)

        # --- Y ---
        row += 1
        col = 0
        ttk.Label(lframe, text=_("Y:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.probeYmin = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeYmin.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeYmin, _("Y minimum"))
        self.addWidget(self.probeYmin)

        col += 1
        self.probeYmax = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeYmax.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeYmax, _("Y maximum"))
        self.addWidget(self.probeYmax)

        col += 1
        self.probeYstep = ttk.Label(
            lframe,
            # foreground="DarkBlue", background="gray90",
            width=5
        )
        self.probeYstep.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeYstep, _("Y step"))

        col += 1
        self.probeYbins = ttk.Spinbox(
            lframe,
            from_=2,
            to_=1000,
            command=self.draw,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=3,
        )
        self.probeYbins.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeYbins, _("Y bins"))
        self.addWidget(self.probeYbins)

        # Max Z
        row += 1
        col = 0

        ttk.Label(lframe, text=_("Z:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.probeZmin = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeZmin.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeZmin, _("Z Minimum depth to scan"))
        self.addWidget(self.probeZmin)

        col += 1
        self.probeZmax = tkextra.FloatEntry(
            lframe,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=5
        )
        self.probeZmax.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.probeZmax, _("Z safe to move"))
        self.addWidget(self.probeZmax)

        lframe.grid_columnconfigure(1, weight=2)
        lframe.grid_columnconfigure(2, weight=2)
        lframe.grid_columnconfigure(3, weight=1)

        self.loadConfig()

    # -----------------------------------------------------------------------
    def setValues(self):
        probe = globGCode.probe
        self.probeXmin.set(str(probe.xmin))
        self.probeXmax.set(str(probe.xmax))
        self.probeXbins.delete(0, "end")
        self.probeXbins.insert(0, probe.xn)
        self.probeXstep["text"] = str(probe.xstep())

        self.probeYmin.set(str(probe.ymin))
        self.probeYmax.set(str(probe.ymax))
        self.probeYbins.delete(0, "end")
        self.probeYbins.insert(0, probe.yn)
        self.probeYstep["text"] = str(probe.ystep())

        self.probeZmin.set(str(probe.zmin))
        self.probeZmax.set(str(probe.zmax))

    # -----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr("Probe", "xmin", self.probeXmin.get())
        gconfig.setstr("Probe", "xmax", self.probeXmax.get())
        gconfig.setstr("Probe", "xn", self.probeXbins.get())
        gconfig.setstr("Probe", "ymin", self.probeYmin.get())
        gconfig.setstr("Probe", "ymax", self.probeYmax.get())
        gconfig.setstr("Probe", "yn", self.probeYbins.get())
        gconfig.setstr("Probe", "zmin", self.probeZmin.get())
        gconfig.setstr("Probe", "zmax", self.probeZmax.get())

    # -----------------------------------------------------------------------
    def loadConfig(self):
        self.probeXmin.set(gconfig.getfloat("Probe", "xmin"))
        self.probeXmax.set(gconfig.getfloat("Probe", "xmax"))
        self.probeYmin.set(gconfig.getfloat("Probe", "ymin"))
        self.probeYmax.set(gconfig.getfloat("Probe", "ymax"))
        self.probeZmin.set(gconfig.getfloat("Probe", "zmin"))
        self.probeZmax.set(gconfig.getfloat("Probe", "zmax"))

        self.probeXbins.delete(0, "end")
        self.probeXbins.insert(0, max(2, gconfig.getint("Probe", "xn", 5)))

        self.probeYbins.delete(0, "end")
        self.probeYbins.insert(0, max(2, gconfig.getint("Probe", "yn", 5)))
        self.change(False)

    # -----------------------------------------------------------------------
    def getMargins(self, event=None):
        self.probeXmin.set(str(globCNC.vars["xmin"]))
        self.probeXmax.set(str(globCNC.vars["xmax"]))
        self.probeYmin.set(str(globCNC.vars["ymin"]))
        self.probeYmax.set(str(globCNC.vars["ymax"]))
        self.draw()

    # -----------------------------------------------------------------------
    def change(self, verbose=True):
        return True  # FIXME
        probe = globGCode.probe
        error = False
        try:
            probe.xmin = float(self.probeXmin.get())
            probe.xmax = float(self.probeXmax.get())
            probe.xn = max(2, int(self.probeXbins.get()))
            self.probeXstep["text"] = f"{probe.xstep():.5g}"
        except ValueError:
            self.probeXstep["text"] = ""
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid X probing region"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        if probe.xmin >= probe.xmax:
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid X range [xmin>=xmax]"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        try:
            probe.ymin = float(self.probeYmin.get())
            probe.ymax = float(self.probeYmax.get())
            probe.yn = max(2, int(self.probeYbins.get()))
            self.probeYstep["text"] = f"{probe.ystep():.5g}"
        except ValueError:
            self.probeYstep["text"] = ""
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid Y probing region"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        if probe.ymin >= probe.ymax:
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid Y range [ymin>=ymax]"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        try:
            probe.zmin = float(self.probeZmin.get())
            probe.zmax = float(self.probeZmax.get())
        except ValueError:
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid Z probing region"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        if probe.zmin >= probe.zmax:
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid Z range [zmin>=zmax]"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        if ProbeCommonFrame.probeUpdate():
            if verbose:
                tk.messagebox.showerror(
                    _("Probe Error"),
                    _("Invalid probe feed rate"),
                    parent=self.winfo_toplevel(),
                )
            error = True

        return error

    # -----------------------------------------------------------------------
    def draw(self):
        if not self.change():
            self.event_generate("<<DrawProbe>>")

    # -----------------------------------------------------------------------
    def setZero(self, event=None):
        x = globCNC.vars["wx"]
        y = globCNC.vars["wy"]
        globGCode.probe.setZero(x, y)
        self.draw()

    # -----------------------------------------------------------------------
    def clear(self, event=None):
        ans = tk.messagebox.askquestion(
            _("Delete autolevel information"),
            _("Do you want to delete all autolevel in formation?"),
            parent=self.winfo_toplevel(),
        )
        if ans != tk.messagebox.YES:
            return
        globGCode.probe.clear()
        self.draw()

    # -----------------------------------------------------------------------
    # Probe an X-Y area
    # -----------------------------------------------------------------------
    def scan(self, event=None):
        if self.change():
            return
        self.event_generate("<<DrawProbe>>")
        # absolute
        self.app.run(lines=globGCode.probe.scan())

    # -----------------------------------------------------------------------
    # Scan autolevel margins
    # -----------------------------------------------------------------------
    def scanMargins(self, event=None):
        if self.change():
            return
        self.app.run(lines=globGCode.probe.scanMargins())
