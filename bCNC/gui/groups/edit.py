""" This file was created due to the refactoring of
    EditorPage.py

    Authors:
             @m1ch
"""

from .. import utils
from .. import cncribbon

from globalVariables import N_
from globalConfig import icon as gicon

name = "EditGroup"


# =============================================================================
# Edit Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(
            self,
            master,
            N_("Edit"),
            app,
            [
                (
                    _("Autolevel"),
                    "level",
                    lambda a=app: a.insertCommand("AUTOLEVEL", True),
                ),
                (
                    _("Color"),
                    "color",
                    lambda a=app: a.event_generate("<<ChangeColor>>"),
                ),
                (
                    _("Import"),
                    "load",
                    lambda a=app: a.insertCommand("IMPORT", True)
                ),
                (
                    _("Postprocess Inkscape g-code"),
                    "inkscape",
                    lambda a=app: a.insertCommand("INKSCAPE all", True),
                ),
                (
                    _("Round"),
                    "digits",
                    lambda s=app: s.insertCommand("ROUND", True)
                ),
            ],
        )
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<Add>>",
            image=gicon["add"],
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Insert a new block or line of code [Ins or Ctrl-Enter]")
        )
        self.addWidget(b)

        menulist = [
            (
                _("Line"),
                "add",
                lambda a=self.app: a.event_generate("<<AddLine>>")
            ),
            (
                _("Block"),
                "add",
                lambda a=self.app: a.event_generate("<<AddBlock>>")
            ),
        ]
        b = utils.MenuButton(
            self.frame,
            menulist,
            text=_("Add"),
            image=gicon["triangle_down"],
            compound="right",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col + 1, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b, _("Insert a new block or line of code [Ins or Ctrl-Enter]")
        )

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<Clone>>",
            image=gicon["clone"],
            text=_("Clone"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Clone selected lines or blocks [Ctrl-D]"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<Delete>>",
            image=gicon["x"],
            text=_("Delete"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Delete selected lines or blocks [Del]"))
        self.addWidget(b)

        # ---
        col, row = 2, 0
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<EnableToggle>>",
            image=gicon["toggle"],
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _("Toggle enable/disable block of g-code [Ctrl-L]")
        )
        self.addWidget(b)

        menulist = [
            (
                _("Enable"),
                "enable",
                lambda a=self.app: a.event_generate("<<Enable>>")
            ),
            (
                _("Disable"),
                "disable",
                lambda a=self.app: a.event_generate("<<Disable>>"),
            ),
        ]
        b = utils.MenuButton(
            self.frame,
            menulist,
            text=_("Active"),
            image=gicon["triangle_down"],
            compound="right",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col + 1, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Enable or disable blocks of gcode"))

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<Expand>>",
            image=gicon["expand"],
            text=_("Expand"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(
            b,
            _("Toggle expand/collapse blocks of gcode [Ctrl-E]")
        )
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<Comment>>",
            image=gicon["comment"],
            text=_("Comment"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("(Un)Comment selected lines"))
        self.addWidget(b)
        # ---
        col += 2
        row = 0
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<Join>>",
            image=gicon["union"],
            text=_("Join"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Join selected blocks"))
        self.addWidget(b)
        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            self.app,
            "<<Split>>",
            image=gicon["cut"],
            text=_("Split"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Split selected blocks"))
        self.addWidget(b)
