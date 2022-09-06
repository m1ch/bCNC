""" This file was created due to the refactoring of
    TerminalPage.py - TerminalFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

# from globalConfig import config as gconfig
from globalVariables import N_
from .. import utils
from .. import cncribbon


# =============================================================================
class SideFrame(cncribbon.PageFrame):
    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, N_("Terminal"), app)

        # ---
        # FIXME: Replase Listbox with treeview
        self.terminal = tk.Listbox(
            self,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            selectmode="extended",
            height=5,
        )
        self.terminal.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical",
                           command=self.terminal.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.terminal.config(yscrollcommand=sb.set)
        self.terminal.bind("<<Copy>>", self.copy)
        self.terminal.bind("<Control-Key-c>", self.copy)
        utils.ToolTip(self.terminal,
                      _("Terminal communication with controller"))

        # ---
        self.buffer = tk.Listbox(
            self,
            background="LightYellow",
            selectmode="extended",
            height=5
        )
        self.buffer.grid(row=1, column=0, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.buffer.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.buffer.config(yscrollcommand=sb.set)
        utils.ToolTip(self.buffer, _("Buffered commands"))
        self.buffer.bind("<<Copy>>", self.copy)
        self.buffer.bind("<Control-Key-c>", self.copy)

        # ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    # ----------------------------------------------------------------------
    def clear(self, event=None):
        self.terminal.delete(0, "end")

    # ----------------------------------------------------------------------
    def copy(self, event):
        self.clipboard_clear()
        self.clipboard_append(
            "\n".join(
                [event.widget.get(x) for x in event.widget.curselection()])
        )
        return "break"
