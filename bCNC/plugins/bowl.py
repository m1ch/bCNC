# $Id$
#
# Author:    https://github.com/carlosgs
# Date:      14-Sep-2015

import math

from cnc import globCNC
from gcode import globGCode

from cnc import Block
from tools._plugin import Plugin

__author__ = "Carlos Garcia Saura"
__email__ = ""
__name__ = _("Bowl")


# =============================================================================
# Bowl class
# =============================================================================
class Bowl:
    def __init__(self, name):
        self.name = name

    # ----------------------------------------------------------------------
    # r       = sphere radius
    # res     = pressure angle
    # pocket  = progressive (carves the sphere pocketing each layer)
    # ----------------------------------------------------------------------
    def calc(self, D, res, pocket):
        blocks = []
        block = Block(self.name)

        # Load tool and material settings
        toolDiam = globCNC.vars["diameter"]
        toolRadius = toolDiam / 2.0
        stepz = globCNC.vars["stepz"]
        stepxy = toolDiam * (globCNC.vars["stepover"] / 100.0)

        if toolDiam <= 0 or stepxy <= 0 or stepz <= 0 or D <= 0 or res <= 0:
            return blocks

        currDepth = 0.0

        def setCutFeedrate():
            block.append(globCNC.gcode_generate(
                1, [("f", globCNC.vars["cutfeed"])]))

        def addCircumference(radius):
            block.append(globCNC.garc(2, radius, 0.0, i=-radius))

        # Mills a circle, pocketing it if needed
        def addSingleCircle(radius, depth):
            if pocket:
                block.append(globCNC.grapid(0.0, 0.0))
                block.append(globCNC.zenter(depth))
                setCutFeedrate()
                currRadius = 0.0
                while radius > currRadius + stepxy:
                    currRadius += stepxy
                    block.append(globCNC.gline(currRadius, 0))
                    addCircumference(currRadius)
                if radius - currRadius > 0:
                    block.append(globCNC.gline(radius, 0))
                    addCircumference(radius)
            else:
                block.append(globCNC.grapid(radius, 0.0))
                block.append(globCNC.zenter(depth))
                setCutFeedrate()
                addCircumference(radius)

        # Mills a circle in steps of height "stepz"
        def addCircle(radius, depth, currDepth):
            while depth < currDepth - stepz:
                currDepth -= stepz
                addSingleCircle(radius, currDepth)
            if currDepth - depth > 0:
                addSingleCircle(radius, depth)
            return depth

        block.append(globCNC.zsafe())
        r = D / 2.0
        r -= toolRadius  # Removes offset of ball-end tool
        angleInc = res
        currAngle = 0.0
        angle = math.pi / 2.0  # 90 degrees
        while angle > currAngle + angleInc:
            currAngle += angleInc
            radius = r * math.cos(-currAngle)
            # Removes vertical offset (centers the ball tool in Z=0,
            # rather than the tip)
            depth = r * math.sin(-currAngle) - toolRadius
            currDepth = addCircle(radius, depth, currDepth)
        if angle - currAngle > 0:
            radius = r * math.cos(-angle)
            depth = r * math.sin(-angle) - toolRadius
            currDepth = addCircle(radius, depth, currDepth)

        blocks.append(block)
        return blocks


# =============================================================================
# Create a simple Bowl
# =============================================================================
class Tool(Plugin):
    __doc__ = _("Generate a bowl cavity")

    def __init__(self, master):
        Plugin.__init__(self, master, "Bowl")
        self.group = "Generator"
        self.icon = "bowl"
        self.variables = [
            ("name", "db", "", _("Name")),
            ("D", "mm", 30.0, _("Diameter")),
            ("res", "float", 10.0, _("Resolution (degrees)")),
            ("pocket", "bool", 1, _("Progressive")),
        ]
        self.buttons.append("exe")

    # ----------------------------------------------------------------------
    def execute(self, app):
        n = self["name"]
        if not n or n == "default":
            n = "Bowl"
        bowl = Bowl(n)
        blocks = bowl.calc(self.fromMm("D"),
                           math.radians(self["res"]),
                           self["pocket"])
        if len(blocks) > 0:
            active = app.activeBlock()
            if active == 0:
                active = 1
            globGCode.insBlocks(active, blocks, "Create BOWL")
            app.refresh()
            app.setStatus(_("Generated: BOWL"))
        else:
            app.setStatus(_("Error: Check the Bowl and End Mill parameters"))
