""" This file was created due to the refactoring of
    ControlPage.py - abcControlFrame

    Authors:
             @m1ch
"""

import tkinter as tk
from tkinter import ttk
# import Unicode
import math

from globalConfig import config as gconfig
from sender import globSender

from .. import utils

_LOWSTEP = 0.0001
_HIGHSTEP = 1000.0
_HIGHASTEP = 90.0
_NOASTEP = "BC"


name = "abcControlFrame"


# ----------------------------------------------------------------------
@staticmethod
def _stepPower(step):
    try:
        step = float(step)
        if step <= 0.0:
            step = 1.0
    except Exception:
        step = 1.0
    power = math.pow(10.0, math.floor(math.log10(step)))
    return round(step / power) * power, power


# =============================================================================
# abc ControlFrame
# =============================================================================
class SideFrame(utils.CollapsiblePageLabelFrame):
    def __init__(self, master, app):
        utils.CollapsiblePageLabelFrame.__init__(
            self, master, app, name="abcControl", text=_("abcControl")
        )

        frame = ttk.Frame(self.frame)
        frame.pack(side="top", fill="x")

        row, col = 0, 0
        ttk.Label(frame, text=_("A")).grid(row=row, column=col)

        col += 3
        ttk.Label(frame, text=_("C")).grid(row=row, column=col)

        # ---
        row += 1
        col = 0

        width = 3
        height = 2

        b = ttk.Button(
            frame,
            text="▲",
            command=self.moveAup,
            # width=width,
            # height=height,
            style='Panel.TButton',
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move +A"))
        self.addWidget(b)

        col += 2
        b = ttk.Button(
            frame,
            text="◸",
            command=self.moveBdownCup,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )

        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move -B +C"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="▲",
            command=self.moveCup,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move +C"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="◹",
            command=self.moveBupCup,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move +B +C"))
        self.addWidget(b)

        col += 2
        b = ttk.Button(
            frame, text="\u00D710", command=self.mulStep,
            # width=3, padx=1, pady=1
        )
        b.grid(row=row, column=col, sticky="ews")
        utils.ToolTip(b, _("Multiply step by 10"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame, text=_("+"), command=self.incStep,
            # width=3, padx=1, pady=1
        )
        b.grid(row=row, column=col, sticky="ews")
        utils.ToolTip(b, _("Increase step by 1 unit"))
        self.addWidget(b)

        # ---
        row += 1

        col = 1
        ttk.Label(frame, text=_("B"), width=3,
                  #   anchor="e"
                  ).grid(row=row, column=col, sticky="e")

        col += 1
        b = ttk.Button(
            frame,
            text="◀",
            command=self.moveBdown,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move -B"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="◯",
            command=self.go2abcorigin,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Return ABC to 0."))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="▶",
            command=self.moveBup,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move +B"))
        self.addWidget(b)

        # --
        col += 1
        ttk.Label(frame, text="", width=2).grid(row=row, column=col)

        col += 1
        self.step = ttk.Combobox(frame, width=6)
        self.step['state'] = 'readonly'
        self.step['values'] = list(
            map(float, gconfig.get("abcControl", "abcsteplist").split())
        )
        # self.step = tkextra.Combobox(
        #     frame, width=6, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
        # )
        # self.step.fill(
        #     map(float, gconfig.get("abcControl", "abcsteplist").split())
        # )
        self.step.set(gconfig.get("abcControl", "step"))
        self.step.grid(row=row, column=col, columnspan=2, sticky="ew")
        utils.ToolTip(self.step, _("Step for every move operation"))
        self.addWidget(self.step)

        # -- Separate astep --
        try:
            astep = gconfig.get("abcControl", "astep")
            self.astep = ttk.Combobox(frame, width=4)
            self.astep['state'] = 'readonly'
            self.astep['values'] = astep
            # self.astep = tkextra.Combobox(
            #     frame, width=4, background=gconfig.getstr('_colors', "GLOBAL_CONTROL_BACKGROUND")
            # )
            # self.astep.set(astep)
            self.astep.grid(row=row, column=0, columnspan=1, sticky="ew")
            asl = [_NOASTEP]
            asl.extend(
                map(float,
                    gconfig.get("abcControl", "asteplist").split()))
            self.astep.fill(asl)
            utils.ToolTip(self.astep, _("Step for A move operation"))
            self.addWidget(self.astep)
        except Exception:
            self.astep = self.step

        # Default steppings
        try:
            self.step1 = gconfig.getfloat("abcControl", "step1")
        except Exception:
            self.step1 = 0.1

        try:
            self.step2 = gconfig.getfloat("abcControl", "step2")
        except Exception:
            self.step2 = 1

        try:
            self.step3 = gconfig.getfloat("abcControl", "step3")
        except Exception:
            self.step3 = 10

        # ---
        row += 1
        col = 0

        b = ttk.Button(
            frame,
            text="▼",
            command=self.moveAdown,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move -A"))
        self.addWidget(b)

        col += 2
        b = ttk.Button(
            frame,
            text="◺",
            command=self.moveBdownCdown,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move -B -C"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="▼",
            command=self.moveCdown,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move -C"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(
            frame,
            text="◿",
            command=self.moveBupCdown,
            # width=width,
            # height=height,
            # activebackground="LightYellow",
        )
        b.grid(row=row, column=col, sticky="ew")
        utils.ToolTip(b, _("Move +B -C"))
        self.addWidget(b)

        col += 2
        b = ttk.Button(
            frame, text="\u00F710", command=self.divStep,
            # padx=1, pady=1
        )
        b.grid(row=row, column=col, sticky="ewn")
        utils.ToolTip(b, _("Divide step by 10"))
        self.addWidget(b)

        col += 1
        b = ttk.Button(frame, text=_("-"), command=self.decStep,
                       #    padx=1, pady=1
                       )
        b.grid(row=row, column=col, sticky="ewn")
        utils.ToolTip(b, _("Decrease step by 1 unit"))
        self.addWidget(b)

        try:
            self.tk.call("grid", "anchor", self, "center")
        except tk.TclError:
            pass

    # ----------------------------------------------------------------------
    def saveConfig(self):
        gconfig.setstr("abcControl", "step", self.step.get())
        if self.astep is not self.step:
            gconfig.setstr("abcControl", "astep", self.astep.get())

    # ----------------------------------------------------------------------
    # Jogging
    # ----------------------------------------------------------------------
    def getStep(self, axis="a"):
        if axis == "a":
            aas = self.astep.get()
            if aas == _NOASTEP:
                return self.step.get()
            else:
                return aas
        else:
            return self.step.get()

    def moveBup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"B{self.step.get()}")

    def moveBdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"B-{self.step.get()}")

    def moveCup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"C{self.step.get()}")

    def moveCdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"C-{self.step.get()}")

    def moveBdownCup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        # XXX: Possible error in original code lead to %C string; fixed by guessing from methods below.
        # Original: globSender.mcontrol.jog("B-%C%s"%(self.step.get(),self.step.get()))
        globSender.mcontrol.jog(f"B-{self.step.get()}C{self.step.get()}")

    def moveBupCup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"B{self.step.get()}C{self.step.get()}")

    def moveBdownCdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"B-{self.step.get()}C-{self.step.get()}")

    def moveBupCdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"B{self.step.get()}C-{self.step.get()}")

    def moveAup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"A{self.getStep('z')}")

    def moveAdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"A-{self.getStep('z')}")

    def go2abcorigin(self, event=None):
        self.sendGCode("G90")
        self.sendGCode("G0B0C0")
        self.sendGCode("G0A0")

    # ----------------------------------------------------------------------
    def setStep(self, s, aas=None):
        self.step.set(f"{s:.4g}")
        if self.astep is self.step or aas is None:
            self.event_generate("<<Status>>", data=_("Step: {:g}").format(s))
        else:
            self.astep.set(f"{aas:.4g}")
            self.event_generate(
                "<<Status>>", data=_("Step: {:g}   Astep:{:g} ").format(s, aas)
            )

    # ----------------------------------------------------------------------
    def incStep(self, event=None):
        if event is not None and not self.acceptKey():
            return
        step, power = _stepPower(self.step.get())
        s = step + power
        if s < _LOWSTEP:
            s = _LOWSTEP
        elif s > _HIGHSTEP:
            s = _HIGHSTEP
        if self.astep is not self.step and self.astep.get() != _NOASTEP:
            step, power = _stepPower(self.astep.get())
            aas = step + power
            if aas < _LOWSTEP:
                aas = _LOWSTEP
            elif aas > _HIGHASTEP:
                aas = _HIGHASTEP
        else:
            aas = None
        self.setStep(s, aas)

    # ----------------------------------------------------------------------
    def decStep(self, event=None):
        if event is not None and not self.acceptKey():
            return
        step, power = _stepPower(self.step.get())
        s = step - power
        if s <= 0.0:
            s = step - power / 10.0
        if s < _LOWSTEP:
            s = _LOWSTEP
        elif s > _HIGHSTEP:
            s = _HIGHSTEP
        if self.astep is not self.step and self.astep.get() != _NOASTEP:
            step, power = _stepPower(self.astep.get())
            aas = step - power
            if aas <= 0.0:
                aas = step - power / 10.0
            if aas < _LOWSTEP:
                aas = _LOWSTEP
            elif aas > _HIGHASTEP:
                aas = _HIGHASTEP
        else:
            aas = None
        self.setStep(s, aas)

    # ----------------------------------------------------------------------
    def mulStep(self, event=None):
        if event is not None and not self.acceptKey():
            return
        step, power = _stepPower(self.step.get())
        s = step * 10.0
        if s < _LOWSTEP:
            s = _LOWSTEP
        elif s > _HIGHSTEP:
            s = _HIGHSTEP
        if self.astep is not self.step and self.astep.get() != _NOASTEP:
            step, power = _stepPower(self.astep.get())
            aas = step * 10.0
            if aas < _LOWSTEP:
                aas = _LOWSTEP
            elif aas > _HIGHASTEP:
                aas = _HIGHASTEP
        else:
            aas = None
        self.setStep(s, aas)

    # ----------------------------------------------------------------------
    def divStep(self, event=None):
        if event is not None and not self.acceptKey():
            return
        step, power = _stepPower(self.step.get())
        s = step / 10.0
        if s < _LOWSTEP:
            s = _LOWSTEP
        elif s > _HIGHSTEP:
            s = _HIGHSTEP
        if self.astep is not self.step and self.astep.get() != _NOASTEP:
            step, power = _stepPower(self.astep.get())
            aas = step / 10.0
            if aas < _LOWSTEP:
                aas = _LOWSTEP
            elif aas > _HIGHASTEP:
                aas = _HIGHASTEP
        else:
            aas = None
        self.setStep(s, aas)

    # ----------------------------------------------------------------------
    def setStep1(self, event=None):
        if event is not None and not self.acceptKey():
            return
        self.setStep(self.step1, self.step1)

    # ----------------------------------------------------------------------
    def setStep2(self, event=None):
        if event is not None and not self.acceptKey():
            return
        self.setStep(self.step2, self.step2)

    # ----------------------------------------------------------------------

    def setStep3(self, event=None):
        if event is not None and not self.acceptKey():
            return
        self.setStep(self.step3, self.step2)
