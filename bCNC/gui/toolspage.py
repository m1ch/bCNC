# $Id$
#
# Author:       vvlachoudis@gmail.com
# Date: 24-Aug-2014

import glob
import os
import sys
import traceback
from operator import attrgetter
import tkinter as tk

from globalConfig import config as gconfig
from globalConfig import icon as gicon
from globalConstants import __prg__, __prgpath__

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


class Tools:
    """Tools container class"""

    def __init__(self,):  # gcode):
        from pydoc import locate

        tools = ("camera",
                 "config",
                 "font",
                 "color",
                 "controller",
                 "cut",
                 "drill",
                 "endmill",
                 "events",
                 "material",
                 "pocket",
                 "profile",
                 "shortcut",
                 "stock",
                 "tabs")

        # self.gcode = gcode
        self.inches = False
        self.digits = 4
        self.active = tk.StringVar()

        self.tools = {}
        self.buttons = {}
        self.widget = {}
        self.listbox = None

        for cls in tools:
            mod = locate(f"tools.{cls}")
            tool = mod.Tool(self)
            self.addTool(tool)

        # Load plugins:
        for name, module in gconfig.items("_plugins"):
            my_class = locate(f"{module}.Tool")
            plugin = my_class(self)
            self.addTool(plugin)

        return  # FIXME
        # Find plugins in the plugins directory and load them
        for f in glob.glob(f"{__prgpath__}/plugins/*.py"):
            name, ext = os.path.splitext(os.path.basename(f))

            try:
                my_class = locate(f"plugins.{name}.Tool")
            except (ImportError, AttributeError):
                typ, val, tb = sys.exc_info()
                traceback.print_exception(typ, val, tb)
                return
            tool = my_class(self)
            self.addTool(tool)

    # ----------------------------------------------------------------------
    def addTool(self, tool):
        self.tools[tool.name.upper()] = tool

    # ----------------------------------------------------------------------
    # Return a list of plugins
    # ----------------------------------------------------------------------
    def pluginList(self):
        plugins = [x for x in self.tools.values() if x.plugin]
        return sorted(plugins, key=attrgetter("name"))

    # ----------------------------------------------------------------------
    def setListbox(self, listbox):
        self.listbox = listbox

    # ----------------------------------------------------------------------
    def setWidget(self, name, widget):
        self.widget[name] = widget

    # ----------------------------------------------------------------------
    def __getitem__(self, name):
        return self.tools[name.upper()]

    # ----------------------------------------------------------------------
    def getActive(self):
        try:
            return self.tools[self.active.get().upper()]
        except Exception:
            self.active.set("CNC")
            return self.tools["CNC"]

    # ----------------------------------------------------------------------
    def setActive(self, value):
        self.active.set(value)

    # ----------------------------------------------------------------------
    def toMm(self, value):
        if self.inches:
            return value * 25.4
        else:
            return value

    # ----------------------------------------------------------------------
    def fromMm(self, value):
        if self.inches:
            return value / 25.4
        else:
            return value

    # ----------------------------------------------------------------------
    def names(self):
        lst = [x.name for x in self.tools.values()]
        lst.sort()
        return lst

    # ----------------------------------------------------------------------
    # Load from config file
    # ----------------------------------------------------------------------
    def loadConfig(self):
        self.active.set(gconfig.getstr(__prg__, "tool", "CNC"))
        for tool in self.tools.values():
            tool.load()

    # ----------------------------------------------------------------------
    # Save to config file
    # ----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr(__prg__, "tool", self.active.get())
        for tool in self.tools.values():
            tool.save()

    # ----------------------------------------------------------------------
    # def cnc(self):
    #     return globGCode.cnc

    # ----------------------------------------------------------------------
    def addButton(self, name, button):
        self.buttons[name] = button

    # ----------------------------------------------------------------------
    def activateButtons(self, tool):
        for btn in self.buttons.values():
            btn.config(state="disabled")
        for name in tool.buttons:
            self.buttons[name].config(state="normal")
        self.buttons["exe"].config(text=self.active.get())

        # Update execute button with plugin icon if available
        icon = self.tools[self.active.get().upper()].icon
        if icon is None:
            icon = "gear"
        self.buttons["exe"].config(image=gicon[icon])
