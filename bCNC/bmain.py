#!/usr/bin/env python3
# $Id: bCNC.py,v 1.6 2014/10/15 15:04:48 bnv Exp bnv $
#
# Author: vvlachoudis@gmail.com
# Date: 24-Aug-2014

import os
import socket
from struct import pack
import sys
import time
import traceback
import webbrowser
from datetime import datetime
import tkinter
from queue import Empty
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pydoc import locate

try:
    import serial
except ImportError:
    serial = None
    print("testing mode, could not import serial")

import Utils
from globalConstants import (
    __prg__,
    __version__,
    __date__,
    __author__,
    __email__,
    __www__,
    __contribute__,
    __translations__,
    __credits__,
    __prgpath__,
    _maxRecent,
)
from globalConfig import config as gconfig

from cnc import globCNC
from gcode import globGCode
from sender import globSender


from cnc import WAIT

import rexx
import Updates
# Load configuration before anything else
# and if needed replace the  translate function _()
# before any string is initialized
from gui import tkdialogs
from gui import tkextra
from gui import bfiledialog
from gui import cnccanvas as CNCCanvas
from gui import ribbon as Ribbon
import Pendant
# from gui.cncribbon import Page
# from gui.controlpage import ControlPage
# from gui.editorpage import EditorPage
# from gui.filepage import FilePage
# from gui.probepage import ProbePage
# from gui.terminalpage import TerminalPage
from gui.toolspage import Tools  # , ToolsPage
from gui import utils
from gui import styles
from sender import NOT_CONNECTED, STATECOLOR, STATECOLORDEF


if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
    print("ERROR: Python3.8 or newer is required to run bCNC!!")
    exit(1)

__platform_fingerprint__ = "".join([
    f"({sys.platform} ",
    f"py{sys.version_info.major}.",
    f"{sys.version_info.minor}.",
    f"{sys.version_info.micro})"
])

_openserial = True  # override ini parameters
_device = None
_baud = None

MONITOR_AFTER = 200  # ms
DRAW_AFTER = 300  # ms

RX_BUFFER_SIZE = 128

MAX_HISTORY = 500

FILETYPES = [
    (
        _("All accepted"),
        (
            "*.ngc",
            "*.cnc",
            "*.nc",
            "*.tap",
            "*.gcode",
            "*.dxf",
            "*.probe",
            "*.orient",
            "*.stl",
            "*.svg",
        ),
    ),
    (_("G-Code"), ("*.ngc", "*.cnc", "*.nc", "*.tap", "*.gcode")),
    (_("G-Code clean"), ("*.txt")),
    ("DXF", "*.dxf"),
    ("SVG", "*.svg"),
    (_("Probe"), ("*.probe", "*.xyz")),
    (_("Orient"), "*.orient"),
    ("STL", "*.stl"),
    (_("All"), "*"),
]

geometry = None


# =============================================================================
# Main Application window
# =============================================================================
class Application(tk.Tk):
    pages = {}
    groups = {}
    leftpanels = {}

    def __init__(self, **kw):
        tk.Tk.__init__(self, **kw)
        styles.load_styles()
        Utils.loadIcons()
        tkinter.CallWrapper = Utils.CallWrapper
        tkextra.bindClasses(self)

        # self.sender = globSender

        photo = tk.PhotoImage(file=f"{__prgpath__}/bCNC.png")
        self.iconphoto(True, photo)
        self.title(f"{__prg__} {__version__} {__platform_fingerprint__}")
        self.widgets = []

        # Global variables
        # self.gcode = globGCode
        self.mcontrol = None
        self.tools = Tools()
        self.loadConfig()

        # build sceleton of main window ---------------------------------------
        # --- Ribbon ---
        self.ribbon = Ribbon.TabRibbonFrame(self)
        self.ribbon.pack(side="top", fill="x")
        # --- main frame ---
        self.mainframe()
        # Add status bar on bottom of main window
        self.statusbar()

        # Add pages as defined in the ini-file --------------------------------
        # NOTE: Not required pages wound be loaded anymore!

        errors = []
        for name in gconfig.getstr(__prg__, "ribbon").split():
            side = "left"
            if name[-1] == ">":
                name = name[:-1]
                side = "right"
            if name == "CAM":
                name = "Tools"
            # FIXME: Maybe add the filename rather than the tab-name to the ini
            #        to avoid this explicit assertion
            m = gconfig.getstr("_guipages", name.lower())
            page_module = locate(m)
            page = page_module.Page(self.ribbon, self)

            # page_class = locate(f"gui.pages.{name.lower()}.{module}")
            # page = page_class(self.ribbon, self)
            self.pages[page.name] = page
            self.ribbon.addPage(page, side)
        # create page widgets -------------------------------------------------
        # fist create Pages
        # for cls in (
        #     ControlPage,
        #     EditorPage,
        #     FilePage,
        #     ProbePage,
        #     TerminalPage,
        #     ToolsPage,
        # ):
        #     page = cls(self.ribbon, self)
        #     self.pages[page.name] = page

        # then add their properties (in separate loop)
        for name, page in self.pages.items():
            for n in gconfig.getstr(__prg__,
                                    f"{page.name}.ribbon").split():
                try:
                    page.addRibbonGroup(n)
                except KeyError:
                    errors.append(n)

            for n in gconfig.getstr(__prg__, f"{page.name}.page").split():
                last = n[-1]
                if ((n == "abcDRO" or n == "abcControl")
                        and globCNC.enable6axisopt is False):
                    sys.stdout.write("Not Loading 6 axis displays\n")

                else:
                    try:
                        if last == "*":
                            page.addPageFrame(n[:-1], fill="both", expand=True)
                        else:
                            page.addPageFrame(n)
                    except KeyError:
                        errors.append(n)

        if errors:
            tk.messagebox.showwarning(
                "bCNC configuration",
                f"The following pages \"{' '.join(errors)}\" are found in "
                "your ${HOME}/.bCNC initialization "
                "file, which are either spelled wrongly or "
                "no longer exist in bCNC",
                parent=self,
            )

        # remember the editor list widget
        self.dro = self.leftpanels["DRO"]
        self.abcdro = self.leftpanels["abcDRO"]
        self.gstate = self.leftpanels["State"]
        self.control = self.leftpanels["Control"]
        self.abccontrol = self.leftpanels["abcControl"]
        self.editor = self.leftpanels["Editor"].editor
        self.terminal = self.leftpanels["Terminal"].terminal
        self.buffer = self.leftpanels["Terminal"].buffer

        # XXX FIXME Do we need it or I can takes from Page every time?
        self.autolevel = self.leftpanels["Probe:Autolevel"]

        # Add pages as defined in the ini-file
        # for name in gconfig.getstr(__prg__, "ribbon").split():
        #     last = name[-1]
        #     if last == ">":
        #         name = name[:-1]
        #         side = "right"
        #     else:
        #         side = "left"
        #     self.ribbon.addPage(self.pages[name], side)

        # Restore last page
        # Select "Probe:Probe" tab to show the dialogs!
        self.pages["Probe"].tabChange()
        self.ribbon.changePage(gconfig.getstr(__prg__, "page", "File"))

        probe = self.leftpanels["Probe:Probe"]
        tkextra.bindEventData(
            self, "<<OrientSelect>>", lambda e, f=probe: f.selectMarker(
                int(e.data))
        )
        tkextra.bindEventData(
            self,
            "<<OrientChange>>",
            lambda e, s=self: s.canvas.orientChange(int(e.data)),
        )
        self.bind("<<OrientUpdate>>", probe.orientUpdate)

        # Global bindings
        self.bind("<<Undo>>", self.undo)
        self.bind("<<Redo>>", self.redo)
        self.bind("<<Copy>>", self.copy)
        self.bind("<<Cut>>", self.cut)
        self.bind("<<Paste>>", self.paste)

        self.bind("<<Connect>>", self.openClose)

        self.bind("<<New>>", self.newFile)
        self.bind("<<Open>>", self.loadDialog)
        self.bind("<<Import>>", lambda x, s=self: s.importFile())
        self.bind("<<Save>>", self.saveAll)
        self.bind("<<SaveAs>>", self.saveDialog)
        self.bind("<<Reload>>", self.reload)

        # self.bind("<<Recent0>>", self.sender._loadRecent0)
        self.bind("<<Recent0>>", lambda event, a=0:
                  globSender.loadRecent(a))
        self.bind("<<Recent1>>", lambda event, a=1:
                  globSender.loadRecent(a))
        self.bind("<<Recent2>>", lambda event, a=2:
                  globSender.loadRecent(a))
        self.bind("<<Recent3>>", lambda event, a=3:
                  globSender.loadRecent(a))
        self.bind("<<Recent4>>", lambda event, a=4:
                  globSender.loadRecent(a))
        self.bind("<<Recent5>>", lambda event, a=5:
                  globSender.loadRecent(a))
        self.bind("<<Recent6>>", lambda event, a=6:
                  globSender.loadRecent(a))
        self.bind("<<Recent7>>", lambda event, a=7:
                  globSender.loadRecent(a))
        self.bind("<<Recent8>>", lambda event, a=8:
                  globSender.loadRecent(a))
        self.bind("<<Recent9>>", lambda event, a=9:
                  globSender.loadRecent(a))

        self.bind("<<TerminalClear>>", self.leftpanels["Terminal"].clear)
        self.bind("<<AlarmClear>>", self.alarmClear)
        self.bind("<<Help>>", globSender.help)
        # Do not send the event otherwise it will skip the feedHold/resume
        self.bind("<<FeedHold>>", lambda e: globSender.feedHold())
        self.bind("<<Resume>>", lambda e: globSender.resume())
        self.bind("<<Run>>", lambda e: globSender.run())
        self.bind("<<Stop>>", globSender.stopRun)
        self.bind("<<Pause>>", globSender.pause)

        tkextra.bindEventData(self, "<<Status>>", self.updateStatus)
        tkextra.bindEventData(self, "<<Coords>>", self.updateCanvasCoords)

        # Editor bindings
        self.bind("<<Add>>", self.editor.insertItem)
        self.bind("<<AddBlock>>", self.editor.insertBlock)
        self.bind("<<AddLine>>", self.editor.insertLine)
        self.bind("<<Clone>>", self.editor.clone)
        self.canvas.bind("<Control-Key-Prior>", self.editor.orderUp)
        self.canvas.bind("<Control-Key-Next>", self.editor.orderDown)
        self.canvas.bind("<Control-Key-d>", self.editor.clone)
        self.canvas.bind("<Control-Key-c>", self.copy)
        self.canvas.bind("<Control-Key-x>", self.cut)
        self.canvas.bind("<Control-Key-v>", self.paste)
        self.bind("<<Delete>>", self.editor.deleteBlock)
        self.canvas.bind("<Delete>", self.editor.deleteBlock)
        self.canvas.bind("<BackSpace>", self.editor.deleteBlock)
        try:
            self.canvas.bind("<KP_Delete>", self.editor.deleteBlock)
        except Exception:
            pass
        self.bind("<<Invert>>", self.editor.invertBlocks)
        self.bind("<<Expand>>", self.editor.toggleExpand)
        self.bind("<<EnableToggle>>", self.editor.toggleEnable)
        self.bind("<<Enable>>", self.editor.enable)
        self.bind("<<Disable>>", self.editor.disable)
        self.bind("<<ChangeColor>>", self.editor.changeColor)
        self.bind("<<Comment>>", self.editor.commentRow)
        self.bind("<<Join>>", self.editor.joinBlocks)
        self.bind("<<Split>>", self.editor.splitBlocks)

        # Canvas X-bindings
        self.bind("<<ViewChange>>", self.viewChange)
        self.bind("<<AddMarker>>", self.canvas.setActionAddMarker)
        self.bind("<<MoveGantry>>", self.canvas.setActionGantry)
        self.bind("<<SetWPOS>>", self.canvas.setActionWPOS)

        frame = self.leftpanels["Probe:Tool"]
        self.bind("<<ToolCalibrate>>", frame.calibrate)
        self.bind("<<ToolChange>>", frame.change)

        self.bind("<<AutolevelMargins>>", self.autolevel.getMargins)
        self.bind("<<AutolevelZero>>", self.autolevel.setZero)
        self.bind("<<AutolevelClear>>", self.autolevel.clear)
        self.bind("<<AutolevelScan>>", self.autolevel.scan)
        self.bind("<<AutolevelScanMargins>>", self.autolevel.scanMargins)

        self.bind("<<CameraOn>>", self.canvas.cameraOn)
        self.bind("<<CameraOff>>", self.canvas.cameraOff)

        self.bind("<<CanvasFocus>>", self.canvasFocus)
        self.bind("<<Draw>>", self.draw)
        self.bind("<<DrawProbe>>", lambda e,
                  c=self.canvasFrame: c.drawProbe(True))
        self.bind("<<DrawOrient>>", self.canvas.drawOrient)

        self.bind("<<ListboxSelect>>", self.selectionChange)
        self.bind("<<Modified>>", self.drawAfter)

        self.bind("<Control-Key-a>", self.selectAll)
        self.bind("<Control-Key-A>", self.unselectAll)
        self.bind("<Escape>", self.unselectAll)
        self.bind("<Control-Key-i>", self.selectInvert)

        self.bind("<<SelectAll>>", self.selectAll)
        self.bind("<<SelectNone>>", self.unselectAll)
        self.bind("<<SelectInvert>>", self.selectInvert)
        self.bind("<<SelectLayer>>", self.selectLayer)

        self.bind("<Control-Key-e>", self.editor.toggleExpand)
        self.bind("<Control-Key-n>", self.showInfo)
        self.bind("<<ShowInfo>>", self.showInfo)
        self.bind("<Control-Key-l>", self.editor.toggleEnable)
        self.bind("<Control-Key-q>", self.quit)
        self.bind("<Control-Key-o>", self.loadDialog)
        self.bind("<Control-Key-r>", self.drawAfter)
        self.bind("<Control-Key-s>", self.saveAll)
        self.bind("<Control-Key-y>", self.redo)
        self.bind("<Control-Key-z>", self.undo)
        self.bind("<Control-Key-Z>", self.redo)
        self.canvas.bind("<Key-space>", self.commandFocus)
        self.bind("<Control-Key-space>", self.commandFocus)
        self.bind("<<CommandFocus>>", self.commandFocus)

        tools = self.pages["CAM"]
        self.bind("<<ToolAdd>>", tools.add)
        self.bind("<<ToolDelete>>", tools.delete)
        self.bind("<<ToolClone>>", tools.clone)
        self.bind("<<ToolRename>>", tools.rename)

        self.bind("<Prior>", self.control.moveZup)
        self.bind("<Next>", self.control.moveZdown)

        if self._swapKeyboard == 1:
            self.bind("<Right>", self.control.moveYup)
            self.bind("<Left>", self.control.moveYdown)
            self.bind("<Up>", self.control.moveXdown)
            self.bind("<Down>", self.control.moveXup)
            self.bind(".", self.abccontrol.moveAup)
            self.bind(",", self.abccontrol.moveAdown)
        elif self._swapKeyboard == -1:
            self.bind("<Right>", self.control.moveYdown)
            self.bind("<Left>", self.control.moveYup)
            self.bind("<Up>", self.control.moveXup)
            self.bind("<Down>", self.control.moveXdown)
            self.bind(",", self.abccontrol.moveAup)
            self.bind(".", self.abccontrol.moveAdown)
        else:
            self.bind("<Right>", self.control.moveXup)
            self.bind("<Left>", self.control.moveXdown)
            self.bind("<Up>", self.control.moveYup)
            self.bind("<Down>", self.control.moveYdown)
            self.bind(".", self.abccontrol.moveAup)
            self.bind(",", self.abccontrol.moveAdown)

        try:
            self.bind("<KP_Prior>", self.control.moveZup)
            self.bind("<KP_Next>", self.control.moveZdown)

            if self._swapKeyboard == 1:
                self.bind("<KP_Right>", self.control.moveYup)
                self.bind("<KP_Left>", self.control.moveYdown)
                self.bind("<KP_Up>", self.control.moveXdown)
                self.bind("<KP_Down>", self.control.moveXup)
            elif self._swapKeyboard == -1:
                self.bind("<KP_Right>", self.control.moveYdown)
                self.bind("<KP_Left>", self.control.moveYup)
                self.bind("<KP_Up>", self.control.moveXup)
                self.bind("<KP_Down>", self.control.moveXdown)
            else:
                self.bind("<KP_Right>", self.control.moveXup)
                self.bind("<KP_Left>", self.control.moveXdown)
                self.bind("<KP_Up>", self.control.moveYup)
                self.bind("<KP_Down>", self.control.moveYdown)
        except tk.TclError:
            pass

        self.bind("<Key-plus>", self.control.incStep)
        self.bind("<Key-equal>", self.control.incStep)
        self.bind("<KP_Add>", self.control.incStep)
        self.bind("<Key-minus>", self.control.decStep)
        self.bind("<Key-underscore>", self.control.decStep)
        self.bind("<KP_Subtract>", self.control.decStep)

        self.bind("<Key-asterisk>", self.control.mulStep)
        self.bind("<KP_Multiply>", self.control.mulStep)
        self.bind("<Key-slash>", self.control.divStep)
        self.bind("<KP_Divide>", self.control.divStep)

        self.bind("<Key-1>", self.control.setStep1)
        self.bind("<Key-2>", self.control.setStep2)
        self.bind("<Key-3>", self.control.setStep3)

        self.bind("<Key-exclam>", globSender.feedHold)
        self.bind("<Key-asciitilde>", globSender.resume)

        for x in self.widgets:
            if isinstance(x, ttk.Entry):
                x.bind("<Escape>", self.canvasFocus)

        self.bind("<FocusIn>", self.focusIn)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.canvas.focus_set()

        # Fill basic global variables
        globCNC.vars["state"] = NOT_CONNECTED
        globCNC.vars["color"] = STATECOLOR[NOT_CONNECTED]
        self._pendantFileUploaded = None
        self._drawAfter = None  # after handle for modification
        self._inFocus = False
        # END - insertCount lines where ok was applied to for $xxx commands
        self._insertCount = (0)
        self._selectI = 0
        self.monitorSerial()
        self.canvasFrame.toggleDrawFlag()

        # Auto start pendant and serial
        if gconfig.getbool("Connection", "pendant"):
            self.startPendant(False)

        if _openserial and gconfig.getbool("Connection", "openserial"):
            self.openClose()

        # Filedialog Load history
        for i in range(_maxRecent):
            filename = gconfig.getrecent(i)
            if filename is None:
                break
            bfiledialog.append2History(os.path.dirname(filename))

    # -----------------------------------------------------------------------
    def mainframe(self):
        # Main frame
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # --- Left side ---
        self.leftpane = ttk.Frame(self.paned)
        self.paned.add(self.leftpane)  # , minsize=340)

        pageframe = ttk.Frame(self.leftpane, width=340)
        pageframe.pack_propagate(False)
        pageframe.pack(side="top", expand=True, fill="both")
        self.ribbon.setPageFrame(pageframe)

        # Command bar
        f = ttk.Frame(self.leftpane)
        f.pack(side="bottom", fill="x")
        self.cmdlabel = ttk.Label(f, text=_("Command:"))
        self.cmdlabel.pack(side="left")
        self.command = ttk.Entry(f,)
        self.command.pack(side="right", fill="x", expand=True)
        self.command.bind("<Return>", self.cmdExecute)
        self.command.bind("<Up>", self.commandHistoryUp)
        self.command.bind("<Down>", self.commandHistoryDown)
        self.command.bind("<FocusIn>", self.commandFocusIn)
        self.command.bind("<FocusOut>", self.commandFocusOut)
        self.command.bind("<Key>", self.commandKey)
        self.command.bind("<Control-Key-z>", self.undo)
        self.command.bind("<Control-Key-Z>", self.redo)
        self.command.bind("<Control-Key-y>", self.redo)
        utils.ToolTip(
            self.command,
            _(
                "MDI Command line: Accept g-code commands or macro "
                "commands (RESET/HOME...) or editor commands "
                "(move,inkscape, round...) [Space or Ctrl-Space]"
            ),
        )
        self.widgets.append(self.command)

        # --- Right side ---
        frame = ttk.Frame(self.paned)
        self.paned.add(frame)

        # --- Canvas ---
        self.canvasFrame = CNCCanvas.CanvasFrame(frame, self)
        self.canvasFrame.pack(side="top", fill="both", expand=True)
        # XXX FIXME do I need the self.canvas?
        self.canvas = self.canvasFrame.canvas

    # -----------------------------------------------------------------------
    def statusbar(self):
        # Status bar
        frame = ttk.Frame(self)
        frame.pack(side="bottom", fill="x")
        self.statusbar = tkextra.ProgressBar(frame, height=20, relief="sunken")
        self.statusbar.pack(side="left", fill="x", expand=True)
        self.statusbar.configText(fill="DarkBlue", justify="left", anchor="w")

        self.statusz = ttk.Label(
            frame,
            style="StatusBar.TLabel",
        )
        self.statusz.pack(side="right")
        self.statusy = ttk.Label(
            frame,
            style="StatusBar.TLabel",
        )
        self.statusy.pack(side="right")
        self.statusx = ttk.Label(
            frame,
            style="StatusBar.TLabel",
        )
        self.statusx.pack(side="right")

        # Buffer bar
        self.bufferbar = tkextra.ProgressBar(
            frame, height=20, width=40, relief="sunken")
        self.bufferbar.pack(side="right", expand="no")
        self.bufferbar.setLimits(0, 100)
        utils.ToolTip(self.bufferbar, _("Controller buffer fill"))

    # -----------------------------------------------------------------------
    def setStatus(self, msg, force_update=False):
        self.statusbar.configText(text=msg, fill="DarkBlue")
        if force_update:
            self.statusbar.update_idletasks()
            self.bufferbar.update_idletasks()

    # -----------------------------------------------------------------------
    # Set a status message from an event
    # -----------------------------------------------------------------------
    def updateStatus(self, event):
        self.setStatus(_(event.data))

    # -----------------------------------------------------------------------
    # Show popup dialog asking for value entry, useful in g-code scripts
    # -----------------------------------------------------------------------
    def entry(
        self,
        message="Enter value",
        title="",
        input_="",
        type_="str",
        from_=None,
        to_=None,
    ):
        d = tkdialogs.InputDialog(
            self, title, message, input, type_, from_, to_)
        v = d.show()

        # XXX: basestring replaced
        if isinstance(v, (str, bytes)):
            v = v.strip()
        print("entered " + str(type(v)) + ": " + str(v))
        return v

    # -----------------------------------------------------------------------
    # Update canvas coordinates
    # -----------------------------------------------------------------------
    def updateCanvasCoords(self, event):
        x, y, z = event.data.split()
        self.statusx["text"] = "X: " + x
        self.statusy["text"] = "Y: " + y
        self.statusz["text"] = "Z: " + z

    # ----------------------------------------------------------------------
    # Accept the user key if not editing any text
    # ----------------------------------------------------------------------
    def acceptKey(self, skipRun=False):
        if not skipRun and globSender.running:
            return False
        focus = self.focus_get()
        if (
            isinstance(focus, ttk.Entry)
            or isinstance(focus, ttk.Spinbox)
            or isinstance(focus, tk.Listbox)
            or isinstance(focus, tk.Text)
            or isinstance(focus, tk.scrolledtext.ScrolledText)
        ):
            return False
        return True

    # -----------------------------------------------------------------------
    def quit(self, event=None):
        if globSender.running and self._quit < 1:
            tk.messagebox.showinfo(
                _("Running"),
                _("CNC is currently running, please stop it before."),
                parent=self,
            )
            self._quit += 1
            return
        del self.widgets[:]

        if self.fileModified():
            return

        self.canvas.cameraOff()
        self.saveConfig()
        self.destroy()
        if Utils.errors and Utils._errorReport:
            tkdialogs.ReportDialog.sendErrorReport()

    # ---------------------------------------------------------------------
    def configWidgets(self, var, value):
        for w in self.widgets:
            if isinstance(w, tuple):
                try:
                    w[0].entryconfig(w[1], state=value)
                except tk.TclError:
                    pass
            elif isinstance(w, tkextra.Combobox):
                w.configure(state=value)
            else:
                w[var] = value

    # ---------------------------------------------------------------------
    def busy(self):
        try:
            self.config(cursor="watch")
            self.update_idletasks()
        except tk.TclError:
            pass

    # ----------------------------------------------------------------------
    def notBusy(self):
        try:
            self.config(cursor="")
        except tk.TclError:
            pass

    # ---------------------------------------------------------------------
    def enable(self):
        self.configWidgets("state", "normal")
        self.statusbar.clear()
        self.statusbar.config(background="LightGray")
        self.bufferbar.clear()
        self.bufferbar.config(background="LightGray")
        self.bufferbar.setText("")

    # ---------------------------------------------------------------------
    def disable(self):
        self.configWidgets("state", "disabled")

    # ----------------------------------------------------------------------
    # Check for updates
    # ----------------------------------------------------------------------
    def checkUpdates(self):
        # Find bCNC version
        Updates.CheckUpdateDialog(self, __version__)

    # ----------------------------------------------------------------------
    # Show the error message, if no serial is present
    # ----------------------------------------------------------------------
    def showSerialError(self):
        tk.messagebox.showerror(
            _("python serial missing"),
            _(
                "ERROR: Please install the python pyserial module\n"
                "Windows:\n\tC:\\PythonXX\\Scripts\\easy_install pyserial\n"
                "Mac:\tpip install pyserial\n"
                "Linux:\tsudo apt-get install python-serial\n"
                "\tor yum install python-serial\n"
                "\tor dnf install python-pyserial"
            ),
            parent=self,
        )

    # -----------------------------------------------------------------------
    def loadShortcuts(self):
        for name, value in gconfig.items("Shortcut"):
            # Convert to uppercase
            key = name.title()
            self.unbind(f"<{key}>")  # unbind any possible old value
            if value:
                self.bind(f"<{key}>", lambda e, s=self, c=value: s.execute(c))

    # -----------------------------------------------------------------------
    def showUserFile(self):
        webbrowser.open(Utils.iniUser)
        # os.startfile(Utils.iniUser)

    # -----------------------------------------------------------------------
    def loadConfig(self):
        global geometry

        if geometry is None:
            geometry = "x".join([
                f"{gconfig.getint(__prg__, 'width', 900)}",
                f"{gconfig.getint(__prg__, 'height', 650)}"
            ])
        try:
            self.geometry(geometry)
        except Exception:
            pass

        # restore windowsState
        try:
            self.wm_state(gconfig.getstr(__prg__, "windowstate", "normal"))
        except Exception:
            pass

        self._swapKeyboard = gconfig.getint("Control", "swap", 0)

        # self._onStart = gconfig.getstr("Events", "onstart", "")
        # globSender._onStop = gconfig.getstr("Events", "onstop", "")

        tkextra.Balloon.font = gconfig.getfont("balloon", tkextra.Balloon.font)

        Ribbon._FONT = gconfig.getfont("ribbon.label", Ribbon._FONT)
        Ribbon._TABFONT = gconfig.getfont("ribbon.tab", Ribbon._TABFONT)

        Ribbon._ACTIVE_COLOR = gconfig.getstr(
            "Color", "ribbon.active", Ribbon._ACTIVE_COLOR
        )
        Ribbon._LABEL_SELECT_COLOR = gconfig.getstr(
            "Color", "ribbon.select", Ribbon._LABEL_SELECT_COLOR
        )

        self.tools.loadConfig()
        self.loadShortcuts()

    # -----------------------------------------------------------------------
    def saveConfig(self):
        # Program
        gconfig.setstr(__prg__, "width", str(self.winfo_width()))
        gconfig.setstr(__prg__, "height", str(self.winfo_height()))
        gconfig.setstr(__prg__, "sash", str(self.paned.sash_coord(0)[0]))

        # save windowState
        gconfig.setstr(__prg__, "windowstate", str(self.wm_state()))
        gconfig.setstr(__prg__, "page", str(
            self.ribbon.getActivePage().name))

        # Connection
        # Page.saveConfig()
        for frame in self.leftpanels.values():
            frame.saveConfig()
        globSender.saveConfig()
        self.tools.saveConfig()
        self.canvasFrame.saveConfig()

    # -----------------------------------------------------------------------
    def loadHistory(self):
        try:
            f = open(Utils.hisFile)
        except Exception:
            return
        self.history = [x.strip() for x in f]
        self._historySearch = None
        f.close()

    # -----------------------------------------------------------------------
    def saveHistory(self):
        try:
            f = open(Utils.hisFile, "w")
        except Exception:
            return
        f.write("\n".join(self.history))
        f.close()

    # -----------------------------------------------------------------------
    def cut(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.editor.cut()
            return "break"

    # -----------------------------------------------------------------------
    def copy(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.editor.copy()
            return "break"

    # -----------------------------------------------------------------------
    def paste(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.editor.paste()
            return "break"

    # -----------------------------------------------------------------------
    def undo(self, event=None):
        if not globSender.running and globGCode.canUndo():
            globGCode.undo()
            self.editor.fill()
            self.drawAfter()
        return "break"

    # -----------------------------------------------------------------------
    def redo(self, event=None):
        if not globSender.running and globGCode.canRedo():
            globGCode.redo()
            self.editor.fill()
            self.drawAfter()
        return "break"

    # -----------------------------------------------------------------------
    def addUndo(self, undoinfo):
        globGCode.addUndo(undoinfo)

    # -----------------------------------------------------------------------
    def about(self, event=None, timer=None):
        tkdialogs.AboutDialog(self)

    # -----------------------------------------------------------------------
    def alarmClear(self, event=None):
        self._alarm = False

    # -----------------------------------------------------------------------
    # Display information on selected blocks
    # -----------------------------------------------------------------------
    def showInfo(self, event=None):
        self.canvas.showInfo(self.editor.getSelectedBlocks())
        return "break"

    # -----------------------------------------------------------------------
    def showStats(self, **_):
        tkdialogs.ShowStats(self, globGCode)

    # -----------------------------------------------------------------------
    def reportDialog(self, event=None):
        tkdialogs.ReportDialog(self)

    # -----------------------------------------------------------------------
    def viewChange(self, event=None):
        if globSender.running:
            self._selectI = 0  # last selection pointer in items
        self.draw()

    # ----------------------------------------------------------------------
    def refresh(self, event=None):
        self.editor.fill()
        self.draw()

    # ----------------------------------------------------------------------
    def draw(self):
        view = CNCCanvas.VIEWS.index(self.canvasFrame.view.get())
        self.canvas.draw(view)
        self.selectionChange()

    # ----------------------------------------------------------------------
    # Redraw with a small delay
    # ----------------------------------------------------------------------
    def drawAfter(self, event=None):
        if self._drawAfter is not None:
            self.after_cancel(self._drawAfter)
        self._drawAfter = self.after(DRAW_AFTER, self.draw)
        return "break"

    # -----------------------------------------------------------------------
    def canvasFocus(self, event=None):
        self.canvas.focus_set()
        return "break"

    # -----------------------------------------------------------------------
    def selectAll(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.editor.copy()
            self.ribbon.changePage("Editor")
            self.editor.selectAll()
            self.selectionChange()
            return "break"

    # -----------------------------------------------------------------------
    def unselectAll(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.ribbon.changePage("Editor")
            self.editor.selectClear()
            self.selectionChange()
            return "break"

    # -----------------------------------------------------------------------
    def selectInvert(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.ribbon.changePage("Editor")
            self.editor.selectInvert()
            self.selectionChange()
            return "break"

    # -----------------------------------------------------------------------
    def selectLayer(self, event=None):
        focus = self.focus_get()
        if focus in (self.canvas, self.editor):
            self.ribbon.changePage("Editor")
            self.editor.selectLayer()
            self.selectionChange()
            return "break"

    # -----------------------------------------------------------------------
    def find(self, event=None):
        self.ribbon.changePage("Editor")

    # -----------------------------------------------------------------------
    def findNext(self, event=None):
        self.ribbon.changePage("Editor")

    # -----------------------------------------------------------------------
    def replace(self, event=None):
        self.ribbon.changePage("Editor")

    # -----------------------------------------------------------------------
    def activeBlock(self):
        return self.editor.activeBlock()

    # -----------------------------------------------------------------------
    # Keyboard binding to <Return>
    # -----------------------------------------------------------------------
    def cmdExecute(self, event):
        self.commandExecute()

    # ----------------------------------------------------------------------
    def insertCommand(self, cmd, execute=False):
        self.command.delete(0, "end")
        self.command.insert(0, cmd)
        if execute:
            self.commandExecute(False)

    # -----------------------------------------------------------------------
    # Execute command from command line
    # -----------------------------------------------------------------------
    def commandExecute(self, addHistory=True):
        self._historyPos = None
        self._historySearch = None

        line = self.command.get().strip()
        if not line:
            return

        if self._historyPos is not None:
            if globSender.history[self._historyPos] != line:
                globSender.history.append(line)
        elif not globSender.history or globSender.history[-1] != line:
            globSender.history.append(line)

        if len(globSender.history) > MAX_HISTORY:
            globSender.history.pop(0)
        self.command.delete(0, "end")
        self.execute(line)

    # -----------------------------------------------------------------------
    # Execute a single command
    # -----------------------------------------------------------------------
    def execute(self, line):
        try:
            line = globSender.evaluate(line)
        except Exception:
            tk.messagebox.showerror(
                _("Evaluation error"), sys.exc_info()[1], parent=self
            )
            return "break"

        if line is None:
            return "break"

        if globSender.executeGcode(line):
            return "break"

        oline = line.strip()
        line = oline.replace(",", " ").split()
        cmd = line[0].upper()

        # ABO*UT: About dialog
        if rexx.abbrev("ABOUT", cmd, 3):
            self.about()

        elif rexx.abbrev("AUTOLEVEL", cmd, 4):
            self.executeOnSelection("AUTOLEVEL", True)

        # CAM*ERA: camera actions
        elif rexx.abbrev("CAMERA", cmd, 3):
            # FIXME will make crazy the button state
            if rexx.abbrev("SWITCH", line[1].upper(), 1):
                self.groups["Probe:Camera"].switchCamera()

            elif rexx.abbrev("SPINDLE", line[1].upper(), 2):
                self.leftpanels["Probe:Camera"].registerSpindle()

            elif rexx.abbrev("CAMERA", line[1].upper(), 1):
                self.leftpanels["Probe:Camera"].registerCamera()

        # CLE*AR: clear terminal
        elif rexx.abbrev("CLEAR", cmd, 3) or cmd == "CLS":
            self.ribbon.changePage("Terminal")
            self.leftpanels["Terminal"].clear()

        # CLOSE: close path - join end with start with a line segment
        elif rexx.abbrev("CLOSE", cmd, 4):
            self.executeOnSelection("CLOSE", True)

        # CONT*ROL: switch to control tab
        elif rexx.abbrev("CONTROL", cmd, 4):
            self.ribbon.changePage("Control")

        # CUT [depth] [pass-per-depth] [z-surface] [feed] [feedz]: replicate
        # selected blocks to cut-height
        # default values are taken from the active material
        elif cmd == "CUT":
            try:
                depth = float(line[1])
            except Exception:
                depth = None

            try:
                step = float(line[2])
            except Exception:
                step = None

            try:
                surface = float(line[3])
            except Exception:
                surface = None

            try:
                feed = float(line[4])
            except Exception:
                feed = None

            try:
                feedz = float(line[5])
            except Exception:
                feedz = None
            self.executeOnSelection(
                "CUT", True, depth, step, surface, feed, feedz)

        # DOWN: move downward in cutting order the selected blocks
        # UP: move upwards in cutting order the selected blocks
        elif cmd == "DOWN":
            self.editor.orderDown()
        elif cmd == "UP":
            self.editor.orderUp()

        # DIR*ECTION
        elif rexx.abbrev("DIRECTION", cmd, 3):
            if rexx.abbrev("CLIMB", line[1].upper(), 2):
                direction = -2
            elif rexx.abbrev("CONVENTIONAL", line[1].upper(), 2):
                direction = 2
            elif rexx.abbrev("CW", line[1].upper(), 2):
                direction = 1
            elif rexx.abbrev("CCW", line[1].upper(), 2):
                direction = -1
            else:
                tk.messagebox.showerror(
                    _("Direction command error"),
                    _("Invalid direction {} specified").format(line[1]),
                    parent=self,
                )
                return "break"
            self.executeOnSelection("DIRECTION", True, direction)

        # DRI*LL [depth] [peck]: perform drilling at all penetrations points
        elif rexx.abbrev("DRILL", cmd, 3):
            try:
                h = float(line[1])
            except Exception:
                h = None

            try:
                p = float(line[2])
            except Exception:
                p = None
            self.executeOnSelection("DRILL", True, h, p)

        # ECHO <msg>: echo message
        elif cmd == "ECHO":
            self.setStatus(oline[5:].strip())

        # FEED on/off: append feed commands on every motion line for
        # feed override testing
        elif cmd == "FEED":
            try:
                globCNC.appendFeed = line[1].upper() == "ON"
            except Exception:
                globCNC.appendFeed = True
            self.setStatus(
                globCNC.appendFeed
                and "Feed appending turned on"
                or "Feed appending turned off"
            )

        # INV*ERT: invert selected blocks
        elif rexx.abbrev("INVERT", cmd, 3):
            self.editor.invertBlocks()

        # MSG|MESSAGE <msg>: echo message
        elif cmd in ("MSG", "MESSAGE"):
            tk.messagebox.showinfo(
                "Message", oline[oline.find(" ") + 1:].strip(), parent=self
            )

        # FIL*TER: filter editor blocks with text
        elif rexx.abbrev("FILTER", cmd, 3) or cmd == "ALL":
            try:
                self.editor.filter = line[1]
            except Exception:
                self.editor.filter = None
            self.editor.fill()

        # ED*IT: edit current line or item
        elif rexx.abbrev("EDIT", cmd, 2):
            self.edit()

        # IM*PORT <filename>: import filename with gcode or dxf at cursor
        # location or at the end of the file
        elif rexx.abbrev("IMPORT", cmd, 2):
            try:
                self.importFile(line[1])
            except Exception:
                self.importFile()

        # INK*SCAPE: remove unnecessary Z motion as a result of inkscape
        # gcodetools
        elif rexx.abbrev("INKSCAPE", cmd, 3):
            if len(line) > 1 and rexx.abbrev("ALL", line[1].upper()):
                self.editor.selectAll()
            self.executeOnSelection("INKSCAPE", True)

        # ISLAND set or toggle island tag
        elif rexx.abbrev("ISLAND", cmd, 3):
            if len(line) > 1:
                if line[1].upper() == "1":
                    isl = True
                else:
                    isl = False
            else:
                isl = None
            self.executeOnSelection("ISLAND", True, isl)

        # ISO1: switch to ISO1 projection
        elif cmd == "ISO1":
            self.canvasFrame.viewISO1()
        # ISO2: switch to ISO2 projection
        elif cmd == "ISO2":
            self.canvasFrame.viewISO2()
        # ISO3: switch to ISO3 projection
        elif cmd == "ISO3":
            self.canvasFrame.viewISO3()

        # LO*AD [filename]: load filename containing g-code
        elif rexx.abbrev("LOAD", cmd, 2) and len(line) == 1:
            self.loadDialog()

        # MIR*ROR [H*ORIZONTAL/V*ERTICAL]: mirror selected objects
        # horizontally or vertically
        elif rexx.abbrev("MIRROR", cmd, 3):
            if len(line) == 1:
                return "break"
            line1 = line[1].upper()
            if not self.editor.curselection():
                self.editor.selectAll()
            if rexx.abbrev("HORIZONTAL", line1):
                self.executeOnSelection("MIRRORH", False)
            elif rexx.abbrev("VERTICAL", line1):
                self.executeOnSelection("MIRRORV", False)

        elif rexx.abbrev("ORDER", cmd, 2):
            if line[1].upper() == "UP":
                self.editor.orderUp()
            elif line[1].upper() == "DOWN":
                self.editor.orderDown()

        # MO*VE [|CE*NTER|BL|BR|TL|TR|UP|DOWN|x] [[y [z]]]:
        # move selected objects either by mouse or by coordinates
        elif rexx.abbrev("MOVE", cmd, 2):
            if len(line) == 1:
                self.canvas.setActionMove()
                return "break"
            line1 = line[1].upper()
            dz = 0.0
            if rexx.abbrev("CENTER", line1, 2):
                dx = -(globCNC.vars["xmin"] + globCNC.vars["xmax"]) / 2.0
                dy = -(globCNC.vars["ymin"] + globCNC.vars["ymax"]) / 2.0
                self.editor.selectAll()
            elif line1 == "BL":
                dx = -globCNC.vars["xmin"]
                dy = -globCNC.vars["ymin"]
                self.editor.selectAll()
            elif line1 == "BC":
                dx = -(globCNC.vars["xmin"] + globCNC.vars["xmax"]) / 2.0
                dy = -globCNC.vars["ymin"]
                self.editor.selectAll()
            elif line1 == "BR":
                dx = -globCNC.vars["xmax"]
                dy = -globCNC.vars["ymin"]
                self.editor.selectAll()
            elif line1 == "TL":
                dx = -globCNC.vars["xmin"]
                dy = -globCNC.vars["ymax"]
                self.editor.selectAll()
            elif line1 == "TC":
                dx = -(globCNC.vars["xmin"] + globCNC.vars["xmax"]) / 2.0
                dy = -globCNC.vars["ymax"]
                self.editor.selectAll()
            elif line1 == "TR":
                dx = -globCNC.vars["xmax"]
                dy = -globCNC.vars["ymax"]
                self.editor.selectAll()
            elif line1 == "LC":
                dx = -globCNC.vars["xmin"]
                dy = -(globCNC.vars["ymin"] + globCNC.vars["ymax"]) / 2.0
                self.editor.selectAll()
            elif line1 == "RC":
                dx = -globCNC.vars["xmax"]
                dy = -(globCNC.vars["ymin"] + globCNC.vars["ymax"]) / 2.0
                self.editor.selectAll()
            elif line1 in ("UP", "DOWN"):
                dx = line1
                dy = dz = line1
            else:
                try:
                    dx = float(line[1])
                except Exception:
                    dx = 0.0
                try:
                    dy = float(line[2])
                except Exception:
                    dy = 0.0
                try:
                    dz = float(line[3])
                except Exception:
                    dz = 0.0
            self.executeOnSelection("MOVE", False, dx, dy, dz)

        # OPT*IMIZE: reorder selected blocks to minimize rapid motions
        elif rexx.abbrev("OPTIMIZE", cmd, 3):
            if not self.editor.curselection():
                tk.messagebox.showinfo(
                    _("Optimize"),
                    _("Please select the blocks of gcode you want "
                      + "to optimize."),
                    parent=self,
                )
            else:
                self.executeOnSelection("OPTIMIZE", True)

        # # FIXME comment for ORIENT not OPTIMIZE
        # OPT*IMIZE: reorder selected blocks to minimize rapid motions
        elif rexx.abbrev("ORIENT", cmd, 4):
            if not self.editor.curselection():
                self.editor.selectAll()
            self.executeOnSelection("ORIENT", False)

        # ORI*GIN x y z: move origin to x,y,z by moving all to -x -y -z
        elif rexx.abbrev("ORIGIN", cmd, 3):
            try:
                dx = -float(line[1])
            except Exception:
                dx = 0.0
            try:
                dy = -float(line[2])
            except Exception:
                dy = 0.0
            try:
                dz = -float(line[3])
            except Exception:
                dz = 0.0
            self.editor.selectAll()
            self.executeOnSelection("MOVE", False, dx, dy, dz)

        # POC*KET: create pocket path
        elif rexx.abbrev("POCKET", cmd, 3):
            self.pocket()

        # PROF*ILE [offset]: create profile path
        elif rexx.abbrev("PROFILE", cmd, 3):
            if len(line) > 1:
                self.profile(line[1])
            else:
                self.profile()

        # REV*ERSE: reverse path direction
        elif rexx.abbrev("REVERSE", cmd, 3):
            self.executeOnSelection("REVERSE", True)

        # ROT*ATE [CCW|CW|FLIP|ang] [x0 [y0]]: rotate selected blocks
        # counter-clockwise(90) / clockwise(-90) / flip(180)
        # 90deg or by a specific angle and a pivot point
        elif rexx.abbrev("ROTATE", cmd, 3):
            line1 = line[1].upper()
            x0 = y0 = 0.0
            if line1 == "CCW":
                ang = 90.0
            elif line1 == "CW":
                ang = -90.0
            elif line1 == "FLIP":
                ang = 180.0
            else:
                try:
                    ang = float(line[1])
                except Exception:
                    pass
                try:
                    x0 = float(line[2])
                except Exception:
                    pass
                try:
                    y0 = float(line[3])
                except Exception:
                    pass
            self.executeOnSelection("ROTATE", False, ang, x0, y0)

        # ROU*ND [n]: round all digits to n fractional digits
        elif rexx.abbrev("ROUND", cmd, 3):
            acc = None
            if len(line) > 1:
                if rexx.abbrev("ALL", line[1].upper()):
                    self.editor.selectAll()
                else:
                    try:
                        acc = int(line[1])
                    except Exception:
                        pass
            self.executeOnSelection("ROUND", False, acc)

        # RU*LER: measure distances with mouse ruler
        elif rexx.abbrev("RULER", cmd, 2):
            self.canvas.setActionRuler()

        # STAT*ISTICS: show statistics of current job
        elif rexx.abbrev("STATISTICS", cmd, 4):
            self.showStats()

        # STEP [s]: set motion step size to s
        elif cmd == "STEP":
            try:
                self.control.setStep(float(line[1]))
            except Exception:
                pass

        # SPI*NDLE [ON|OFF|speed]: turn on/off spindle
        elif rexx.abbrev("SPINDLE", cmd, 3):
            if len(line) > 1:
                if line[1].upper() == "OFF":
                    self.gstate.spindle.set(False)
                elif line[1].upper() == "ON":
                    self.gstate.spindle.set(True)
                else:
                    try:
                        rpm = int(line[1])
                        if rpm == 0:
                            self.gstate.spindleSpeed.set(0)
                            self.gstate.spindle.set(False)
                        else:
                            self.gstate.spindleSpeed.set(rpm)
                            self.gstate.spindle.set(True)
                    except Exception:
                        pass
            else:
                # toggle spindle
                self.gstate.spindle.set(not self.gstate.spindle.get())
            self.gstate.spindleControl()

        # STOP: stop current run
        elif cmd == "STOP":
            globSender.stopRun()

        # TAB*S [ntabs] [dtabs] [dx] [dy] [z]: create tabs on selected blocks
        # default values are taken from the active tab
        elif rexx.abbrev("TABS", cmd, 3):
            tabs = self.tools["TABS"]
            try:
                ntabs = int(line[1])
            except Exception:
                ntabs = int(tabs["ntabs"])
            try:
                dtabs = float(line[2])
            except Exception:
                dtabs = tabs.fromMm("dtabs")
            try:
                dx = float(line[3])
            except Exception:
                dx = tabs.fromMm("dx")
            try:
                dy = float(line[4])
            except Exception:
                dy = tabs.fromMm("dy")
            try:
                z = float(line[5])
            except Exception:
                z = tabs.fromMm("z")
            try:
                circular = bool(line[6])
            except Exception:
                circular = True
            self.executeOnSelection(
                "TABS", True, ntabs, dtabs, dx, dy, z, circular)

        # TERM*INAL: switch to terminal tab
        elif rexx.abbrev("TERMINAL", cmd, 4):
            self.ribbon.changePage("Terminal")

        # TOOL [diameter]: set diameter of cutting tool
        elif cmd in ("BIT", "TOOL", "MILL"):
            try:
                diam = float(line[1])
            except Exception:
                tool = self.tools["EndMill"]
                diam = self.tools.fromMm(tool["diameter"])
            self.setStatus(_("EndMill: {} {}").format(tool["name"], diam))

        # TOOLS
        elif cmd == "TOOLS":
            self.ribbon.changePage("CAM")

        # UNL*OCK: unlock grbl
        elif rexx.abbrev("UNLOCK", cmd, 3):
            globSender.unlock()

        # US*ER cmd: execute user command, cmd=number or name
        elif rexx.abbrev("USER", cmd, 2):
            n = gconfig.getint("Buttons", "n", 6)
            try:
                idx = int(line[1])
            except Exception:
                try:
                    name = line[1].upper()
                    for i in range(n):
                        if name == gconfig.getstr(
                                "Buttons",
                                f"name.{int(i)}",
                                "").upper():
                            idx = i
                            break
                except Exception:
                    return "break"
            if idx < 0 or idx >= n:
                self.setStatus(_("Invalid user command {}").format(line[1]))
                return "break"
            cmd = gconfig.getstr("Buttons", f"command.{int(idx)}", "")
            for line in cmd.splitlines():
                self.execute(line)  # FIXME: Recursion

        # RR*APID:
        elif rexx.abbrev("RRAPID", cmd, 2):
            self.leftpanels["Probe:Probe"].recordRapid()

        # RF*EED:
        elif rexx.abbrev("RFEED", cmd, 2):
            self.leftpanels["Probe:Probe"].recordFeed()

        # RP*OINT:
        elif rexx.abbrev("RPOINT", cmd, 2):
            self.leftpanels["Probe:Probe"].recordPoint()

        # RC*IRCLE:
        elif rexx.abbrev("RCIRCLE", cmd, 2):
            self.leftpanels["Probe:Probe"].recordCircle()

        # RFI*NISH:
        elif rexx.abbrev("RFINISH", cmd, 3):
            self.leftpanels["Probe:Probe"].recordFinishAll()

        # XY: switch to XY view
        # YX: switch to XY view
        elif cmd in ("XY", "YX"):
            self.canvasFrame.viewXY()

        # XZ: switch to XZ view
        # ZX: switch to XZ view
        elif cmd in ("XZ", "ZX"):
            self.canvasFrame.viewXZ()

        # YZ: switch to YZ view
        # ZY: switch to YZ view
        elif cmd in ("YZ", "ZY"):
            self.canvasFrame.viewYZ()

        else:
            rc = globSender.executeCommand(oline)
            if rc:
                tk.messagebox.showerror(rc[0], rc[1], parent=self)
            return "break"

    # -----------------------------------------------------------------------
    # Execute a command over the selected lines
    # -----------------------------------------------------------------------
    def executeOnSelection(self, cmd, blocksonly, *args):
        if blocksonly:
            items = self.editor.getSelectedBlocks()
        else:
            items = self.editor.getCleanSelection()
        if not items:
            tk.messagebox.showwarning(
                _("Nothing to do"),
                _("Operation {} requires some gcode to be selected").format(
                    cmd),
                parent=self,
            )
            return

        self.busy()
        sel = None
        if cmd == "AUTOLEVEL":
            sel = globGCode.autolevel(items)
        elif cmd == "CUT":
            sel = globGCode.cut(items, *args)
        elif cmd == "CLOSE":
            sel = globGCode.close(items)
        elif cmd == "DIRECTION":
            sel = globGCode.cutDirection(items, *args)
        elif cmd == "DRILL":
            sel = globGCode.drill(items, *args)
        elif cmd == "ORDER":
            globGCode.orderLines(items, *args)
        elif cmd == "INKSCAPE":
            globGCode.inkscapeLines()
        elif cmd == "ISLAND":
            globGCode.island(items, *args)
        elif cmd == "MIRRORH":
            globGCode.mirrorHLines(items)
        elif cmd == "MIRRORV":
            globGCode.mirrorVLines(items)
        elif cmd == "MOVE":
            globGCode.moveLines(items, *args)
        elif cmd == "OPTIMIZE":
            globGCode.optimize(items)
        elif cmd == "ORIENT":
            globGCode.orientLines(items)
        elif cmd == "REVERSE":
            globGCode.reverse(items, *args)
        elif cmd == "ROUND":
            globGCode.roundLines(items, *args)
        elif cmd == "ROTATE":
            globGCode.rotateLines(items, *args)
        elif cmd == "TABS":
            sel = globGCode.createTabs(items, *args)

        # Fill listbox and update selection
        self.editor.fill()
        if sel is not None:
            if isinstance(sel, str):
                tk.messagebox.showerror(_("Operation error"), sel, parent=self)
            else:
                self.editor.select(sel, clear=True)
        self.drawAfter()
        self.notBusy()
        self.setStatus(
            f"{cmd} {' '.join([str(a) for a in args if a is not None])}"
        )

    # -----------------------------------------------------------------------
    def profile(
        self,
        direction=None,
        offset=0.0,
        overcut=False,
        name=None,
        pocket=False,
    ):
        tool = self.tools["EndMill"]
        ofs = self.tools.fromMm(tool["diameter"]) / 2.0
        sign = 1.0

        if direction is None:
            pass
        elif rexx.abbrev("INSIDE", direction.upper()):
            sign = -1.0
        elif rexx.abbrev("OUTSIDE", direction.upper()):
            sign = 1.0
        else:
            try:
                ofs = float(direction) / 2.0
            except Exception:
                pass

        # additional offset
        try:
            ofs += float(offset)
        except Exception:
            pass

        self.busy()
        blocks = self.editor.getSelectedBlocks()
        # on return we have the blocks with the new blocks to select
        msg = globGCode.profile(blocks, ofs * sign, overcut, name, pocket)
        if msg:
            tk.messagebox.showwarning(
                "Open paths", f"WARNING: {msg}", parent=self)
        self.editor.fill()
        self.editor.selectBlocks(blocks)
        self.draw()
        self.notBusy()
        self.setStatus(_("Profile block distance={:g}").format(ofs * sign))

    # -----------------------------------------------------------------------
    def pocket(self, name=None):
        tool = self.tools["EndMill"]
        diameter = self.tools.fromMm(tool["diameter"])
        try:
            stepover = tool["stepover"] / 100.0
        except TypeError:
            stepover = 0.0

        self.busy()
        blocks = self.editor.getSelectedBlocks()
        # on return we have the blocks with the new blocks to select
        msg = globGCode.pocket(blocks, diameter, stepover, name)
        if msg:
            tk.messagebox.showwarning(
                _("Open paths"), _("WARNING: {}").format(msg), parent=self
            )
        self.editor.fill()
        self.editor.selectBlocks(blocks)
        self.draw()
        self.notBusy()

    # -----------------------------------------------------------------------
    def trochprofile_bcnc(
        self,
        cutDiam=0.0,
        direction=None,
        offset=0.0,
        overcut=False,
        adaptative=False,
        adaptedRadius=0.0,
        tooldiameter=0.0,
        targetDepth=0.0,
        depthIncrement=0.0,
        tabsnumber=0.0,
        tabsWidth=0.0,
        tabsHeight=0.0,
    ):
        adaptedRadius = float(adaptedRadius)
        ofs = float(cutDiam) / 2.0
        sign = 1.0

        if direction is None:
            pass
        elif rexx.abbrev("INSIDE", direction.upper()):
            sign = -1.0
        elif rexx.abbrev("OUTSIDE", direction.upper()):
            sign = 1.0
        elif rexx.abbrev("ON", direction.upper()):
            ofs = 0
        else:
            try:
                ofs = float(direction) / 2.0
            except Exception:
                pass

        # additional offset
        try:
            ofs += float(offset)
        except Exception:
            pass

        self.busy()
        blocks = self.editor.getSelectedBlocks()
        # on return we have the blocks with the new blocks to select
        msg = globGCode.trochprofile_cnc(
            blocks,
            ofs * sign,
            overcut,
            adaptative,
            adaptedRadius,
            cutDiam,
            tooldiameter,
            targetDepth,
            depthIncrement,
            tabsnumber,
            tabsWidth,
            tabsHeight,
        )
        if msg:
            tk.messagebox.showwarning(
                "Open paths", f"WARNING: {msg}", parent=self)
        msg2 = adaptative
        if msg2:
            tk.messagebox.showwarning(
                "Adaptative",
                "WARNING: Adaptive route generated, but Trocoidal still does "
                + "not implement it. Use will give wrong results in the "
                + "corners!",
                parent=self,
            )

        self.editor.fill()
        self.editor.selectBlocks(blocks)
        self.draw()
        self.notBusy()
        self.setStatus(_("Profile block distance={:g}").format(ofs * sign))

    # -----------------------------------------------------------------------
    def edit(self, event=None):
        page = self.ribbon.getActivePage()
        if page.name == "Editor":
            self.editor.edit()
        elif page.name == "CAM":
            page.edit()

    # -----------------------------------------------------------------------
    def commandFocus(self, event=None):
        self.command.focus_set()

    # -----------------------------------------------------------------------
    def commandFocusIn(self, event=None):
        self.cmdlabel["foreground"] = "Blue"

    # -----------------------------------------------------------------------
    def commandFocusOut(self, event=None):
        self.cmdlabel["foreground"] = "Black"

    # -----------------------------------------------------------------------
    # FIXME why it is not called?
    # -----------------------------------------------------------------------
    def commandKey(self, event):
        if event.char or event.keysym in ("BackSpace"):
            self._historyPos = None
            self._historySearch = None

    # -----------------------------------------------------------------------
    def commandHistoryUp(self, event=None):
        if self._historyPos is None:
            s = self.command.get()
            if globSender.history:
                self._historyPos = len(globSender.history) - 1
            else:
                self._historySearch = None
                return
            if s and self._historySearch is None:
                self._historySearch = s.strip().upper()
        else:
            self._historyPos = max(0, self._historyPos - 1)

        if self._historySearch:
            for i in range(self._historyPos, -1, -1):
                h = globSender.history[i]
                if h.upper().startswith(self._historySearch):
                    self._historyPos = i
                    break

        self.command.delete(0, "end")
        self.command.insert(0, globSender.history[self._historyPos])

    # -----------------------------------------------------------------------
    def commandHistoryDown(self, event=None):
        if self._historyPos is None:
            self._historySearch = None
            return
        else:
            self._historyPos += 1
            if self._historyPos >= len(globSender.history):
                self._historyPos = None
                self._historySearch = None

        if self._historySearch:
            for i in range(self._historyPos, len(globSender.history)):
                h = globSender.history[i]
                if h.upper().startswith(self._historySearch):
                    self._historyPos = i
                    break

        self.command.delete(0, "end")
        if self._historyPos is not None:
            self.command.insert(0, globSender.history[self._historyPos])

    # -----------------------------------------------------------------------
    def select(self, items, double, clear, toggle=True):
        self.editor.select(items, double, clear, toggle)
        self.selectionChange()

    # ----------------------------------------------------------------------
    # Selection has changed highlight the canvas
    # ----------------------------------------------------------------------
    def selectionChange(self, event=None):
        items = self.editor.getSelection()
        self.canvas.clearSelection()
        if not items:
            return
        self.canvas.select(items)
        self.canvas.activeMarker(self.editor.getActive())

    # -----------------------------------------------------------------------
    # Create a new file
    # -----------------------------------------------------------------------
    def newFile(self, event=None):
        if globSender.running:
            return
        if self.fileModified():
            return
        globGCode.init()
        globGCode.headerFooter()
        self.editor.fill()
        self.draw()
        self.title(f"{__prg__} {__version__} {__platform_fingerprint__}")

    # -----------------------------------------------------------------------
    # load dialog
    # -----------------------------------------------------------------------
    def loadDialog(self, event=None):
        if globSender.running:
            return
        filename = filedialog.askopenfilename(
            title=_("Open file"),
            initialdir=gconfig.getstr("File", "dir"),
            initialfile=gconfig.getstr("File", "file"),
            # initialfile=os.path.join(
            #     gconfig.getstr("File", "dir"), gconfig.getstr("File", "file")
            # ),
            filetypes=FILETYPES,
        )
        # filename = bfiledialog.askopenfilename(
        #     master=self,
        #     title=_("Open file"),
        #     initialfile=os.path.join(
        #         gconfig.getstr("File", "dir"), gconfig.getstr("File", "file")
        #     ),
        #     filetypes=FILETYPES,
        # )
        if filename:
            self.load(filename)
        return "break"

    # -----------------------------------------------------------------------
    # save dialog
    # -----------------------------------------------------------------------
    def saveDialog(self, event=None):
        if globSender.running:
            return
        fn, ext = os.path.splitext(gconfig.getstr("File", "file"))
        if ext in (".dxf", ".DXF"):
            ext = ".ngc"
        filename = filedialog.asksaveasfilename(
            title=_("Save file"),
            initialdir=gconfig.getstr("File", "dir"),
            initialfile=f"{fn}{ext}",
            defaultextension=ext,
            # initialfile=os.path.join(
            #     gconfig.getstr("File", "dir"), f"{fn}{ext}"),
            filetypes=FILETYPES,
        )
        # filename = bfiledialog.asksaveasfilename(
        #     master=self,
        #     title=_("Save file"),
        #     initialfile=os.path.join(gconfig.getstr("File", "dir"), fn + ext),
        #     filetypes=FILETYPES,
        # )
        if filename:
            self.save(filename)
        return "break"

    # -----------------------------------------------------------------------
    def fileModified(self):
        if globGCode.isModified():
            ans = tk.messagebox.askquestion(
                _("File modified"),
                _("Gcode was modified do you want to save it first?"),
                type=tk.messagebox.YESNOCANCEL,
                parent=self,
            )
            if ans == tk.messagebox.CANCEL:
                return True
            if ans == tk.messagebox.YES or ans is True:
                self.saveAll()

        if not globGCode.probe.isEmpty() and not globGCode.probe.saved:
            ans = tk.messagebox.askquestion(
                _("Probe File modified"),
                _("Probe was modified do you want to save it first?"),
                type=tk.messagebox.YESNOCANCEL,
                parent=self,
            )
            if ans == tk.messagebox.CANCEL:
                return True
            if ans == tk.messagebox.YES or ans is True:
                if globGCode.probe.filename == "":
                    self.saveDialog()
                else:
                    globGCode.probe.save()
        return False

    # -----------------------------------------------------------------------
    # Load a file into editor
    # -----------------------------------------------------------------------
    def load(self, filename, autoloaded=False):
        fn, ext = os.path.splitext(filename)
        if ext == ".probe":
            pass
        else:
            if self.fileModified():
                return

            msg = _("Autolevel/probe information already exists.\nDelete it?")
            if not globGCode.probe.isEmpty():
                ans = tk.messagebox.askquestion(
                    _("Existing Autolevel"),
                    msg,
                    parent=self,
                )
                if ans == tk.messagebox.YES or ans is True:
                    globGCode.probe.init()

        self.setStatus(_("Loading: {} ...").format(filename), True)
        globSender.load(filename)

        if ext == ".probe":
            self.autolevel.setValues()
            self.event_generate("<<DrawProbe>>")

        elif ext == ".orient":
            self.event_generate("<<DrawOrient>>")
            self.event_generate("<<OrientSelect>>", data=0)
            self.event_generate("<<OrientUpdate>>")

        else:
            self.editor.selectClear()
            self.editor.fill()
            self.canvas.reset()
            self.draw()
            self.canvas.fit2Screen()
            self.leftpanels["CAM"].populate()

        if autoloaded:
            self.setStatus(
                _("'{}' reloaded at '{}'").format(
                    filename, str(datetime.now()))
            )
        else:
            self.setStatus(_("'{}' loaded").format(filename))
        self.title(
            f"{__prg__} {__version__}: {globGCode.filename} "
            + f"{__platform_fingerprint__}"
        )

    # -----------------------------------------------------------------------
    def save(self, filename):
        globSender.save(filename)
        self.setStatus(_("'{}' saved").format(filename))
        self.title(
            f"{__prg__} {__version__}: {globGCode.filename} "
            + f"{__platform_fingerprint__}"
        )

    # -----------------------------------------------------------------------
    def saveAll(self, event=None):
        if globGCode.filename:
            globSender.saveAll()
        else:
            self.saveDialog()
        return "break"

    # -----------------------------------------------------------------------
    def reload(self, event=None):
        self.load(globGCode.filename)

    # -----------------------------------------------------------------------
    def importFile(self, filename=None):
        from gcode import GCode
        if filename is None:
            filename = filedialog.askopenfilename(
                initialdir=gconfig.getstr("File", "dir"),
                initialfile=gconfig.getstr("File", "file"),
                # initialfile=os.path.join(
                #     gconfig.getstr("File", "dir"),
                #     gconfig.getstr("File", "file")
                # ),
                filetypes=[
                    (_("G-Code"), ("*.ngc", "*.nc", "*.gcode")),
                    ("DXF", "*.dxf"),
                    ("All", "*"),
                ],
            )
            # filename = bfiledialog.askopenfilename(
            #     master=self,
            #     title=_("Import Gcode/DXF file"),
            #     initialfile=os.path.join(
            #         gconfig.getstr("File", "dir"),
            #         gconfig.getstr("File", "file")
            #     ),
            #     filetypes=[
            #         (_("G-Code"), ("*.ngc", "*.nc", "*.gcode")),
            #         ("DXF", "*.dxf"),
            #         ("All", "*"),
            #     ],
            # )
        if filename:
            fn, ext = os.path.splitext(filename)
            ext = ext.lower()
            gcode = GCode()
            if ext == ".dxf":
                gcode.importDXF(filename)
            elif ext == ".svg":
                gcode.importSVG(filename)
            else:
                gcode.load(filename)
            sel = self.editor.getSelectedBlocks()
            if not sel:
                pos = None
            else:
                pos = sel[-1]
            self.addUndo(globGCode.insBlocksUndo(pos, gcode.blocks))
            del gcode
            self.editor.fill()
            self.draw()
            self.canvas.fit2Screen()

    # -----------------------------------------------------------------------
    def focusIn(self, event):
        if self._inFocus:
            return
        # FocusIn is generated for all sub-windows, handle only the main window
        if self is not event.widget:
            return
        self._inFocus = True
        if globGCode.checkFile():
            if globGCode.isModified():
                ans = tk.messagebox.askquestion(
                    _("Warning"),
                    _(
                        "Gcode file {} was changed since "
                        "editing started\n"
                        "Reload new version?"
                    ).format(globGCode.filename),
                    parent=self,
                )
                if ans == tk.messagebox.YES or ans is True:
                    globGCode.resetModified()
                    self.load(globGCode.filename)
            else:
                self.load(globGCode.filename, True)
        self._inFocus = False
        globGCode.syncFileTime()

    # -----------------------------------------------------------------------
    def openClose(self, event=None):
        serialPage = self.leftpanels["Serial"]
        if globSender.serial is not None:
            self.close()
            serialPage.connectBtnStyle("Unconnected.Panel.TButton")
        else:
            serialPage = self.leftpanels["Serial"]
            device = _device or serialPage.portCombo.get()  # .split("\t")[0]
            baudrate = _baud or serialPage.baudCombo.get()
            if self.open(device, baudrate):
                serialPage.connectBtnStyle("Connected.Panel.TButton")
                self.enable()

    # -----------------------------------------------------------------------
    def open(self, device, baudrate):
        try:
            return globSender.open(device, baudrate)
        except Exception:
            globSender.serial = None
            self.thread = None
            tk.messagebox.showerror(
                _("Error opening serial"), sys.exc_info()[1], parent=self
            )
        return False

    # -----------------------------------------------------------------------
    def close(self):
        try:
            self.dro.updateState()
        except tk.TclError:
            pass

    # -----------------------------------------------------------------------
    # An entry function should be called periodically during compiling
    # to check if the Pause or Stop buttons are pressed
    # @return true if the compile has to abort
    # -----------------------------------------------------------------------
    def checkStop(self):
        try:
            self.update()  # very tricky function of Tk
        except tk.TclError:
            pass
        return self._stop

    # -----------------------------------------------------------------------
    # Send enabled gcode file to the CNC machine
    # -----------------------------------------------------------------------
    def run(self, lines=None):
        self.cleanAfter = True  # Clean when this operation stops
        print("Will clean after this operation")

        if globSender.serial is None and not globCNC.developer:
            tk.messagebox.showerror(
                _("Serial Error"), _("Serial is not connected"), parent=self
            )
            return
        if globSender.running:
            if self._pause:
                globSender.resume()
                return
            tk.messagebox.showerror(
                _("Already running"), _("Please stop before"), parent=self
            )
            return

        self.editor.selectClear()
        self.selectionChange()
        globCNC.vars["errline"] = ""

        # the buffer of the machine should be empty?
        self.initRun()
        self.canvas.clearSelection()
        self._runLines = sys.maxsize  # temporary WARNING this value is used
        # by Sender._serialIO to check if we
        # are still sending or we finished
        self._gcount = 0  # count executed lines
        self._selectI = 0  # last selection pointer in items
        self._paths = None  # temporary
        globCNC.vars["running"] = True  # enable running status
        globCNC.vars["_OvChanged"] = True  # force a feed change if any
        _onStart = gconfig.getstr("Events", "onstart", "")
        if _onStart:
            try:
                os.system(_onStart)
            except Exception:
                pass

        if lines is None:
            self.statusbar.setLimits(0, 9999)
            self.statusbar.setProgress(0, 0)
            self._paths = globGCode.compile(globSender.queue, self.checkStop)
            if self._paths is None:
                globSender.emptyQueue()
                globSender.purgeController()
                return
            elif not self._paths:
                globSender.runEnded()
                tk.messagebox.showerror(
                    _("Empty gcode"),
                    _("Not gcode file was loaded"),
                    parent=self
                )
                return

            # reset colors
            before = time.time()
            for ij in self._paths:  # Slow loop
                if not ij:
                    continue
                path = globGCode[ij[0]].path(ij[1])
                if path:
                    color = self.canvas.itemcget(path, "fill")
                    if color != CNCCanvas.ENABLE_COLOR:
                        self.canvas.itemconfig(
                            path, width=1, fill=CNCCanvas.ENABLE_COLOR
                        )
                    # Force a periodic update since this loop can take time
                    if time.time() - before > 0.25:
                        self.update()
                        before = time.time()

            # the buffer of the machine should be empty?
            self._runLines = len(self._paths) + 1  # plus the wait
        else:
            n = 1  # including one wait command
            for line in globCNC.compile(lines):
                if line is not None:
                    globSender.queue_command(line)
                    # if isinstance(line, str):
                    #     globSender.queue.put(line + "\n")
                    # else:
                    #     globSender.queue.put(line)
                    n += 1
            # set it at the end to be sure that all lines are queued
            self._runLines = n
        # globSender.queue.put((WAIT,))  # wait at the end to become idle
        globSender.queue_command((WAIT,))  # wait at the end to become idle

        self.setStatus(_("Running..."))
        self.statusbar.setLimits(0, self._runLines)
        self.statusbar.configText(fill="White")
        self.statusbar.config(background="DarkGray")

        self.bufferbar.configText(fill="White")
        self.bufferbar.config(background="DarkGray")
        self.bufferbar.setText("")

    # -----------------------------------------------------------------------
    # Start the web pendant
    # -----------------------------------------------------------------------
    def startPendant(self, showInfo=True):
        started = Pendant.start(self)
        if showInfo:
            hostName = f"http://{socket.gethostname()}:{Pendant.port}"
            if started:
                tk.messagebox.showinfo(
                    _("Pendant"),
                    _("Pendant started:\n") + hostName,
                    parent=self
                )
            else:
                dr = tk.messagebox.askquestion(
                    _("Pendant"),
                    _("Pendant already started:\n")
                    + hostName
                    + _("\nWould you like open it locally?"),
                    parent=self,
                )
                if dr == "yes":
                    webbrowser.open(hostName, new=2)

    # -----------------------------------------------------------------------
    # Stop the web pendant
    # -----------------------------------------------------------------------
    def stopPendant(self):
        if Pendant.stop():
            tk.messagebox.showinfo(_("Pendant"), _(
                "Pendant stopped"), parent=self)

    # -----------------------------------------------------------------------
    # Inner loop to catch any generic exception
    # -----------------------------------------------------------------------
    def _monitorSerial(self):
        # Check serial output
        t = time.time()

        # dump in the terminal what ever you can in less than 0.1s
        inserted = False
        while globSender.log.qsize() > 0 and time.time() - t < 0.1:
            try:
                msg, line = globSender.log.get_nowait()
                line = str(line).rstrip("\n")
                inserted = True

                if msg == globSender.MSG_BUFFER:
                    self.buffer.insert("end", line)

                elif msg == globSender.MSG_SEND:
                    self.terminal.insert("end", line)
                    self.terminal.itemconfig("end", foreground="Blue")

                elif msg == globSender.MSG_RECEIVE:
                    self.terminal.insert("end", line)
                    if self._insertCount:
                        # when counting is started, then continue
                        self._insertCount += 1
                    elif line and line[0] in ("[", "$"):
                        # start the counting on the first line received
                        # starting with $ or [
                        self._insertCount = 1

                elif msg == globSender.MSG_OK:
                    if self.terminal.size() > 0:
                        if self._insertCount:
                            pos = self.terminal.size() - self._insertCount
                            self._insertCount = 0
                        else:
                            pos = "end"
                        self.terminal.insert(pos, self.buffer.get(0))
                        self.terminal.itemconfig(pos, foreground="Blue")
                        self.buffer.delete(0)
                    self.terminal.insert("end", line)

                elif msg == globSender.MSG_ERROR:
                    if self.terminal.size() > 0:
                        if self._insertCount:
                            pos = self.terminal.size() - self._insertCount
                            self._insertCount = 0
                        else:
                            pos = "end"
                        self.terminal.insert(pos, self.buffer.get(0))
                        self.terminal.itemconfig(pos, foreground="Blue")
                        self.buffer.delete(0)
                    self.terminal.insert("end", line)
                    self.terminal.itemconfig("end", foreground="Red")

                elif msg == globSender.MSG_RUNEND:
                    self.terminal.insert("end", line)
                    self.terminal.itemconfig("end", foreground="Magenta")
                    self.setStatus(line)
                    self.enable()

                elif msg == globSender.MSG_CLEAR:
                    self.buffer.delete(0, "end")

                else:
                    # Unknown?
                    self.buffer.insert("end", line)
                    self.terminal.itemconfig("end", foreground="Magenta")

                if self.terminal.size() > 1000:
                    self.terminal.delete(0, 500)
            except Empty:
                break

        if inserted:
            self.terminal.see("end")

        # Check pendant
        try:
            cmd = globSender.pendant.get_nowait()
            self.execute(cmd)
        except Empty:
            pass

        # Load file from pendant
        if self._pendantFileUploaded is not None:
            self.load(self._pendantFileUploaded)
            self._pendantFileUploaded = None

        # Update position if needed
        if globSender._posUpdate:
            state = globCNC.vars["state"]
            style = "StateBtn.TButton"
            try:
                # globCNC.vars["color"] = STATECOLOR[state]
                state_ = state.replace(":", "_").replace(" ", "_")
                style = f"{state_}.StateBtn.TButton"
            except KeyError:
                if self._alarm:
                    # globCNC.vars["color"] = STATECOLOR["Alarm"]
                    style = "Alarm.StateBtn.TButton"
                else:
                    # globCNC.vars["color"] = STATECOLORDEF
                    style = "Default.StateBtn.TButton"
            self._pause = "Hold" in state
            self.dro.updateState(style)
            self.dro.updateCoords()
            self.canvas.gantry(
                globCNC.vars["wx"],
                globCNC.vars["wy"],
                globCNC.vars["wz"],
                globCNC.vars["mx"],
                globCNC.vars["my"],
                globCNC.vars["mz"],
            )
            if state == "Run":
                self.gstate.updateFeed()
            globSender._posUpdate = False

        # Update status string
        if globSender._gUpdate:
            self.gstate.updateG()
            globSender._gUpdate = False

        # Update probe and draw point
        if globSender._probeUpdate:
            self.leftpanels["Probe:Probe"].updateProbe()
            self.leftpanels["ProbeCommon"].updateTlo()
            self.canvas.drawProbe()
            globSender._probeUpdate = False

        # Update any possible variable?
        if globSender._update:
            if globSender._update == "toolheight":
                self.leftpanels["Probe:Tool"].updateTool()
            elif globSender._update == "TLO":
                self.leftpanels["ProbeCommon"].updateTlo()
            globSender._update = None

        if globSender.running:
            self.statusbar.setProgress(
                self._runLines - globSender.get_queue_size(), self._gcount
            )
            globCNC.vars["msg"] = self.statusbar.msg
            self.bufferbar.setProgress(globSender.getBufferFill())
            self.bufferbar.setText(f"{globSender.getBufferFill()}%")

            if self._selectI >= 0 and self._paths:
                while self._selectI <= self._gcount and self._selectI < len(
                    self._paths
                ):
                    if self._paths[self._selectI]:
                        i, j = self._paths[self._selectI]
                        path = globGCode[i].path(j)
                        if path:
                            self.canvas.itemconfig(
                                path, width=2, fill=CNCCanvas.PROCESS_COLOR
                            )
                    self._selectI += 1

            if self._gcount >= self._runLines:
                globSender.runEnded()

    # -----------------------------------------------------------------------
    # "thread" timed function looking for messages in the serial thread
    # and reporting back in the terminal
    # -----------------------------------------------------------------------
    def monitorSerial(self):
        try:
            self._monitorSerial()
        except Exception:
            typ, val, tb = sys.exc_info()
            traceback.print_exception(typ, val, tb)
        self.after(MONITOR_AFTER, self.monitorSerial)

    # -----------------------------------------------------------------------
    def get(self, section, item):
        return gconfig.get(section, item)

    # -----------------------------------------------------------------------
    def set(self, section, item, value):
        return gconfig.set(section, item, value)


if __name__ == "__main__":
    sys.stderr.write("ERROR: The program cannot be started from this file!\n")
    sys.stderr.write("\tPlease use __main__.py instead!\n")

    sys.exit()
