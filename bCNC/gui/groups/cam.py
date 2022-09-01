""" This file was created due to the refactoring of
    ToolsPage.py

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter.ttk import Style

import Utils
from globalVariables import N_

from .. import ribbon
from .. import cncribbon
from .. import utils

name = "CAMGroup"


# =============================================================================
# CAM Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(self, master, N_("CAM"), app)
        self.grid3rows()

        # ===
        col, row = 0, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["cut32"],
            text=_("Cut"),
            compound="top",
            anchor="w",
            variable=app.tools.active,
            value="Cut",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, rowspan=3, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Cut for the full stock thickness selected code"))
        self.addWidget(b)

        col += 1
        # Find plugins in the plugins directory and load them
        for group in ["CAM_Core+"]:
            for tool in app.tools.pluginList():
                if tool.group != group:
                    continue
                # ===
                if tool.oneshot:
                    b = utils.LabelButton(
                        self.frame,
                        image=Utils.icons[tool.icon + "32"],
                        text=_(tool.name),
                        compound="top",
                        anchor="w",
                        command=lambda s=self, a=app, t=tool: a.tools[
                            t.name.upper()
                        ].execute(a),
                        # command=tool.execute,
                        style='RibbonGroup.Toolbutton',
                    )
                else:
                    b = utils.LabelRadiobutton(
                        self.frame,
                        image=Utils.icons[tool.icon + "32"],
                        text=tool.name,
                        compound="top",
                        anchor="w",
                        variable=app.tools.active,
                        value=tool.name,
                        # background=ribbon._BACKGROUND,
                        style='RibbonGroup.Toolbutton',
                    )

                b.grid(row=row, column=col, rowspan=3,
                       padx=1, pady=0, sticky="nsew")
                utils.ToolTip(b, tool.__doc__)
                self.addWidget(b)

                col += 1

        # ===
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["profile32"],
            text=_("Profile"),
            compound="top",
            anchor="w",
            variable=app.tools.active,
            value="Profile",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, rowspan=3, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Perform a profile operation on selected code"))
        self.addWidget(b)

        # ===
        col += 1
        row = 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["pocket"],
            text=_("Pocket"),
            compound="left",
            anchor="w",
            variable=app.tools.active,
            value="Pocket",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Perform a pocket operation on selected code"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["drill"],
            text=_("Drill"),
            compound="left",
            anchor="w",
            variable=app.tools.active,
            value="Drill",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Insert a drill cycle on current objects/location"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["tab"],
            text=_("Tabs"),
            compound="left",
            anchor="w",
            variable=app.tools.active,
            value="Tabs",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Insert holding tabs"))
        self.addWidget(b)

        # ---
        col += 1
        row = 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["island"],
            text=_("Island"),
            compound="left",
            anchor="w",
            command=lambda s=app: s.insertCommand("ISLAND", True),
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Toggle island"))
        self.addWidget(b)

        # ---
        row += 1

        # Find plugins in the plugins directory and load them
        for group in ["CAM_Core", "CAM"]:
            for tool in app.tools.pluginList():
                if tool.group != group:
                    continue
                # ===
                if tool.oneshot:
                    b = utils.LabelButton(
                        self.frame,
                        image=Utils.icons[tool.icon],
                        text=_(tool.name),
                        compound="left",
                        anchor="w",
                        command=lambda s=self, a=app, t=tool: a.tools[
                            t.name.upper()
                        ].execute(a),
                        style='RibbonGroup.Toolbutton',
                    )
                else:
                    b = utils.LabelRadiobutton(
                        self.frame,
                        image=Utils.icons[tool.icon],
                        text=tool.name,
                        compound="left",
                        anchor="w",
                        variable=app.tools.active,
                        value=tool.name,
                        # background=ribbon._BACKGROUND,
                        style='RibbonGroup.Toolbutton',
                    )

                b.grid(row=row, column=col, padx=2, pady=0, sticky="nsew")
                utils.ToolTip(b, tool.__doc__)
                self.addWidget(b)

                row += 1
                if row == 3:
                    col += 1
                    row = 0

        self.add_menu()

    def add_menu(self):
        self.label.menu = tk.Menu(self.label, tearoff=False)
        self.label["menu"] = self.label.menu
        menu = self.label.menu
        for group in ("Artistic", "Generator", "Development"):
            submenu = tk.Menu(menu, tearoff=False)
            menu.add_cascade(label=group, menu=submenu)
            # Find plugins in the plugins directory and load them
            for tool in self.app.tools.pluginList():
                if tool.group != group:
                    continue
                # cmd = lambda a=self.app, t=tool: a.tools[t.name.upper()
                #         ].execute(a),
                if tool.oneshot:
                    cmd = self.app.tools[tool.name.upper()].execute
                    submenu.add_command(
                        label=_(tool.name),
                        image=Utils.icons[tool.icon],
                        compound="left",
                        command=lambda cmd=cmd, a=self.app: cmd(a)
                    )
                else:
                    val = tool.name
                    cmd = self.app.tools.active.set
                    submenu.add_command(
                        label=_(tool.name),
                        image=Utils.icons[tool.icon],
                        compound="left",
                        command=lambda cmd=cmd, v=val: cmd(v)
                        # variable=self.app.tools.active,
                        # value=tool.name,
                    )

    # ----------------------------------------------------------------------
    # def createMenu(self):
    #     # FIXME: No redefinition required!
    #     menu = tk.Menu(self, tearoff=False)
    #     for group in ("Artistic", "Generator", "Development"):
    #         submenu = tk.Menu(menu, tearoff=False)
    #         menu.add_cascade(label=group, menu=submenu)
    #         # Find plugins in the plugins directory and load them
    #         for tool in self.app.tools.pluginList():
    #             if tool.group != group:
    #                 continue
    #             if tool.oneshot:
    #                 submenu.add_command(
    #                     label=_(tool.name),
    #                     image=Utils.icons[tool.icon],
    #                     compound="left",
    #                     command=lambda s=self, a=self.app, t=tool: a.tools[
    #                         t.name.upper()
    #                     ].execute(a),
    #                 )
    #             else:
    #                 submenu.add_radiobutton(
    #                     label=_(tool.name),
    #                     image=Utils.icons[tool.icon],
    #                     compound="left",
    #                     variable=self.app.tools.active,
    #                     value=tool.name,
    #                 )
    #     return menu
