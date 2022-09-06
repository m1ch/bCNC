""" This file was created due to the refactoring of
    ControlPage.py - DROFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

from cnc import globCNC
from sender import globSender, NOT_CONNECTED
from globalConfig import config as gconfig
from globalConfig import icon as gicon

from .. import utils
from .. import cncribbon


name = "DROFrame"


# =============================================================================
# DRO Frame
# =============================================================================
class SideFrame(cncribbon.PageFrame):
    dro_status = ("Helvetica", 12, "bold")
    dro_wpos = ("Helvetica", 12, "bold")
    dro_mpos = ("Helvetica", 12)

    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, "DRO", app)

        self.dro_status = gconfig.getfont("dro.status",
                                          self.dro_status)
        self.dro_wpos = gconfig.getfont("dro.wpos", self.dro_wpos)
        self.dro_mpos = gconfig.getfont("dro.mpos", self.dro_mpos)

        row = 0
        col = 0
        ttk.Label(self, text=_("Status:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.stateBtn = ttk.Button(
            self,
            text=NOT_CONNECTED,
            command=self.showState,
            cursor="hand1",
        )
        self.stateBtn.grid(row=row, column=col, columnspan=3, sticky="ew")
        utils.ToolTip(
            self.stateBtn,
            _(
                "Show current state of the machine\n"
                "Click to see details\n"
                "Right-Click to clear alarm/errors"
            ),
        )
        self.stateBtn.bind("<Button-3>", self.stateMenu)

        row += 1
        col = 0
        ttk.Label(self, text=_("WPos:")).grid(row=row, column=col, sticky="e")

        # work
        col += 1
        self.xwork = ttk.Entry(
            self,
            font=self.dro_wpos,
            style="Panel.TEntry",
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.xwork.grid(row=row, column=col, padx=1, sticky="ew")
        utils.ToolTip(self.xwork, _("X work position (click to set)"))
        self.xwork.bind("<FocusIn>", self.workFocus)
        self.xwork.bind("<Return>", self.setX)
        self.xwork.bind("<KP_Enter>", self.setX)

        # ---
        col += 1
        self.ywork = ttk.Entry(
            self,
            font=self.dro_wpos,
            style="Panel.TEntry",
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.ywork.grid(row=row, column=col, padx=1, sticky="ew")
        utils.ToolTip(self.ywork, _("Y work position (click to set)"))
        self.ywork.bind("<FocusIn>", self.workFocus)
        self.ywork.bind("<Return>", self.setY)
        self.ywork.bind("<KP_Enter>", self.setY)

        # ---
        col += 1
        self.zwork = ttk.Entry(
            self,
            font=self.dro_wpos,
            style="Panel.TEntry",
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.zwork.grid(row=row, column=col, padx=1, sticky="ew")
        utils.ToolTip(self.zwork, _("Z work position (click to set)"))
        self.zwork.bind("<FocusIn>", self.workFocus)
        self.zwork.bind("<Return>", self.setZ)
        self.zwork.bind("<KP_Enter>", self.setZ)

        # Machine
        row += 1
        col = 0
        ttk.Label(self, text=_("MPos:")).grid(row=row, column=col, sticky="e")

        col += 1
        self.xmachine = ttk.Label(
            self,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.xmachine.grid(row=row, column=col, padx=1, sticky="ew")

        col += 1
        self.ymachine = ttk.Label(
            self,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.ymachine.grid(row=row, column=col, padx=1, sticky="ew")

        col += 1
        self.zmachine = ttk.Label(
            self,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors',
            # "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.zmachine.grid(row=row, column=col, padx=1, sticky="ew")

        # Set buttons
        row += 1
        col = 1

        self.xzero = ttk.Button(
            self,
            text=_("X=0"),
            command=self.setX0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.xzero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            self.xzero, _("Set X coordinate to zero "
                          + "(or to typed coordinate in WPos)")
        )
        self.addWidget(self.xzero)

        col += 1
        self.yzero = ttk.Button(
            self,
            text=_("Y=0"),
            command=self.setY0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.yzero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            self.yzero, _("Set Y coordinate to zero "
                          + "(or to typed coordinate in WPos)")
        )
        self.addWidget(self.yzero)

        col += 1
        self.zzero = ttk.Button(
            self,
            text=_("Z=0"),
            command=self.setZ0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.zzero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            self.zzero, _("Set Z coordinate to zero "
                          + "(or to typed coordinate in WPos)")
        )
        self.addWidget(self.zzero)

        # Set buttons
        row += 1
        col = 1
        self.xyzero = ttk.Button(
            self,
            text=_("XY=0"),
            command=self.setXY0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.xyzero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            self.xyzero, _("Set XY coordinate to zero "
                           + "(or to typed coordinate in WPos)")
        )
        self.addWidget(self.xyzero)

        col += 1
        self.xyzzero = ttk.Button(
            self,
            text=_("XYZ=0"),
            command=self.setXYZ0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        self.xyzzero.grid(row=row, column=col, pady=0,
                          sticky="ew", columnspan=2)
        utils.ToolTip(
            self.xyzzero,
            _("Set XYZ coordinate to zero (or to typed coordinate in WPos)"),
        )
        self.addWidget(self.xyzzero)

        # Set buttons
        row += 1
        col = 1
        f = ttk.Frame(self)
        f.grid(row=row, column=col, columnspan=3, pady=0, sticky="ew")

        b = ttk.Button(
            f,
            text=_("Set WPOS"),
            image=gicon["origin"],
            compound="left",
            # activebackground="LightYellow",
            command=lambda s=self: s.event_generate("<<SetWPOS>>"),
            # padx=2,
            # pady=1,
        )
        b.pack(side="left", fill="x", expand=True)
        utils.ToolTip(b, _("Set WPOS to mouse location"))
        self.addWidget(b)

        b = ttk.Button(
            f,
            text=_("Move Gantry"),
            image=gicon["gantry"],
            compound="left",
            # activebackground="LightYellow",
            command=lambda s=self: s.event_generate("<<MoveGantry>>"),
            # padx=2,
            # pady=1,
        )
        b.pack(side="right", fill="x", expand=True)
        utils.ToolTip(b, _("Move gantry to mouse location [g]"))
        self.addWidget(b)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

    # ----------------------------------------------------------------------
    def stateMenu(self, event=None):
        menu = tk.Menu(self, tearoff=0)

        menu.add_command(
            label=_("Show Info"),
            image=gicon["info"],
            compound="left",
            command=self.showState,
        )
        menu.add_command(
            label=_("Clear Message"),
            image=gicon["clear"],
            compound="left",
            command=lambda s=self: s.event_generate("<<AlarmClear>>"),
        )
        menu.add_separator()

        menu.add_command(
            label=_("Feed hold"),
            image=gicon["pause"],
            compound="left",
            command=lambda s=self: s.event_generate("<<FeedHold>>"),
        )
        menu.add_command(
            label=_("Resume"),
            image=gicon["start"],
            compound="left",
            command=lambda s=self: s.event_generate("<<Resume>>"),
        )

        menu.tk_popup(event.x_root, event.y_root)

    # ----------------------------------------------------------------------
    def updateState(self, style=None):
        if not style:
            style = "StateBtn.TButton"
        msg = globSender._msg or globCNC.vars["state"]
        if globCNC.vars["pins"] is not None and globCNC.vars["pins"] != "":
            msg += " [" + globCNC.vars["pins"] + "]"
        self.stateBtn.config(text=msg,)
        # background=globCNC.vars["color"])
        self.stateBtn["style"] = style

    # ----------------------------------------------------------------------
    def updateCoords(self):
        try:
            focus = self.focus_get()
        except Exception:
            focus = None
        if focus is not self.xwork:
            self.xwork.delete(0, "end")
            self.xwork.insert(0, self.padFloat(globCNC.drozeropad,
                                               globCNC.vars["wx"]))
        if focus is not self.ywork:
            self.ywork.delete(0, "end")
            self.ywork.insert(0, self.padFloat(globCNC.drozeropad,
                                               globCNC.vars["wy"]))
        if focus is not self.zwork:
            self.zwork.delete(0, "end")
            self.zwork.insert(0, self.padFloat(globCNC.drozeropad,
                                               globCNC.vars["wz"]))

        self.xmachine["text"] = self.padFloat(globCNC.drozeropad,
                                              globCNC.vars["mx"])
        self.ymachine["text"] = self.padFloat(globCNC.drozeropad,
                                              globCNC.vars["my"])
        self.zmachine["text"] = self.padFloat(globCNC.drozeropad,
                                              globCNC.vars["mz"])
        self.app.abcdro.updateCoords()

    # ----------------------------------------------------------------------
    def padFloat(self, decimals, value):
        if decimals > 0:
            return f"{value:0.{decimals}f}"
        else:
            return value

    # ----------------------------------------------------------------------
    # Do not give the focus while we are running
    # ----------------------------------------------------------------------
    def workFocus(self, event=None):
        if globSender.running:
            self.app.focus_set()

    # ----------------------------------------------------------------------
    def setX0(self, event=None):
        globSender.mcontrol._wcsSet("0", None, None, None, None, None)

    # ----------------------------------------------------------------------
    def setY0(self, event=None):
        globSender.mcontrol._wcsSet(None, "0", None, None, None, None)

    # ----------------------------------------------------------------------
    def setZ0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, "0", None, None, None)

    # ----------------------------------------------------------------------
    def setXY0(self, event=None):
        globSender.mcontrol._wcsSet("0", "0", None, None, None, None)

    # ----------------------------------------------------------------------
    def setXYZ0(self, event=None):
        globSender.mcontrol._wcsSet("0", "0", "0", None, None, None)

    # ----------------------------------------------------------------------
    def setX(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.xwork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(value, None, None, None, None, None)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def setY(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.ywork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(None, value, None, None, None, None)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def setZ(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.zwork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(None, None, value, None, None, None)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def showState(self):
        err = globCNC.vars["errline"]
        if err:
            msg = _("Last error: {}\n").format(globCNC.vars["errline"])
        else:
            msg = ""

        state = globCNC.vars["state"]
        # FIXME:
        # msg += ERROR_CODES.get(
        #     state, _("No info available.\nPlease contact the author.")
        # )
        tk.messagebox.showinfo(_("State: {}").format(state), msg, parent=self)
