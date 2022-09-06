#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015

import tkinter as tk
from tkinter import ttk

from . import utils
from . import styles
from globalConfig import icon as gicon

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"

_TABFONT = ("Sans", "-14", "bold")
_FONT = ("Sans", "-11")

_BACKGROUND_DISABLE = "#A6A2A0"
_BACKGROUND = "#E6E2E0"
_BACKGROUND_GROUP = "#B6B2B0"

_BACKGROUND_GROUP2 = "#B0C0C0"
_BACKGROUND_GROUP3 = "#A0C0A0"
_BACKGROUND_GROUP4 = "#B0C0A0"

_FOREGROUND_GROUP = "White"
_ACTIVE_COLOR = "LightYellow"
_LABEL_SELECT_COLOR = "#C0FFC0"

# Ribbon show state
RIBBON_HIDDEN = 0  # Hidden
RIBBON_SHOWN = 1  # Displayed
RIBBON_TEMP = -1  # Show temporarily


# =============================================================================
# Frame Group with a button at bottom
# =============================================================================
class LabelGroup(ttk.Frame):
    def __init__(self, master, name, command=None, **kw):
        if "style" not in kw:
            kw["style"] = 'RibbonGroup.TFrame'
        ttk.Frame.__init__(self, master, **kw)
        self.name = name

        ttk.Separator(
            self, orient='vertical', style="Ribbon.TSeparator").pack(
                side="right", fill='y')

        # frame to insert the buttons
        self.frame = ttk.Frame(self, style='RibbonGroup.TFrame')
        self.frame.pack(side="top", expand=True, fill="both", padx=0, pady=0)

        self.add_label(name, command)

    def add_label(self, name, command):
        f = ttk.Frame(self, height=styles.RIBBON_LABEL_HEIGHT,
                      style='Bottom.RibbonGroup.TFrame')
        f.pack(fill='both')
        f.pack_propagate(False)
        if command:
            self.label = utils.LabelButton(f,
                                           self,
                                           f"<<{name}>>",
                                           command=command,
                                           text=name,
                                           image=gicon["triangle_down"],
                                           compound='right',
                                           style='Bottom.RibbonGroup.TButton')
            self.label.pack(side="bottom", fill="x", pady=0)
        else:
            self.label = ttk.Label(f,
                                   text=name,
                                   style='Bottom.RibbonGroup.TLabel')
            self.label.pack(side="bottom", pady=0)

    # -----------------------------------------------------------------------
    def grid2rows(self):
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

    # -----------------------------------------------------------------------
    def grid3rows(self):
        self.grid2rows()
        self.frame.grid_rowconfigure(2, weight=1)


# =============================================================================
# A label group with a drop down menu
# =============================================================================
class MenuGroup(LabelGroup):
    def __init__(self, master, name, menulist=None, **kw):
        LabelGroup.__init__(self, master, name, command=self._showMenu, **kw)
        self._menulist = menulist

        f = ttk.Frame(self, height=styles.RIBBON_LABEL_HEIGHT,
                      style='Bottom.RibbonGroup.TFrame')
        f.pack(fill='both')
        f.pack_propagate(False)

        self.label = ttk.Menubutton(f,
                                    text=name,
                                    image=gicon["triangle_down"],
                                    compound='right',
                                    style='Bottom.RibbonGroup.TButton')
        self.label.pack(side="bottom", fill="x", pady=0)

        if menulist:
            self.add_menu(menulist)
            # utils.MenuButton.createMenuFromList(self.label, self._menulist)
        # self.add_menu(name, menulist)

    def add_label(self, name, command):
        pass

    def add_menu(self, menulist):
        self.label.menu = tk.Menu(self.label, tearoff=False)
        self.label["menu"] = self.label.menu
        menu = mainmenu = self.label.menu

        if menulist:
            for item in menulist:
                if item is None:
                    menu.add_separator()
                elif isinstance(item, str):
                    menu = tk.Menu(mainmenu)
                    mainmenu.add_cascade(label=item, menu=menu)
                else:
                    name, icon, cmd = item
                    if icon is None:
                        icon = "empty"
                    menu.add_command(
                        label=name,
                        image=gicon[icon],
                        compound="left",
                        command=cmd
                    )

        # f = ttk.Frame(self, height=styles.RIBBON_LABEL_HEIGHT,
        #               style='Bottom.RibbonGroup.TFrame')
        # f.pack(fill='both')
        # f.pack_propagate(False)

        # self.label = ttk.Menubutton(f,
        #                             text=name,
        #                             style='Bottom.RibbonGroup.TButton')
        # self.label.pack(side="bottom", fill="x", pady=0)
        # mainmenu = menu = tk.Menu(
        #     self.label, tearoff=False, activebackground=_ACTIVE_COLOR)

        # for item in menulist:
        #     if item is None:
        #         menu.add_separator()
        #     elif isinstance(item, str):
        #         menu = tk.Menu(mainmenu)
        #         mainmenu.add_cascade(label=item, menu=menu)
        #     else:
        #         name, icon, cmd = item
        #         if icon is None:
        #             icon = "empty"
        #         menu.add_command(
        #             label=name,
        #             image=gicon[icon],
        #             compound="left",
        #             command=cmd
        #         )

    # -----------------------------------------------------------------------
    def createMenu(self):
        if self._menulist is not None:
            utils.MenuButton.createMenuFromList(self.label, self._menulist)
            return None
            return utils.MenuButton.createMenuFromList(self, self._menulist)
        else:
            return None

    # -----------------------------------------------------------------------
    def _showMenu(self):
        menu = self.createMenu()
        if menu is not None:
            menu.tk_popup(self.winfo_rootx(),
                          self.winfo_rooty() + self.winfo_height())


# =============================================================================
# Page Tab buttons
# =============================================================================
class TabButton(ttk.Radiobutton):
    def __init__(self, master, **kw):
        if "style" not in kw:
            kw["style"] = 'Tabs.Toolbutton'
        ttk.Radiobutton.__init__(
            self,
            master,
            **kw
        )

    # -----------------------------------------------------------------------
    # Bind events on TabFrame
    # ----------------------------------------------------------------------
    def bindClicks(self, tabframe):
        self.bind("<Double-1>", tabframe.double)
        self.bind("<Button-1>", tabframe.dragStart)
        self.bind("<B1-Motion>", tabframe.drag)
        self.bind("<ButtonRelease-1>", tabframe.dragStop)
        self.bind("<Control-ButtonRelease-1>", tabframe.pinActive)

        self.bind("<Left>", tabframe._tabLeft)
        self.bind("<Right>", tabframe._tabRight)
        self.bind("<Down>", tabframe._tabDown)


# =============================================================================
# Page
# =============================================================================
# class Page:  # <--- should be possible to be a toplevel as well
#     _motionClasses = (
#         utils.LabelButton,
#         utils.LabelRadiobutton,
#         utils.LabelCheckbutton,
#         utils.LabelCombobox,
#         utils.MenuButton,
#     )
#     _name_ = None
#     _icon_ = None
#     _doc_ = "Tooltip"

#     # -----------------------------------------------------------------------
#     def __init__(self, master, **kw):
#         self.master = master
#         self.name = self._name_
#         self._icon = gicon[self._icon_]
#         self._tab = None  # Tab button
#         self.ribbons = []
#         self.frames = []
#         self.ribbon = ttk.Frame(master)
#         self.leftpanel = ttk.Frame(master)
#         self.init()
#         self.create()

#     # -----------------------------------------------------------------------
#     # Override initialization
#     # -----------------------------------------------------------------------
#     def init(self):
#         pass

#     # -----------------------------------------------------------------------
#     # The tab page can change master if undocked
#     # -----------------------------------------------------------------------
#     # FIXME XXX SHOULD BE REMOVED
#     # -----------------------------------------------------------------------
#     def create(self):
#         self.createPage()

#     # -----------------------------------------------------------------------
#     # FIXME XXX SHOULD BE REMOVED
#     # -----------------------------------------------------------------------
#     def createPage(self):
#         self.page = tk.Frame(self.master._pageFrame)
#         return self.page

#     # -----------------------------------------------------------------------
#     # Called when a page is activated
#     # -----------------------------------------------------------------------
#     def activate(self):
#         pass

#     # -----------------------------------------------------------------------
#     def refresh(self):
#         pass

#     # ----------------------------------------------------------------------
#     def canUndo(self):
#         return True

#     # ----------------------------------------------------------------------
#     def canRedo(self):
#         return True

#     # ----------------------------------------------------------------------
#     def resetUndo(self):
#         pass

#     # ----------------------------------------------------------------------
#     def undo(self, event=None):
#         pass

#     # ----------------------------------------------------------------------
#     def redo(self, event=None):
#         pass

#     # ----------------------------------------------------------------------
#     def refreshUndoButton(self):
#         # Check if frame provides undo/redo
#         if self.master is None:
#             return
#         if self.page is None:
#             return

#         if self.canUndo():
#             state = "normal"
#         else:
#             state = "disabled"
#         self.master.tool["undo"].config(state=state)
#         self.master.tool["undolist"].config(state=state)

#         if self.canRedo():
#             state = "normal"
#         else:
#             state = "disabled"
#         self.master.tool["redo"].config(state=state)

#     # -----------------------------------------------------------------------
#     def keyboardFocus(self):
#         self._tab.focus_set()

#     # -----------------------------------------------------------------------
#     # Return the closest widget along a direction
#     # -----------------------------------------------------------------------
#     @staticmethod
#     def __compareDown(x, y, xw, yw):
#         return yw > y + 1

#     @staticmethod
#     def __compareUp(x, y, xw, yw):
#         return yw < y - 1

#     @staticmethod
#     def __compareRight(x, y, xw, yw):
#         return xw > x + 1

#     @staticmethod
#     def __compareLeft(x, y, xw, yw):
#         return xw < x - 1

#     # -----------------------------------------------------------------------
#     @staticmethod
#     def __closest(widget, compare, x, y):
#         closest = None
#         dc2 = 10000000
#         if widget is None:
#             return closest, dc2
#         for child in widget.winfo_children():
#             for class_ in Page._motionClasses:
#                 if isinstance(child, class_):
#                     if child["state"] == "disabled":
#                         continue
#                     xw = child.winfo_rootx()
#                     yw = child.winfo_rooty()
#                     if compare(x, y, xw, yw):
#                         d2 = (xw - x) ** 2 + (yw - y) ** 2
#                         if d2 < dc2:
#                             closest = child
#                             dc2 = d2
#                     break
#             else:
#                 c, d2 = Page.__closest(child, compare, x, y)
#                 if d2 < dc2:
#                     closest = c
#                     dc2 = d2
#         return closest, dc2

#     # -----------------------------------------------------------------------
#     # Select/Focus the closest element
#     # -----------------------------------------------------------------------
#     def _ribbonUp(self, event=None):
#         x = event.widget.winfo_rootx()
#         y = event.widget.winfo_rooty()
#         closest, d2 = Page.__closest(self.ribbon, Page.__compareUp, x, y)
#         if closest is not None:
#             closest.focus_set()

#     # -----------------------------------------------------------------------
#     def _ribbonDown(self, event=None):
#         x = event.widget.winfo_rootx()
#         y = event.widget.winfo_rooty()
#         closest, d2 = Page.__closest(self.ribbon, Page.__compareDown, x, y)
#         if closest is not None:
#             closest.focus_set()

#     # -----------------------------------------------------------------------
#     def _ribbonLeft(self, event=None):
#         x = event.widget.winfo_rootx()
#         y = event.widget.winfo_rooty()
#         closest, d2 = Page.__closest(self.ribbon, Page.__compareLeft, x, y)
#         if closest is not None:
#             closest.focus_set()

#     # -----------------------------------------------------------------------
#     def _ribbonRight(self, event=None):
#         x = event.widget.winfo_rootx()
#         y = event.widget.winfo_rooty()
#         closest, d2 = Page.__closest(self.ribbon, Page.__compareRight, x, y)
#         if closest is not None:
#             closest.focus_set()


# =============================================================================
# TabRibbonFrame
# =============================================================================
class TabRibbonFrame(ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master, style='TopBar.TFrame')

        self.oldActive = None
        self.activePage = tk.StringVar(self)
        self.tool = {}
        self.pages = {}

        # === Top frame with buttons ===
        frame = ttk.Frame(self, style='TopBar.TFrame')
        frame.pack(side="top", fill="x")

        # Add basic buttons
        def add_button(icon, cmd_event, tooltip, side):
            kw = {
                "image": gicon[icon],
                "style": 'TopBar.TButton'
            }
            if type(cmd_event) is str:
                kw["recipient"] = self
                kw["event"] = cmd_event
            else:
                kw["command"] = cmd_event
            b = utils.LabelButton(frame, **kw)
            if tooltip:
                utils.ToolTip(b, tooltip)
            b.pack(side=side, fill="y")

        add_button("new", "<<New>>", _("New file"), "left")
        add_button("load", "<<Open>>", _("Open file [Ctrl-O]"), "left")
        add_button("save", "<<Save>>", _("Save all [Ctrl-S]"), "left")
        add_button("undo", "<<Undo>>", _("Undo [Ctrl-Z]"), "left")
        # FIXME: Undolist not implemented
        # add_button("triangle_down", self.undolist, None, "left")
        add_button("redo", "<<Redo>>", _("Redo [Ctrl-Y]"), "left")

        ttk.Separator(frame, orient="vertical").pack(
            side="left", fill='y', padx=5)

        add_button("info", "<<Help>>", _("Help [F1]"), "right")

        ttk.Separator(frame, orient="vertical").pack(
            side="right", fill='y', padx=5)

        # --- TabBar ---
        self._tabFrame = ttk.Frame(frame, style='TopBar.TFrame')
        self._tabFrame.pack(side="left", fill="both", expand=True)

        # ==== Ribbon Frame ====
        self._ribbonFrame = ttk.Frame(self, style='Ribbon.TFrame')
        self._ribbonFrame.pack(fill="both", expand=True, padx=0, pady=0)

        self.setPageFrame(None)

    # -----------------------------------------------------------------------
    def setPageFrame(self, frame):
        self._pageFrame = frame

    # -----------------------------------------------------------------------
    def undolist(self, event=None):
        self.event_generate("<<UndoList>>")

    # -----------------------------------------------------------------------
    def getActivePage(self):
        return self.pages[self.activePage.get()]

    # -----------------------------------------------------------------------
    # Add page to the tabs
    # -----------------------------------------------------------------------
    def addPage(self, page, side="left"):
        self.pages[page.name] = page
        page._tab = TabButton(
            self._tabFrame,
            image=page._icon,
            text=_(page.name),
            compound="left",
            value=page.name,
            variable=self.activePage,
            command=self.changePage,
        )
        utils.ToolTip(page._tab, page.__doc__)

        page._tab.pack(side=side, fill="y", padx=5)

    # ----------------------------------------------------------------------
    # Unpack the old page
    # ----------------------------------------------------------------------
    def _forgetPage(self):
        if self.oldActive:
            for frame, _ in self.oldActive.ribbons:
                frame.pack_forget()
            for frame, _ in self.oldActive.frames:
                frame.pack_forget()
            self.oldActive = None

    # ----------------------------------------------------------------------
    # Change ribbon and page
    # ----------------------------------------------------------------------
    def changePage(self, page=None):
        if page is not None:
            if isinstance(page, str):  # not isinstance(page, Page):
                if page not in self.pages:
                    return
                page = self.pages[page]
            self.activePage.set(page.name)
        else:
            if self.activePage.get() in self.pages:
                page = self.pages[self.activePage.get()]
            else:
                return

        if page is self.oldActive:
            return

        self._forgetPage()

        for frame, args in page.ribbons:
            frame.pack(in_=self._ribbonFrame, **args)

        for frame, args in page.frames:
            # try:
            frame.pack(in_=self._pageFrame, **args)
            # except tk.TclError:
            #     print("ERROR: Pleas fixme!")

        self.oldActive = page
        page.activate()
        self.event_generate("<<ChangePage>>", data=page.name)
