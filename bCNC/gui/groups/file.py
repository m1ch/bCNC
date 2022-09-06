""" This file was created due to the refactoring of
    FilePage.py

    Authors:
             @m1ch
"""

import os
import tkinter as tk

from globalVariables import N_
from globalConfig import config as gconfig
from globalConfig import icon as gicon
from globalConstants import _maxRecent

from .. import styles
from .. import utils
from .. import cncribbon

name = "FileGroup"


# =============================================================================
# Recent Menu button
# =============================================================================
class _RecentMenuButton(utils.MenuButton):
    # ----------------------------------------------------------------------
    def createMenu(self):
        menu = tk.Menu(self, tearoff=0, activebackground=styles.ACTIVE_COLOR)
        for i in range(_maxRecent):
            filename = gconfig.getrecent(i)
            if filename is None:
                break
            path = os.path.dirname(filename)
            fn = os.path.basename(filename)
            menu.add_command(
                label="%d %s" % (i + 1, fn),
                compound="left",
                image=gicon["new"],
                accelerator=path,  # Show as accelerator in order to be aligned
                command=lambda s=self, i=i: s.event_generate(
                    "<<Recent%d>>" % (i)),
            )
        if i == 0:  # no entry
            self.event_generate("<<Open>>")
            return None
        return menu


# =============================================================================
# File Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("File"), app)
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<<New>>",
            image=gicon["new32"],
            text=_("New"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("New gcode/dxf file"))
        self.addWidget(b)

        # ---
        col, row = 1, 0

        b = utils.LabelButton(
            self.frame,
            self,
            "<<Open>>",
            image=gicon["open32"],
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=2, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Open existing gcode/dxf file [Ctrl-O]"))
        self.addWidget(b)

        col, row = 1, 2
        b = _RecentMenuButton(
            self.frame,
            None,
            text=_("Open"),
            image=gicon["triangle_down"],
            style='RibbonGroup.TButton',
            compound="right",
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Open recent file"))
        self.addWidget(b)

        # ---
        col, row = 2, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Import>>",
            image=gicon["import32"],
            text=_("Import"),
            compound="top",
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Import gcode/dxf file"))
        self.addWidget(b)

        # ---
        col, row = 3, 0
        b = utils.LabelButton(
            self.frame,
            self,
            "<<Save>>",
            image=gicon["save32"],
            command=app.save,
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, rowspan=2, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Save gcode/dxf file [Ctrl-S]"))
        self.addWidget(b)

        col, row = 3, 2
        b = utils.LabelButton(
            self.frame,
            self,
            "<<SaveAs>>",
            text=_("Save"),
            image=gicon["triangle_down"],
            compound="right",
            style='RibbonGroup.TButton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Save gcode/dxf AS"))
        self.addWidget(b)
