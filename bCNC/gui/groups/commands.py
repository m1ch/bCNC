""" This file was created due to the refactoring of
    TerminalPage.py

    Authors:
             @m1ch
"""

import Utils
from globalVariables import N_
from .. import commands
from .. import utils
from .. import cncribbon

name = "CommandsGroup"


# =============================================================================
# Commands Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(
            self,
            master,
            N_("Commands"),
            app,
            [
                (_("Restore Settings"),
                 "grbl_settings", commands.grblRestoreSettings),
                (_("Restore Workspace"),
                 "grbl_params", commands.grblRestoreWCS),
                (_("Restore All"), "reset", commands.grblRestoreAll),
            ],
        )
        self.grid3rows()

        # Disable state for some SMOOTHIE commands
        # state = (app.sender.controller in
        #          ("GRBL0", "GRBL1") and "normal" or DISABLED,)
        state = "normal"  # FIXME
        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_settings"],
            text=_("Settings"),
            compound="left",
            anchor="w",
            state=state,
            command=commands.viewSettings,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$$ Display settings of Grbl"))
        if state == "normal":
            self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_params"],
            text=_("Parameters"),
            compound="left",
            anchor="w",
            command=commands.viewParameters,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$# Display parameters of Grbl"))
        self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_state"],
            text=_("State"),
            compound="left",
            anchor="w",
            command=commands.viewState,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$G Display state of Grbl"))
        self.addWidget(b)

        # ---
        col += 1
        row = 0
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_build"],
            text=_("Build"),
            compound="left",
            anchor="w",
            command=commands.viewBuild,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$I Display build information of Grbl"))
        self.addWidget(b)

        row += 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_startup"],
            text=_("Startup"),
            compound="left",
            anchor="w",
            state=state,
            command=commands.viewStartup,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$N Display startup configuration of Grbl"))
        if state == "normal":
            self.addWidget(b)

        row += 1
        # FIXME Checkbutton!!!!!
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_check"],
            text=_("Check gcode"),
            compound="left",
            anchor="w",
            state=state,
            command=commands.checkGcode,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$C Enable/Disable checking of gcode"))
        if state == "normal":
            self.addWidget(b)

        # ---
        col += 1
        row = 1
        b = utils.LabelButton(
            self.frame,
            image=Utils.icons["grbl_help"],
            text=_("Help"),
            compound="left",
            anchor="w",
            command=commands.grblHelp,
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("$ Display build information of Grbl"))
        self.addWidget(b)
