# $Id: CNC.py,v 1.8 2014/10/15 15:03:49 bnv Exp $
#
# XXX: This file is extracted from CNC.py originaly writen by
#      vvlachoudis@gmail.com
#
# Author: M1ch
# Date: 2022-07-28

import math
import os
import re
import types

import undo
from bmath import (
    sqrt,
    Vector,
)
from bpath import Path, Segment
from dxf import DXF
from svgcode import SVGcode
from cnc import (
    BLOCKPAT,
    SKIP,
    XY,
    XZ,
    YZ,
    ERROR_HANDLING,
    MAXINT,
    Probe,
    Orient,
    Block,
    getValue,
    globCNC,
)


# =============================================================================
# Gcode file
# =============================================================================
class GCode:
    LOOP_MERGE = False

    # ----------------------------------------------------------------------
    def __init__(self):
        self.header = ""
        self.footer = ""
        self.undoredo = undo.UndoRedo()
        self.probe = Probe()
        self.orient = Orient()
        self.vars = {}  # local variables
        self.init()

    # ----------------------------------------------------------------------
    def init(self):
        self.filename = ""
        self.blocks = []  # list of blocks
        self.vars.clear()
        self.undoredo.reset()
        self._lastModified = 0
        self._modified = False

    # ----------------------------------------------------------------------
    # Recalculate enabled path margins
    # ----------------------------------------------------------------------
    def calculateEnableMargins(self):
        globCNC.resetEnableMargins()
        for block in self.blocks:
            if block.enable:
                globCNC.vars["xmin"] = min(globCNC.vars["xmin"], block.xmin)
                globCNC.vars["ymin"] = min(globCNC.vars["ymin"], block.ymin)
                globCNC.vars["zmin"] = min(globCNC.vars["zmin"], block.zmin)
                globCNC.vars["xmax"] = max(globCNC.vars["xmax"], block.xmax)
                globCNC.vars["ymax"] = max(globCNC.vars["ymax"], block.ymax)
                globCNC.vars["zmax"] = max(globCNC.vars["zmax"], block.zmax)

    # ----------------------------------------------------------------------
    def isModified(self):
        return self._modified

    # ----------------------------------------------------------------------
    def resetModified(self):
        self._modified = False

    # ----------------------------------------------------------------------
    def __getitem__(self, item):
        return self.blocks[item]

    # ----------------------------------------------------------------------
    def __setitem__(self, item, value):
        self.blocks[item] = value

    # ----------------------------------------------------------------------
    # Evaluate code expressions if any and return line
    # ----------------------------------------------------------------------
    def evaluate(self, line, app=None):
        if isinstance(line, int):
            return None

        elif isinstance(line, list):
            for i, expr in enumerate(line):
                if isinstance(expr, types.CodeType):
                    result = eval(expr, globCNC.vars, self.vars)
                    if isinstance(result, float):
                        line[i] = str(round(result, globCNC.digits))
                    else:
                        line[i] = str(result)
            return "".join(line)

        elif isinstance(line, types.CodeType):
            import traceback  # noqa: F401

            v = self.vars
            v["os"] = os
            v["app"] = app
            return eval(line, globCNC.vars, self.vars)

        else:
            return line

    # ----------------------------------------------------------------------
    # add new line to list create block if necessary
    # ----------------------------------------------------------------------
    def _addLine(self, line):
        if line.startswith("(Block-name:"):
            self._blocksExist = True
            pat = BLOCKPAT.match(line)
            if pat:
                value = pat.group(2).strip()
                if not self.blocks or len(self.blocks[-1]):
                    self.blocks.append(Block(value))
                else:
                    self.blocks[-1]._name = value
                return

        # FIXME: Code to import legacy tabs can be probably removed in year
        # 2020 or so:
        if line.startswith("(Block-tab:"):
            pat = BLOCKPAT.match(line)
            if pat:
                value = pat.group(2).strip()
                items = map(float, value.split())
                tablock = Block(f"legacy [tab,island,minz:{items[4]:f}]")
                tablock.color = "orange"
                tablock.extend(self.createTab(*items))
                self.insBlocks(-1, [tablock], "Legacy tab")
                print(
                    "WARNING: Converted legacy tabs loaded from file to new "
                    f"g-code island tabs: {tablock._name}"
                )

        if not self.blocks:
            self.blocks.append(Block("Header"))

        cmds = globCNC.parseLine(line)
        if cmds is None:
            self.blocks[-1].append(line)
            return

        globCNC.motionStart(cmds)

        # rapid move up = end of block
        if self._blocksExist:
            self.blocks[-1].append(line)
        elif globCNC.gcode == 0 and globCNC.dz > 0.0:
            self.blocks[-1].append(line)
            self.blocks.append(Block())
        elif globCNC.gcode == 0 and len(self.blocks) == 1:
            self.blocks.append(Block())
            self.blocks[-1].append(line)
        else:
            self.blocks[-1].append(line)

        globCNC.motionEnd()

    # ----------------------------------------------------------------------
    # Load a file into editor
    # ----------------------------------------------------------------------
    def load(self, filename=None):
        if filename is None:
            filename = self.filename
        self.init()
        self.filename = filename
        try:
            f = open(self.filename)
        except Exception:
            return False
        self._lastModified = os.stat(self.filename).st_mtime
        globCNC.initPath()
        globCNC.resetAllMargins()
        self._blocksExist = False
        for line in f:
            self._addLine(line[:-1].replace("\x0d", ""))
        self._trim()
        f.close()
        return True

    # ----------------------------------------------------------------------
    # Save to a file
    # ----------------------------------------------------------------------
    def save(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            f = open(self.filename, "w")
        except Exception:
            return False

        for block in self.blocks:
            block.write(f)
        f.close()
        self._lastModified = os.stat(self.filename).st_mtime
        self._modified = False
        return True

    # ----------------------------------------------------------------------
    # Save in TXT format
    # -Enabled Blocks only
    # -Cleaned from bCNC metadata and comments
    # -Uppercase
    # ----------------------------------------------------------------------
    def saveTXT(self, filename):
        txt = open(filename, "w")
        for block in self.blocks:
            if block.enable:
                for line in block:
                    cmds = globCNC.parseLine(line)
                    if cmds is None:
                        continue
                    txt.write(f"{line.upper()}\n")
        txt.close()
        return True

    # ----------------------------------------------------------------------
    def addBlockFromString(self, name, text):
        if not text:
            return
        block = Block(name)
        block.extend(text.splitlines())
        self.blocks.append(block)

    # ----------------------------------------------------------------------
    # If empty insert a header and a footer
    # ----------------------------------------------------------------------
    def headerFooter(self):
        if not self.blocks:
            self.addBlockFromString("Header", self.header)
            self.addBlockFromString("Footer", self.footer)
            return True
        return False

    # ----------------------------------------------------------------------
    # Load DXF file into gcode
    # ----------------------------------------------------------------------
    def importDXF(self, filename):
        try:
            dxf = DXF(filename, "r")
        except Exception:
            return False
        self.filename = ""

        dxf.readFile()
        dxf.close()

        # prepare dxf file
        dxf.sort()
        dxf.convert2Polylines()
        dxf.expandBlocks()

        empty = len(self.blocks) == 0
        if empty:
            self.addBlockFromString("Header", self.header)

        if globCNC.inch:
            units = DXF.INCHES
        else:
            units = DXF.MILLIMETERS

        undoinfo = []
        for name, layer in dxf.layers.items():
            enable = not bool(layer.isFrozen())
            entities = dxf.entities(name)
            if not entities:
                continue
            self.importEntityPoints(None,
                                    entities,
                                    name,
                                    enable,
                                    layer.color())
            path = Path(name)
            path.fromDxf(dxf, entities, units)
            path.removeZeroLength()
            if path.color is None:
                path.color = layer.color()
            if path.color == "#FFFFFF":
                path.color = None
            # Lowered accuracy due to problems interfacing arcs and
            # lines in DXF
            opath = path.split2contours(0.0001)
            if not opath:
                continue
            while opath:
                li = 0
                llen = 0.0
                for i, p in enumerate(opath):
                    if p.length() > llen:
                        li = i
                        llen = p.length()
                longest = opath.pop(li)
                longest.directionSet(
                    1
                )  # turn path to CW (conventional when milling outside)

                # Can be time consuming
                if self.LOOP_MERGE:
                    longest.mergeLoops(opath)

                undoinfo.extend(self.importPath(None, longest, None, enable))

            undoinfo.extend(self.importPath(None, opath, None, enable))

        if empty:
            self.addBlockFromString("Footer", self.footer)
        return True

    # ----------------------------------------------------------------------
    # Save in DXF format
    # ----------------------------------------------------------------------
    def saveDXF(self, filename):
        try:
            dxf = DXF(filename, "w")
        except Exception:
            return False
        if globCNC.inch:
            dxf.units = DXF.INCHES
        else:
            dxf.units = DXF.MILLIMETERS
        dxf.writeHeader()
        for block in self.blocks:
            name = block.name()
            if ":" in name:
                name = name.split(":")[0]
            for line in block:
                cmds = globCNC.parseLine(line)
                if cmds is None:
                    continue
                globCNC.motionStart(cmds)
                if globCNC.gcode == 1:  # line
                    dxf.line(
                        globCNC.x,
                        globCNC.y,
                        globCNC.xval,
                        globCNC.yval,
                        name
                    )
                elif globCNC.gcode in (2, 3):  # arc
                    xc, yc = globCNC.motionCenter()
                    sphi = math.atan2(globCNC.y - yc, globCNC.x - xc)
                    ephi = math.atan2(globCNC.yval - yc, globCNC.xval - xc)
                    if ephi <= sphi + 1e-10:
                        ephi += 2.0 * math.pi
                    if globCNC.gcode == 2:
                        dxf.arc(
                            xc,
                            yc,
                            globCNC.rval,
                            math.degrees(ephi),
                            math.degrees(sphi),
                            name,
                        )
                    else:
                        dxf.arc(
                            xc,
                            yc,
                            globCNC.rval,
                            math.degrees(sphi),
                            math.degrees(ephi),
                            name,
                        )
                globCNC.motionEnd()
        dxf.writeEOF()
        dxf.close()
        return True

    # ----------------------------------------------------------------------
    # Get scaling factor for SVG files
    # ----------------------------------------------------------------------
    def SVGscale(self, dpi=96.0):  # same as inkscape 0.9x (according to jscut)
        if globCNC.inch:
            return 1.0 / dpi
        return 25.4 / dpi

    # ----------------------------------------------------------------------
    # Load SVG file into gcode
    # ----------------------------------------------------------------------
    def importSVG(self, filename):
        svgcode = SVGcode(filename)

        empty = len(self.blocks) == 0
        if empty:
            self.addBlockFromString("Header", self.header)

        # FIXME: UI to set SVG samples_per_unit
        ppi = 96.0  # 96 pixels per inch.
        scale = self.SVGscale(ppi)
        samples_per_unit = 200.0
        for path in svgcode.get_gcode(scale,
                                      samples_per_unit,
                                      globCNC.digits,
                                      ppi=ppi):
            self.addBlockFromString(path["id"], path["path"])

        if empty:
            self.addBlockFromString("Footer", self.footer)
        return True

    # ----------------------------------------------------------------------
    # get document margins
    # ----------------------------------------------------------------------
    def getMargins(self):
        # Get bounding box of document
        minx, miny, maxx, maxy = 0, 0, 0, 0
        for i, block in enumerate(self.blocks):
            paths = self.toPath(i)
            for path in paths:
                minx2, miny2, maxx2, maxy2 = path.bbox()
                minx, miny, maxx, maxy = (
                    min(minx, minx2),
                    min(miny, miny2),
                    max(maxx, maxx2),
                    max(maxy, maxy2),
                )
        return minx, miny, maxx, maxy

    # ----------------------------------------------------------------------
    # Save in SVG format
    # ----------------------------------------------------------------------
    def saveSVG(self, filename):
        try:
            svg = open(filename, "w")
        except Exception:
            return False

        padding = 10
        scale = self.SVGscale()

        # Get bounding box of document
        minx, miny, maxx, maxy = self.getMargins()

        svg.write(
            "<!-- SVG generated by bCNC: "
            "https://github.com/vlachoudis/bCNC -->\n"
        )
        svg.write(
            f"<svg viewBox=\"{(minx * scale) - padding} "
            f"{(-maxy * scale) - padding} "
            f"{((maxx - minx) * scale) + padding * 2} "
            f"{((maxy - miny) * scale) + padding * 2}\">\n"
        )

        def svgLine(scale, px, py, type_="L"):
            return f"\t{type_} {px * scale} {py * scale}\n"

        def svgArc(scale, gcode, r, ax, ay, bx, by, cx, cy):
            sphi = math.atan2(ay - yc, ax - xc)
            ephi = math.atan2(by - yc, bx - xc)
            arcSweep = ephi - sphi
            arcSweep = 0 if arcSweep <= math.radians(180) else 1
            # Arc
            if gcode == 2:
                if ephi <= sphi + 1e-10:
                    ephi += 2.0 * math.pi
                return "\tA {} {} {} {} {} {} {}\n".format(
                    r * scale,
                    r * scale,
                    0,
                    arcSweep,
                    1,
                    bx * scale,
                    by * scale,
                )
            else:
                if ephi <= sphi + 1e-10:
                    ephi += 2.0 * math.pi
                return "\tA {} {} {} {} {} {} {}\n".format(
                    r * scale,
                    r * scale,
                    0,
                    arcSweep,
                    0,
                    bx * scale,
                    by * scale,
                )

        for block in self.blocks:

            name = block.name()
            color = block.color
            if color is None:
                color = "black"
            width = 2
            if ":" in name:
                name = name.split(":")[0]
            svgpath = ""
            lastx, lasty = 0, 0
            firstx, firsty = None, None

            # Write paths
            for line in block:
                cmds = globCNC.parseLine(line)
                if cmds is None:
                    continue
                globCNC.motionStart(cmds)

                if globCNC.gcode == 0:  # rapid line (move)
                    svgpath += svgLine(
                        scale, globCNC.xval, -globCNC.yval, "M")
                else:
                    lastx, lasty = globCNC.xval, globCNC.yval
                    if firstx is None:
                        firstx, firsty = globCNC.x, globCNC.y

                if globCNC.gcode == 1:  # line
                    svgpath += svgLine(scale, globCNC.xval, -globCNC.yval)

                elif globCNC.gcode in (2, 3):  # arc
                    xc, yc = globCNC.motionCenter()

                    # In case of full circle, we need to split circle
                    # in two arcs:
                    midx = globCNC.x
                    midy = globCNC.y
                    if (
                        globCNC.y == globCNC.yval
                        and globCNC.x == globCNC.xval
                    ):  # is full circle?
                        midx = globCNC.x + (xc - globCNC.x) * 2
                        midy = globCNC.y + (yc - globCNC.y) * 2
                        svgpath += svgArc(
                            scale,
                            globCNC.gcode,
                            globCNC.rval,
                            globCNC.x,
                            -globCNC.y,
                            midx,
                            -midy,
                            xc,
                            -yc,
                        )
                    # Finish arc
                    svgpath += svgArc(
                        scale,
                        globCNC.gcode,
                        globCNC.rval,
                        midx,
                        -midy,
                        globCNC.xval,
                        -globCNC.yval,
                        xc,
                        -yc,
                    )
                globCNC.motionEnd()

            if firstx == lastx and firsty == lasty:
                svgpath += "\tZ\n"

            if len(svgpath) > 0:
                for line in block.write_header().splitlines():
                    svg.write(f"\t<!-- {line} -->\n")
                svg.write(
                    f"\t<path d=\"\n{svgpath}\t\" stroke=\"{color}\" "
                    f"stroke-width=\"{width}\" fill=\"none\" />\n"
                )

        svg.write("</svg>\n")
        svg.close()
        return True

    # ----------------------------------------------------------------------
    # Import POINTS from entities
    # ----------------------------------------------------------------------
    def importEntityPoints(self, pos, entities, name, enable=True, color=None):
        undoinfo = []
        i = 0
        while i < len(entities):
            if entities[i].type != "POINT":
                i += 1
                continue

            block = Block(f"{name} [P]")
            block.enable = enable

            block.color = entities[i].color()
            if block.color is None:
                block.color = color

            x, y = entities[i].start()
            block.append(f"g0 {self.fmt('x', x, 7)} {self.fmt('y', y, 7)}")
            block.append(globCNC.zenter(globCNC["surface"]))
            block.append(globCNC.zsafe())
            undoinfo.append(self.addBlockUndo(pos, block))
            if pos is not None:
                pos += 1
            del entities[i]

        return undoinfo

    # ----------------------------------------------------------------------
    # convert a block to path
    # ----------------------------------------------------------------------
    def toPath(self, bid):
        block = self.blocks[bid]
        paths = []
        path = Path(block.name())
        self.initPath(bid)
        start = Vector(globCNC.x, globCNC.y)

        # get only first path that enters the surface
        # ignore the deeper ones
        passno = 0
        for line in block:
            # flatten helical paths
            line = re.sub(r"\s?z-?[0-9\.]+", "", line)

            # break after first depth pass
            if line == "( ---------- cut-here ---------- )":
                passno = 0
                if path:
                    paths.append(path)
                    path = Path(block.name())
            if line[:5] == "(pass":
                passno += 1
            if passno > 1:
                continue

            cmds = globCNC.parseLine(line)
            if cmds is None:
                continue
            globCNC.motionStart(cmds)
            end = Vector(globCNC.xval, globCNC.yval)
            if globCNC.gcode == 0:  # rapid move (new block)
                if path:
                    paths.append(path)
                    path = Path(block.name())
            elif globCNC.gcode == 1:  # line
                if globCNC.dx != 0.0 or globCNC.dy != 0.0:
                    path.append(Segment(1, start, end))
            elif globCNC.gcode in (2, 3):  # arc
                xc, yc = globCNC.motionCenter()
                center = Vector(xc, yc)
                path.append(Segment(globCNC.gcode, start, end, center))
            globCNC.motionEnd()
            start = end
        if path:
            paths.append(path)
        return paths

    # ----------------------------------------------------------------------
    # create a block from Path
    # @param z      I       ending depth
    # @param zstart I       starting depth
    # ----------------------------------------------------------------------
    def fromPath(
        self,
        path,
        block=None,
        z=None,
        retract=True,
        entry=False,
        exit_=True,
        zstart=None,
        ramp=None,
        comments=True,
        exitpoint=None,
        truncate=None,
    ):
        # Recursion for multiple paths
        if not isinstance(path, Path):
            block = Block("new")
            for p in path:
                block.extend(
                    self.fromPath(
                        p,
                        None,
                        z,
                        retract,
                        entry,
                        exit_,
                        zstart,
                        ramp,
                        comments,
                        exitpoint,
                        truncate,
                    )
                )
                block.append("( ---------- cut-here ---------- )")
            del block[-1]  # remove trailing cut-here
            return block

        if z is None:
            z = globCNC["surface"]
        if zstart is None:
            zstart = z

        # Calculate helix step
        zstep = abs(z - zstart)

        # Preprocess ramp
        if ramp is None:
            ramp = 0
        if ramp == 0:
            ramp = path.length()  # full helix (default)
        ramp = min(ramp, path.length())  # Never ramp longer than single pass!

        # Calculate helical feedrate
        helixfeed = globCNC["cutfeed"]
        if zstep > 0:
            # Compensate helix feed, so we never plunge too fast on
            # short/steep paths
            # FIXME: Add UI to disable this feature??? Not
            # sure if that's needed.
            rampratio = zstep / min(path.length(), ramp)
            helixfeed2 = round(globCNC["cutfeedz"] / rampratio)
            helixfeed = min(globCNC["cutfeed"], helixfeed2)

        #
        if block is None:
            if isinstance(path, Path):
                block = Block(path.name)
            else:
                block = Block(path[0].name)

        # Generate g-code for single path segment
        def addSegment(segment, z=None, cm=""):
            x, y = segment.B

            # Generate LINE
            if segment.type == Segment.LINE:
                x, y = segment.B
                # rounding problem from #903 was manifesting here. Had to lower
                # the decimal precision to globCNC.digits
                if z is None:
                    block.append(
                        f"g1 {self.fmt('x', x, 7)} {self.fmt('y', y, 7)}" + cm)
                else:
                    block.append(
                        f"g1 {self.fmt('x', x, 7)} {self.fmt('y', y, 7)} "
                        f"{self.fmt('z', z, 7)}"
                        + cm
                    )

            # Generate ARCS
            elif segment.type in (Segment.CW, Segment.CCW):
                ij = segment.C - segment.A
                if abs(ij[0]) < 1e-5:
                    ij[0] = 0.0
                if abs(ij[1]) < 1e-5:
                    ij[1] = 0.0
                if z is None:
                    block.append(
                        f"g{int(segment.type)} "
                        + f"{self.fmt('x', x, 7)} "
                        + f"{self.fmt('y', y, 7)} "
                        + f"{self.fmt('i', ij[0], 7)} "
                        + f"{self.fmt('j', ij[1], 7)} "
                        + cm
                    )
                else:
                    block.append(
                        f"g{int(segment.type)} "
                        + f"{self.fmt('x', x, 7)} "
                        + f"{self.fmt('y', y, 7)} "
                        + f"{self.fmt('i', ij[0], 7)} "
                        + f"{self.fmt('j', ij[1], 7)} "
                        + f"{self.fmt('z', z, 7)} "
                        + cm
                    )

        # Get island height of segment
        def getSegmentZTab(segment, altz=float("-inf")):
            if segment._inside:
                return max(segment._inside)
            else:
                return altz

        # Generate block from path
        if isinstance(path, Path):
            x, y = path[0].A

            # decide if flat or ramp/helical:
            if z == zstart:
                zh = z
            elif zstart is not None:
                zh = zstart

            # test if not starting in tab/island!
            ztab = getSegmentZTab(path[0], z)

            # Retract to zsafe
            if retract:
                block.append(f"g0 {self.fmt('z', globCNC.vars['safe'], 7)}")

            # Rapid to beginning of the path
            block.append(f"g0 {self.fmt('x', x, 7)} {self.fmt('y', y, 7)}")

            # Descend to pass (plunge to the beginning of path)
            if entry:
                # if entry feed to Z
                block.append(globCNC.zenter(max(zh, ztab), 7))
            else:
                # without entry just rapid to Z
                block.append(f"g0 {self.fmt('z', max(zh, ztab), 7)}")

            # Begin pass
            if comments:
                block.append("(entered)")

            # Loop over segments
            setfeed = True
            ztabprev = float("-inf")
            ramping = True
            for sid, segment in enumerate(path):
                zhprev = zh

                # Ramp down
                zh -= (segment.length() / ramp) * zstep  # ramp
                zh = max(zh, z)  # Never cut deeper than z!

                # Reset feedrate if not ramping anymore
                if zh == zhprev and ramping:
                    helixfeed = globCNC["cutfeed"]
                    setfeed = True
                    ramping = False

                # Get tab height
                ztab = getSegmentZTab(segment)

                # Retract over tabs
                # has tab height changed? tab boundary crossed?
                if ztab != ztabprev:
                    # if we need to enter the toolpath after done
                    # clearing the tab
                    if (ztab == float("-inf") or ztab < ztabprev) and (
                        zh < ztabprev or zhprev < ztabprev
                    ):
                        if comments:
                            block.append(
                                "(tab down " + str(max(zhprev, ztab)) + ")")
                        block.append(globCNC.zenter(max(zhprev, ztab), 7))
                        setfeed = True
                    elif (
                        zh < ztab or zhprev < ztab
                    ):  # if we need to go higher in order to clear the tab
                        if comments:
                            block.append("(tab up " + str(max(zh, ztab)) + ")")
                        block.append(globCNC.zexit(max(zh, ztab), 7))
                        setfeed = True
                ztabprev = ztab

                # Cut next segment of toolpath
                # Never cut deeper than tabs!
                addSegment(segment, max(zh, ztab))

                # Set feed if needed
                if setfeed:
                    block[-1] += f" {self.fmt('f', round(helixfeed))}"
                    setfeed = False

                # Truncate
                if truncate is not None:
                    truncate -= segment.length()
                    if truncate <= -1e-7:
                        break

            # Exit toolpath
            if exit_:
                if comments:
                    block.append("(exiting)")
                if exitpoint is not None:
                    block.append(
                        f"g1 {self.fmt('x', exitpoint[0])} "
                        f"{self.fmt('y', exitpoint[1])}"
                    )
                block.append(globCNC.zsafe())

        return block

    # ----------------------------------------------------------------------
    # Import paths as block
    # return ids of blocks added in newblocks list if declared
    # ----------------------------------------------------------------------
    def importPath(
            self, pos, paths, newblocks=None, enable=True, multiblock=True):
        undoinfo = []
        if isinstance(paths, Path):
            block = self.fromPath(paths)
            block.enable = enable
            block.color = paths.color
            undoinfo.append(self.addBlockUndo(pos, block))
            if newblocks is not None:
                newblocks.append(pos)
        else:
            block = None
            for path in paths:
                if block is None:
                    block = Block(path.name)
                block = self.fromPath(path, block)
                if multiblock:
                    block.enable = enable
                    undoinfo.append(self.addBlockUndo(pos, block))
                    if newblocks is not None:
                        newblocks.append(pos)
                    if pos is not None:
                        pos += 1
                    block = None
            if not multiblock:
                block.enable = enable
                undoinfo.append(self.addBlockUndo(pos, block))
                if newblocks is not None:
                    newblocks.append(pos)
        return undoinfo

    # ----------------------------------------------------------------------
    # sync file timestamp
    # ----------------------------------------------------------------------
    def syncFileTime(self):
        try:
            self._lastModified = os.stat(self.filename).st_mtime
        except Exception:
            return False

    # ----------------------------------------------------------------------
    # Check if a new version exists
    # ----------------------------------------------------------------------
    def checkFile(self):
        try:
            return os.stat(self.filename).st_mtime > self._lastModified
        except Exception:
            return False

    # ----------------------------------------------------------------------
    def fmt(self, c, v, d=None):
        return globCNC.fmt(c, v, d)

    # ----------------------------------------------------------------------
    def _trim(self):
        if not self.blocks:
            return
        # Delete last block if empty
        last = self.blocks[-1]
        if len(last) == 1 and len(last[0]) == 0:
            del last[0]
        if len(self.blocks[-1]) == 0:
            self.blocks.pop()

    # ----------------------------------------------------------------------
    # Undo/Redo operations
    # ----------------------------------------------------------------------
    def undo(self):
        self.undoredo.undo()

    # ----------------------------------------------------------------------
    def redo(self):
        self.undoredo.redo()

    # ----------------------------------------------------------------------
    def addUndo(self, undoinfo, msg=None):
        if not undoinfo:
            return
        self.undoredo.add(undoinfo, msg)
        self._modified = True

    # ----------------------------------------------------------------------
    def canUndo(self):
        return self.undoredo.canUndo()

    # ----------------------------------------------------------------------
    def canRedo(self):
        return self.undoredo.canRedo()

    # ----------------------------------------------------------------------
    # Change all lines in editor
    # ----------------------------------------------------------------------
    def setLinesUndo(self, lines):
        undoinfo = (self.setLinesUndo, list(self.lines()))
        # Delete all blocks and create new ones
        del self.blocks[:]
        globCNC.initPath()
        self._blocksExist = False
        for line in lines:
            self._addLine(line)
        self._trim()
        return undoinfo

    # ----------------------------------------------------------------------
    def setAllBlocksUndo(self, blocks=[]):
        undoinfo = [self.setAllBlocksUndo, self.blocks]
        self.blocks = blocks
        return undoinfo

    # ----------------------------------------------------------------------
    # Change a single line in a block
    # ----------------------------------------------------------------------
    def setLineUndo(self, bid, lid, line):
        undoinfo = (self.setLineUndo, bid, lid, self.blocks[bid][lid])
        self.blocks[bid][lid] = line
        return undoinfo

    # ----------------------------------------------------------------------
    # Insert a new line into block
    # ----------------------------------------------------------------------
    def insLineUndo(self, bid, lid, line):
        undoinfo = (self.delLineUndo, bid, lid)
        block = self.blocks[bid]
        if lid >= len(block):
            block.append(line)
        else:
            block.insert(lid, line)
        return undoinfo

    # ----------------------------------------------------------------------
    # Clone line inside a block
    # ----------------------------------------------------------------------
    def cloneLineUndo(self, bid, lid):
        return self.insLineUndo(bid, lid, self.blocks[bid][lid])

    # ----------------------------------------------------------------------
    # Delete line from block
    # ----------------------------------------------------------------------
    def delLineUndo(self, bid, lid):
        block = self.blocks[bid]
        undoinfo = (self.insLineUndo, bid, lid, block[lid])
        del block[lid]
        return undoinfo

    # ----------------------------------------------------------------------
    # Add a block
    # ----------------------------------------------------------------------
    def addBlockUndo(self, bid, block):
        if bid is None:
            bid = len(self.blocks)
        if bid >= len(self.blocks):
            undoinfo = (self.delBlockUndo, len(self.blocks))
            self.blocks.append(block)
        else:
            undoinfo = (self.delBlockUndo, bid)
            self.blocks.insert(bid, block)
        return undoinfo

    # ----------------------------------------------------------------------
    # Clone a block
    # ----------------------------------------------------------------------
    def cloneBlockUndo(self, bid, pos=None):
        if pos is None:
            pos = bid
        return self.addBlockUndo(pos, Block(self.blocks[bid]))

    # ----------------------------------------------------------------------
    # Delete a whole block
    # ----------------------------------------------------------------------
    def delBlockUndo(self, bid):
        block = self.blocks.pop(bid)
        undoinfo = (self.addBlockUndo, bid, block)
        return undoinfo

    # ----------------------------------------------------------------------
    # Insert a list of other blocks from another gcode file probably
    # ----------------------------------------------------------------------
    def insBlocksUndo(self, bid, blocks):
        if bid is None or bid >= len(self.blocks):
            bid = len(self.blocks)
        undoinfo = (
            "Insert blocks", self.delBlocksUndo, bid, bid + len(blocks))
        self.blocks[bid:bid] = blocks
        return undoinfo

    # ----------------------------------------------------------------------
    # Delete a range of blocks
    # ----------------------------------------------------------------------
    def delBlocksUndo(self, from_, to_):
        blocks = self.blocks[from_:to_]
        undoinfo = ("Delete blocks", self.insBlocksUndo, from_, blocks)
        del self.blocks[from_:to_]
        return undoinfo

    # ----------------------------------------------------------------------
    # Insert blocks and push the undo info
    # ----------------------------------------------------------------------
    def insBlocks(self, bid, blocks, msg=""):
        if self.headerFooter():  # just in case
            bid = 1
        self.addUndo(self.insBlocksUndo(bid, blocks), msg)

    # ----------------------------------------------------------------------
    # Set block expand
    # ----------------------------------------------------------------------
    def setBlockExpandUndo(self, bid, expand):
        undoinfo = (self.setBlockExpandUndo, bid, self.blocks[bid].expand)
        self.blocks[bid].expand = expand
        return undoinfo

    # ----------------------------------------------------------------------
    # Set block state
    # ----------------------------------------------------------------------
    def setBlockEnableUndo(self, bid, enable):
        undoinfo = (self.setBlockEnableUndo, bid, self.blocks[bid].enable)
        self.blocks[bid].enable = enable
        return undoinfo

    # ----------------------------------------------------------------------
    # Set block color
    # ----------------------------------------------------------------------
    def setBlockColorUndo(self, bid, color):
        undoinfo = (self.setBlockColorUndo, bid, self.blocks[bid].color)
        self.blocks[bid].color = color
        return undoinfo

    # ----------------------------------------------------------------------
    # Swap two blocks
    # ----------------------------------------------------------------------
    def swapBlockUndo(self, a, b):
        undoinfo = (self.swapBlockUndo, a, b)
        tmp = self.blocks[a]
        self.blocks[a] = self.blocks[b]
        self.blocks[b] = tmp
        return undoinfo

    # ----------------------------------------------------------------------
    # Move block from location src to location dst
    # ----------------------------------------------------------------------
    def moveBlockUndo(self, src, dst):
        if src == dst:
            return None
        undoinfo = (self.moveBlockUndo, dst, src)
        if dst > src:
            self.blocks.insert(dst - 1, self.blocks.pop(src))
        else:
            self.blocks.insert(dst, self.blocks.pop(src))
        return undoinfo

    # ----------------------------------------------------------------------
    # Invert selected blocks
    # ----------------------------------------------------------------------
    def invertBlocksUndo(self, blocks):
        undoinfo = []
        first = 0
        last = len(blocks) - 1
        while first < last:
            undoinfo.append(self.swapBlockUndo(blocks[first], blocks[last]))
            first += 1
            last -= 1
        return undoinfo

    # ----------------------------------------------------------------------
    # Move block upwards
    # ----------------------------------------------------------------------
    def orderUpBlockUndo(self, bid):
        if bid == 0:
            return None
        undoinfo = (self.orderDownBlockUndo, bid - 1)
        # swap with the block above
        before = self.blocks[bid - 1]
        self.blocks[bid - 1] = self.blocks[bid]
        self.blocks[bid] = before
        return undoinfo

    # ----------------------------------------------------------------------
    # Move block downwards
    # ----------------------------------------------------------------------
    def orderDownBlockUndo(self, bid):
        if bid >= len(self.blocks) - 1:
            return None
        undoinfo = (self.orderUpBlockUndo, bid + 1)
        # swap with the block below
        after = self[bid + 1]
        self[bid + 1] = self[bid]
        self[bid] = after
        return undoinfo

    # ----------------------------------------------------------------------
    # Insert block lines
    # ----------------------------------------------------------------------
    def insBlockLinesUndo(self, bid, lines):
        undoinfo = (self.delBlockLinesUndo, bid)
        block = Block()
        for line in lines:
            block.append(line)
        self.blocks.insert(bid, block)
        return undoinfo

    # ----------------------------------------------------------------------
    # Delete a whole block lines
    # ----------------------------------------------------------------------
    def delBlockLinesUndo(self, bid):
        lines = [x for x in self.blocks[bid]]
        undoinfo = (self.insBlockLinesUndo, bid, lines)
        del self.blocks[bid]
        return undoinfo

    # ----------------------------------------------------------------------
    # Set Block name
    # ----------------------------------------------------------------------
    def setBlockNameUndo(self, bid, name):
        undoinfo = (self.setBlockNameUndo, bid, self.blocks[bid]._name)
        self.blocks[bid]._name = name
        return undoinfo

    # ----------------------------------------------------------------------
    # Add an operation code in the name as [drill, cut, in/out...]
    # ----------------------------------------------------------------------
    def addBlockOperationUndo(self, bid, operation, remove=None):
        undoinfo = (self.setBlockNameUndo, bid, self.blocks[bid]._name)
        self.blocks[bid].addOperation(operation, remove)
        return undoinfo

    # ----------------------------------------------------------------------
    # Replace the lines of a block
    # ----------------------------------------------------------------------
    def setBlockLinesUndo(self, bid, lines):
        block = self.blocks[bid]
        undoinfo = (self.setBlockLinesUndo, bid, block[:])
        del block[:]
        block.extend(lines)
        return undoinfo

    # ----------------------------------------------------------------------
    # Move line upwards
    # ----------------------------------------------------------------------
    def orderUpLineUndo(self, bid, lid):
        if lid == 0:
            return None
        block = self.blocks[bid]
        undoinfo = (self.orderDownLineUndo, bid, lid - 1)
        block.insert(lid - 1, block.pop(lid))
        return undoinfo

    # ----------------------------------------------------------------------
    # Move line downwards
    # ----------------------------------------------------------------------
    def orderDownLineUndo(self, bid, lid):
        block = self.blocks[bid]
        if lid >= len(block) - 1:
            return None
        undoinfo = (self.orderUpLineUndo, bid, lid + 1)
        block.insert(lid + 1, block.pop(lid))
        return undoinfo

    # ----------------------------------------------------------------------
    # Expand block with autolevel information
    # ----------------------------------------------------------------------
    def autolevelBlock(self, block):
        new = []
        autolevel = not self.probe.isEmpty()
        for line in block:
            cmds = globCNC.compileLine(line)
            if cmds is None:
                new.append(line)
                continue
            elif isinstance(cmds, str):
                cmds = globCNC.breakLine(cmds)
            else:
                new.append(line)
                continue

            globCNC.motionStart(cmds)
            if (autolevel and globCNC.gcode in (0, 1, 2, 3)
                    and globCNC.mval == 0):
                xyz = globCNC.motionPath()
                if not xyz:
                    # while auto-levelling, do not ignore non-movement
                    # commands, just append the line as-is
                    new.append(line)
                else:
                    extra = ""
                    for c in cmds:
                        if (c[0].upper() not in
                                ("G", "X", "Y", "Z", "I", "J", "K", "R")):
                            extra += c
                    x1, y1, z1 = xyz[0]
                    if globCNC.gcode == 0:
                        g = 0
                    else:
                        g = 1
                    for x2, y2, z2 in xyz[1:]:
                        for x, y, z in self.probe.splitLine(x1, y1, z1, x2,
                                                            y2, z2):
                            new.append(
                                "".join([
                                    f"G{int(g)}",
                                    f"{self.fmt('X', x / globCNC.unit)}",
                                    f"{self.fmt('Y', y / globCNC.unit)}",
                                    f"{self.fmt('Z', z / globCNC.unit)}",
                                    extra,
                                ])
                            )
                            extra = ""
                        x1, y1, z1 = x2, y2, z2
                globCNC.motionEnd()
            else:
                globCNC.motionEnd()
                new.append(line)
        return new

    # ----------------------------------------------------------------------
    # Execute autolevel on selected blocks
    # ----------------------------------------------------------------------
    def autolevel(self, items):
        undoinfo = []
        operation = "autolevel"
        for bid in items:
            block = self.blocks[bid]
            if block.name() in ("Header", "Footer"):
                continue
            if not block.enable:
                continue
            lines = self.autolevelBlock(block)
            undoinfo.append(self.addBlockOperationUndo(bid, operation))
            undoinfo.append(self.setBlockLinesUndo(bid, lines))
        if undoinfo:
            self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Return string representation of whole file
    # ----------------------------------------------------------------------
    def __repr__(self):
        return "\n".join(list(self.lines()))

    # ----------------------------------------------------------------------
    # Iterate over the items
    # ----------------------------------------------------------------------
    def iterate(self, items):
        for bid, lid in items:
            if lid is None:
                block = self.blocks[bid]
                for i in range(len(block)):
                    yield bid, i
            else:
                yield bid, lid

    # ----------------------------------------------------------------------
    # Iterate over all lines
    # ----------------------------------------------------------------------
    def lines(self):
        for block in self.blocks:
            yield from block

    # ----------------------------------------------------------------------
    # initialize cnc path based on block bid
    # ----------------------------------------------------------------------
    def initPath(self, bid=0):
        if bid == 0:
            globCNC.initPath()
        else:
            # Use the ending point of the previous block
            # since the starting (sxyz is after the rapid motion)
            block = self.blocks[bid - 1]
            globCNC.initPath(block.ex, block.ey, block.ez)

    # ----------------------------------------------------------------------
    # Move blocks/lines up
    # ----------------------------------------------------------------------
    def orderUp(self, items):
        sel = []  # new selection
        undoinfo = []
        for bid, lid in items:
            if isinstance(lid, int):
                undoinfo.append(self.orderUpLineUndo(bid, lid))
                sel.append((bid, lid - 1))
            elif lid is None:
                undoinfo.append(self.orderUpBlockUndo(bid))
                if bid == 0:
                    return items
                else:
                    sel.append((bid - 1, None))
        self.addUndo(undoinfo, "Move Up")
        return sel

    # ----------------------------------------------------------------------
    # Move blocks/lines down
    # ----------------------------------------------------------------------
    def orderDown(self, items):
        sel = []  # new selection
        undoinfo = []
        for bid, lid in reversed(items):
            if isinstance(lid, int):
                undoinfo.append(self.orderDownLineUndo(bid, lid))
                sel.append((bid, lid + 1))
            elif lid is None:
                undoinfo.append(self.orderDownBlockUndo(bid))
                if bid >= len(self.blocks) - 1:
                    return items
                else:
                    sel.append((bid + 1, None))
        self.addUndo(undoinfo, "Move Down")
        sel.reverse()
        return sel

    # ----------------------------------------------------------------------
    # Peck distance
    # Target depth
    # Depth increment
    # Retract height=safe height
    # ----------------------------------------------------------------------
    def drill(
        self,
        items,
        depth=None,
        peck=None,
        dwell=None,
        distance=None,
        number=0,
        center=True,
    ):
        # find the penetration points and drill
        # skip all g1 movements on the horizontal plane
        if depth is None:
            depth = globCNC["surface"] - globCNC["thickness"]
        if (
            depth < globCNC["surface"] - globCNC["thickness"]
            or depth > globCNC["surface"]
        ):
            return (
                f"ERROR: Drill depth {depth:g} outside stock surface: "
                f"{globCNC['surface']:g} .. "
                f"{globCNC['surface'] - globCNC['thickness']:g}\n"
                f"Please change stock surface in Tools->Stock or drill depth."
            )
        if abs(depth - (globCNC["surface"] - globCNC["thickness"])) < 1e-7:
            opname = "drill"
        else:
            opname = f"drill:{depth:g}"
        # Incorrect peck values can block drilling cycle calculation
        peck = peck or 0.0
        if peck == 0.0:
            peck = None
        if peck is not None:
            if math.copysign(1.0, depth) * math.copysign(1.0, peck) != -1:
                pecksignstr = "less"
                if math.copysign(1.0, peck) < 0:
                    pecksignstr = "greater"
                return (
                    f"Invalid peck depth value of {peck:g}. In this "
                    f"configuration, peck value should be {pecksignstr} than "
                    f"zero."
                )
        # pecking value is well defined.

        undoinfo = []

        def drillHole(lines):
            # drill point
            if peck is None:
                lines.append(globCNC.zenter(depth))
                lines.append(globCNC.zsafe())
            else:
                z = globCNC["surface"]
                while z > depth:
                    z = max(z - peck, depth)
                    lines.append(globCNC.zenter(z))
                    lines.append(globCNC.zsafe())
                    if dwell:
                        lines.append(f"g4 {self.fmt('p', dwell)}")

        for bid in items:
            block = self.blocks[bid]
            if block.name() in ("Header", "Footer"):
                continue
            block.enable = True

            # construct new name
            undoinfo.append(self.addBlockOperationUndo(bid, opname))

            # 1st detect limits of first pass
            self.initPath(bid)
            globCNC.z = globCNC.zval = 1000.0
            lines = []

            if center:
                # Drill in center only
                for path in self.toPath(bid):
                    x, y = path.center()
                    lines.append(f"g0 {self.fmt('x', x)} {self.fmt('y', y)}")
                    drillHole(lines)

            elif distance is None and number == 0:
                # Drill on path begining only
                for i, line in enumerate(block):
                    cmds = globCNC.parseLine(line)
                    if cmds is None:
                        lines.append(line)
                        continue
                    globCNC.motionStart(cmds)
                    if globCNC.dz < 0.0:
                        drillHole(lines)
                    elif globCNC.dz > 0.0:
                        # retract
                        pass
                    elif globCNC.gcode == 0:
                        # add all rapid movements
                        lines.append(line)
                    elif globCNC.gcode == 1:
                        # ignore normal movements
                        pass
                    globCNC.motionEnd()
            else:
                # Drill multiple holes along path
                for path in self.toPath(bid):

                    length = path.length()
                    if number > 0:
                        distance = length / float(number)
                    s = 0.0  # running length

                    while s < length:
                        P = path.distPoint(s)
                        s += distance
                        lines.append(
                            f"g0 {self.fmt('x', P[0])} {self.fmt('y', P[1])}")
                        drillHole(lines)

            undoinfo.append(self.setBlockLinesUndo(bid, lines))
        self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Perform a cut on a path an add it to block
    # @param newblock O block to add the cut paths
    # @param block  I   existing block
    # @param path   I   path to cut
    # @param z      I   starting z surface
    # @param depth  I   ending depth
    # @param stepz  I   stepping in z
    # ----------------------------------------------------------------------
    def cutPath(
        self,
        newblock,
        block,
        path,
        z,
        depth,
        stepz,
        helix=False,
        helixBottom=True,
        ramp=0,
        islandPaths=[],
        exitpoint=None,
        springPass=False,
    ):
        closed = path.isClosed()
        zigzag = True  # FIXME: Add UI to set this?
        entry = True
        exit_ = False

        # Calculate ramp
        if ramp > 0:
            ramp = abs(ramp) * globCNC.vars["diameter"]  # n times tool diameter
        if ramp < 0:
            ramp = abs(ramp)  # absolute
        if ramp == 0:
            ramp = None  # No ramp

        # Calculate exit point for thread milling
        centr = Vector(path.center())
        if exitpoint == 1:
            exitpoint = centr
        elif exitpoint == -1:
            exitpoint = path[-1].B + (path[-1].B - centr)
        else:
            exitpoint = None

        # Mark in which island we are inside
        if islandPaths:
            for island in reversed(islandPaths):
                path.intersectPath(island)
            for island in reversed(islandPaths):
                path.markInside(island, island._inside)

        # Decide if doing additional "appendix" passes after loop
        # (eg.: spring pass or helixbottom)
        appendix = False
        if (springPass and closed) or (helix and helixBottom):
            appendix = True

        # iterate over depth passes:
        retract = True
        while (z - depth) > 1e-7:
            # Go one step lower
            z = max(z - stepz, depth)

            # Detect last pass of loop
            if abs(z - depth) < 1e-7 and not appendix:
                exit_ = True

            # Flat cuts:
            if not helix:
                newblock.append(f"(pass {z:f})")
                if zigzag:
                    self.fromPath(
                        path,
                        newblock,
                        z,
                        retract,
                        True,
                        exit_,
                        exitpoint=exitpoint
                    )
                    if not closed:
                        path.invert()
                else:
                    self.fromPath(
                        path,
                        newblock,
                        z,
                        True,
                        True,
                        exit_,
                        exitpoint=exitpoint
                    )

            # Helical/Ramp cuts:
            else:
                if helixBottom:
                    exit_ = False

                if closed:
                    newblock.append(
                        f"(pass {z + stepz:f} to {z:f})")
                    self.fromPath(
                        path,
                        newblock,
                        z,
                        retract,
                        entry,
                        exit_,
                        z + stepz,
                        ramp,
                        exitpoint=exitpoint,
                    )
                else:
                    # Cut open path back and forth while descending
                    newblock.append(
                        f"(pass {z + stepz:f} to {z + stepz / 2:f})")
                    self.fromPath(
                        path,
                        newblock,
                        z + stepz / 2,
                        retract,
                        entry,
                        False,
                        z + stepz,
                        ramp,
                        exitpoint=exitpoint,
                    )
                    path.invert()
                    newblock.append(f"(pass {z + stepz / 2:f} to {z:f})")
                    self.fromPath(
                        path,
                        newblock,
                        z,
                        False,
                        False,
                        exit_,
                        z + stepz / 2,
                        ramp,
                        exitpoint=exitpoint,
                    )
                    path.invert()

            retract = False
            entry = False

        # Do appendix passes like spring pass or helixbottom
        if appendix:
            if springPass and closed:
                ramp = None  # Do not truncate pass when inverting direction
                path.invert()
                if not closed:
                    retract = True
                    entry = True
                newblock.append(f"(pass {z:f} spring)")
            else:
                newblock.append(f"(pass {z:f} bottom)")

            self.fromPath(
                path,
                newblock,
                z,
                retract,
                entry,
                True,
                exitpoint=exitpoint,
                truncate=ramp,
            )

        return newblock

    # ----------------------------------------------------------------------
    # Close paths by joining end with start with a line segment
    # ----------------------------------------------------------------------
    def close(self, items):
        undoinfo = []
        for bid in items:
            block = self.blocks[bid]
            if block.name() in ("Header", "Footer"):
                continue
            undoinfo.append(
                self.insLineUndo(
                    bid, MAXINT, globCNC.gline(block.sx, block.sy))
            )
        self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Create a cut my replicating the initial top-only path multiple times
    # until the maximum height
    # ----------------------------------------------------------------------
    def cut(
        self,
        items,
        depth=None,
        stepz=None,
        surface=None,
        feed=None,
        feedz=None,
        cutFromTop=False,
        helix=False,
        helixBottom=True,
        ramp=0,
        islandsLeave=False,
        islandsCut=False,
        islandsSelectedOnly=True,
        exitpoint=None,
        springPass=False,
        islandsCompensate=False,
    ):
        if surface is None:
            surface = globCNC["surface"]
        if stepz is None:
            stepz = globCNC["stepz"]
        if depth is None:
            depth = surface - globCNC["thickness"]

        # override temporarily the feed if needed
        if feed is not None:  # swap feed with cnc[cutfeed]
            globCNC["cutfeed"], feed = feed, globCNC["cutfeed"]
        if feedz is not None:
            globCNC["cutfeedz"], feedz = feedz, globCNC["cutfeedz"]

        # Test if cutting within stock boundaries
        if surface > globCNC["surface"]:
            return (
                "ERROR: Starting cut height is higher than stock surface. "
                "Please change stock surface in Tools->Stock or cut depth."
            )
        if (
            depth < globCNC["surface"] - globCNC["thickness"]
            or depth > globCNC["surface"]
        ):
            return (
                "ERROR: Cut depth {depth:g} outside stock surface: "
                f"{globCNC['surface']:g} .. "
                f"{globCNC['surface'] - globCNC['thickness']:g}\n"
                "Please change stock surface in Tools->Stock or cut depth."
            )

        # Determine operation block name
        if abs(depth - (globCNC["surface"] - globCNC["thickness"])) < 1e-7:
            opname = "cut"
            if helix:
                opname = "helicut"
        else:
            opname = f"cut:{depth:g}"
            if helix:
                opname = f"helicut:{depth:g}"

        stepz = abs(stepz)
        undoinfo = []

        # Get list of islands and remove them from items
        islands = []
        islandPaths = []
        if islandsLeave:
            for bid, block in enumerate(self.blocks):
                if islandsSelectedOnly and bid not in items:
                    continue
                if block.operationTest("island"):
                    islands.append(bid)
                    # determine island height
                    islz = globCNC["safe"]
                    if block.operationGet("minz") is not None:
                        islz = float(block.operationGet("minz"))
                    # determine if we should offset island
                    # (tabs are always offset)
                    isloffset = False
                    if islandsCompensate or block.operationTest("tab"):
                        isloffset = True
                    # load island paths
                    for islandPath in self.toPath(bid):
                        # compensate for cutter diameter if needed
                        if isloffset:
                            islandPath = islandPath.offsetClean(
                                globCNC.vars["diameter"] / 2
                            )[0]
                        islandPath._inside = islz
                        islandPaths.append(islandPath)

        # Remove islands from paths to cut if not requested
        # TODO: maybe also remove all islands with "tab" tag
        if not islandsCut and islands:
            for island in islands:
                if island in items:
                    items.remove(island)
        # Check if there are any paths left
        if not items:
            return "You must select toolpaths along with islands!"

        for bid in items:
            block = self.blocks[bid]
            if block.name() in ("Header", "Footer"):
                continue
            block.enable = True
            newblock = Block(block.name())

            # Do not apply islands on islands:
            islandPathsClean = islandPaths
            if bid in items and bid in islands:
                islandPathsClean = []

            for path in self.toPath(bid):

                if cutFromTop:
                    self.cutPath(
                        newblock,
                        block,
                        path,
                        surface + stepz,
                        depth,
                        stepz,
                        helix,
                        helixBottom,
                        ramp,
                        islandPathsClean,
                        exitpoint,
                        springPass,
                    )
                else:
                    self.cutPath(
                        newblock,
                        block,
                        path,
                        surface,
                        depth,
                        stepz,
                        helix,
                        helixBottom,
                        ramp,
                        islandPathsClean,
                        exitpoint,
                        springPass,
                    )
            if newblock:
                undoinfo.append(self.addBlockOperationUndo(bid, opname))
                undoinfo.append(self.setBlockLinesUndo(bid, newblock))
        self.addUndo(undoinfo)

        # restore feed
        if feed is not None:
            globCNC["cutfeed"] = feed
        if feedz is not None:
            globCNC["cutfeedz"] = feedz

    def createTab(self, x=0, y=0, dx=0, dy=0, z=0, circ=True):
        path = Path("tab")

        dx = dx / 2.0
        dy = dy / 2.0

        if not circ:
            # Square tabs (intersect better with trochoids)
            A = A0 = Vector(x - dx, y - dy)
            B = Vector(x + dx, y - dy)
            path.append(Segment(Segment.LINE, A, B))
            A = B
            B = Vector(x + dx, y + dy)
            path.append(Segment(Segment.LINE, A, B))
            A = B
            B = Vector(x - dx, y + dy)
            path.append(Segment(Segment.LINE, A, B))
            A = B
            B = A0
            path.append(Segment(Segment.LINE, A, B))
        else:
            # Circular tabs (intersect better with angled lines)
            A = Vector(x - max(dx, dy), y)
            C = Vector(x, y)
            seg = Segment(Segment.CCW, A, A)
            seg.setCenter(C)
            path.append(seg)

        # compensate for cutter radius
        # update: this is now done right before cutting,
        # so no need to do it here!
        # path = path.offsetClean(globCNC.vars["diameter"]/2)[0]

        return self.fromPath(
            path, None, None, False, False, False, None, None, False)

    # ----------------------------------------------------------------------
    # Create tabs to selected blocks
    # @param ntabs  number of tabs
    # @param dtabs  distance between tabs
    # @param dx     width of tabs
    # @param dy     depth of tabs
    # @param z      height of tabs
    # @param isl    create tabs in form of islands?
    # ----------------------------------------------------------------------
    def createTabs(self, items, ntabs, dtabs, dx, dy, z, circ=True):
        msg = None
        undoinfo = []
        if ntabs == 0 and dtabs == 0:
            return

        tablocks = []
        for bid in items:
            block = self.blocks[bid]
            if block.name() in ("Header", "Footer"):
                continue

            # update minz for selected islands/tabs rather than doing
            # tabs of tabs
            if block.operationTest("island"):
                block._name = f"{block.nameNop()} [island,minz:{z:f}]"
                continue

            else:
                tablock = Block(f"{block.nameNop()} [tab,island,minz:{z:f}]")
                # tablock.color = "#FF0000"
                tablock.color = "orange"
                tablock.enable = (
                    False  # Prevent tabs from being accidentaly cut as path
                )

                # Add regular tabs
                for path in self.toPath(bid):
                    length = path.length()
                    d = max(length / float(ntabs), dtabs)
                    # running length
                    s = d / 2.0  # start from half distance to add first tab

                    while s <= length:
                        P = path.distPoint(s)
                        s += d
                        # Make island tabs
                        tablock.extend(
                            self.createTab(P[0], P[1], dx, dy, z, circ))
                        tablock.append("( ---------- cut-here ---------- )")

                del tablock[-1]  # remove last cut-here
                tablocks.append(tablock)
        self.insBlocks(bid + 1, tablocks, "Tabs created")
        self.addUndo(undoinfo)

        return msg

    # ----------------------------------------------------------------------
    # Reverse direction of cut
    # ----------------------------------------------------------------------
    def reverse(self, items):
        undoinfo = []
        remove = ["cut", "climb", "conventional", "cw", "ccw", "reverse"]
        for bid in items:
            operation = "reverse"

            if self.blocks[bid].name() in ("Header", "Footer"):
                continue
            newpath = Path(self.blocks[bid].name())

            # Not sure if this is good idea...
            # Might get confusing if something goes wrong,
            # but seems to work fine
            if self.blocks[bid].operationTest("conventional"):
                operation += ",climb"
            if self.blocks[bid].operationTest("climb"):
                operation += ",conventional"
            if self.blocks[bid].operationTest("cw"):
                operation += ",ccw"
            if self.blocks[bid].operationTest("ccw"):
                operation += ",cw"

            for path in self.toPath(bid):
                path.invert()
                newpath.extend(path)
            if newpath:
                block = self.fromPath(newpath)
                undoinfo.append(
                    self.addBlockOperationUndo(bid, operation, remove))
                undoinfo.append(self.setBlockLinesUndo(bid, block))
        self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Change cut direction
    # 1     CW
    # -1    CCW
    # 2     Conventional = CW for inside profiles and pockets,
    #                  CCW for outside profiles
    # -2    Climb = CCW for inside profiles and pockets,
    #               CW for outside profiles
    # ----------------------------------------------------------------------
    def cutDirection(self, items, direction=-1):

        undoinfo = []
        msg = None

        remove = ["cut", "reverse", "climb", "conventional", "cw", "ccw"]
        for bid in items:
            if self.blocks[bid].name() in ("Header", "Footer"):
                continue

            opdir = direction
            operation = ""

            # Decide conventional/climb/error:
            side = self.blocks[bid].operationSide()
            if abs(direction) > 1 and side == 0:
                msg = "Conventional/Climb feature only works for paths with "\
                      + "'in/out/pocket' tags!\n"
                msg += "Some of the selected paths were not taged (or are"\
                       + "both in+out). You can still use CW/CCW for them."
                continue
            if direction == 2:
                operation = "conventional,"
                if side == -1:
                    opdir = 1  # inside CW
                if side == 1:
                    opdir = -1  # outside CCW
            elif direction == -2:
                operation = "climb,"
                if side == -1:
                    opdir = -1  # inside CCW
                if side == 1:
                    opdir = 1  # outside CW

            # Decide CW/CCW tag
            if opdir == 1:
                operation += "cw"
            elif opdir == -1:
                operation += "ccw"

            # Process paths
            for path in self.toPath(bid):
                if not path.directionSet(opdir):
                    msg = "Error determining direction of path!"
                if path:
                    block = self.fromPath(path)
                    undoinfo.append(
                        self.addBlockOperationUndo(bid, operation, remove))
                    undoinfo.append(self.setBlockLinesUndo(bid, block))
        self.addUndo(undoinfo)

        return msg

    # ----------------------------------------------------------------------
    # Toggle or set island tag on block
    # ----------------------------------------------------------------------
    def island(self, items, island=None):

        undoinfo = []
        remove = ["island"]
        for bid in items:
            isl = island

            if self.blocks[bid].name() in ("Header", "Footer"):
                continue

            if isl is None:
                isl = not self.blocks[bid].operationTest("island")
            if isl:
                tag = "island"
                self.blocks[bid].color = "#ff0000"
            else:
                tag = ""
                self.blocks[bid].color = None

            undoinfo.append(self.addBlockOperationUndo(bid, tag, remove))

        self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Return information for a block
    # return XXX
    # ----------------------------------------------------------------------
    def info(self, bid):
        paths = self.toPath(bid)
        if not paths:
            return None, 1
        if len(paths) > 1:
            closed = paths[0].isClosed()
            return len(paths), paths[0]._direction(closed)
        else:
            closed = paths[0].isClosed()
            return int(closed), paths[0]._direction(closed)

    # ----------------------------------------------------------------------
    # make a profile on block
    # offset +/- defines direction = tool/2
    # return new blocks inside the blocks list
    # ----------------------------------------------------------------------
    def profile(self, blocks, offset, overcut=False, name=None, pocket=False):
        undoinfo = []
        msg = ""
        newblocks = []

        remove = [
            "cut",
            "reverse",
            "climb",
            "conventional",
            "cw",
            "ccw",
            "in",
            "out",
        ]

        for bid in reversed(blocks):
            if self.blocks[bid].name() in ("Header", "Footer"):
                continue
            newpath = []
            for path in self.toPath(bid):
                if name is not None:
                    newname = Block.operationName(path.name, name)
                elif offset > 0:
                    newname = Block.operationName(
                        path.name, "out,conventional,ccw", remove
                    )
                    path.directionSet(
                        -1
                    )  # turn path to CCW (conventional when milling outside)
                else:
                    newname = Block.operationName(
                        path.name, "in,conventional,cw", remove
                    )
                    path.directionSet(
                        1
                    )  # turn path to CW (conventional when milling inside)

                if not path.isClosed():
                    m = f"Path: '{path.name}' is OPEN"
                    if m not in msg:
                        if msg:
                            msg += "\n"
                        msg += m

                opath = path.offsetClean(offset, overcut, newname)
                if opath:
                    newpath.extend(opath)
            if newpath:
                # remember length to shift all new blocks the are inserted
                # before
                before = len(newblocks)
                undoinfo.extend(
                    self.importPath(bid + 1, newpath, newblocks, True, False)
                )
                new = len(newblocks) - before
                for i in range(before):
                    newblocks[i] += new
                self.blocks[bid].enable = False
        self.addUndo(undoinfo)

        # return new blocks inside the blocks list
        del blocks[:]
        # TODO: Not sure how to make the pocket block to cut before profile
        # (to reduce machine load when cuting to dimension)
        # Idealy it should be generated as single block containing both pocket
        # and profile
        if pocket:
            msg = msg + self.pocket(
                newblocks, abs(offset), globCNC.vars["stepover"] / 50, name, True
            )
        blocks.extend(newblocks)
        return msg

    # ----------------------------------------------------------------------
    # Generate a pocket path
    # ----------------------------------------------------------------------
    def _pocket(self, path, diameter, stepover, depth):
        # FIXME: recursions are slow and shall be avoided! Replace recursion
        #        via a loop!

        # python's internal recursion limit hit us before bCNC's
        # limit came to place
        # so i increased python's limit to bCNC's limit + 100
        maxdepth = 10000
        import sys

        sys.setrecursionlimit(max(sys.getrecursionlimit(), maxdepth + 100))

        if depth > maxdepth:
            return None
        if depth == 0:
            offset = diameter / 2.0
        else:
            offset = diameter * stepover

        opath = path.offset(offset)

        if not opath:
            return None

        opath.intersectSelf()
        opath.removeExcluded(path, offset)
        opath.removeZeroLength(abs(offset) / 100.0)
        opath = opath.split2contours()

        if not opath:
            return None

        newpath = []
        for pout in opath:
            pin = self._pocket(pout, diameter, stepover, depth + 1)
            if not pin:
                newpath.append(pout)

            # else: # FIXME
            # 1. Find closest node that we can move with
            #    a straight line without intersecting the path
            # 2. rotate the pout to start from this node
            # 3. join with a normal line
            # else
            # join with a rapid move as a separate path
            elif len(pin) == 1:
                # FIXME maybe it is dangerous!!
                # Have to check before making a straight move
                pin[0].join(pout)
                newpath.append(pin[0])

            else:
                # FIXME needs to check if we can go in normal move
                # needs to find the closest segment and rotate
                # pin[-1].join(pout)
                newpath.extend(pin)
                newpath.append(pout)
        return newpath

    # ----------------------------------------------------------------------
    # make a pocket on block
    # return new blocks inside the blocks list
    # ----------------------------------------------------------------------
    def pocket(self, blocks, diameter, stepover, name, nested=False):
        undoinfo = []
        msg = ""
        newblocks = []
        for bid in reversed(blocks):
            if self.blocks[bid].name() in ("Header", "Footer"):
                continue
            newpath = []
            for path in self.toPath(bid):
                if not path.isClosed():
                    m = f"Path: '{path.name}' is OPEN"
                    if m not in msg:
                        if msg:
                            msg += "\n"
                        msg += m
                    path.close()

                # Remove tiny segments
                path.removeZeroLength(abs(diameter) / 100.0)
                # Convert very small arcs to lines
                path.convert2Lines(abs(diameter) / 10.0)

                path.directionSet(
                    1
                )  # turn path to CW (conventional when milling inside)

                D = path.direction()
                if D == 0:
                    D = 1

                remove = [
                    "cut",
                    "reverse",
                    "climb",
                    "conventional",
                    "cw",
                    "ccw",
                    "pocket",
                ]
                if name is None:
                    path.name = Block.operationName(
                        path.name, "pocket,conventional,cw", remove
                    )
                else:
                    path.name = Block.operationName(path.name, name, remove)

                newpath.extend(self._pocket(path, -D * diameter, stepover, 0))

            if newpath:
                # remember length to shift all new blocks
                # the are inserted before
                before = len(newblocks)
                undoinfo.extend(
                    self.importPath(bid + 1, newpath, newblocks, True, False)
                )
                new = len(newblocks) - before
                for i in range(before):
                    newblocks[i] += new
                if not nested:
                    self.blocks[bid].enable = False
        self.addUndo(undoinfo)

        # return new blocks inside the blocks list
        del blocks[:]
        blocks.extend(newblocks)
        return msg

    # ----------------------------------------------------------------------
    # make a trochoidal profile on block
    # offset +/- defines direction = tool/2
    # return new blocks inside the blocks list
    # ----------------------------------------------------------------------
    def trochprofile_cnc(
        self,
        blocks,
        offset,
        overcut=False,
        adaptative=True,
        adaptedRadius=0.0,
        cutDiam=0.0,
        tooldiameter=0.0,
        targetDepth=0.0,
        depthIncrement=0.0,
        tabsnumber=0.0,
        tabsWidth=0.0,
        tabsHeight=0.0,
    ):
        undoinfo = []
        msg = ""
        newblocks = []
        for bid in reversed(blocks):
            if self.blocks[bid].name() in ("Header", "Footer"):
                continue
            newpath = []
            for path in self.toPath(bid):
                explain = "Tr "
                if offset > 0:
                    explain += "out "
                elif offset < 0:
                    explain += "in "
                explain += str(cutDiam)
                if cutDiam != abs(2 * offset):
                    explain += " offs " + str(abs(offset) - cutDiam / 2.0)
                if offset < 0:
                    if adaptative:
                        explain += " Adapt bit " + str(tooldiameter)
                    if overcut:
                        explain += " overc"
                newname = Block.operationName(path.name, explain)

                if not path.isClosed():
                    m = f"Path: '{path.name}' is OPEN"
                    if m not in msg:
                        if msg:
                            msg += "\n"
                        msg += m

                # Remove tiny segments
                path.removeZeroLength(abs(offset) / 100.0)
                # Convert very small arcs to lines
                path.convert2Lines(abs(offset) / 10.0)
                D = path.direction()
                if D == 0:
                    D = 1
                opath = path.offset(D * offset, newname)
                if opath:
                    opath.intersectSelf()
                    opath.removeExcluded(path, D * offset)
                    opath.removeZeroLength(abs(offset) / 100.0)
                opath = opath.split2contours()
                if opath:
                    if overcut is True or adaptative is True:
                        for p in opath:
                            p.trochovercut(
                                D * offset, overcut, adaptative, adaptedRadius
                            )
                    newpath.extend(opath)
            if newpath:
                # remember length to shift all new blocks the are
                # inserted before
                before = len(newblocks)
                undoinfo.extend(
                    self.importPath(bid + 1, newpath, newblocks, True, False)
                )
                new = len(newblocks) - before
                for i in range(before):
                    newblocks[i] += new
                self.blocks[bid].enable = False
        self.addUndo(undoinfo)

        # return new blocks inside the blocks list
        del blocks[:]
        blocks.extend(newblocks)

        self.cut(
            reversed(blocks),
            targetDepth,
            depthIncrement,
            0,
            900,
            120,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
        )
        return msg

    # ----------------------------------------------------------------------
    def adaptative_clearence(
        self,
        blocks,
        offset,
        overcut=False,
        adaptative=True,
        adaptedRadius=0.0,
        cutDiam=0.0,
        tooldiameter=0.0,
        name=None,
    ):
        undoinfo = []
        msg = ""
        newblocks = []
        for bid in reversed(blocks):
            if self.blocks[bid].name() in ("Header", "Footer"):
                continue
            newpath = []
            for path in self.toPath(bid):
                explain = "Clear "
                if offset > 0:
                    explain += "out "
                elif offset < 0:
                    explain += "in "
                explain += str(cutDiam)
                if cutDiam != abs(2 * offset):
                    explain += " offs " + str(abs(offset) - cutDiam / 2.0)
                if offset < 0:
                    if adaptative:
                        explain += " Adapt bit " + str(tooldiameter)
                    if overcut:
                        explain += " overc"
                newname = Block.operationName(path.name, explain)

                if not path.isClosed():
                    m = f"Path: '{path.name}' is OPEN"
                    if m not in msg:
                        if msg:
                            msg += "\n"
                        msg += m

                # Remove tiny segments
                path.removeZeroLength(abs(offset) / 100.0)
                # Convert very small arcs to lines
                path.convert2Lines(abs(offset) / 10.0)
                D = path.direction()
                if D == 0:
                    D = 1
                opath = path.offset(D * offset, newname)
                if opath:
                    opath.intersectSelf()
                    opath.removeExcluded(path, D * offset)
                    opath.removeZeroLength(abs(offset) / 100.0)
                opath = opath.split2contours()
                if opath:
                    for p in opath:
                        p.two_bit_adaptative_cut(
                            D * offset, overcut, adaptative, adaptedRadius
                        )
                    newpath.extend(opath)
            if newpath:
                # remember length to shift all new blocks the are
                # inserted before
                before = len(newblocks)
                undoinfo.extend(
                    self.importPath(bid + 1, newpath, newblocks, True, False)
                )
                new = len(newblocks) - before
                for i in range(before):
                    newblocks[i] += new
                self.blocks[bid].enable = False
        self.addUndo(undoinfo)

        # return new blocks inside the blocks list
        blocks.extend(newblocks)
        return msg

    # ----------------------------------------------------------------------
    # draw a hole (circle with radius)
    # ----------------------------------------------------------------------
    def hole(self, bid, radius):
        block = self.blocks[bid]

        # Find starting location
        self.initPath(bid)
        for i, line in enumerate(block):
            cmds = globCNC.parseLine(line)
            if cmds is None:
                continue
            globCNC.motionStart(cmds)
            globCNC.motionEnd()

        # FIXME: doesn't work; lid not defined
        # New lines to append
        pos = 1  # pos = lid + 1
        block.insert(pos, f"g0 {self.fmt('x', globCNC.x + radius)}")
        pos += 1
        block.insert(pos, f"g1 {self.fmt('z', -0.001)}")
        pos += 1
        block.insert(pos, f"g2 {self.fmt('i', -radius)}")
        pos += 1

    # ----------------------------------------------------------------------
    # Modify the lines according to the supplied function and arguments
    # ----------------------------------------------------------------------
    def modify(self, items, func, tabFunc, *args):
        undoinfo = []
        old = {}  # Motion commands: Last value
        new = {}  # Motion commands: New value
        relative = False

        for bid, lid in self.iterate(items):
            block = self.blocks[bid]

            if isinstance(lid, int):
                cmds = globCNC.parseLine(block[lid])
                if cmds is None:
                    continue
                globCNC.motionStart(cmds)

                # Collect all values
                new.clear()
                for cmd in cmds:
                    if cmd.upper() == "G91":
                        relative = True
                    if cmd.upper() == "G90":
                        relative = False
                    c = cmd[0].upper()
                    # record only coordinates commands
                    if c not in "XYZIJKR":
                        continue
                    try:
                        new[c] = old[c] = float(cmd[1:]) * globCNC.unit
                    except Exception:
                        new[c] = old[c] = 0.0

                # Modify values with func
                if func(new, old, relative, *args):
                    # Reconstruct new line
                    newcmd = []
                    present = ""
                    for cmd in cmds:
                        c = cmd[0].upper()
                        if c in "XYZIJKR":  # Coordinates
                            newcmd.append(self.fmt(c, new[c] / globCNC.unit))
                        # Motion
                        elif c == "G" and int(cmd[1:]) in (0, 1, 2, 3):
                            newcmd.append(f"G{int(globCNC.gcode)}")
                        else:  # the rest leave unchanged
                            newcmd.append(cmd)
                        present += c
                    # Append motion commands if not exist and changed
                    check = "XYZ"
                    if "I" in new or "J" in new or "K" in new:
                        check += "IJK"
                    for c in check:
                        try:
                            if c not in present and new.get(c) != old.get(c):
                                newcmd.append(
                                    self.fmt(c, new[c] / globCNC.unit))
                        except Exception:
                            pass
                    undoinfo.append(
                        self.setLineUndo(bid, lid, " ".join(newcmd)))
                globCNC.motionEnd()
                # reset arc offsets
                for i in "IJK":
                    if i in old:
                        old[i] = 0.0

        # FIXME I should add it later, check all functions using it
        self.addUndo(undoinfo)

    # ----------------------------------------------------------------------
    # Move position by dx,dy,dz
    # ----------------------------------------------------------------------
    def moveFunc(self, new, old, relative, dx, dy, dz):
        if relative:
            return False
        changed = False
        if "X" in new:
            changed = True
            new["X"] += dx
        if "Y" in new:
            changed = True
            new["Y"] += dy
        if "Z" in new:
            changed = True
            new["Z"] += dz
        return changed

    # ----------------------------------------------------------------------
    def orderLines(self, items, direction):
        if direction == "UP":
            self.orderUp(items)
        elif direction == "DOWN":
            self.orderDown(items)
        else:
            pass

    # ----------------------------------------------------------------------
    # Move position by dx,dy,dz
    # ----------------------------------------------------------------------
    def moveLines(self, items, dx, dy, dz=0.0):
        return self.modify(items, self.moveFunc, None, dx, dy, dz)

    # ----------------------------------------------------------------------
    # Rotate position by c(osine), s(ine) of an angle around center (x0,y0)
    # ----------------------------------------------------------------------
    def rotateFunc(self, new, old, relative, c, s, x0, y0):
        if "X" not in new and "Y" not in new:
            return False
        x = getValue("X", new, old)
        y = getValue("Y", new, old)
        new["X"] = c * (x - x0) - s * (y - y0) + x0
        new["Y"] = s * (x - x0) + c * (y - y0) + y0

        if "I" in new or "J" in new:
            i = getValue("I", new, old)
            j = getValue("J", new, old)
            if globCNC.plane in (XY, XZ):
                new["I"] = c * i - s * j
            if globCNC.plane in (XY, YZ):
                new["J"] = s * i + c * j
        return True

    # ----------------------------------------------------------------------
    # Transform (rototranslate) position with the following function:
    #   xn = c*x - s*y + xo
    #   yn = s*x + c*y + yo
    # it is like the rotate but the rotation center is not defined
    # ----------------------------------------------------------------------
    def transformFunc(self, new, old, relative, c, s, xo, yo):
        if "X" not in new and "Y" not in new:
            return False
        x = getValue("X", new, old)
        y = getValue("Y", new, old)
        new["X"] = c * x - s * y + xo
        new["Y"] = s * x + c * y + yo

        if "I" in new or "J" in new:
            i = getValue("I", new, old)
            j = getValue("J", new, old)
            new["I"] = c * i - s * j
            new["J"] = s * i + c * j
        return True

    # ----------------------------------------------------------------------
    # Rotate items around optional center (on XY plane)
    # ang in degrees (counter-clockwise)
    # ----------------------------------------------------------------------
    def rotateLines(self, items, ang, x0=0.0, y0=0.0):
        a = math.radians(ang)
        c = math.cos(a)
        s = math.sin(a)
        if ang in (0.0, 90.0, 180.0, 270.0, -90.0, -180.0, -270.0):
            c = round(c)  # round numbers to avoid nasty extra digits
            s = round(s)
        return self.modify(items, self.rotateFunc, None, c, s, x0, y0)

    # ----------------------------------------------------------------------
    # Use the orientation information to orient selected code
    # ----------------------------------------------------------------------
    def orientLines(self, items):
        if not self.orient.valid:
            return "ERROR: Orientation information is not valid"
        c = math.cos(self.orient.phi)
        s = math.sin(self.orient.phi)
        return self.modify(
            items,
            self.transformFunc,
            None,
            c,
            s,
            self.orient.xo,
            self.orient.yo
        )

    # ----------------------------------------------------------------------
    # Mirror Horizontal
    # ----------------------------------------------------------------------
    def mirrorHFunc(self, new, old, relative, *kw):
        changed = False
        for axis in "XI":
            if axis in new:
                new[axis] = -new[axis]
                changed = True
        if globCNC.gcode in (2, 3):  # Change  2<->3
            globCNC.gcode = 5 - globCNC.gcode
            changed = True
        return changed

    # ----------------------------------------------------------------------
    # Mirror Vertical
    # ----------------------------------------------------------------------
    def mirrorVFunc(self, new, old, relative, *kw):
        changed = False
        for axis in "YJ":
            if axis in new:
                new[axis] = -new[axis]
                changed = True
        if globCNC.gcode in (2, 3):  # Change  2<->3
            globCNC.gcode = 5 - globCNC.gcode
            changed = True
        return changed

    # ----------------------------------------------------------------------
    # Mirror horizontally/vertically
    # ----------------------------------------------------------------------
    def mirrorHLines(self, items):
        return self.modify(items, self.mirrorHFunc, None)

    # ----------------------------------------------------------------------
    def mirrorVLines(self, items):
        return self.modify(items, self.mirrorVFunc, None)

    # ----------------------------------------------------------------------
    # Round all digits with accuracy
    # ----------------------------------------------------------------------
    def roundFunc(self, new, old, relative):
        for name, value in new.items():
            new[name] = round(value, globCNC.digits)
        return bool(new)

    # ----------------------------------------------------------------------
    # Round line by the amount of digits
    # ----------------------------------------------------------------------
    def roundLines(self, items, acc=None):
        if acc is not None:
            globCNC.digits = acc
        return self.modify(items, self.roundFunc, None)

    # ----------------------------------------------------------------------
    # Inkscape g-code tools on slice/slice it raises the tool to the
    # safe height then plunges again.
    # Comment out all these patterns
    #
    # FIXME needs re-working...
    # ----------------------------------------------------------------------
    def inkscapeLines(self):

        # Loop over all blocks
        self.initPath()
        newlines = []
        last = -1  # line location when it was last raised with dx=dy=0.0

        for line in self.lines():
            # step id
            # 0 - normal cutting z<0
            # 1 - z>0 raised  with dx=dy=0.0
            # 2 - z<0 plunged with dx=dy=0.0
            cmd = globCNC.parseLine(line)
            if cmd is None:
                newlines.append(line)
                continue
            globCNC.motionStart(cmd)
            if globCNC.dx == 0.0 and globCNC.dy == 0.0:
                if globCNC.z > 0.0 and globCNC.dz > 0.0:
                    last = len(newlines)
                elif globCNC.z < 0.0 and globCNC.dz < 0.0 and last >= 0:
                    for i in range(last, len(newlines)):
                        s = newlines[i]
                        if s and s[0] != "(":
                            newlines[i] = f"({s})"
                    last = -1
            else:
                last = -1
            newlines.append(line)
            globCNC.motionEnd()

        self.addUndo(self.setLinesUndo(newlines))

    # ----------------------------------------------------------------------
    # Remove the line number for lines
    # ----------------------------------------------------------------------
    def removeNlines(self, items):
        pass

    # ----------------------------------------------------------------------
    # Re-arrange using genetic algorithms a set of blocks to minimize
    # rapid movements.
    # ----------------------------------------------------------------------
    def optimize(self, items):
        n = len(items)

        matrix = []
        for i in range(n):
            matrix.append([0.0] * n)

        # Find distances between blocks (end to start)
        for i in range(n):
            block = self.blocks[items[i]]
            x1 = block.ex
            y1 = block.ey
            for j in range(n):
                if i == j:
                    continue
                block = self.blocks[items[j]]
                x2 = block.sx
                y2 = block.sy
                dx = x1 - x2
                dy = y1 - y2
                # Compensate for machines, which have different
                # speed of X and Y:
                dx /= globCNC.feedmax_x
                dy /= globCNC.feedmax_y
                matrix[i][j] = sqrt(dx * dx + dy * dy)

        best = [0]
        unvisited = list(range(1, n))
        while unvisited:
            last = best[-1]
            row = matrix[last]
            # from all the unvisited places search the closest one
            mindist = 1e30
            for i, u in enumerate(unvisited):
                d = row[u]
                if d < mindist:
                    mindist = d
                    si = i
            best.append(unvisited.pop(si))

        undoinfo = []
        for i in range(len(best)):
            b = best[i]
            if i == b:
                continue
            ptr = best.index(i)
            undoinfo.append(self.swapBlockUndo(items[i], items[b]))
            best[i], best[ptr] = best[ptr], best[i]
        self.addUndo(undoinfo, "Optimize")

    # ----------------------------------------------------------------------
    # Use probe information to modify the g-code to autolevel
    # ----------------------------------------------------------------------
    def compile(self, queue, stopFunc=None):
        """

        Args:
            queue (funktion): Funtion to add element to queue
            stopFunc (funktion, optional): ???. Defaults to None.

        Returns:
            str: Path
        """
        paths = []

        def add(line, path):
            queue(line)
            # FIXME
            # if line is not None:
            #     if isinstance(line, str):
            #         queue.put(line + "\n")
            #     else:
            #         queue.put(line)
            paths.append(path)

        autolevel = not self.probe.isEmpty()
        self.initPath()
        for line in globCNC.compile(globCNC.startup.splitlines()):
            add(line, None)

        every = 1
        for i, block in enumerate(self.blocks):
            if not block.enable:
                continue
            for j, line in enumerate(block):
                every -= 1
                if every <= 0:
                    if stopFunc is not None and stopFunc():
                        return None
                    every = 50

                newcmd = []
                cmds = globCNC.compileLine(line)
                if cmds is None:
                    continue
                elif isinstance(cmds, str):
                    cmds = globCNC.breakLine(cmds)
                else:
                    # either CodeType or tuple, list[] append at it as is
                    if (isinstance(cmds, types.CodeType)
                            or isinstance(cmds, int)):
                        add(cmds, None)
                    else:
                        add(cmds, (i, j))
                    continue

                skip = False
                expand = None
                globCNC.motionStart(cmds)

                # FIXME append feed on cut commands. It will be obsolete
                # in grbl v1.0
                if globCNC.appendFeed and globCNC.gcode in (1, 2, 3):
                    # Check is not existing in cmds
                    for c in cmds:
                        if c[0] in ("f", "F"):
                            break
                    else:
                        cmds.append(
                            self.fmt("F", globCNC.feed / globCNC.unit))

                if (autolevel and globCNC.gcode in (0, 1, 2, 3)
                        and globCNC.mval == 0):
                    xyz = globCNC.motionPath()
                    if not xyz:
                        # while auto-levelling, do not ignore non-movement
                        # commands, just append the line as-is
                        add(line, None)
                    else:
                        extra = ""
                        for c in cmds:
                            if c[0].upper() not in (
                                "G",
                                "X",
                                "Y",
                                "Z",
                                "I",
                                "J",
                                "K",
                                "R",
                            ):
                                extra += c
                        x1, y1, z1 = xyz[0]
                        if globCNC.gcode == 0:
                            g = 0
                        else:
                            g = 1
                        for x2, y2, z2 in xyz[1:]:
                            for x, y, z in self.probe.splitLine(x1, y1, z1,
                                                                x2, y2, z2):
                                add(
                                    "".join([
                                        f"G{int(g)}",
                                        f"{self.fmt('X', x / globCNC.unit)}",
                                        f"{self.fmt('Y', y / globCNC.unit)}",
                                        f"{self.fmt('Z', z / globCNC.unit)}",
                                        f"{extra}",
                                    ]),
                                    (i, j),
                                )
                                extra = ""
                            x1, y1, z1 = x2, y2, z2
                    globCNC.motionEnd()
                    continue
                else:
                    # FIXME expansion policy here variable needed
                    # Canned cycles
                    if globCNC.drillPolicy == 1 and globCNC.gcode in (
                        81,
                        82,
                        83,
                        85,
                        86,
                        89,
                    ):
                        expand = globCNC.macroGroupG8X()
                    # Tool change
                    elif globCNC.mval == 6:
                        if globCNC.toolPolicy == 0:
                            pass  # send to grbl
                        elif globCNC.toolPolicy == 1:
                            skip = True  # skip whole line
                        elif globCNC.toolPolicy >= 2:
                            expand = globCNC.compile(globCNC.toolChange())
                    globCNC.motionEnd()

                if expand is not None:
                    for line in expand:
                        add(line, None)
                    expand = None
                    continue
                elif skip:
                    skip = False
                    continue

                for cmd in cmds:
                    c = cmd[0]
                    try:
                        value = float(cmd[1:])
                    except Exception:
                        value = 0.0
                    if c.upper() in ("F", "X", "Y", "Z",
                                     "I", "J", "K", "R", "P"):
                        cmd = self.fmt(c, value)
                    else:
                        opt = ERROR_HANDLING.get(cmd.upper(), 0)
                        if opt == SKIP:
                            cmd = None
                    if cmd is not None:
                        newcmd.append(cmd)

                add("".join(newcmd), (i, j))

        return paths


globGCode = GCode()
