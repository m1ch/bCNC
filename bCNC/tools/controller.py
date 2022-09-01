""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

import time

from cnc import globCNC
from gcode import globGCode
from sender import globSender


from ._database import _Base

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Controller setup
# =============================================================================
class Tool(_Base):
    """ Refactored from Class Controller
    """
    def __init__(self, master):
        _Base.__init__(self, master)
        self.name = "Controller"
        self.variables = [
            ("grbl_0", "float", 10, _("$0 Step pulse time [us]")),
            ("grbl_1", "int", 25, _("$1 Step idle delay [ms]")),
            ("grbl_2", "int", 0, _("$2 Step port invert [mask]")),
            ("grbl_3", "int", 0, _("$3 Direction port invert [mask]")),
            ("grbl_4", "bool", 0, _("$4 Step enable invert")),
            ("grbl_5", "bool", 0, _("$5 Limit pins invert")),
            ("grbl_6", "bool", 0, _("$6 Probe pin invert")),
            ("grbl_10", "int", 1, _("$10 Status report [mask]")),
            ("grbl_11", "float", 0.010, _("$11 Junction deviation [mm]")),
            ("grbl_12", "float", 0.002, _("$12 Arc tolerance [mm]")),
            ("grbl_13", "bool", 0, _("$13 Report inches")),
            ("grbl_20", "bool", 0, _("$20 Soft limits")),
            ("grbl_21", "bool", 0, _("$21 Hard limits")),
            ("grbl_22", "bool", 0, _("$22 Homing cycle")),
            ("grbl_23", "int", 0, _("$23 Homing direction invert [mask]")),
            ("grbl_24", "float", 25.0, _("$24 Homing feed [mm/min]")),
            ("grbl_25", "float", 500.0, _("$25 Homing seek [mm/min]")),
            ("grbl_26", "int", 250, _("$26 Homing debounce [ms]")),
            ("grbl_27", "float", 1.0, _("$27 Homing pull-off [mm]")),
            ("grbl_30", "float", 1000.0, _("$30 Max spindle speed [RPM]")),
            ("grbl_31", "float", 0.0, _("$31 Min spindle speed [RPM]")),
            ("grbl_32", "bool", 0, _("$32 Laser mode enable")),
            ("grbl_100", "float", 250.0, _("$100 X steps/mm")),
            ("grbl_101", "float", 250.0, _("$101 Y steps/mm")),
            ("grbl_102", "float", 250.0, _("$102 Z steps/mm")),
            ("grbl_110", "float", 500.0, _("$110 X max rate [mm/min]")),
            ("grbl_111", "float", 500.0, _("$111 Y max rate [mm/min]")),
            ("grbl_112", "float", 500.0, _("$112 Z max rate [mm/min]")),
            ("grbl_120", "float", 10.0, _("$120 X acceleration [mm/sec^2]")),
            ("grbl_121", "float", 10.0, _("$121 Y acceleration [mm/sec^2]")),
            ("grbl_122", "float", 10.0, _("$122 Z acceleration [mm/sec^2]")),
            ("grbl_130", "float", 200.0, _("$130 X max travel [mm]")),
            ("grbl_131", "float", 200.0, _("$131 Y max travel [mm]")),
            ("grbl_132", "float", 200.0, _("$132 Z max travel [mm]")),
            ("grbl_140", "float", 200.0, _("$140 X homing pull-off [mm]")),
            ("grbl_141", "float", 200.0, _("$141 Y homing pull-off [mm]")),
            ("grbl_142", "float", 200.0, _("$142 Z homing pull-off [mm]")),
        ]
        self.buttons.append("exe")

    # ----------------------------------------------------------------------
    def execute(self, app):
        lines = []
        for n, t, d, _c in self.variables:
            v = self[n]
            try:
                if t == "float":
                    if v == float(globCNC.vars[n]):
                        continue
                else:
                    if v == int(globCNC.vars[n]):
                        continue
            except Exception:
                continue
            lines.append(f"${n[5:]}={str(v)}")
            lines.append("%wait")
        lines.append("$$")
        app.run(lines=lines)

    # ----------------------------------------------------------------------
    def beforeChange(self, app):
        app.sendGCode("$$")
        time.sleep(1)

    # ----------------------------------------------------------------------
    def populate(self):
        for var in self.variables:
            n, t, d, lp = var[:4]
            try:
                if t == "float":
                    self.values[n] = float(globCNC.vars[n])
                else:
                    self.values[n] = int(globCNC.vars[n])
            except KeyError:
                pass
        _Base.populate(self)
