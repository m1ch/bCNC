""" This File was refactored from original File
    EditorPage.py - EditorPage

"""
# $Id$
#
# Author: vvlachoudis@gmail.com
# Date: 18-Jun-2015

from . import _page

from globalVariables import N_

__author__ = "Vasilis Vlachoudis"
__email__ = "vvlachoudis@gmail.com"


# =============================================================================
# Editor Page
# =============================================================================
class Page(_page.Page):
    __doc__ = _("GCode editor")
    _name_ = N_("Editor")
    _icon_ = "edit"

    # ----------------------------------------------------------------------
    # Add a widget in the widgets list to enable disable during the run
    # ----------------------------------------------------------------------
    # def register(self):
    #     self._register(
    #         groups=(
    #             "Clipboard",
    #             "Select",
    #             "Edit",
    #             "Move",
    #             "Order",
    #             "Transform",
    #             "Route",
    #             "Info",
    #         ),
    #         frames=("Editor",),
    #     )
    #     self._register(
    #         (
    #             ClipboardGroup,
    #             SelectGroup,
    #             EditGroup,
    #             MoveGroup,
    #             OrderGroup,
    #             TransformGroup,
    #             RouteGroup,
    #             InfoGroup,
    #         ),
    #         (EditorFrame,),
    #     )
