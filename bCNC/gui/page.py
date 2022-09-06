"""

    Combination of:
        Ribbon.py - Page
        CNCRibbon.py - Page
"""
from tkinter import ttk

from .. import commands
from .. import utils
from globalConfig import icon as gicon


# =============================================================================
# CNC Page interface between the basic Page class and the bCNC class
# =============================================================================
class Page:
    _motionClasses = (
        utils.LabelButton,
        utils.LabelRadiobutton,
        utils.LabelCheckbutton,
        # utils.LabelCombobox,
        utils.MenuButton,
    )
    _name_ = None
    _icon_ = None
    _doc_ = "Tooltip"

    def __init__(self, master, app, name):
        self.app = app
        self.master = master
        self.name = name
        self._icon = gicon[self._icon_]
        self._tab = None  # Tab button
        self.ribbons = []
        self.frames = []
        self.ribbon = ttk.Frame(master)
        self.leftpanel = ttk.Frame(master)
        self.init()
        self.create()
        self.register()

    # -----------------------------------------------------------------------
    # Override initialization
    # -----------------------------------------------------------------------
    def init(self):
        pass

    # -----------------------------------------------------------------------
    # The tab page can change master if undocked
    # -----------------------------------------------------------------------
    # FIXME XXX SHOULD BE REMOVED
    # -----------------------------------------------------------------------
    def create(self):
        self.createPage()

    # -----------------------------------------------------------------------
    # FIXME XXX SHOULD BE REMOVED
    # -----------------------------------------------------------------------
    def createPage(self):
        self.page = ttk.Frame(self.master._pageFrame)
        return self.page

    # -----------------------------------------------------------------------
    # Called when a page is activated
    # -----------------------------------------------------------------------
    def activate(self):
        pass

    # -----------------------------------------------------------------------
    def refresh(self):
        pass

    # ----------------------------------------------------------------------
    def canUndo(self):
        return True

    # ----------------------------------------------------------------------
    def canRedo(self):
        return True

    # ----------------------------------------------------------------------
    def resetUndo(self):
        pass

    # ----------------------------------------------------------------------
    def undo(self, event=None):
        pass

    # ----------------------------------------------------------------------
    def redo(self, event=None):
        pass

    # ----------------------------------------------------------------------
    def refreshUndoButton(self):
        # Check if frame provides undo/redo
        if self.master is None:
            return
        if self.page is None:
            return

        if self.canUndo():
            state = "normal"
        else:
            state = "disabled"
        self.master.tool["undo"].config(state=state)
        self.master.tool["undolist"].config(state=state)

        if self.canRedo():
            state = "normal"
        else:
            state = "disabled"
        self.master.tool["redo"].config(state=state)

    # -----------------------------------------------------------------------
    def keyboardFocus(self):
        self._tab.focus_set()

    # ----------------------------------------------------------------------
    # Should be overridden with the groups and frames to register
    # ----------------------------------------------------------------------
    def register(self):
        pass

    # ----------------------------------------------------------------------
    # Register groups
    # ----------------------------------------------------------------------
    def _register(self, groups=None, frames=None):
        from pydoc import locate
        from globalConfig import config as gconfig

        def register_group(group):
            if group in self.app.groups:
                return
            # if g not in self.app.groups:
            #     continue # FIXME: Shall this rais an error?
            module_path = gconfig.getstr("_guigroups", group)
            group_class = locate(module_path)
            w = group_class.RibbonGroup(self.master._ribbonFrame, self.app)
            self.app.groups[w.name] = w

        if groups:
            if type(groups) is str:
                register_group(groups)
            else:
                for g in groups:
                    register_group(g)

        def register_frame(frame):
            if frame in self.app.leftpanels:
                return
            # if f not in self.app.groups:
            #     continue # FIXME: Shall this rais an error?
            module_path = gconfig.getstr("_guiframes", frame)
            frame_class = locate(module_path)
            w = frame_class.SideFrame(self.master._pageFrame, self.app)
            self.app.leftpanels[w.name] = w

        if frames:
            if isinstance(frames, str):
                register_frame(frames)
            else:
                for f in frames:
                    register_frame(f)

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
    def addRibbonGroup(self, name, **args):
        if not args:
            args = {"side": "left", "fill": "both"}
        self.ribbons.append((self.app.groups[name], args))

    # ----------------------------------------------------------------------
    def addPageFrame(self, name, **args):
        if "side" not in args:
            args["side"] = "top"
        if "fill" not in args:
            args["fill"] = "both"
        if isinstance(name, str):
            self.frames.append((self.app.leftpanels[name], args))
        else:
            self.frames.append((name, args))

    # -----------------------------------------------------------------------
    # Select/Focus the closest element
    # -----------------------------------------------------------------------
    def _ribbonUp(self, event=None):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty()
        closest, d2 = Page.__closest(self.ribbon, Page.__compareUp, x, y)
        if closest is not None:
            closest.focus_set()

    # -----------------------------------------------------------------------
    def _ribbonDown(self, event=None):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty()
        closest, d2 = Page.__closest(self.ribbon, Page.__compareDown, x, y)
        if closest is not None:
            closest.focus_set()

    # -----------------------------------------------------------------------
    def _ribbonLeft(self, event=None):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty()
        closest, d2 = Page.__closest(self.ribbon, Page.__compareLeft, x, y)
        if closest is not None:
            closest.focus_set()

    # -----------------------------------------------------------------------
    def _ribbonRight(self, event=None):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty()
        closest, d2 = Page.__closest(self.ribbon, Page.__compareRight, x, y)
        if closest is not None:
            closest.focus_set()

    # -----------------------------------------------------------------------
    # Return the closest widget along a direction
    # -----------------------------------------------------------------------
    @staticmethod
    def __compareDown(x, y, xw, yw):
        return yw > y + 1

    @staticmethod
    def __compareUp(x, y, xw, yw):
        return yw < y - 1

    @staticmethod
    def __compareRight(x, y, xw, yw):
        return xw > x + 1

    @staticmethod
    def __compareLeft(x, y, xw, yw):
        return xw < x - 1

    # -----------------------------------------------------------------------
    @staticmethod
    def __closest(widget, compare, x, y):
        closest = None
        dc2 = 10000000
        if widget is None:
            return closest, dc2
        for child in widget.winfo_children():
            for class_ in Page._motionClasses:
                if isinstance(child, class_):
                    if child["state"] == "disabled":
                        continue
                    xw = child.winfo_rootx()
                    yw = child.winfo_rooty()
                    if compare(x, y, xw, yw):
                        d2 = (xw - x) ** 2 + (yw - y) ** 2
                        if d2 < dc2:
                            closest = child
                            dc2 = d2
                    break
            else:
                c, d2 = Page.__closest(child, compare, x, y)
                if d2 < dc2:
                    closest = c
                    dc2 = d2
        return closest, dc2

    # # ----------------------------------------------------------------------
    # @staticmethod
    # def saveConfig():
    #     for frame in Page.frames.values():
    #         frame.saveConfig()

    # # ----------------------------------------------------------------------
    # @staticmethod
    # def loadConfig():
    #     for frame in Page.frames.values():
    #         frame.loadConfig()
