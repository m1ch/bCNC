#
# Copyright and User License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Copyright Vasilis.Vlachoudis@cern.ch for the
# European Organization for Nuclear Research (CERN)
#
# Please consult the flair documentation for the license
#
# DISCLAIMER
# ~~~~~~~~~~
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY, OF
# SATISFACTORY QUALITY, AND FITNESS FOR A PARTICULAR PURPOSE
# OR USE ARE DISCLAIMED. THE COPYRIGHT HOLDERS AND THE
# AUTHORS MAKE NO REPRESENTATION THAT THE SOFTWARE AND
# MODIFICATIONS THEREOF, WILL NOT INFRINGE ANY PATENT,
# COPYRIGHT, TRADE SECRET OR OTHER PROPRIETARY RIGHT.
#
# LIMITATION OF LIABILITY
# ~~~~~~~~~~~~~~~~~~~~~~~
# THE COPYRIGHT HOLDERS AND THE AUTHORS SHALL HAVE NO
# LIABILITY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL,
# CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES OF ANY
# CHARACTER INCLUDING, WITHOUT LIMITATION, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR PROFITS,
# OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY THEORY
# OF CONTRACT, WARRANTY, TORT (INCLUDING NEGLIGENCE), PRODUCT
# LIABILITY OR OTHERWISE, ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#
# Author:   Vasilis.Vlachoudis@cern.ch
# Date:     02-Aug-2006

import subprocess
import os
import sys
import time
import webbrowser
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from globalConstants import (__prg__,
                               __version__,
                               __www__,
                               __contribute__,
                               __translations__,
                               __credits__,
                               __date__)
from globalConfig import config as gconfig
from cnc import globCNC

import Utils
from . import bfiledialog
from . import tkextra

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Similar to the Dialog.py from Tk but transient to master
#
# This class displays a dialog box, waits for a button in the dialog
# to be invoked, then returns the index of the selected button.  If the
# dialog somehow gets destroyed, -1 is returned.
#
# Arguments:
# w -       Window to use for dialog top-level.
# title -   Title to display in dialog's decorative frame.
# text -    Message to display in dialog.
# bitmap -  Bitmap to display in dialog (empty string means none).
# default - Index of button that is to display the default ring
#           (-1 means none).
# args -    One or more strings to display in buttons across the
#           bottom of the dialog box.
# =============================================================================
class Dialog(tk.Toplevel):
    def __init__(self, master=None, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, class_="Dialog", **kw)
        self.transient(master)
        self.title(cnf["title"])
        self.iconname("Dialog")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.num = cnf["default"]

        cnf = tk._cnfmerge((cnf, kw))

        fbot = ttk.Frame(self,)  # relief="raised", bd=1)
        ftop = ttk.Frame(self,)  # relief="raised", bd=1)
        fbot.pack(side="bottom", fill="both")
        ftop.pack(side="top", fill="both", expand=True)
        self.tk.call("grid", "anchor", fbot._w, "center")

        lbl = ttk.Label(
            ftop, text=cnf["text"], wraplength="3i",
            # font="TkCaptionFont", justify="left"
        )
        lbl.pack(side="right", fill="both", expand=True, padx="3m", pady="3m")

        if cnf["bitmap"]:
            lbl = ttk.Label(ftop, bitmap=cnf["bitmap"])
            lbl.pack(side="left", padx="3m", pady="3m")

        # Create a row of buttons at the bottom of the dialog
        for i, s in enumerate(cnf["strings"]):
            b = ttk.Button(fbot, text=s, command=lambda s=self,
                           n=i: s.close(n))
            b.bind("<Return>", lambda e: e.widget.invoke())
            if i == cnf["default"]:
                b.config(default="active")
                b.focus_set()
            else:
                b.config(default="normal")
            b.grid(column=i, row=0, sticky="ew", padx=10, pady=4)

        self.bind("<Escape>", lambda e, s=self: s.close())
        self.bind("<Right>", lambda e: e.widget.event_generate("<Tab>"))
        self.bind("<Left>", lambda e: e.widget.event_generate("<Shift-Tab>"))

        self.deiconify()
        self.wait_visibility()
        self.grab_set()
        self.focus_set()
        self.wait_window()

    # -----------------------------------------------------------------------
    def close(self, num=-1):
        self.num = num
        self.destroy()


# =============================================================================
# Input dialog
# =============================================================================
class InputDialog(tk.Toplevel):
    """
    Input dialog:
    valid types:
            str = any string
            int = any integer
            spin  = Spin box with limits from_, to_
            float = any float
    """

    def __init__(
        self, master, title, message, input_="",
        type_="str", from_=None, to_=None
    ):

        tk.Toplevel.__init__(self, master)
        self.transient(master)
        ttk.Label(self, text=message,
                  justify="left").pack(expand=True, fill="both", side="top")

        if type_ == "int":
            self.entry = tkextra.IntegerEntry(self)
            self.entry.insert(0, input_)
            w = self.entry

        elif type_ == "float":
            self.entry = tkextra.FloatEntry(self)
            self.entry.insert(0, input_)
            w = self.entry

        elif type_ == "spin":
            self.entry = tk.IntVar()
            self.entry.set(input_)
            w = ttk.Spinbox(self, text=self.entry, from_=from_, to_=to_)

        else:  # default str
            self.entry = ttk.Entry(self)
            self.entry.insert(0, input_)
            w = self.entry

        w.pack(padx=5, expand=True, fill="x")

        frame = ttk.Frame(self)
        b = ttk.Button(frame, text="Cancel", command=self.cancel)
        b.pack(side="right", pady=5)
        b = ttk.Button(frame, text="Ok", command=self.ok)
        b.pack(side="right", pady=5)
        frame.pack(fill="x")

        self.input = None
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        self.focus_set()
        w.focus_set()

    # --------------------------------------------------------------------
    def show(self):
        grab_window = self.grab_current()
        if grab_window is not None:
            grab_window.grab_release()
        self.wait_window()
        if grab_window is not None:
            grab_window.grab_set()
        return self.input

    # --------------------------------------------------------------------
    def ok(self, event=None):
        try:
            self.input = self.entry.get()
            self.destroy()
        except ValueError:
            pass

    # --------------------------------------------------------------------
    def cancel(self, event=None):
        self.destroy()


# =============================================================================
# Find/Replace dialog
# =============================================================================
class FindReplaceDialog(tk.Toplevel):
    def __init__(self, master, replace=True):
        tk.Toplevel.__init__(self, master)
        self.transient(master)
        self.replace = replace
        self.caseVar = tk.IntVar()

        main_frame = ttk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side="bottom", padx=10, pady=5)

        btn = ttk.Button(
            bottom_frame, text="Find", underline=0, width=8, command=self._find
        )
        btn.pack(side="left")

        if self.replace:
            self.title("Replace")

            btn = ttk.Button(
                bottom_frame,
                text="Replace",
                underline=0,
                width=8,
                command=self._replace,
            )
            btn.pack(side="left")

            btn = ttk.Button(
                bottom_frame,
                text="Replace All",
                underline=8,
                width=8,
                command=self._replaceAll,
            )
            btn.pack(side="left")

        else:
            self.title("Find")

        btn = ttk.Button(
            bottom_frame, text="Close", underline=0,
            width=8, command=self._close
        )
        btn.pack(side="right")

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        findString_frame = ttk.Frame(top_frame)
        findString_frame.pack(side="top", fill="x")

        label = ttk.Label(findString_frame, text="Find string: ", width=12)
        label.pack(side="left")

        self.findString_entry = ttk.Entry(
            findString_frame,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        )
        self.findString_entry.pack(side="right", fill="x", expand=True)

        if self.replace:
            replaceString_frame = ttk.Frame(top_frame)
            replaceString_frame.pack(side="top", fill="x")

            label = ttk.Label(replaceString_frame,
                              text="Replace to: ", width=12)
            label.pack(side="left")

            self.replaceString_entry = ttk.Entry(
                replaceString_frame,
                # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
            )
            self.replaceString_entry.pack(side="right", fill="x", expand=True)

        options_frame = ttk.Frame(top_frame)
        options_frame.pack(side="top", fill="x")
        self.case_check = ttk.Checkbutton(
            options_frame,
            text="Match case? ",
            onvalue=0,
            offvalue=1,
            variable=self.caseVar,
        )
        self.case_check.pack(side="right")
        self.case_check.deselect()

        self.bind("<Escape>", self._close)
        self.bind("<Alt-Key-c>", self._close)
        self.bind("<Alt-Key-f>", self._find)
        self.bind("<Control-Key-f>", self._find)
        self.bind("<Return>", self._find)
        self.bind("<Alt-Key-r>", self._replace)
        self.bind("<Control-Key-r>", self._replace)
        self.bind("<Alt-Key-a>", self._replaceAll)
        self.bind("<Control-Key-a>", self._replaceAll)

    # --------------------------------------------------------------------
    # Show dialog and wait for events
    # --------------------------------------------------------------------
    def show(self, find=None, replace=None, replaceAll=None, target=None):
        if target:
            self.findString_entry.insert("0", target)
            self.findString_entry.select_range("0", "end")
        else:
            self.findString_entry.delete("0", "end")
        self.objFind = find
        self.objReplace = replace
        self.objReplaceAll = replaceAll
        self.findString_entry.focus_set()
        self.grab_set()
        self.focus_set()
        self.wait_window()

    # --------------------------------------------------------------------
    def _find(self, event=None):
        self.findString = self.findString_entry.get()
        if self.objFind:
            self.objFind(self.findString, self.caseVar.get())

    # --------------------------------------------------------------------
    def _replace(self, event=None):
        self.findString = self.findString_entry.get()
        self.replaceString = self.replaceString_entry.get()
        if self.objReplace:
            self.objReplace(self.findString,
                            self.replaceString,
                            self.caseVar.get())

    # --------------------------------------------------------------------
    def _replaceAll(self, event=None):
        self.findString = self.findString_entry.get()
        self.replaceString = self.replaceString_entry.get()
        if self.objReplaceAll:
            self.objReplaceAll(self.findString,
                               self.replaceString,
                               self.caseVar.get())

    # --------------------------------------------------------------------
    def _close(self, event=None):
        self.destroy()


# =============================================================================
# Printer dialog
# =============================================================================
class Printer(tk.Toplevel):
    PAPER_FORMAT = {
        "A3": (29.7, 42.0),
        "B3": (35.3, 50.0),
        "A4": (21.0, 29.7),
        "B4": (25.0, 35.3),
        "A5": (14.8, 21.0),
        "B5": (17.6, 25.0),
        "Letter": (21.6, 27.9),
    }
    printTo = 1  # 1 = cmd, 0 = filename
    cmd = "lpr -P%p"
    printer = ""
    filename = "output.ps"
    landscape = False
    paper = "A4"
    copies = 1

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.transient(master)
        self.title("Print")

        self.printCmd = tk.IntVar()
        self.printCmd.set(Printer.printTo)
        self.landscapeVar = tk.IntVar()
        self.landscapeVar.set(Printer.landscape)
        self.paperVar = tk.StringVar()
        self.paperVar.set(Printer.paper)
        self.copiesVar = tk.IntVar()
        self.copiesVar.set(Printer.copies)

        # -----
        frame = ttk.LabelFrame(self, text="Print To")
        frame.pack(side="top", fill="both", expand=True)

        b = ttk.Radiobutton(
            frame,
            text="Printer:",
            variable=self.printCmd,
            value=1,
            command=self.printToChange,
        )
        b.grid(row=0, column=0, sticky="w")

        self.printer_combo = ttk.Combobox(frame, width=30)
        self.printer_combo['state'] = 'readonly'
        # self.printer_combo = tkextra.Combobox(frame, width=30)
        self.printer_combo.grid(row=0, column=1, columnspan=2, sticky="ew")
        self.fillPrinters()

        self.cmd_label = ttk.Label(frame, text="Command:")
        self.cmd_label.grid(row=1, column=0, sticky="e")

        self.cmd_entry = ttk.Entry(
            frame,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=30
        )
        self.cmd_entry.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.cmd_entry.insert(0, Printer.cmd)

        b = ttk.Radiobutton(
            frame,
            text="File Name:",
            variable=self.printCmd,
            value=0,
            command=self.printToChange,
        )
        b.grid(row=2, column=0, sticky="w")

        self.file_entry = ttk.Entry(
            frame,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=25
        )
        self.file_entry.grid(row=2, column=1, sticky="ew")

        self.browse_btn = ttk.Button(frame, text="Browse", command=self.browse)
        self.browse_btn.grid(row=2, column=2, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        # ------
        frame = ttk.LabelFrame(self, text="Options")
        frame.pack(fill="both")

        row = 0
        lbl = ttk.Label(frame, text="Orientation")
        lbl.grid(row=row, column=0, sticky="e")

        b = ttk.Radiobutton(frame, text="Portrait",
                            variable=self.landscapeVar, value=0)
        b.grid(row=row, column=1, sticky="w")

        b = ttk.Radiobutton(frame, text="Landscape",
                            variable=self.landscapeVar, value=1)
        b.grid(row=row, column=2, columnspan=2, sticky="w")

        row += 1
        lbl = ttk.Label(frame, text="Paper Size")
        lbl.grid(row=row, column=0, sticky="e")

        paperlist = sorted(Printer.PAPER_FORMAT.keys())
        o = ttk.OptionMenu(frame, self.paperVar, *paperlist)
        o.grid(row=row, column=1, sticky="w")

        lbl = ttk.Label(frame, text="Copies")
        lbl.grid(row=row, column=2, sticky="e")

        s = ttk.Spinbox(
            frame,
            text=self.copiesVar,
            from_=1,
            to=100,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
            width=3,
        )
        s.grid(row=row, column=3, sticky="w")

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # -------
        frame = ttk.Frame(self)
        frame.pack(fill="x")

        b = ttk.Button(frame, text="Cancel", command=self.cancel)
        b.pack(side="right")

        b = ttk.Button(frame, text="Print", command=self.ok)
        b.pack(side="right")

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        # --- Basic Variables ---
        self.rc = False
        self.hnd = None
        self.printToChange()

    # --------------------------------------------------------------------
    def fillPrinters(self):
        # On unix
        if sys.platform in ("linux", "linux2"):
            try:
                f = open("/etc/printcap")
                for line in f:
                    if len(line) == 0:
                        continue
                    if line[0] == "#":
                        continue
                    field = line.split(":")
                    self.printer_combo.insert("end", field[0])
                    if Printer.printer == "":
                        Printer.printer = field[0]
                f.close()
            except OSError:
                pass
        else:
            raise Exception("Unknown operating system")
        self.printer_combo.set(Printer.printer)

    # --------------------------------------------------------------------
    def show(self):
        # Return Variables
        self.rc = False
        self.hnd = None

        self.cmd_entry.config(state="normal")
        self.file_entry.config(state="normal")
        self.cmd_entry.delete(0, "end")
        self.cmd_entry.insert(0, Printer.cmd)
        self.file_entry.delete(0, "end")
        self.file_entry.insert(0, Printer.filename)

        self.printCmd.set(Printer.printTo)
        self.landscapeVar.set(Printer.landscape)
        self.paperVar.set(Printer.paper)

        self.printToChange()

        self.grab_set()
        self.wait_window()
        return self.rc

    # --------------------------------------------------------------------
    def ok(self, event=None):
        self.rc = True
        Printer.printTo = self.printCmd.get()
        Printer.cmd = self.cmd_entry.get()
        Printer.printer = self.printer_combo.get()
        Printer.filename = self.file_entry.get()
        Printer.landscape = self.landscapeVar.get()
        Printer.paper = self.paperVar.get()
        Printer.copies = self.copiesVar.get()
        self.destroy()

    # --------------------------------------------------------------------
    def cancel(self, event=None):
        self.rc = False
        self.destroy()

    # --------------------------------------------------------------------
    def printToChange(self):
        if self.printCmd.get():
            self.printer_combo['state'] = "normal"
            # self.printer_combo.config(state="normal")
            self.cmd_label.config(state="normal")
            self.cmd_entry.config(state="normal")
            self.file_entry.config(state="disabled")
            self.browse_btn.config(state="disabled")
        else:
            self.printer_combo['state'] = "disabled"
            # self.printer_combo.config(state="disabled")
            self.cmd_label.config(state="disabled")
            self.cmd_entry.config(state="disabled")
            self.file_entry.config(state="normal")
            self.browse_btn.config(state="normal")

    # --------------------------------------------------------------------
    def browse(self):
        fn = filedialog.asksaveasfilename(
            # title=_("Import Gcode/DXF file"),
            initialfile=self.file_entry.get(),
            filetypes=[
                ("Postscript file", "*.ps"),
                ("Encapsulated postscript file", "*.eps"),
                ("All", "*"),
            ],
        )
        # fn = bfiledialog.asksaveasfilename(
        #     master=self,
        #     initialfile=self.file_entry.get(),
        #     filetypes=[
        #         ("Postscript file", "*.ps"),
        #         ("Encapsulated postscript file", "*.eps"),
        #         ("All", "*"),
        #     ],
        # )
        if len(fn) > 0:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, fn)

    # --------------------------------------------------------------------
    # Return the printer command
    # --------------------------------------------------------------------
    @staticmethod
    def command():
        printer = Printer.printer
        bar = printer.find("|")
        if bar > 0:
            printer = printer[:bar]

        if Printer.cmd.find("%p") == -1:
            cmd = Printer.cmd + f" -P {printer}"
        else:
            cmd = Printer.cmd.replace("%p", f"{printer}")

        if cmd.find("%#") == -1:
            cmd += " -# %d" % (Printer.copies)
        else:
            cmd = cmd.replace("%#", f"{int(Printer.copies)}")
        return cmd

    # --------------------------------------------------------------------
    # I/O
    # Return a file handle or None where to write the data
    # --------------------------------------------------------------------
    def open(self):
        self.hnd = None
        if self.rc:
            if Printer.printTo:
                self.hnd = subprocess.Popen(
                    Printer.command(), shell=True, stdout=subprocess.PIPE
                ).stdout
            else:
                self.hnd = open(Printer.filename, "w")
        return self.hnd

    # --------------------------------------------------------------------
    def write(self, s):
        try:
            self.hnd.write(s)
            return True
        except Exception:
            return False

    # --------------------------------------------------------------------
    def close(self):
        if self.hnd:
            self.hnd.close()


# =============================================================================
# Show progress information
# =============================================================================
class ProgressDialog(tk.Toplevel):
    def __init__(self, master, title):
        tk.Toplevel.__init__(self, master)
        self.transient(master)
        self.title(title)
        self.bar = tkextra.ProgressBar(
            self, width=200, height=24, background="DarkGray"
        )
        self.bar.pack(side="top", expand=True, fill="x")
        self.label = ttk.Label(self, width=60)
        self.label.pack(side="top", expand=True, fill="both")
        b = ttk.Button(self, text="Stop",
                       #   foreground="Darkred",
                       command=self.stop)
        b.pack(side="bottom", fill="x", pady=2)
        self.ended = False

        self.bind("<Escape>", self.stop)
        self.protocol("WM_DELETE_WINDOW", self.stop)

        self.wait_visibility()
        self.update_idletasks()
        self.grab_set()

        x = (master.winfo_rootx()
             + (master.winfo_width() - self.winfo_width()) / 2)
        y = (master.winfo_rooty()
             + (master.winfo_height() - self.winfo_height()) / 2)
        self.geometry(f"+{int(x)}+{int(y)}")
        self.lastTime = time.time()
        self.refreshInterval = 0.25

    # --------------------------------------------------------------------
    def setLimits(self, low=0.0, high=100.0, step=1.0):
        self.bar.setLimits(low, high, step)
        self.startTime = time.time()

    # --------------------------------------------------------------------
    def show(self, pos, text=None):
        if time.time() - self.lastTime < self.refreshInterval:
            return
        self.lastTime = time.time()
        self.bar.setProgress(pos)
        if text is not None:
            self.label["text"] = text
        self.update()
        return self.ended

    # --------------------------------------------------------------------
    def close(self):
        self.grab_release()
        self.destroy()

    # --------------------------------------------------------------------
    def stop(self):
        self.ended = True
        self.close()


class AboutDialog(tk.Toplevel):
    """Display the about dialog and wait the window to be closed
    """

    def __init__(self, master, event=None, timer=None):
        tk.Toplevel.__init__(self, master)
        self.transient(master)
        self.title(_("About {} v{}").format(__prg__, __version__))

        frame = ttk.Frame(self, style="Dialog.TFrame")
        frame.pack(side="top", expand=True, fill="both", padx=5, pady=5)

        # -----
        row = 0
        la = ttk.Label(
            frame,
            image=Utils.icons["bCNC"],
            style="Dialog.TLabel"
        )
        la.grid(row=row, column=0, columnspan=2, padx=5, pady=5)

        row += 1
        la = ttk.Label(
            frame,
            text=_(
                "bCNC/\tAn advanced fully featured\n"
                "\tg-code sender for GRBL."
            ),
            style="Text1.Dialog.TLabel"
        )
        la.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=1)

        # -----
        row += 1
        ttk.Separator(frame, orient="horizontal").grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=5,
            pady=5
        )

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="www:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="e", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__www__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="w", padx=2, pady=2)
        la.bind("<Button-1>", lambda e: webbrowser.open(__www__))

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="email:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="e", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__email__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="w", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="author:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="ne", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__author__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="contributors:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="ne", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__contribute__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="translations:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="ne", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__translations__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="credits:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="ne", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__credits__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="version:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="e", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__version__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        # -----
        row += 1
        la = ttk.Label(
            frame,
            text="last change:",
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=0, sticky="e", padx=10, pady=2)

        la = ttk.Label(
            frame,
            text=__date__,
            style="Text2.Dialog.TLabel",
        )
        la.grid(row=row, column=1, sticky="nw", padx=2, pady=2)

        def closeFunc(e=None, t=self):
            return t.destroy()

        b = ttk.Button(self,
                       text=_("Close"),
                       command=closeFunc,
                       style='Dialog.TButton')
        b.pack(pady=5)
        frame.grid_columnconfigure(1, weight=1)

        self.bind("<Escape>", closeFunc)
        self.bind("<Return>", closeFunc)
        self.bind("<KP_Enter>", closeFunc)

        self.deiconify()
        self.wait_visibility()
        self.resizable(False, False)

        try:
            self.grab_set()
        except Exception:
            pass
        b.focus_set()
        self.lift()
        if timer:
            self.after(timer, closeFunc)
        self.wait_window()


class ShowStats(tk.Toplevel):
    """Show Stats
    """
    # FIXME: Very primitive

    def __init__(self, master, gcode):
        tk.Toplevel.__init__(self, master)
        self.transient(master)

        self.title(_("Statistics"))

        if globCNC.inch:
            unit = "in"
        else:
            unit = "mm"

        # count enabled blocks
        e = 0
        le = 0
        r = 0
        t = 0
        for block in gcode.blocks:
            if block.enable:
                e += 1
                le += block.length
                r += block.rapid
                t += block.time

        # ===========
        frame = ttk.LabelFrame(self, text=_(
            "Enabled GCode"), style="Dialog.TLabelFrame.Label")
        frame.pack(fill="both")

        # ---
        row, col = 0, 0
        ttk.Label(frame, text=_("Margins X:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(
            frame,
            text=f"{globCNC.vars['xmin']:g} .. {globCNC.vars['xmax']:g} "
                 + f"[{globCNC.vars['xmax'] - globCNC.vars['xmin']:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text="... Y:").grid(row=row, column=col, sticky="e")
        col += 1
        ttk.Label(
            frame,
            text=f"{globCNC.vars['ymin']:g} .. {globCNC.vars['ymax']:g} "
                 + f"[{globCNC.vars['ymax'] - globCNC.vars['ymin']:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text="... Z:").grid(row=row, column=col, sticky="e")
        col += 1
        ttk.Label(
            frame,
            text=f"{globCNC.vars['zmin']:g} .. {globCNC.vars['zmax']:g} "
                 + f"[{globCNC.vars['zmax'] - globCNC.vars['zmin']:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("# Blocks:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(frame, text=str(e), style="Blue.Text1.Dialog.TLabel").grid(
            row=row, column=col, sticky="w"
        )

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("Length:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(frame,
                  text=f"{le:g} {unit}",
                  style="Blue.Text1.Dialog.TLabel").grid(
            row=row, column=col, sticky="w"
        )

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("Rapid:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(frame,
                  text=f"{r:g} {unit}",
                  style="Blue.Text1.Dialog.TLabel").grid(
            row=row, column=col, sticky="w"
        )

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("Time:")).grid(row=row, column=col, sticky="e")
        col += 1
        h, m = divmod(t, 60)  # t in min
        s = (m - int(m)) * 60
        ttk.Label(
            frame,
            text=f"{int(h)}:{int(m):02}:{int(s):02} s",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        frame.grid_columnconfigure(1, weight=1)

        # ===========
        frame = ttk.LabelFrame(self, text=_(
            "All GCode"), style="Dialog.TLabelFrame.Label")
        frame.pack(fill="both")

        # ---
        row, col = 0, 0
        ttk.Label(frame, text=_("Margins X:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        tmp = globCNC.vars['axmax'] - globCNC.vars['axmin']
        ttk.Label(
            frame,
            text=f"{globCNC.vars['axmin']:g} .. {globCNC.vars['axmax']:g} "
                 + f"[{tmp:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text="... Y:").grid(row=row, column=col, sticky="e")
        col += 1
        tmp = globCNC.vars['aymax'] - globCNC.vars['aymin']
        ttk.Label(
            frame,
            text=f"{globCNC.vars['aymin']:g} .. {globCNC.vars['aymax']:g} "
                 + f"[{tmp:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text="... Z:").grid(row=row, column=col, sticky="e")
        col += 1
        tmp = globCNC.vars['azmax'] - globCNC.vars['azmin']
        ttk.Label(
            frame,
            text=f"{globCNC.vars['azmin']:g} .. {globCNC.vars['azmax']:g} "
                 + f"[{tmp:g}] {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("# Blocks:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(
            frame,
            text=str(len(gcode.blocks)),
            style="Blue.Text1.Dialog.TLabel"
        ).grid(
            row=row,
            column=col,
            sticky="w"
        )
        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("Length:")).grid(
            row=row, column=col, sticky="e")
        col += 1
        ttk.Label(
            frame,
            text=f"{globCNC.totalLength:g} {unit}",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        # ---
        row += 1
        col = 0
        ttk.Label(frame, text=_("Time:")).grid(row=row, column=col, sticky="e")
        col += 1
        h, m = divmod(globCNC.totalTime, 60)  # t in min
        s = (m - int(m)) * 60
        ttk.Label(
            frame,
            text=f"{int(int(h))}:{int(int(m)):02}:{int(int(s)):02} s",
            style="Blue.Text1.Dialog.TLabel",
        ).grid(row=row, column=col, sticky="w")

        frame.grid_columnconfigure(1, weight=1)

        # ===========
        frame = ttk.Frame(self)
        frame.pack(fill="x")

        def closeFunc(e=None, t=self):
            return t.destroy()

        b = ttk.Button(frame,
                       text=_("Close"),
                       command=closeFunc,
                       style='Dialog.TButton')
        b.pack(pady=5)
        frame.grid_columnconfigure(1, weight=1)

        self.bind("<Escape>", closeFunc)
        self.bind("<Return>", closeFunc)
        self.bind("<KP_Enter>", closeFunc)

        # ----
        self.deiconify()
        self.wait_visibility()
        self.resizable(False, False)

        try:
            self.grab_set()
        except Exception:
            pass
        b.focus_set()
        self.lift()
        self.wait_window()


# =============================================================================
# Error message reporting dialog
# =============================================================================
class ReportDialog(tk.Toplevel):
    _shown = False  # avoid re-entry when multiple errors are displayed

    def __init__(self, master):
        if ReportDialog._shown:
            return
        ReportDialog._shown = True

        tk.Toplevel.__init__(self, master)
        if master is not None:
            self.transient(master)
        self.title(_("Error Reporting"))

        # Label Frame
        frame = ttk.LabelFrame(self, text=_("Report"))
        frame.pack(side="top", expand=True, fill="both")

        la = ttk.Label(
            frame,
            text=_("The following report is about to be send "
                   + "to the author of {}").format(__prg__),
            # justify="left",
            # anchor="w",
        )
        la.pack(side="top")

        self.text = ScrolledText(frame, width=50, height=10)
        # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")

        # self.text = tk.Text(
        #     frame,
        #     background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        # )
        self.text.pack(side="left", expand=True, fill="both")

        # sb = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview)
        # sb.pack(side="right", fill="y")
        # self.text.config(yscrollcommand=sb.set)

        # email frame
        frame = ttk.Frame(self)
        frame.pack(side="top", fill="x")

        la = ttk.Label(frame, text=_("Your email"))
        la.pack(side="left")

        self.email = ttk.Entry(frame,)
        # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"))
        self.email.pack(side="left", expand=True, fill="x")

        # Automatic error reporting
        self.err = tk.BooleanVar()
        self.err.set(_errorReport)
        b = ttk.Checkbutton(
            frame,
            text=_("Automatic error reporting"),
            variable=self.err,
            # anchor="e",
            # justify="right",
        )
        b.pack(side="right")

        # Buttons
        frame = ttk.Frame(self)
        frame.pack(side="bottom", fill="x")

        b = ttk.Button(frame, text=_("Close"),
                       compound="left", command=self.cancel)
        b.pack(side="right")
        b = ttk.Button(
            frame,
            text=_("Send report"),
            # Error reporting endpoint is currently offline (#824),
            # disabled this to avoid timeout and confusion
            state="disabled",
            compound="left",
            command=self.send,
        )
        b.pack(side="right")

        # Fill report
        txt = [
            f"Program     : {__prg__}",
            f"Version     : {__version__}",
            f"Last Change : {__date__}",
            f"Platform    : {sys.platform}",
            f"Python      : {sys.version}",
            f"TkVersion   : {tk.TkVersion}",
            f"TclVersion  : {tk.TclVersion}",
            "\nTraceback:",
        ]
        for e in errors:
            if e != "" and e[-1] == "\n":
                txt.append(e[:-1])
            else:
                txt.append(e)

        self.text.insert("0.0", "\n".join(txt))

        # Guess email
        user = os.getenv("USER")
        host = os.getenv("HOSTNAME")
        if user and host:
            email = f"{user}@{host}"
        else:
            email = ""
        self.email.insert(0, email)

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", self.close)

        # Wait action
        self.wait_visibility()
        self.grab_set()
        self.focus_set()
        self.wait_window()

    # ----------------------------------------------------------------------
    def close(self, event=None):
        ReportDialog._shown = False
        self.destroy()

    # ----------------------------------------------------------------------
    def send(self):
        # FIXME: Pytho2 only code here!
        import httplib
        import urllib
        from globalVariables import glob_errors

        # global errors
        email = self.email.get()
        desc = self.text.get("1.0", "end").strip()

        # Send information
        self.config(cursor="watch")
        self.text.config(cursor="watch")
        self.update_idletasks()
        params = urllib.urlencode({"email": email, "desc": desc})
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain",
        }
        conn = httplib.HTTPConnection("www.bcnc.org:80")
        try:
            conn.request("POST", "/flair/send_email_bcnc.php", params, headers)
            response = conn.getresponse()
        except Exception:
            tk.messagebox.showwarning(
                _("Error sending report"),
                _("There was a problem connecting to the web site"),
                parent=self,
            )
        else:
            if response.status == 200:
                tk.messagebox.showinfo(
                    _("Report successfully send"),
                    _("Report was successfully uploaded to web site"),
                    parent=self,
                )
                del glob_errors[:]
            else:
                tk.messagebox.showwarning(
                    _("Error sending report"),
                    _("There was an error sending the report\n"
                      + "Code={} {}").format(int(response.status),
                                             response.reason),
                    parent=self,
                )
        conn.close()
        self.config(cursor="")
        self.cancel()

    # ----------------------------------------------------------------------
    def cancel(self):
        from globalVariables import glob_error_report, glob_errors
        # global _errorReport, errors
        glob_error_report = self.err.get()
        gconfig.set("Connection", "errorreport", str(bool(self.err.get())))
        del glob_errors[:]
        self.close()

    # ----------------------------------------------------------------------
    @staticmethod
    def sendErrorReport():
        ReportDialog(None)


# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    sd = Printer(root)
    sd = FindReplaceDialog(root)
    d = InputDialog(root, "Title", "Message Line1\nMessage Line2")
    root.mainloop()
