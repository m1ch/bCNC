""" Refactored from
    ToolsPage.py -

    @m1ch - 2022.08.29
"""

from ._database import DataBase

__author__ = "Vasilis Vlachoudis"
__email__ = "Vasilis.Vlachoudis@cern.ch"


# =============================================================================
# Cut material
# =============================================================================
class Tool(DataBase):
    """ Refactored from Class Cut
    """
    help = "\n".join([
        "Cut selected toolpath into Z depth of stock material.",
        "",
        "For short paths, you should probably use helical cut with "
        + "bottom.",
        "For long toolpaths and pocketing you should use ramp cut "
        + "(length around 10).",
        "Also there's classic flat cuting strategy, but that will lead to "
        + "plunging straight down to material, which is not really "
        + "desirable (especially when milling harder materials).",
        "",
        "If you have generated tabs and want them to be left uncut, you "
        + "should check \"leave islands\" and uncheck "
        + "\"cut contours of islands\"",
        "If you want islands to get finishing pass, cou can use "
        + "\"cut contours of selected islands\" or cut them "
        + "individually afterwards.",
    ])
    icon = "cut"
    variables = [
        ("name", "db", "", _("Name")),
        ("surface", "mm", "", _("Surface Z")),
        ("depth", "mm", "", _("Target Depth")),
        ("stepz", "mm", "", _("Depth Increment")),
        ("feed", "mm", "", _("Feed")),
        ("feedz", "mm", "", _("Plunge Feed")),
        (
            "strategy",
            "flat,helical+bottom,helical,ramp",
            "helical+bottom",
            _("Cutting strategy"),
        ),
        (
            "ramp",
            "int",
            10,
            _("Ramp length"),
            _(
                "positive value = relative to tool diameter (5 to 10 "
                + "probably makes sense), negative = absolute ramp "
                + "distance (you probably don't need this). Also note "
                + "that ramp can't currently be shorter than affected "
                + "g-code segment."
            ),
        ),
        ("cutFromTop", "bool", False, _("First cut at surface height")),
        (
            "spring",
            "bool",
            False,
            _("Spring pass"),
            _(
                "Do the last cut once more in opposite direction. "
                + "Helix bottom is disabled in such case."
            ),
        ),
        (
            "exitpoint",
            "on path,inside,outside",
            "on path",
                _("Exit strategy (useful for threads)"),
            _(
                "You should probably always use 'on path', unless "
                + "you are threadmilling!"
            ),
        ),
        ("islandsLeave", "bool", True, _("Leave islands uncut")),
        (
            "islandsSelectedOnly",
            "bool",
            True,
            _("Only leave selected islands uncut"),
        ),
        (
            "islandsCompensate",
            "bool",
            False,
            _("Compensate islands for cutter radius"),
            _(
                "Add additional margin/offset around islands to "
                    + "compensate for endmill radius. This is automatically "
                + "done for all islands if they are marked as tabs."
            ),
        ),
        ("islandsCut", "bool", True,
         _("Cut contours of selected islands")),
    ]

    def __init__(self, master):
        DataBase.__init__(self, master, "Cut")
        self.buttons.append("exe")

    # ----------------------------------------------------------------------
    def execute(self, app):
        # Cuting dimensions
        surface = self.fromMm("surface", None)
        depth = self.fromMm("depth", None)
        step = self.fromMm("stepz", None)

        # Cuting speed
        try:
            feed = self.fromMm("feed", None)
        except Exception:
            feed = None
        try:
            feedz = self.fromMm("feedz", None)
        except Exception:
            feedz = None

        # Cuting strategy
        strategy = self["strategy"]
        cutFromTop = self["cutFromTop"]
        springPass = self["spring"]

        # Islands
        islandsLeave = self["islandsLeave"]
        islandsCut = self["islandsCut"]
        islandsSelectedOnly = self["islandsSelectedOnly"]
        islandsCompensate = self["islandsCompensate"]

        # Decide if helix or ramp
        helix = False
        if strategy in ["helical+bottom", "helical", "ramp+bottom", "ramp"]:
            helix = True

        # Decide if ramp
        ramp = 0
        if strategy in ["ramp+bottom", "ramp"]:
            helixBottom = True
            ramp = self["ramp"]
            if ramp < 0:
                ramp = self.master.fromMm(float(ramp))

        # Decide if bottom
        helixBottom = False
        if strategy in ["helical+bottom", "ramp+bottom", "ramp"]:
            helixBottom = True

        # Decide exit point
        exitpoint = self["exitpoint"]
        if exitpoint == "inside":
            exitpoint = 1
        elif exitpoint == "outside":
            exitpoint = -1
        else:
            exitpoint = None

        # Execute cut
        app.executeOnSelection(
            "CUT",
            True,
            depth,
            step,
            surface,
            feed,
            feedz,
            cutFromTop,
            helix,
            helixBottom,
            ramp,
            islandsLeave,
            islandsCut,
            islandsSelectedOnly,
            exitpoint,
            springPass,
            islandsCompensate,
        )
        app.setStatus(_("CUT selected paths"))
