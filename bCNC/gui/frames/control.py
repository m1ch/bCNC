""" This file was created due to the refactoring of
    ControlPage.py - ControlFrame

    Authors:
             @m1ch
"""

from tkinter import ttk
import math

from globalConfig import config as gconfig
from cnc import globCNC
from sender import globSender


from .. import utils

_LOWSTEP = 0.0001
_HIGHSTEP = 1000.0
_HIGHZSTEP = 10.0
_NOZSTEP = "XY"


name = "ControlFrame"


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
# ControlFrame
# =============================================================================
class SideFrame(utils.CollapsiblePageLabelFrame):
    def __init__(self, master, app):
        self.app = app
        utils.CollapsiblePageLabelFrame.__init__(
            self, master, app, name="Control", text=_("Control"))

        frame = ttk.Frame(self.frame, style='Panel.TFrame')
        frame.pack(side="top", expand=True)

        control_button_size = 50
        row_heits = (26,
                     control_button_size,
                     control_button_size,
                     control_button_size)
        col_width = (control_button_size,
                     18,
                     control_button_size,
                     control_button_size,
                     control_button_size,
                     18,
                     55)

        f = ttk.Frame(frame, width=col_width[-2])
        f.grid(row=0, column=5)

        def place_button(btn):
            f = ttk.Frame(
                frame,
                width=col_width[btn[0][0]],
                height=row_heits[btn[0][1]],
            )
            f.pack_propagate(False)
            f.grid(row=btn[0][1], column=btn[0][0], sticky="nsew")
            b = ttk.Button(
                f,
                text=btn[1],
                command=btn[2],
                style='Control.Panel.TButton',
            )
            b.place(relx=.5,
                    rely=.5,
                    height=row_heits[btn[0][1]] - 2,
                    width=col_width[btn[0][0]] - 2,
                    anchor="center")  # pack(fill="both")
            utils.ToolTip(b, btn[3])
            # self.addWidget(b)

        buttons = (
            ((0, 1), "▲",
             self.moveZup, _("Move +Z")),
            ((0, 3), "▼",
             self.moveZdown, _("Move -Z")),
            ((2, 1), "◸",
             self.moveXdownYup, _("Move -X +Y")),
            ((3, 1), "▲",
             self.moveYup, _("Move +Y")),
            ((4, 1), "◹",
             self.moveXupYup, _("Move +X +Y")),
            ((2, 2), "◀",
             self.moveXdown, _("Move -X")),
            ((3, 2), "◯",
             self.go2origin, _("Move to Origin.\n"
                               + "User configurable button.\n"
                               + "Right click to configure.")),
            ((4, 2), "▶",
             self.moveXup, _("Move +X")),
            ((2, 3), "◺",
             self.moveXdownYdown, _("Move -X -Y")),
            ((3, 3), "▼",
             self.moveYdown, _("Move -Y")),
            ((4, 3), "◿",
             self.moveXupYdown, _("Move +X -Y")),
        )

        for b in buttons:
            place_button(b)

        f = ttk.Frame(frame, height=row_heits[0])
        f.pack_propagate(False)
        f.grid(row=0, column=0, sticky="ews")
        ttk.Label(f, text="Z").pack(side="bottom")
        f = ttk.Frame(frame, height=row_heits[0])
        f.pack_propagate(False)
        f.grid(row=0, column=3, sticky="ews")
        ttk.Label(f, text="Y").pack(side="bottom")
        f = ttk.Frame(frame, width=col_width[1])
        f.pack_propagate(False)
        f.grid(row=2, column=1, sticky="nse")
        ttk.Label(f, text="X").pack(side="right")
        f = ttk.Frame(frame, width=col_width[-2])
        f.grid(row=0, column=5)

        f = ttk.Frame(frame, width=col_width[-1], height=row_heits[1])
        f.pack_propagate(False)
        f.grid(row=1, column=6, sticky="ew")
        b = ttk.Button(
            f, text="\u00D710", command=self.mulStep,
            width=4,
            style='Panel.TButton'
        )
        b.pack(side="left")  # grid(row=0, column=0, sticky="ew")
        utils.ToolTip(b, _("Multiply step by 10"))
        # self.addWidget(b)
        b = ttk.Button(f, text=_("+"), command=self.incStep,
                       #    width=3,
                       style='Panel.TButton')
        b.pack(side="left")  # grid(row=0, column=1, sticky="ew")
        utils.ToolTip(b, _("Increase step by 1 unit"))
        # self.addWidget(b)

        f = ttk.Frame(frame, width=col_width[-1], height=row_heits[1])
        f.pack_propagate(False)
        f.grid(row=3, column=6, sticky="ewn")
        b = ttk.Button(
            f, text="\u00F710", command=self.divStep,
            width=4,
            style='Panel.TButton')  # , padx=1, pady=1)
        b.pack(side="left")  # grid(row=0, column=0, sticky="ewn")
        utils.ToolTip(b, _("Divide step by 10"))
        # self.addWidget(b)
        b = ttk.Button(f, text=_("-"), command=self.decStep,
                       #    width=3,
                       style='Panel.TButton')
        b.pack(side="left")  # grid(row=0, column=1, sticky="ewn")
        utils.ToolTip(b, _("Decrease step by 1 unit"))
        # self.addWidget(b)

        f = ttk.Frame(frame, width=col_width[-1], height=row_heits[2])
        f.pack_propagate(False)
        f.grid(row=2, column=6, sticky="ew")
        self.step = ttk.Combobox(
            f,
            style='Panel.TCombobox',
            # width=6,
        )
        self.step['values'] = list(
            map(float,
                gconfig.get("Control", "steplist").split())
        )
        self.step['state'] = 'normal'  # 'readonly'

        # grid(row=2, column=6, columnspan=2, sticky="ew")
        self.step.pack(side="right")
        self.step.set(gconfig.get("Control", "step"))
        utils.ToolTip(self.step, _("Step for every move operation"))
        # self.addWidget(self.step)

        # -- Separate zstep --
        f = ttk.Frame(frame, width=col_width[0], height=row_heits[2])
        f.pack_propagate(False)
        f.grid(row=2, column=0, sticky="ew")
        try:
            zstep = gconfig.get("Control", "zstep")
            self.zstep = ttk.Combobox(
                f,
                style='Control.Panel.TCombobox',
                # width=6,
            )
            # grid(row=2, column=0, columnspan=1, sticky="ew")
            self.zstep.pack(side="right")
            self.zstep.set(zstep)
            zsl = [_NOZSTEP]
            zsl.extend(
                map(float, gconfig.get("Control", "zsteplist").split()))
            self.zstep['values'] = zsl
            self.zstep['state'] = 'normal'  # 'readonly'
            utils.ToolTip(self.zstep, _("Step for Z move operation"))
            # self.addWidget(self.zstep)
        except Exception:
            self.zstep = self.step

        # Default steppings
        try:
            self.step1 = gconfig.getfloat("Control", "step1")
        except Exception:
            self.step1 = 0.1

        try:
            self.step2 = gconfig.getfloat("Control", "step2")
        except Exception:
            self.step2 = 1

        try:
            self.step3 = gconfig.getfloat("Control", "step3")
        except Exception:
            self.step3 = 10

    # ----------------------------------------------------------------------

    def saveConfig(self):
        gconfig.setstr("Control", "step", self.step.get())
        if self.zstep is not self.step:
            gconfig.setstr("Control", "zstep", self.zstep.get())

    # ----------------------------------------------------------------------
    # Jogging
    # ----------------------------------------------------------------------
    def getStep(self, axis="x"):
        if axis == "z":
            zs = self.zstep.get()
            if zs == _NOZSTEP:
                return self.step.get()
            else:
                return zs
        else:
            return self.step.get()

    def moveXup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X{self.step.get()}")

    def moveXdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X-{self.step.get()}")

    def moveYup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"Y{self.step.get()}")

    def moveYdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"Y-{self.step.get()}")

    def moveXdownYup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X-{self.step.get()}Y{self.step.get()}")

    def moveXupYup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X{self.step.get()}Y{self.step.get()}")

    def moveXdownYdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X-{self.step.get()}Y-{self.step.get()}")

    def moveXupYdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"X{self.step.get()}Y-{self.step.get()}")

    def moveZup(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"Z{self.getStep('z')}")

    def moveZdown(self, event=None):
        if event is not None and not self.acceptKey():
            return
        globSender.mcontrol.jog(f"Z-{self.getStep('z')}")

    def go2origin(self, event=None):
        self.sendGCode("G90")
        self.sendGCode("G0Z%d" % (globCNC.vars["safe"]))
        self.sendGCode("G0X0Y0")
        self.sendGCode("G0Z0")

    # ----------------------------------------------------------------------
    def setStep(self, s, zs=None):
        self.step.set(f"{s:.4g}")
        if self.zstep is self.step or zs is None:
            self.event_generate("<<Status>>", data=_("Step: {:g}").format(s))
        else:
            self.zstep.set(f"{zs:.4g}")
            self.event_generate(
                "<<Status>>", data=_("Step: {:g}  Zstep: {:g} ").format(s, zs))

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
        if self.zstep is not self.step and self.zstep.get() != _NOZSTEP:
            step, power = _stepPower(self.zstep.get())
            zs = step + power
            if zs < _LOWSTEP:
                zs = _LOWSTEP
            elif zs > _HIGHZSTEP:
                zs = _HIGHZSTEP
        else:
            zs = None
        self.setStep(s, zs)

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
        if self.zstep is not self.step and self.zstep.get() != _NOZSTEP:
            step, power = _stepPower(self.zstep.get())
            zs = step - power
            if zs <= 0.0:
                zs = step - power / 10.0
            if zs < _LOWSTEP:
                zs = _LOWSTEP
            elif zs > _HIGHZSTEP:
                zs = _HIGHZSTEP
        else:
            zs = None
        self.setStep(s, zs)

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
        if self.zstep is not self.step and self.zstep.get() != _NOZSTEP:
            step, power = _stepPower(self.zstep.get())
            zs = step * 10.0
            if zs < _LOWSTEP:
                zs = _LOWSTEP
            elif zs > _HIGHZSTEP:
                zs = _HIGHZSTEP
        else:
            zs = None
        self.setStep(s, zs)

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
        if self.zstep is not self.step and self.zstep.get() != _NOZSTEP:
            step, power = _stepPower(self.zstep.get())
            zs = step / 10.0
            if zs < _LOWSTEP:
                zs = _LOWSTEP
            elif zs > _HIGHZSTEP:
                zs = _HIGHZSTEP
        else:
            zs = None
        self.setStep(s, zs)

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
