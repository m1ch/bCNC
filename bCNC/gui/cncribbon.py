# $Id$
#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015

import tkinter as tk
from tkinter import ttk

from . import ribbon
from . import tkextra
from . import commands

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


# =============================================================================
# Link to main app
# =============================================================================
class _LinkApp:
    def __init__(self, app):
        self.app = app

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    def addWidget(self, widget):
        self.app.widgets.append(widget)

    # ----------------------------------------------------------------------
    # Send a command to Grbl
    # ----------------------------------------------------------------------
    def sendGCode(self, cmd):
        commands.sendGCode(cmd)

    # ----------------------------------------------------------------------
    # Accept the user key if not editing any text
    # ----------------------------------------------------------------------
    def acceptKey(self, skipRun=False):
        return self.app.acceptKey(skipRun)

    # ----------------------------------------------------------------------
    def saveConfig(self):
        pass

    # ----------------------------------------------------------------------
    def loadConfig(self):
        pass


# =============================================================================
# Button Group, a group of widgets that will be placed in the ribbon
# =============================================================================
class ButtonGroup(ribbon.LabelGroup, _LinkApp):
    def __init__(self, master, name, app):
        ribbon.LabelGroup.__init__(self, master, name)
        _LinkApp.__init__(self, app)
        if ":" in name:
            self.label["text"] = name.split(":")[1]


# =============================================================================
# Button Group, a group of widgets that will be placed in the ribbon
# =============================================================================
class ButtonMenuGroup(ribbon.MenuGroup, _LinkApp):
    def __init__(self, master, name, app, menulist=None):
        ribbon.MenuGroup.__init__(self, master, name, menulist)
        _LinkApp.__init__(self, app)


# =============================================================================
# Page, Frame
# =============================================================================
class PageFrame(ttk.Frame, _LinkApp):
    def __init__(self, master, name, app):
        ttk.Frame.__init__(self, master)
        _LinkApp.__init__(self, app)
        self.name = name


# =============================================================================
# Page, LabelFrame
# =============================================================================
class PageLabelFrame(ttk.LabelFrame, _LinkApp):
    def __init__(self, master, name, name_alias_lng, app):
        ttk.LabelFrame.__init__(
            self, master, text=name_alias_lng, style="Panel.TLabelFrame.Label")
        _LinkApp.__init__(self, app)
        self.name = name


# =============================================================================
# Page, ExLabelFrame
# =============================================================================
class PageExLabelFrame(tkextra.ExLabelFrame, _LinkApp):
    def __init__(self, master, name, name_alias_lng, app):
        tkextra.ExLabelFrame.__init__(
            self, master, text=name_alias_lng, style='Panel.TLabelFrame.Label'
        )
        _LinkApp.__init__(self, app)
        self.name = name


# =============================================================================
# CNC Page interface between the basic Page class and the bCNC class
# =============================================================================
# class Page(ribbon.Page):
#     groups = {}
#     frames = {}

#     def __init__(self, master, app, **kw):
#         self.app = app
#         ribbon.Page.__init__(self, master, **kw)
#         self.register()

#     # ----------------------------------------------------------------------
#     # Should be overridden with the groups and frames to register
#     # ----------------------------------------------------------------------
#     def register(self):
#         pass

#     # ----------------------------------------------------------------------
#     # Register groups
#     # ----------------------------------------------------------------------
#     def _register(self, groups=None, frames=None):
#         from pydoc import locate
#         from globalConfig import config as gconfig

#         def register_group(group):
#             if group in self.app.groups:
#                 return
#             # if g not in self.app.groups:
#             #     continue # FIXME: Shall this rais an error?
#             module_path = gconfig.getstr("_guigroups", group)
#             group_class = locate(module_path)
#             w = group_class.RibbonGroup(self.master._ribbonFrame, self.app)
#             self.app.groups[w.name] = w

#         if groups:
#             if type(groups) is str:
#                 register_group(groups)
#             else:
#                 for g in groups:
#                     register_group(g)

#         def register_frame(frame):
#             if frame in self.app.frames:
#                 return
#             # if f not in self.app.groups:
#             #     continue # FIXME: Shall this rais an error?
#             module_path = gconfig.getstr("_guiframes", frame)
#             frame_class = locate(module_path)
#             w = frame_class.SideFrame(self.master._ribbonFrame, self.app)
#             self.app.frames[w.name] = w

#         if frames:
#             if type(frames) is str:
#                 register_frame(frames)
#             else:
#                 for f in frames:
#                     register_frame(f)

#         pass
#         # if groups:
#         #     for g in groups:
#         #         w = g(self.master._ribbonFrame, self.app)
#         #         Page.groups[w.name] = w

#         # if frames:
#         #     for f in frames:
#         #         w = f(self.master._pageFrame, self.app)
#         #         Page.frames[w.name] = w

#     # ----------------------------------------------------------------------
#     # Add a widget in the widgets list to enable disable during the run
#     # ----------------------------------------------------------------------
#     def addWidget(self, widget):
#         self.app.widgets.append(widget)

#     # ----------------------------------------------------------------------
#     # Send a command to Grbl
#     # ----------------------------------------------------------------------
#     def sendGCode(self, cmd):
#         commands.sendGCode(cmd)

#     # ----------------------------------------------------------------------
#     def addRibbonGroup(self, name, **args):
#         if not args:
#             args = {"side": "left", "fill": "both"}
#         self.ribbons.append((self.app.groups[name], args))

#     # ----------------------------------------------------------------------
#     def addPageFrame(self, name, **args):
#         if not args:
#             args = {"side": "top", "fill": "both"}
#         if isinstance(name, str):
#             self.frames.append((self.app.frames[name], args))
#         else:
#             self.frames.append((name, args))

#     # ----------------------------------------------------------------------
#     @staticmethod
#     def saveConfig():
#         for frame in Page.frames.values():
#             frame.saveConfig()

#     # ----------------------------------------------------------------------
#     @staticmethod
#     def loadConfig():
#         for frame in Page.frames.values():
#             frame.loadConfig()
