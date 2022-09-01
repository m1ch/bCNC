""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from cnc import globCNC
from gcode import globGCode

from ._database import _Base

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# CNC machine configuration
# =============================================================================
class Tool(_Base):
    """ Refactored from Class Config
    """
    def __init__(self, master):
        """ToolsPage.Config init

        Args:
          master: A ToolsPage.Tools - object
        """
        _Base.__init__(self, master)
        self.name = "CNC"
        self.variables = [
            ("units", "bool", 0, _("Units (inches)")),
            ("lasercutter", "bool", 0, _("Laser Cutter")),
            ("laseradaptive", "bool", 0, _("Laser Adaptive Power")),
            ("doublesizeicon", "bool", 0, _("Double Size Icon")),
            ("enable6axisopt", "bool", 0, _("Enable 6 Axis Displays")),
            ("acceleration_x", "mm", 25.0, _("Acceleration x")),
            ("acceleration_y", "mm", 25.0, _("Acceleration y")),
            ("acceleration_z", "mm", 5.0, _("Acceleration z")),
            ("feedmax_x", "mm", 3000.0, _("Feed max x")),
            ("feedmax_y", "mm", 3000.0, _("Feed max y")),
            ("feedmax_z", "mm", 2000.0, _("Feed max z")),
            ("travel_x", "mm", 200, _("Travel x")),
            ("travel_y", "mm", 200, _("Travel y")),
            ("travel_z", "mm", 100, _("Travel z")),
            ("round", "int", 4, _("Decimal digits")),
            ("accuracy", "mm", 0.1, _("Plotting Arc accuracy")),
            ("startup", "str", "G90", _("Start up")),
            ("spindlemin", "int", 0, _("Spindle min (RPM)")),
            ("spindlemax", "int", 12000, _("Spindle max (RPM)")),
            ("drozeropad", "int", 0, _("DRO Zero padding")),
            ("header", "text", "", _("Header gcode")),
            ("footer", "text", "", _("Footer gcode")),
        ]

    # ----------------------------------------------------------------------
    # Update variables after edit command
    # ----------------------------------------------------------------------
    def update(self):
        self.master.inches = self["units"]
        self.master.digits = int(self["round"])
        globCNC.decimal = self.master.digits
        globCNC.startup = self["startup"]
        globGCode.header = self["header"]
        globGCode.footer = self["footer"]
        return False
