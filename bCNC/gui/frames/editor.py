""" This file was created due to the refactoring of
    EditorPage.py - EditorFrame

    Authors:
             @m1ch
"""

from tkinter import ttk

from globalConfig import config as gconfig
from .. import cnclist
from .. import cncribbon


# =============================================================================
# Main Frame of Editor
# =============================================================================
class SideFrame(cncribbon.PageFrame):
    def __init__(self, master, app):
        cncribbon.PageFrame.__init__(self, master, "Editor", app)
        self.editor = cnclist.CNCListbox(
            self,
            app,
            selectmode="extended",
            exportselection=0,
            background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        )
        self.editor.pack(side="left", expand=True, fill="both")
        self.addWidget(self.editor)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.editor.yview)
        sb.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=sb.set)
