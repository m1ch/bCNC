# $Id: Updates.py 3349 2014-11-28 14:09:26Z bnv $

# Author:   vvlachoudis@gmail.com
# Date:     5-Apr-2007

import json
import time
import http.client as http
import tkinter as tk
from tkinter import ttk

from globalConfig import config as gconfig
import Utils
from globalConstants import __prg__

from gui import utils

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


# =============================================================================
# Check for updates of bCNC
# =============================================================================
class CheckUpdateDialog(tk.Toplevel):
    def __init__(self, master, version):
        tk.Toplevel.__init__(self, master)
        self.title("Check for updates")
        self.transient(master)

        # Variables
        self.version = version

        # -----
        la = ttk.Label(self, image=Utils.icons["bCNC"],)
                    #   relief="raised", padx=0, pady=0)
        la.pack(side="top", fill="both")

        # ----
        frame = tk.LabelFrame(self, text="Version", padx=3, pady=5)
        frame.pack(side="top", fill="both")

        la = ttk.Label(frame, text=_("Installed Version:"))
        la.grid(row=0, column=0, sticky="e", pady=1)

        la = ttk.Label(frame, text=version,)  # anchor="w")
        la.grid(row=0, column=1, sticky="ew")
        utils.ToolTip(la, _("Running version of bCNC"))

        la = ttk.Label(frame, text=_("Latest Github Version:"))
        la.grid(row=1, column=0, sticky="e", pady=1)

        self.webversion = ttk.Label(frame, )  # anchor="w")
        self.webversion.grid(row=1, column=1, sticky="ew")
        utils.ToolTip(self.webversion,
                      _("Latest release version on github"))
        la = ttk.Label(frame, text=_("Published at:"))
        la.grid(row=2, column=0, sticky="e", pady=1)

        self.published = ttk.Label(frame, )  # anchor="w")
        self.published.grid(row=2, column=1, sticky="ew")
        utils.ToolTip(
            self.published, _("Published date of the latest github release")
        )

        frame.grid_columnconfigure(1, weight=1)

        # ----
        frame = tk.LabelFrame(self, text=_("Check Interval"),)  # padx=3, pady=5)
        frame.pack(fill="both")

        la = ttk.Label(frame, text=_("Last Check:"))
        la.grid(row=0, column=0, sticky="e", pady=1)

        # Last check
        lastCheck = gconfig.getint(__prg__, "lastcheck", 0)
        if lastCheck == 0:
            lastCheckStr = "unknown"
        else:
            lastCheckStr = time.asctime(time.localtime(lastCheck))

        la = ttk.Label(frame, text=lastCheckStr,)  # anchor="w")
        la.grid(row=0, column=1, sticky="ew")
        utils.ToolTip(la, _("Date last checked"))

        la = ttk.Label(frame, text=_("Interval (days):"))
        la.grid(row=1, column=0, sticky="e", pady=1)

        checkInt = gconfig.getint(__prg__, "checkinterval", 30)
        self.checkInterval = tk.IntVar()
        self.checkInterval.set(checkInt)

        s = ttk.Spinbox(
            frame,
            text=self.checkInterval,
            from_=0,
            to_=365,
            # background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND"),
        )
        s.grid(row=1, column=1, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        utils.ToolTip(s, _("Days-interval to remind again for checking"))

        # ----
        frame = ttk.Frame(self)
        frame.pack(side="bottom", fill="x")
        b = ttk.Button(
            frame,
            text=_("Close"),
            image=Utils.icons["x"],
            compound="left",
            command=self.later,
        )
        b.pack(side="right")

        self.checkButton = ttk.Button(
            frame,
            text=_("Check Now"),
            image=Utils.icons["global"],
            compound="left",
            command=self.check,
        )
        self.checkButton.pack(side="right")
        utils.ToolTip(
            self.checkButton, _("Check the web site for new versions of bCNC")
        )

        self.bind("<Escape>", self.close)

        self.wait_window()

    # ----------------------------------------------------------------------
    def isNewer(self, version):
        av = map(int, self.version.split("."))
        bv = map(int, version.split("."))
        for a, b in zip(av, bv):
            if b > a:
                return True
        return False

    # ----------------------------------------------------------------------
    def check(self):
        h = http.HTTPSConnection("api.github.com")
        h.request(
            "GET",
            "/repos/vlachoudis/bCNC/releases/latest",
            None,
            {"User-Agent": "bCNC"},
        )
        r = h.getresponse()
        if r.status == http.OK:
            data = json.loads(r.read().decode("utf-8"))
            latest_version = data["tag_name"]

            self.webversion.config(text=latest_version)
            self.published.config(text=data["published_at"])

            if self.isNewer(latest_version):
                self.webversion.config(background="LightGreen")
                self.checkButton.config(
                    text=_("Download"), background="LightYellow",
                    command=self.download
                )
                utils.ToolTip(
                    self.checkButton, _("Open web browser to download bCNC")
                )
            else:
                self.checkButton.config(state="disabled")

        else:
            self.webversion.config(
                text=_("Error {} in connection").format(r.status))

        # Save today as lastcheck date
        gconfig.set(__prg__, "lastcheck", str(int(time.time())))

    # ----------------------------------------------------------------------
    def later(self):
        # Save today as lastcheck date
        gconfig.set(__prg__, "lastcheck", str(int(time.time())))
        self.close()

    # ----------------------------------------------------------------------
    def download(self):
        import webbrowser

        webbrowser.open("https://github.com/vlachoudis/bCNC/releases/latest")
        self.checkButton.config(background="LightGray")

    # ----------------------------------------------------------------------
    def close(self, event=None):
        try:
            gconfig.set(
                __prg__, "checkinterval",
                str(int(self.checkInterval.get()))
            )
        except TypeError:
            pass
        self.destroy()


# -----------------------------------------------------------------------------
# Check if interval has passed from last check
# -----------------------------------------------------------------------------
def need2Check():
    lastCheck = gconfig.getint(__prg__, "lastcheck", 0)
    if lastCheck == 0:  # Unknown
        return True

    checkInt = gconfig.getint(__prg__, "checkinterval", 30)
    if checkInt == 0:  # Check never
        return False

    return lastCheck + checkInt * 86400 < int(time.time())


# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    Utils.loadIcons()
    gconfig.load_configuration()
    dlg = CheckUpdateDialog(tk.Tk, 0)
    root.mainloop()
