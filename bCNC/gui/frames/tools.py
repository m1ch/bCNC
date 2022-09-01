""" This file was created due to the refactoring of
    ToolsPage.py - ToolsFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from globalConfig import config as gconfig
from .. import tkextra
import Utils

from .. import cncribbon

_EXE_FONT = ("Helvetica", 12, "bold")


name = "ToolsFrame"


# =============================================================================
# Tools Frame
# =============================================================================
class SideFrame(cncribbon.PageFrame):
    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, "CAM", app)
        self.tools = app.tools

        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(expand=True, fill="both")

        frame = ttk.Frame(paned)
        paned.add(frame)

        b = ttk.Button(
            frame,
            text=_("Execute"),
            image=Utils.icons["gear"],
            compound="left",
            # foreground="DarkRed",
            # activeforeground="DarkRed",
            # activebackground="LightYellow",
            # font=_EXE_FONT,
            command=self.execute,
        )
        b.pack(side="top", fill="x")
        self.tools.addButton("exe", b)

        self.toolList = tkextra.MultiListbox(
            frame,
            ((_("Name"), 24, None), (_("Value"), 12, None)),
            height=20,
            header=False,
            stretch="last",
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        )
        self.toolList.sortAssist = None
        self.toolList.pack(fill="both", expand=True)
        self.toolList.bindList("<Double-1>", self.help)
        self.toolList.bindList("<Return>", self.edit)
        self.toolList.bindList("<Key-space>", self.edit)
        self.toolList.listbox(1).bind("<ButtonRelease-1>", self.edit)
        self.tools.setListbox(self.toolList)
        self.addWidget(self.toolList)

        frame = ttk.Frame(paned)
        paned.add(frame)

        toolHelp = ScrolledText(frame, width=20, height=5)
        # toolHelp = tk.Text(frame, width=20, height=5)
        toolHelp.pack(side="left", expand=True, fill="both")
        # scroll = tk.Scrollbar(frame, command=toolHelp.yview)
        # scroll.pack(side="right", fill="y")
        # toolHelp.configure(yscrollcommand=scroll.set)
        self.addWidget(toolHelp)
        toolHelp.config(state="disabled")

        self.tools.setWidget("paned", paned)
        self.tools.setWidget("toolHelpFrame", frame)
        self.tools.setWidget("toolHelp", toolHelp)

        app.tools.active.trace("w", self.change)
        self.change()

    # ----------------------------------------------------------------------
    # Populate listbox with new values
    # ----------------------------------------------------------------------
    def change(self, a=None, b=None, c=None):
        tool = self.tools.getActive()
        tool.beforeChange(self.app)
        tool.populate()
        tool.update()
        self.tools.activateButtons(tool)

    populate = change

    # ----------------------------------------------------------------------
    # Edit tool listbox
    # ----------------------------------------------------------------------
    def help(self, event=None, rename=False):
        item = self.toolList.get(self.toolList.curselection())[0]
        for var in self.tools.getActive().variables:
            if var[3] == item or _(var[3]) == item:
                varname = var[0]
                helpname = f"Help for ({varname}) {item}"
                if len(var) > 4 and var[4] is not None:
                    helptext = var[4]
                else:
                    helptext = f"{helpname}:\nnot available yet!"
                tk.messagebox.showinfo(helpname, helptext)

    # ----------------------------------------------------------------------
    # Edit tool listbox
    # ----------------------------------------------------------------------
    def edit(self, event=None):
        sel = self.toolList.curselection()
        if not sel:
            return
        if sel[0] == 0 and (event is None or event.keysym == 0):
            self.tools.getActive().rename()
        else:
            self.tools.getActive().edit(event)

    # ----------------------------------------------------------------------
    def execute(self, event=None):
        self.tools.getActive().execute(self.app)

    # ----------------------------------------------------------------------
    def add(self, event=None):
        self.tools.getActive().add()

    # ----------------------------------------------------------------------
    def delete(self, event=None):
        self.tools.getActive().delete()

    # ----------------------------------------------------------------------
    def clone(self, event=None):
        self.tools.getActive().clone()

    # ----------------------------------------------------------------------
    def rename(self, event=None):
        self.tools.getActive().rename()

    # ----------------------------------------------------------------------
