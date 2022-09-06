""" This file was created due to the refactoring of
    ToolsPage.py

    Authors:
             @m1ch
"""

from globalVariables import N_
from globalConfig import icon as gicon

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
            image=gicon["stock32"],
            text=_("Stock"),
            compound="top",
            variable=app.tools.active,
            value="Stock",
            style='RibbonGroup.Toolbutton'
        )
        b.grid(row=row, column=col, rowspan=3, padx=2, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Stock material currently on machine"))
        self.addWidget(b)

        # ===
        col, row = 1, 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["material"],
            text=_("Material"),
            compound="left",
            variable=app.tools.active,
            value="Material",
            style='RibbonGroup.Toolbutton'
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Editable database of material properties"))
        self.addWidget(b)

        # ---
        row += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=gicon["endmill"],
            text=_("End Mill"),
            compound="left",
            variable=app.tools.active,
            value="EndMill",
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
            image=gicon["rename"],
            text=_("Rename"),
            compound="left",
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
            image=gicon["add"],
            text=_("Add"),
            compound="left",
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
            image=gicon["clone"],
            text=_("Clone"),
            compound="left",
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
            image=gicon["x"],
            text=_("Delete"),
            compound="left",
            style='RibbonGroup.Toolbutton',
        )
        b.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Delete selected operation/object"))
        self.addWidget(b)
        app.tools.addButton("delete", b)
