""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

import tkinter as tk

from globalConfig import config as gconfig
from gui import tkextra
import Unicode
import Utils

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
class InPlaceText(tkextra.InPlaceText):
    def defaultBinds(self):
        tkextra.InPlaceText.defaultBinds(self)
        self.edit.bind("<Escape>", self.ok)


# =============================================================================
# Tools Base class
# =============================================================================
class _Base:
    def __init__(self, master, name=None):
        self.master = master
        self.name = name
        self.icon = None
        self.plugin = False
        self.variables = []  # name, type, default, label
        self.values = {}  # database of values
        self.listdb = {}  # lists database
        self.current = None  # currently editing index
        self.n = 0
        self.buttons = []

    # ----------------------------------------------------------------------
    def __setitem__(self, name, value):
        if self.current is None:
            self.values[name] = value
        else:
            self.values[f"{name}.{int(self.current)}"] = value

    # ----------------------------------------------------------------------
    def __getitem__(self, name):
        if self.current is None:
            return self.values.get(name, "")
        else:
            return self.values.get(f"{name}.{int(self.current)}", "")

    # ----------------------------------------------------------------------
    def gcode(self):
        return globGCode

    # ----------------------------------------------------------------------
    # Return a sorted list of all names
    # ----------------------------------------------------------------------
    def names(self):
        lst = []
        for i in range(1000):
            key = f"name.{i}"
            value = self.values.get(key)
            if value is None:
                break
            lst.append(value)
        lst.sort()
        return lst

    # ----------------------------------------------------------------------
    def _get(self, key, t, default):
        if t in ("float", "mm"):
            return gconfig.getfloat(self.name, key, default)
        elif t == "int":
            return gconfig.getint(self.name, key, default)
        elif t == "bool":
            return gconfig.getint(self.name, key, default)
        else:
            return gconfig.getstr(self.name, key, default)

    # ----------------------------------------------------------------------
    # Override with execute command
    # ----------------------------------------------------------------------
    def execute(self, app):
        pass

    # ----------------------------------------------------------------------
    # Update variables after edit command
    # ----------------------------------------------------------------------
    def update(self):
        return False

    # ----------------------------------------------------------------------
    def event_generate(self, msg, **kwargs):
        self.master.listbox.event_generate(msg, **kwargs)

    # ----------------------------------------------------------------------
    def beforeChange(self, app):
        pass

    # ----------------------------------------------------------------------
    def populate(self):
        self.master.listbox.delete(0, "end")
        for var in self.variables:
            n, t, d, lp = var[:4]
            value = self[n]
            if t == "bool":
                if value:
                    value = Unicode.BALLOT_BOX_WITH_X
                else:
                    value = Unicode.BALLOT_BOX
            elif t == "mm" and self.master.inches:
                try:
                    value /= 25.4
                    value = round(value, self.master.digits)
                except Exception:
                    value = ""
            elif t == "float":
                try:
                    value = round(value, self.master.digits)
                except Exception:
                    value = ""
            self.master.listbox.insert("end", (lp, value))

            if t == "color":
                try:
                    self.master.listbox.listbox(1).itemconfig(
                        "end", background=value)
                except tk.TclError:
                    pass

        # Load help
        varhelp = ""
        if hasattr(self, "help") and self.help is not None:
            varhelp += self.help

        varhelpheader = True
        for var in self.variables:
            if len(var) > 4:
                if varhelpheader:
                    varhelp += "\n=== Module options ===\n\n"
                    varhelpheader = False
                varhelp += (
                    "* " + var[0].upper() + ": "
                    + var[3] + "\n" + var[4] + "\n\n"
                )
        try:
            self.master.widget["paned"].remove(self.master.widget["toolHelpFrame"])
        except tk.TclError:
            pass
        self.master.widget["toolHelp"].config(state="normal")
        self.master.widget["toolHelp"].delete(1.0, "end")
        if len(varhelp) > 0:
            for line in varhelp.splitlines():
                if (len(line) > 0
                        and line[0] == "#"
                        and line[1:] in Utils.images.keys()):
                    self.master.widget["toolHelp"].image_create(
                        "end", image=Utils.images[line[1:]]
                    )
                    self.master.widget["toolHelp"].insert("end", "\n")
                else:
                    self.master.widget["toolHelp"].insert("end", line + "\n")
            self.master.widget["paned"].add(self.master.widget[
                "toolHelpFrame"])
        self.master.widget["toolHelp"].config(state="disabled")

    # ----------------------------------------------------------------------
    def _sendReturn(self, active):
        self.master.listbox.selection_clear(0, "end")
        self.master.listbox.selection_set(active)
        self.master.listbox.activate(active)
        self.master.listbox.see(active)
        n, t, d, lp = self.variables[active][:4]
        if t == "bool":
            return  # Forbid changing value of bool
        self.master.listbox.event_generate("<Return>")

    # ----------------------------------------------------------------------
    def _editPrev(self):
        active = self.master.listbox.index("active") - 1
        if active < 0:
            return
        self._sendReturn(active)

    # ----------------------------------------------------------------------
    def _editNext(self):
        active = self.master.listbox.index("active") + 1
        if active >= self.master.listbox.size():
            return
        self._sendReturn(active)

    # ----------------------------------------------------------------------
    # Make current "name" from the database
    # ----------------------------------------------------------------------
    def makeCurrent(self, name):
        if not name:
            return
        # special handling
        for i in range(1000):
            if name == self.values.get(f"name.{i}"):
                self.current = i
                self.update()
                return True
        return False

    # ----------------------------------------------------------------------
    # Edit tool listbox
    # ----------------------------------------------------------------------
    def edit(self, event=None, rename=False):
        lb = self.master.listbox.listbox(1)
        if event is None or event.type == "2":
            keyboard = True
        else:
            keyboard = False
        if keyboard:
            # keyboard event
            active = lb.index("active")
        else:
            active = lb.nearest(event.y)
            self.master.listbox.activate(active)

        ypos = lb.yview()[0]  # remember y position
        save = lb.get("active")

        n, t, d, lp = self.variables[active][:4]

        if t == "int":
            edit = tkextra.InPlaceInteger(lb)
        elif t in ("float", "mm"):
            edit = tkextra.InPlaceFloat(lb)
        elif t == "bool":
            edit = None
            value = int(lb.get(active) == Unicode.BALLOT_BOX)
            if value:
                lb.set(active, Unicode.BALLOT_BOX_WITH_X)
            else:
                lb.set(active, Unicode.BALLOT_BOX)
        elif t == "list":
            edit = tkextra.InPlaceList(lb, values=self.listdb[n])
        elif t == "db":
            if n == "name":
                # Current database
                if rename:
                    edit = tkextra.InPlaceEdit(lb)
                else:
                    edit = tkextra.InPlaceList(lb, values=self.names())
            else:
                # Refers to names from another database
                tool = self.master[n]
                names = tool.names()
                names.insert(0, "")
                edit = tkextra.InPlaceList(lb, values=names)
        elif t == "text":
            edit = InPlaceText(lb)
        elif "," in t:
            choices = [""]
            choices.extend(t.split(","))
            edit = tkextra.InPlaceList(lb, values=choices)
        elif t == "file":
            edit = tkextra.InPlaceFile(lb, save=False)
        elif t == "output":
            edit = tkextra.InPlaceFile(lb, save=True)
        elif t == "color":
            edit = tkextra.InPlaceColor(lb)
            if edit.value is not None:
                try:
                    lb.itemconfig("active", background=edit.value)
                except tk.TclError:
                    pass
        else:
            edit = tkextra.InPlaceEdit(lb)

        if edit is not None:
            value = edit.value
            if value is None:
                return

        if value == save:
            if edit.lastkey == "Up":
                self._editPrev()
            elif edit.lastkey in ("Return", "KP_Enter", "Down"):
                self._editNext()
            return

        if t == "int":
            try:
                value = int(value)
            except ValueError:
                value = ""
        elif t in ("float", "mm"):
            try:
                value = float(value)
                if t == "mm" and self.master.inches:
                    value *= 25.4
            except ValueError:
                value = ""

        if n == "name" and not rename:
            if self.makeCurrent(value):
                self.populate()
        else:
            self[n] = value
            if self.update():
                self.populate()

        self.master.listbox.selection_set(active)
        self.master.listbox.activate(active)
        self.master.listbox.yview_moveto(ypos)
        if edit is not None and not rename:
            if edit.lastkey == "Up":
                self._editPrev()
            elif edit.lastkey in ("Return", "KP_Enter", "Down") and active > 0:
                self._editNext()

    # =========================================================================
    # Additional persistence class for config
    # =========================================================================
    # class _Config:
    # ----------------------------------------------------------------------
    # Load from a configuration file
    # ----------------------------------------------------------------------
    def load(self):
        # Load lists
        lists = []
        for var in self.variables:
            n, t, d, lp = var[:4]
            if t == "list":
                lists.append(n)
        if lists:
            for p in lists:
                self.listdb[p] = []
                for i in range(1000):
                    key = f"_{p}.{i}"
                    value = gconfig.getstr(self.name, key).strip()
                    if value:
                        self.listdb[p].append(value)
                    else:
                        break

        # Check if there is a current
        try:
            self.current = int(gconfig.get(self.name, "current"))
        except Exception:
            self.current = None

        # Load values
        if self.current is not None:
            self.n = self._get("n", "int", 0)
            for i in range(self.n):
                key = f"name.{i}"
                self.values[key] = gconfig.getstr(self.name, key)
                for var in self.variables:
                    n, t, d, lp = var[:4]
                    key = f"{n}.{i}"
                    self.values[key] = self._get(key, t, d)
        else:
            for var in self.variables:
                n, t, d, lp = var[:4]
                self.values[n] = self._get(n, t, d)
        self.update()

    # ----------------------------------------------------------------------
    # Save to a configuration file
    # ----------------------------------------------------------------------
    def save(self):
        # if section do not exist add it
        gconfig.add_section_if_new(self.name)

        if self.listdb:
            for name, lst in self.listdb.items():
                for i, value in enumerate(lst):
                    gconfig.setstr(self.name, f"_{name}.{i}", value)

        # Save values
        if self.current is not None:
            gconfig.setstr(self.name, "current", str(self.current))
            gconfig.setstr(self.name, "n", str(self.n))

            for i in range(self.n):
                key = f"name.{i}"
                value = self.values.get(key)
                if value is None:
                    break
                gconfig.setstr(self.name, key, value)

                for var in self.variables:
                    n, t, d, lp = var[:4]
                    key = f"{n}.{i}"
                    gconfig.setstr(
                        self.name, key, str(self.values.get(key, d)))
        else:
            for var in self.variables:
                n, t, d, lp = var[:4]
                val = self.values.get(n, d)
                gconfig.setstr(self.name, n, str(val))

    # ----------------------------------------------------------------------
    def fromMm(self, name, default=0.0):
        try:
            return self.master.fromMm(float(self[name]))
        except ValueError:
            return default


# =============================================================================
# Base class of all databases
# =============================================================================
class DataBase(_Base):
    def __init__(self, master, name):
        _Base.__init__(self, master, name)
        self.buttons = ["add", "delete", "clone", "rename"]

    # ----------------------------------------------------------------------
    # Add a new item
    # ----------------------------------------------------------------------
    def add(self, rename=True):
        self.current = self.n
        self.values[f"name.{int(self.n)}"] = \
            f"{self.name} {int(self.n + 1):02d}"
        self.n += 1
        self.populate()
        if rename:
            self.rename()

    # ----------------------------------------------------------------------
    # Delete selected item
    # ----------------------------------------------------------------------
    def delete(self):
        if self.n == 0:
            return
        for var in self.variables:
            n, t, d, lp = var[:4]
            for i in range(self.current, self.n):
                try:
                    self.values[f"{n}.{i}"] = self.values[f"{n}.{i + 1}"]
                except KeyError:
                    try:
                        del self.values[f"{n}.{i}"]
                    except KeyError:
                        pass

        self.n -= 1
        if self.current >= self.n:
            self.current = self.n - 1
        self.populate()

    # ----------------------------------------------------------------------
    # Clone selected item
    # ----------------------------------------------------------------------
    def clone(self):
        if self.n == 0:
            return
        for var in self.variables:
            n, t, d, lp = var[:4]
            try:
                if n == "name":
                    self.values[f"{n}.{int(self.n)}"] = (
                        self.values[f"{n}.{int(self.current)}"] + " clone"
                    )
                else:
                    self.values[f"{n}.{int(self.n)}"] = self.values[
                        f"{n}.{int(self.current)}"]
            except KeyError:
                pass
        self.n += 1
        self.current = self.n - 1
        self.populate()

    # ----------------------------------------------------------------------
    # Rename current item
    # ----------------------------------------------------------------------
    def rename(self):
        self.master.listbox.selection_clear(0, "end")
        self.master.listbox.selection_set(0)
        self.master.listbox.activate(0)
        self.master.listbox.see(0)
        self.edit(None, True)


# =============================================================================
# Generic ini configuration
# =============================================================================
class Ini(_Base):
    def __init__(self, master, name, vartype, include=(), ignore=()):
        _Base.__init__(self, master)
        self.name = name

        # detect variables from ini file
        for name, value in gconfig.items(self.name):
            if name in ignore:
                continue
            self.variables.append((name, vartype, value, name))
