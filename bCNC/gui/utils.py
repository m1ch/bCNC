import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
from globalConfig import icon as gicon

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
class _KeyboardFocus:
    # -----------------------------------------------------------------------
    def _bind(self):
        self.bind("<Return>", self._invoke)
        # self.bind("<FocusIn>", self._focusIn)
        # self.bind("<FocusOut>", self._focusOut)

    # -----------------------------------------------------------------------
    # def _focusIn(self, event):
    #     self.__backgroundColor = self.cget("background")
    #     self.config(background=_ACTIVE_COLOR)

    # -----------------------------------------------------------------------
    # def _focusOut(self, event):
    #     self.config(background=self.__backgroundColor)

    # -----------------------------------------------------------------------
    def _invoke(self, event):
        self.invoke()


# =============================================================================
# Button with Label that generates a Virtual Event or calls a command
# =============================================================================
class LabelButton(ttk.Button, _KeyboardFocus):
    def __init__(self, master, recipient=None, event=None, **kw):
        if "background" in kw:
            kw.pop("background")
        if "anchor" in kw:
            kw.pop("anchor")
        if "justify" in kw:
            kw.pop("justify")
        if "style" not in kw:
            kw["style"] = "RibbonGroup.TButton"
        ttk.Button.__init__(self, master, **kw)
        # self.config(
        #     # highlightthickness=0,
        #     padx=2,
        #     pady=0,
        # )
        _KeyboardFocus._bind(self)
        if recipient is not None:
            self.config(command=self.sendEvent)
            self._recipient = recipient
            self._event = event
        else:
            self._recipient = None
            self._event = None

    # -----------------------------------------------------------------------
    def sendEvent(self):
        self._recipient.event_generate(self._event)


# =============================================================================
class LabelCheckbutton(ttk.Checkbutton, _KeyboardFocus):
    def __init__(self, master, **kw):
        if "anchor" in kw:
            kw.pop("anchor")
        if "style" not in kw:
            kw["style"] = "RibbonGroup.Toolbutton"
        ttk.Checkbutton.__init__(self, master, **kw)
        # self.config(
        #     selectcolor=_LABEL_SELECT_COLOR,
        #     activebackground=_ACTIVE_COLOR,
        #     background=_BACKGROUND,
        #     indicatoron=tk.FALSE,
        #     relief="flat",
        #     borderwidth=0,
        #     highlightthickness=0,
        #     padx=0,
        #     pady=0,
        #     font=_FONT,
        # )
        _KeyboardFocus._bind(self)


# =============================================================================
class LabelRadiobutton(ttk.Radiobutton, _KeyboardFocus):
    def __init__(self, master, **kw):
        if "anchor" in kw:
            kw.pop("anchor")
        if "style" not in kw:
            kw["style"] = "RibbonGroup.Toolbutton"
        ttk.Radiobutton.__init__(self, master, **kw)
        # self.config(
        #     selectcolor=_LABEL_SELECT_COLOR,
        #     activebackground=_ACTIVE_COLOR,
        #     background=_BACKGROUND,
        #     indicatoron=tk.FALSE,
        #     borderwidth=0,
        #     highlightthickness=0,
        #     pady=0,
        #     font=_FONT,
        # )
        _KeyboardFocus._bind(self)


# =============================================================================
# class LabelCombobox(tkextra.Combobox, _KeyboardFocus):
#     def __init__(self, master, **kw):
#         tkextra.Combobox.__init__(self, master, **kw)
#         self.config(background=_BACKGROUND, font=_FONT)
#         tk.Frame.config(self, background=_BACKGROUND, padx=0, pady=0)
#         _KeyboardFocus._bind(self)

#     # -----------------------------------------------------------------------
#     def _focusOut(self, event):
#         self.config(background=_BACKGROUND)  # self.__backgroundColor)
#         # self.__backgroundColor)
#         tk.Frame.config(self, background=_BACKGROUND)


# =============================================================================
# Button with Label that popup a menu
# =============================================================================
class MenuButton(ttk.Button, _KeyboardFocus):
    # FIXME: Rework and update all instances
    def __init__(self, master, menulist, **kw):
        if "anchor" in kw:
            kw.pop("anchor")
        ttk.Button.__init__(self, master, command=self.showMenu, **kw)
        # self.config(
        #     highlightthickness=0,
        #     padx=2,
        #     pady=0,
        #     command=self.showMenu,
        # )

        _KeyboardFocus._bind(self)
        self.bind("<Return>", self.showMenu)
        if menulist is not None:
            self._menu = MenuButton.createMenuFromList(self, menulist)
        else:
            self._menu = None

    # -----------------------------------------------------------------------
    def showMenu(self, event=None):
        if self._menu is not None:
            self._showMenu(self._menu)
        else:
            self._showMenu(self.createMenu())

    # -----------------------------------------------------------------------
    def _showMenu(self, menu):
        if menu is not None:
            menu.tk_popup(self.winfo_rootx(),
                          self.winfo_rooty() + self.winfo_height())

    # -----------------------------------------------------------------------
    def createMenu(self):
        return None

    # -----------------------------------------------------------------------
    @staticmethod
    def createMenuFromList(master, menulist):
        mainmenu = menu = tk.Menu(master,
                                  tearoff=0, activebackground=_ACTIVE_COLOR)
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
        # return menu


# =============================================================================
# User Button
# =============================================================================
class UserButton(LabelButton):
    TOOLTIP = _("User configurable button.\n<RightClick> to configure")

    def __init__(self, master, cnc, button, *args, **kwargs):
        if button == 0:
            ttk.Button.__init__(self, master, *args, **kwargs)
        else:
            LabelButton.__init__(self, master, *args, **kwargs)
        self.cnc = cnc
        self.button = button
        self.get()
        self.bind("<Button-3>", self.edit)
        self.bind("<Control-Button-1>", self.edit)
        self["command"] = self.execute

    # ----------------------------------------------------------------------
    # get information from configuration
    # ----------------------------------------------------------------------
    def get(self):
        from configparser import NoOptionError
        if self.button == 0:
            return
        name = self.name()
        self["text"] = name
        try:
            ico = gconfig.get("Buttons", f"icon.{self.button}")
            self["image"] = gicon[ico]
        except (KeyError, NoOptionError):
            self["image"] = gicon["material"]
        self["compound"] = "left"
        tooltip = self.tooltip()
        if not tooltip:
            tooltip = self.TOOLTIP
        ToolTip(self, tooltip)

    # ----------------------------------------------------------------------
    def name(self):
        try:
            return gconfig.get("Buttons", f"name.{int(self.button)}")
        except Exception:
            return str(self.button)

    # ----------------------------------------------------------------------
    def icon(self):
        try:
            return gconfig.get("Buttons", f"icon.{int(self.button)}")
        except Exception:
            return None

    # ----------------------------------------------------------------------
    def tooltip(self):
        try:
            return gconfig.get("Buttons", f"tooltip.{int(self.button)}")
        except Exception:
            return ""

    # ----------------------------------------------------------------------
    def command(self):
        try:
            return gconfig.get("Buttons", f"command.{int(self.button)}")
        except Exception:
            return ""

    # ----------------------------------------------------------------------
    # Edit button
    # ----------------------------------------------------------------------
    def edit(self, event=None):
        UserButtonDialog(self, self)
        self.get()

    # ----------------------------------------------------------------------
    # Execute command
    # ----------------------------------------------------------------------
    def execute(self):
        cmd = self.command()
        if not cmd:
            self.edit()
            return
        for line in cmd.splitlines():
            self.cnc.pendant.put(line)


class ToolTip:
    """

    Source: https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """

    waittime = 500
    tooltip = None

    def __init__(self, master, text=None):

        def on_enter(event):
            self.x_root = event.x_root
            self.y_root = event.y_root
            self.schedule()

        def on_leave(event):
            self.unschedule()
            self.__destroy()

        # Check if an old tooltip is open and destroy in case
        self.__destroy()

        self.id = None
        self.master = master
        self.text = text

        self.master.bind('<Enter>', on_enter)
        self.master.bind('<Leave>', on_leave)

    def schedule(self):
        self.unschedule()
        self.id = self.master.after(self.waittime, self.show)

    def unschedule(self):
        if self.id:
            self.master.after_cancel(self.id)
            self.id = None

    def show(self):
        ToolTip.tooltip = tk.Toplevel(self.master)
        ToolTip.tooltip.overrideredirect(True)
        ToolTip.tooltip.geometry(f'+{self.x_root+15}+{self.y_root+10}')

        label = ttk.Label(self.tooltip, text=self.text, style='Tooltip.TLabel')
        label.pack()

    @staticmethod
    def __destroy():
        if ToolTip.tooltip:
            ToolTip.tooltip.destroy()
            ToolTip.tooltip = None


# =============================================================================
# Frame Group with a button at bottom
# =============================================================================
class LabelGroup(ttk.Frame):
    def __init__(self, master, name, command=None, **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.name = name
        # self.config(
        #     background=_BACKGROUND, borderwidth=0, highlightthickness=0, pady=0
        # )

        # right frame as a separator
        # f = ttk.Frame(self, borderwidth=2,
        #           relief=tk.GROOVE, background=_BACKGROUND_DISABLE)
        # f.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)

        # frame to insert the buttons
        self.frame = ttk.Frame(
            self,
            # background=_BACKGROUND,
            # padx=0,
            # pady=0,
        )
        self.frame.pack(side="top", expand=True,
                        fill="both", padx=0, pady=0)

        if command:
            self.label = LabelButton(self, self, f"<<{name}>>", text=name)
            self.label.config(
                command=command,
                image=gicon["triangle_down"],
                foreground=_FOREGROUND_GROUP,
                background=_BACKGROUND_GROUP,
                highlightthickness=0,
                borderwidth=0,
                pady=0,
                compound=tk.RIGHT,
            )
        else:
            self.label = ttk.Label(
                self,
                text=_(name),
                font=_FONT,
                # foreground=_FOREGROUND_GROUP,
                # background=_BACKGROUND_GROUP,
                # padx=2,
                # pady=0,
            )  # Button takes 1px for border width
        self.label.pack(side=tk.BOTTOM, fill=tk.X, pady=0)

    # -----------------------------------------------------------------------
    def grid2rows(self):
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

    # -----------------------------------------------------------------------
    def grid3rows(self):
        self.grid2rows()
        self.frame.grid_rowconfigure(2, weight=1)


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
        from . import commands
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
class ButtonGroup(LabelGroup, _LinkApp):
    def __init__(self, master, name, app):
        LabelGroup.__init__(self, master, name)
        _LinkApp.__init__(self, app)
        if ":" in name:
            self.label["text"] = name.split(":")[1]


# =============================================================================
# Recent Menu button
# =============================================================================
class RecentMenuButton(MenuButton):
    # ----------------------------------------------------------------------
    def createMenu(self):
        import os
        import ribbon
        from filepage import _maxRecent
        menu = tk.Menu(self, tearoff=0, activebackground=ribbon._ACTIVE_COLOR)
        for i in range(_maxRecent):
            filename = gconfig.getrecent(i)
            if filename is None:
                break
            path = os.path.dirname(filename)
            fn = os.path.basename(filename)
            menu.add_command(
                label="%d %s" % (i + 1, fn),
                compound="left",
                image=gicon["new"],
                accelerator=path,  # Show as accelerator in order to be aligned
                command=lambda s=self, i=i: s.event_generate(
                    "<<Recent%d>>" % (i)),
            )
        if i == 0:  # no entry
            self.event_generate("<<Open>>")
            return None
        return menu


# =============================================================================
# User Configurable Buttons
# =============================================================================
class UserButtonDialog(tk.Toplevel):
    NONE = "<none>"

    def __init__(self, master, button):
        tk.Toplevel.__init__(self, master)
        self.title(_("User configurable button"))
        self.transient(master)
        self.button = button

        # Name
        row, col = 0, 0
        ttk.Label(self, text=_("Name:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.name = ttk.Entry(self,)
        # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"))
        self.name.grid(row=row, column=col, columnspan=2, sticky="ew")
        ToolTip(self.name, _("Name to appear on button"))

        # Icon
        row, col = row + 1, 0
        ttk.Label(self, text=_("Icon:")).grid(row=row, column=col, sticky="e")
        col += 1
        self.icon = ttk.Label(self, relief="raised")
        self.icon.grid(row=row, column=col, sticky="ew")
        col += 1
        lst = list(sorted(gicon.keys()))
        lst.insert(0, UserButtonDialog.NONE)
        self.iconCombo = ttk.Combobox(self, width=5)
        self.iconCombo['state'] = 'readonly'
        self.iconCombo['values'] = lst
        self.iconCombo.bind('<<ComboboxSelected>>', self.iconChange)
        # self.iconCombo = tkextra.Combobox(
        #     self, True, width=5, command=self.iconChange)
        # self.iconCombo.fill(lst)
        self.iconCombo.grid(row=row, column=col, sticky="ew")
        ToolTip(self.iconCombo, _("Icon to appear on button"))

        # Tooltip
        row, col = row + 1, 0
        ttk.Label(self, text=_("Tool Tip:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        self.tooltip = ttk.Entry(self,)
        # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"))
        self.tooltip.grid(row=row, column=col, columnspan=2, sticky="ew")
        ToolTip(self.tooltip, _("Tooltip for button"))

        # Tooltip
        row, col = row + 1, 0
        ttk.Label(self, text=_("Command:")).grid(
            row=row, column=col, sticky="ne")
        col += 1
        self.command = tk.Text(
            self, background=gconfig.getstr(
                '_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=40, height=10
        )
        self.command.grid(row=row, column=col, columnspan=2, sticky="ew")

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(row, weight=1)

        # Actions
        row += 1
        f = ttk.Frame(self)
        f.grid(row=row, column=0, columnspan=3, sticky="ew")
        ttk.Button(f, text=_("Cancel"), command=self.cancel).pack(side="right")
        ttk.Button(f, text=_("Ok"), command=self.ok).pack(side="right")

        # Set variables
        self.name.insert(0, self.button.name())
        self.tooltip.insert(0, self.button.tooltip())
        icon = self.button.icon()
        if icon is None:
            self.iconCombo.set(UserButtonDialog.NONE)
        else:
            self.iconCombo.set(icon)
        self.icon["image"] = gicon.get(icon, "")
        self.command.insert("1.0", self.button.command())

        # Wait action
        self.wait_visibility()
        self.grab_set()
        self.focus_set()
        self.wait_window()

    # ----------------------------------------------------------------------
    def ok(self, event=None):
        n = self.button.button
        gconfig.set("Buttons", f"name.{int(n)}", self.name.get().strip())
        icon = self.iconCombo.get()
        if icon == UserButtonDialog.NONE:
            icon = ""
        gconfig.set("Buttons", f"icon.{int(n)}", icon)
        gconfig.set("Buttons", f"tooltip.{int(n)}", self.tooltip.get().strip())
        gconfig.set("Buttons", f"command.{int(n)}",
                    self.command.get("1.0", "end").strip())
        self.destroy()

    # ----------------------------------------------------------------------
    def cancel(self):
        self.destroy()

    # ----------------------------------------------------------------------
    def iconChange(self):
        self.icon["image"] = gicon.get(self.iconCombo.get(), "")


class PageLabelFrame(ttk.Frame, _LinkApp):
    def __init__(self, master, app, name, text=None, **kw):
        if text is None:
            text = name
        self.name = name
        self.master = master
        ttk.Frame.__init__(self, master, **kw)
        _LinkApp.__init__(self, app)

        self.columnconfigure(1, weight=1)
        ttk.Separator(self, orient="horizontal").grid(
            row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(self,
                  text=text,
                  style="Collapsible.TLabel").grid(row=0, column=0)

        self.frame = ttk.Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, sticky="ew")


class CollapsiblePageLabelFrame(ttk.Frame, _LinkApp):
    def __init__(self, master, app, name, text=None, **kw):
        # import Unicode
        if text is None:
            text = name
        self.name = name
        self.master = master
        ttk.Frame.__init__(self, master, **kw)
        _LinkApp.__init__(self, app)
        self._opened_text = f"△ {text}"
        self._closed_text = f"▽ {text}"

        self.columnconfigure(1, weight=1)

        # f = ttk.Frame(self)
        # f.grid(row=0, column=0, sticky="ew")
        self._separator = ttk.Separator(self, orient="horizontal")
        self._separator.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._isopen = tk.BooleanVar(self, True)
        self._button = ttk.Checkbutton(self,
                                       variable=self._isopen,
                                       command=self._toggle,
                                       style="Collapsible.TButton")
        self._button.grid(row=0, column=0)

        self.frame = ttk.Frame(self)

        self._toggle()

    def _toggle(self):
        if not self._isopen.get():
            self.frame.grid_forget()
            self._button.configure(text=self._closed_text)

        elif self._isopen.get():
            self.frame.grid(row=1, column=0, columnspan=2, sticky="new")
            self._button.configure(text=self._opened_text)

    def toggle(self):
        """Switches the label frame to the opposite state."""
        self._isopen.set(not self._isopen.get())
        self._toggle()
