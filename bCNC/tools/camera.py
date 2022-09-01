""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import _Base

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# -----------------------------------------------------------------------------
class Tool(_Base):
    """ Refactored from Class Camera
    """
    def __init__(self, master):
        _Base.__init__(self, master, "Camera")
        self.variables = [
            ("aligncam", "int", 0, _("Align Camera")),
            ("aligncam_width", "int", 0, _("Align Camera Width")),
            ("aligncam_height", "int", 0, _("Align Camera Height")),
            ("aligncam_angle", "0,90,180,270", 0, _("Align Camera Angle")),
            ("webcam", "int", 0, _("Web Camera")),
            ("webcam_width", "int", 0, _("Web Camera Width")),
            ("webcam_height", "int", 0, _("Web Camera Height")),
            ("webcam_angle", "0,90,180,270", 0, _("Web Camera Angle")),
        ]
