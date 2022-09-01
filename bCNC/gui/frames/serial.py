""" This file was created due to the refactoring of
    FilePage.py - SerialFrame

    Authors:
             @m1ch
"""

import sys
import tkinter as tk
from tkinter import ttk

import Utils
from globalConfig import config as gconfig
from sender import globSender

from .. import utils
from .. import commands

try:
    from serial.tools.list_ports import comports
except Exception:
    print("Using fallback Utils.comports()!")
    from Utils import comports

BAUDS = [2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400]


name = "SerialFrame"


# =============================================================================
# Serial Frame
# =============================================================================
class SideFrame(utils.PageLabelFrame):
    def __init__(self, master, app):
        utils.PageLabelFrame.__init__(
            self, master, app, "Serial", _("Serial"))
        self.autostart = tk.BooleanVar()

        # ---
        frame = self.frame
        col, row = 0, 0
        b = ttk.Label(frame, text=_("Port:"))
        b.grid(row=row, column=col, sticky="e")
        self.addWidget(b)

        # FIXME: renew the selection part of serial
        # FIXME: disconnect if port, baud, or controller changes
        self.portCombo = ttk.Combobox(frame, width=16)
        self.portCombo['state'] = 'readonly'
        self.portCombo.bind('<<ComboboxSelected>>', self.comportClean)
        self.portCombo['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # self.portCombo = tkextra.Combobox(
        #     frame,
        #     False,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     width=16,
        #     command=self.comportClean,
        # )
        self.portCombo.grid(row=row, column=col + 1, sticky="ew")
        utils.ToolTip(
            self.portCombo, _("Select (or manual enter) port to connect")
        )
        self.portCombo.set(gconfig.getstr("Connection", "port"))
        self.addWidget(self.portCombo)

        self.comportRefresh()

        # ---
        row += 1
        b = ttk.Label(frame, text=_("Baud:"))
        b.grid(row=row, column=col, sticky="e")

        self.baudCombo = ttk.Combobox(frame)
        self.baudCombo['state'] = 'readonly'
        self.baudCombo['values'] = BAUDS
        self.baudCombo['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # self.baudCombo = tkextra.Combobox(
        #     frame, True, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        # )
        # self.baudCombo.fill(BAUDS)
        self.baudCombo.grid(row=row, column=col + 1, sticky="ew")
        utils.ToolTip(self.baudCombo, _("Select connection baud rate"))
        self.baudCombo.set(gconfig.getstr("Connection", "baud", "115200"))
        self.addWidget(self.baudCombo)

        # ---
        row += 1
        b = ttk.Label(frame, text=_("Controller:"))
        b.grid(row=row, column=col, sticky="e")

        self.ctrlCombo = ttk.Combobox(frame)
        self.ctrlCombo['state'] = 'readonly'
        self.ctrlCombo['values'] = list(gconfig.getcontrollerslist())
        self.ctrlCombo.bind('<<ComboboxSelected>>', self.ctrlChange)
        self.ctrlCombo['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        self.ctrlCombo.set(gconfig.getstr("Connection", "controller", "GRBL1"))
        # self.ctrlCombo = tkextra.Combobox(
        #     frame,
        #     True,
        #    background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        #     command=self.ctrlChange,
        # )
        # self.ctrlCombo.fill(gconfig.getcontrollerslist())
        self.ctrlCombo.grid(row=row, column=col + 1, sticky="ew")
        utils.ToolTip(self.ctrlCombo, _("Select controller board"))
        self.addWidget(self.ctrlCombo)

        # ---
        row += 1
        b = ttk.Checkbutton(frame,
                            text=_("Connect on startup"),
                            variable=self.autostart)
        b.grid(row=row, column=col, columnspan=2, sticky="w")
        utils.ToolTip(
            b, _("Connect to serial on startup of the program"))
        self.autostart.set(gconfig.getbool("Connection", "openserial"))
        self.addWidget(b)

        # ---
        col += 2
        self.comrefBtn = utils.LabelButton(
            frame,
            image=Utils.icons["refresh"],
            text=_("Refresh"),
            compound="top",
            command=lambda s=self: s.comportRefresh(True),
            style='Panel.TButton',
        )
        self.comrefBtn.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(self.comrefBtn, _("Refresh list of serial ports"))

        # ---
        row = 0

        self.connectBtn = utils.LabelButton(
            frame,
            self,
            "<<Connect>>",
            image=Utils.icons["serial48"],
            text=_("Open"),
            compound="top",
            # command=lambda s=self: s.event_generate("<<Connect>>"),
            style='Panel.TButton',
        )
        self.connectBtn.grid(
            row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew"
        )
        utils.ToolTip(self.connectBtn, _("Open/Close serial port"))
        self.grid_columnconfigure(1, weight=1)

    # -----------------------------------------------------------------------
    def ctrlChange(self, event=None):
        gconfig.setstr("Connection", "controller",self.ctrlCombo.get())
        # globSender.controllerSet(self.ctrlCombo.get())
        # self.app.mcontrol = globSender.mcontrol  # FIXME: Should not be necessary

    # -----------------------------------------------------------------------
    def comportClean(self, event=None):
        clean = self.portCombo.get().split("\t")[0]
        if self.portCombo.get() != clean:
            print("comport fix")
            self.portCombo.set(clean)

    # -----------------------------------------------------------------------
    def comportsGet(self):
        try:
            return comports(include_links=True)
        except TypeError:
            print("Using old style comports()!")
            return comports()

    def comportRefresh(self, dbg=False):
        # Detect devices
        hwgrep = []
        for i in self.comportsGet():
            if dbg:
                # Print list to console if requested
                comport = ""
                for j in i:
                    comport += j + "\t"
                print(comport)
            for hw in i[2].split(" "):
                hwgrep += ["hwgrep://" + hw + "\t" + i[1]]

        # Populate combobox
        devices = sorted(x[0] + "\t" + x[1] for x in self.comportsGet())
        devices += [""]
        devices += sorted(set(hwgrep))
        devices += [""]
        # Pyserial raw spy currently broken in python3
        # TODO: search for python3 replacement for raw spy
        if sys.version_info[0] != 3:
            devices += sorted(
                "spy://" + x[0] + "?raw&color" + "\t(Debug) " + x[1]
                for x in self.comportsGet()
            )
        else:
            devices += sorted(
                "spy://" + x[0] + "?color" + "\t(Debug) " + x[1]
                for x in self.comportsGet()
            )
        devices += ["", "socket://localhost:23", "rfc2217://localhost:2217"]

        # Clean neighbour duplicates
        devices_clean = []
        devprev = ""
        for i in devices:
            if i.split("\t")[0] != devprev:
                devices_clean += [i]
            devprev = i.split("\t")[0]

        self.portCombo['values'] = devices_clean
        # self.portCombo.fill(devices_clean)

    # -----------------------------------------------------------------------
    def saveConfig(self):
        # Connection
        gconfig.setstr("Connection", "controller", globSender.controller)
        gconfig.setstr(
            "Connection", "port", self.portCombo.get().split("\t")[0])
        gconfig.setstr("Connection", "baud", self.baudCombo.get())
        gconfig.setbool("Connection", "openserial", self.autostart.get())

    # -----------------------------------------------------------------------
    def connectBtnStyle(self, style):
        self.connectBtn['style'] = style
