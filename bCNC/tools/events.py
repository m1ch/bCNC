""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import Ini

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# -----------------------------------------------------------------------------
class Tool(Ini):
    """ Refactored from Class Events
    """
    def __init__(self, master):
        Ini.__init__(self, master, "Events", "str")
