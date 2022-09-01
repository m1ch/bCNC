""" This file was created due to the refactoring of
    ToolsPage.py

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk

import Utils
from globalConfig import config as gconfig
from globalConstants import __LANGUAGES__
from globalVariables import N_


from .. import ribbon
from .. import cncribbon
from .. import utils

name = "ConfigGroup"


# =============================================================================
# Config
# =============================================================================
class RibbonGroup(cncribbon.ButtonMenuGroup):
    def __init__(self, master, app):
        cncribbon.ButtonMenuGroup.__init__(self, master, N_("Config"), app)
        self.add_menu((
            (_("User File"), "about", self.app.showUserFile),
            (_("Events"), "event", self._activateEvents),
            (_("Colors"), "color", self._activateColor),
            (_("Fonts"), "font", self._activateFont),
        ))

        self.grid3rows()

        # ===
        col, row = 0, 0
        f = ttk.Frame(self.frame, style='RibbonGroup.TFrame')
        f.grid(row=row, column=col, columnspan=2,
               padx=0, pady=0, sticky="nsew")

        b = ttk.Label(f,
                      image=Utils.icons["globe"],
                      style='RibbonGroup.TLabel')
        b.pack(side="left")

        # Create Language selector
        # Create a Tkinter variable
        self.language = tk.StringVar(master)
        self.language.set(gconfig.getlanguage())  # set the default option

        # Dictionary with options
        languages = list(sorted(__LANGUAGES__.values()))

        # FIXME: Replace by ttk.OptionMenu or ttk.ComboBox
        lang = ttk.Combobox(f, textvariable=self.language, width=16)
        lang['state'] = 'readonly'
        lang['values'] = languages
        # lang.bind('<<ComboboxSelected>>', self.waitChange)
        lang['background'] = gconfig.getstr(
            '_colors', "GLOBAL_CONTROL_BACKGROUND")
        # lang = ttk.OptionMenu(
        #     f,
        #     self.language,
        #     languages[0],
        #     *languages,
        #     style='RibbonGroup.TMenubutton',
        # )
        # lang.config(width=16)

        lang.pack(side="right", fill="x", expand=True)
        utils.ToolTip(
            lang, _("Change program language restart is required")
        )
        self.addWidget(lang)
        self.language.trace('w', self.languageChange)

        # ===
        row += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["config"],
            text=_("Config"),
            compound="left",
            # anchor="w",
            variable=app.tools.active,
            value="CNC",
            style='RibbonGroup.Toolbutton',
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Machine configuration for bCNC"))
        self.addWidget(b)

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["shortcut"],
            text=_("Shortcuts"),
            compound="left",
            # anchor="w",
            variable=app.tools.active,
            value="Shortcut",
            style='RibbonGroup.Toolbutton',
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Shortcuts configuration"))
        self.addWidget(b)

        # ---
        row += 1
        col = 0
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["arduino"],
            text=_("Controller"),
            compound="left",
            # anchor="w",
            variable=app.tools.active,
            value="Controller",
            style='RibbonGroup.Toolbutton',
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Controller (GRBL) configuration"))
        self.addWidget(b)

        # ---
        col += 1
        b = utils.LabelRadiobutton(
            self.frame,
            image=Utils.icons["camera"],
            text=_("Camera"),
            compound="left",
            # anchor="w",
            variable=app.tools.active,
            value="Camera",
            style='RibbonGroup.Toolbutton',
            # background=ribbon._BACKGROUND,
        )
        b.grid(row=row, column=col, padx=1, pady=0, sticky="nsew")
        utils.ToolTip(b, _("Camera Configuration"))
        self.addWidget(b)

    # ----------------------------------------------------------------------
    def languageChange(self, *args):
        lang = self.language.get()
        # find translation
        lang = Utils.getDictKeyByValue(__LANGUAGES__, lang)
        if lang:
            # do nothing if language has not changed
            if lang == gconfig.getlanguage():
                return
            gconfig.setlanguage(lang)
            tk.messagebox.showinfo(
                _("Language change"),
                _("Please restart the program."),
                parent=self.winfo_toplevel(),
            )
            return

    # ----------------------------------------------------------------------
    # def add_menu(self):
    #     self.label.menu = tk.Menu(self.label, tearoff=False)
    #     self.label["menu"] = self.label.menu
    #     menu = self.label.menu

    #     menu.add_command(
    #         label=_("User File"),
    #         image=Utils.icons["about"],
    #         compound="left",
    #         command=self.app.showUserFile,
    #     )
    #     menu.add_radiobutton(
    #         label=_("Events"),
    #         image=Utils.icons["event"],
    #         compound="left",
    #         variable=self.app.tools.active,
    #         value="Events",
    #     )
    #     menu.add_radiobutton(
    #         label=_("Colors"),
    #         image=Utils.icons["color"],
    #         compound="left",
    #         variable=self.app.tools.active,
    #         value="Color",
    #     )
    #     menu.add_radiobutton(
    #         label=_("Fonts"),
    #         image=Utils.icons["font"],
    #         compound="left",
    #         variable=self.app.tools.active,
    #         value="Font",
    #     )

    def _activateEvents(self):
        self.app.tools.active.set("Events")

    def _activateColor(self):
        self.app.tools.active.set("Color")

    def _activateFont(self):
        self.app.tools.active.set("Font")
