""" This file was created due to the refactoring of
    ToolsPage.py

    Authors:
             @m1ch
"""

import Utils
from globalVariables import N_


from .. import ribbon
from .. import cncribbon
from .. import utils

name = "DataBaseGroup"


# =============================================================================
# DataBase Group
# =============================================================================
class RibbonGroup(cncribbon.ButtonGroup):
    def __init__(self, master, app):
        cncribbon.ButtonGroup.__init__(self, master, N_("Database"), app)
        self.grid3rows()

        # ---
        col, row = 0, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["stock32"],
            text=_("Stock"),
            compound="top",
            anchor="w",
            variable=app.tools.active,
            value="Stock",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton'
        )
        b.grid(row=row, column=col, rowspan=3, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Stock material currently on machine"))
        self.addWidget(b)

        # ===
        col, row = 1, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["material"],
            text=_("Material"),
            compound="left",
            anchor="w",
            variable=app.tools.active,
            value="Material",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton'
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Editable database of material properties"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["endmill"],
            text=_("End Mill"),
            compound="left",
            anchor="w",
            variable=app.tools.active,
            value="EndMill",
            # background=ribbon._BACKGROUND,
            style='RibbonGroup.Toolbutton'
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Editable database of EndMills properties"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<ToolRename>>",
            image=Utils.icons["rename"],
            text=_("Rename"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Edit name of current operation/object"))
        self.addWidget(b)
        app.tools.addButton("rename", b)

        # ===
        col, row = 2, 0
        b = utils.LabelButton(
            self.frame,
            app,
            "<<ToolAdd>>",
            image=Utils.icons["add"],
            text=_("Add"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Add a new operation/object"))
        self.addWidget(b)
        app.tools.addButton("add", b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<ToolClone>>",
            image=Utils.icons["clone"],
            text=_("Clone"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Clone selected operation/object"))
        self.addWidget(b)
        app.tools.addButton("clone", b)

        # ---
        row += 1
        b = utils.LabelButton(
            self.frame,
            app,
            "<<ToolDelete>>",
            image=Utils.icons["x"],
            text=_("Delete"),
            compound="left",
            anchor="w",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Delete selected operation/object"))
        self.addWidget(b)
        app.tools.addButton("delete", b)
