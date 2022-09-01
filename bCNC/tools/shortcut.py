""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import _Base

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# -----------------------------------------------------------------------------
class Tool(_Base):
    """ Refactored from Class Shortcut
    """
    def __init__(self, master):
        _Base.__init__(self, master, "Shortcut")
        self.variables = [
            ("F1", "str", "help", _("F1")),
            ("F2", "str", "edit", _("F2")),
            ("F3", "str", "XY", _("F3")),
            ("F4", "str", "ISO1", _("F4")),
            ("F5", "str", "ISO2", _("F5")),
            ("F6", "str", "ISO3", _("F6")),
            ("F7", "str", "", _("F7")),
            ("F8", "str", "", _("F8")),
            ("F9", "str", "", _("F9")),
            ("F10", "str", "", _("F10")),
            ("F11", "str", "", _("F11")),
            ("F12", "str", "", _("F12")),
            ("Shift-F1", "str", "", _("Shift-") + _("F1")),
            ("Shift-F2", "str", "", _("Shift-") + _("F2")),
            ("Shift-F3", "str", "", _("Shift-") + _("F3")),
            ("Shift-F4", "str", "", _("Shift-") + _("F4")),
            ("Shift-F5", "str", "", _("Shift-") + _("F5")),
            ("Shift-F6", "str", "", _("Shift-") + _("F6")),
            ("Shift-F7", "str", "", _("Shift-") + _("F7")),
            ("Shift-F8", "str", "", _("Shift-") + _("F8")),
            ("Shift-F9", "str", "", _("Shift-") + _("F9")),
            ("Shift-F10", "str", "", _("Shift-") + _("F10")),
            ("Shift-F11", "str", "", _("Shift-") + _("F11")),
            ("Shift-F12", "str", "", _("Shift-") + _("F12")),
            ("Control-F1", "str", "", _("Control-") + _("F1")),
            ("Control-F2", "str", "", _("Control-") + _("F2")),
            ("Control-F3", "str", "", _("Control-") + _("F3")),
            ("Control-F4", "str", "", _("Control-") + _("F4")),
            ("Control-F5", "str", "", _("Control-") + _("F5")),
            ("Control-F6", "str", "", _("Control-") + _("F6")),
            ("Control-F7", "str", "", _("Control-") + _("F7")),
            ("Control-F8", "str", "", _("Control-") + _("F8")),
            ("Control-F9", "str", "", _("Control-") + _("F9")),
            ("Control-F10", "str", "", _("Control-") + _("F10")),
            ("Control-F11", "str", "", _("Control-") + _("F11")),
            ("Control-F12", "str", "", _("Control-") + _("F12")),
        ]
        self.buttons.append("exe")

    # ----------------------------------------------------------------------
    def execute(self, app):
        self.save()
        app.loadShortcuts()
