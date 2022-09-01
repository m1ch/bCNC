""" This file was created due to the refactoring of
    ControlPage.py

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from cnc import globCNC
from gcode import globGCode
from sender import globSender


from .. import utils
from .. import cncribbon


name = "abcDROFrame"


# =============================================================================
# DRO Frame ABC
# =============================================================================
class SideFrame(utils.CollapsiblePageLabelFrame):

    dro_status = ("Helvetica", 12, "bold")
    dro_wpos = ("Helvetica", 12, "bold")
    dro_mpos = ("Helvetica", 12)

    def __init__(self, master, app):
        utils.CollapsiblePageLabelFrame.__init__(
            self, master, app, name="abcDRO", text=_("abcDRO"))

        frame = ttk.Frame(self.frame)
        frame.pack(side="top", fill="x")

        self.dro_status = gconfig.getfont(
            "dro.status", self.dro_status)
        self.dro_wpos = gconfig.getfont(
            "dro.wpos", self.dro_wpos)
        self.dro_mpos = gconfig.getfont(
            "dro.mpos", self.dro_mpos)

        row = 0
        col = 0
        ttk.Label(frame, text=_("abcWPos:")).grid(row=row, column=col)

        # work
        col += 1
        self.awork = ttk.Entry(
            frame,
            font=self.dro_wpos,
            style="Panel.TEntry",
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=8,
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.awork.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.awork, _("A work position (click to set)"))
        self.awork.bind("<FocusIn>", self.workFocus)
        self.awork.bind("<Return>", self.setA)
        self.awork.bind("<KP_Enter>", self.setA)

        # ---
        col += 1
        self.bwork = ttk.Entry(
            frame,
            font=self.dro_wpos,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=8,
            style="Panel.TEntry",
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.bwork.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.bwork, _("B work position (click to set)"))
        self.bwork.bind("<FocusIn>", self.workFocus)
        self.bwork.bind("<Return>", self.setB)
        self.bwork.bind("<KP_Enter>", self.setB)

        # ---
        col += 1
        self.cwork = ttk.Entry(
            frame,
            font=self.dro_wpos,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=8,
            style="Panel.TEntry",
            # relief="flat",
            # borderwidth=0,
            # justify="right",
        )
        self.cwork.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(self.cwork, _("C work position (click to set)"))
        self.cwork.bind("<FocusIn>", self.workFocus)
        self.cwork.bind("<Return>", self.setC)
        self.cwork.bind("<KP_Enter>", self.setC)

        # Machine
        row += 1
        col = 0
        ttk.Label(frame, text=_("MPos:")).grid(
            row=row, column=col, sticky="e"),

        col += 1
        self.amachine = ttk.Label(
            frame,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.amachine.grid(row=row, column=col, padx=1, sticky="ew")
        col += 1
        self.bmachine = ttk.Label(
            frame,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.bmachine.grid(row=row, column=col, padx=1, sticky="ew")

        col += 1
        self.cmachine = ttk.Label(
            frame,
            # font=self.dro_mpos,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            # anchor="e",
        )
        self.cmachine.grid(row=row, column=col, padx=1, sticky="ew")

        # Set buttons
        row += 1
        col = 1

        azero = ttk.Button(
            frame,
            text=_("A=0"),
            command=self.setA0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        azero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            azero, _("Set A coordinate to zero "
                     + "(or to typed coordinate in WPos)")
        )
        self.addWidget(azero)

        col += 1
        bzero = ttk.Button(
            frame,
            text=_("B=0"),
            command=self.setB0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        bzero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            bzero, _("Set B coordinate to zero "
                     + "(or to typed coordinate in WPos)")
        )
        self.addWidget(bzero)

        col += 1
        czero = ttk.Button(
            frame,
            text=_("C=0"),
            command=self.setC0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        czero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            czero, _("Set C coordinate to zero "
                     + "(or to typed coordinate in WPos)")
        )
        self.addWidget(czero)

        # Set buttons
        row += 1
        col = 1
        bczero = ttk.Button(
            frame,
            text=_("BC=0"),
            command=self.setBC0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        bczero.grid(row=row, column=col, pady=0, sticky="ew")
        utils.ToolTip(
            bczero, _("Set BC coordinate to zero "
                      + "(or to typed coordinate in WPos)")
        )
        self.addWidget(bczero)

        col += 1
        abczero = ttk.Button(
            frame,
            text=_("ABC=0"),
            command=self.setABC0,
            # activebackground="LightYellow",
            # padx=2,
            # pady=1,
        )
        abczero.grid(row=row, column=col, pady=0, sticky="ew", columnspan=2)
        utils.ToolTip(
            abczero, _("Set ABC coordinate to zero "
                       + "(or to typed coordinate in WPos)")
        )
        self.addWidget(abczero)

    # ----------------------------------------------------------------------

    def updateCoords(self):
        try:
            focus = self.focus_get()
        except Exception:
            focus = None
            if focus is not self.awork:
                self.awork.delete(0, "end")
                self.awork.insert(0, self.padFloat(globCNC.drozeropad,
                                                   globCNC.vars["wa"]))
            if focus is not self.bwork:
                self.bwork.delete(0, "end")
                self.bwork.insert(0, self.padFloat(globCNC.drozeropad,
                                                   globCNC.vars["wb"]))
            if focus is not self.cwork:
                self.cwork.delete(0, "end")
                self.cwork.insert(0, self.padFloat(globCNC.drozeropad,
                                                   globCNC.vars["wc"]))

            self.amachine["text"] = self.padFloat(globCNC.drozeropad,
                                                  globCNC.vars["ma"])
            self.bmachine["text"] = self.padFloat(globCNC.drozeropad,
                                                  globCNC.vars["mb"])
            self.cmachine["text"] = self.padFloat(globCNC.drozeropad,
                                                  globCNC.vars["mc"])

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

    def setA0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, None, "0", None, None)

    # ----------------------------------------------------------------------
    def setB0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, None, None, "0", None)

    # ----------------------------------------------------------------------
    def setC0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, None, None, None, "0")

    # ----------------------------------------------------------------------
    def setBC0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, None, "0", "0", None)

    # ----------------------------------------------------------------------
    def setABC0(self, event=None):
        globSender.mcontrol._wcsSet(None, None, None, "0", "0", "0")

    # ----------------------------------------------------------------------
    def setA(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.awork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(None, None, None, value, None, None)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def setB(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.bwork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(None, None, None, None, value, None)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def setC(self, event=None):
        if globSender.running:
            return
        try:
            value = round(eval(self.cwork.get(), None, globCNC.vars), 3)
            globSender.mcontrol._wcsSet(None, None, None, None, None, value)
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
            tk.messagebox.showinfo(
                _("State: {}").format(state), msg, parent=self)
