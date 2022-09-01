# $Id: CNC.py,v 1.8 2014/10/15 15:03:49 bnv Exp $
#
# Author: vvlachoudis@gmail.com
# Date: 24-Aug-2014

import math
import os
import re

import Unicode
from bmath import (
    solveOverDetermined,
    sqrt,
    atan2,
    cos,
    sin,
    Matrix,
)
from bstl import Binary_STL_Writer
from Helpers import to_zip
from globalConfig import config as gconfig

IDPAT = re.compile(r".*\bid:\s*(.*?)\)")
PARENPAT = re.compile(r"(\(.*?\))")
SEMIPAT = re.compile(r"(;.*)")
OPPAT = re.compile(r"(.*)\[(.*)\]")
CMDPAT = re.compile(r"([A-Za-z]+)")
BLOCKPAT = re.compile(r"^\(Block-([A-Za-z]+):\s*(.*)\)")
AUXPAT = re.compile(r"^(%[A-Za-z0-9]+)\b *(.*)$")

STOP = 0
SKIP = 1
ASK = 2
MSG = 3
WAIT = 4
UPDATE = 5

XY = 0
XZ = 1
YZ = 2

CW = 2
CCW = 3

WCS = ["G54", "G55", "G56", "G57", "G58", "G59"]

DISTANCE_MODE = {"G90": "Absolute", "G91": "Incremental"}
FEED_MODE = {"G93": "1/Time", "G94": "unit/min", "G95": "unit/rev"}
UNITS = {"G20": "inch", "G21": "mm"}
PLANE = {"G17": "XY", "G18": "XZ", "G19": "YZ"}

# Modal Mode from $G and variable set
MODAL_MODES = {
    "G0": "motion",
    "G1": "motion",
    "G2": "motion",
    "G3": "motion",
    "G38.2": "motion",
    "G38.3": "motion",
    "G38.4": "motion",
    "G38.5": "motion",
    "G80": "motion",
    "G54": "WCS",
    "G55": "WCS",
    "G56": "WCS",
    "G57": "WCS",
    "G58": "WCS",
    "G59": "WCS",
    "G17": "plane",
    "G18": "plane",
    "G19": "plane",
    "G90": "distance",
    "G91": "distance",
    "G91.1": "arc",
    "G93": "feedmode",
    "G94": "feedmode",
    "G95": "feedmode",
    "G20": "units",
    "G21": "units",
    "G40": "cutter",
    "G43.1": "tlo",
    "G49": "tlo",
    "M0": "program",
    "M1": "program",
    "M2": "program",
    "M30": "program",
    "M3": "spindle",
    "M4": "spindle",
    "M5": "spindle",
    "M7": "coolant",
    "M8": "coolant",
    "M9": "coolant",
}

ERROR_HANDLING = {}
TOLERANCE = 1e-7
MAXINT = 1000000000  # python3 doesn't have maxint


# -----------------------------------------------------------------------------
# Return a value combined from two dictionaries new/old
# -----------------------------------------------------------------------------
def getValue(name, new, old, default=0.0):
    try:
        return new[name]
    except Exception:
        try:
            return old[name]
        except Exception:
            return default


# =============================================================================
# Probing class and linear interpolation
# =============================================================================
class Probe:
    def __init__(self):
        self.init()

    # ----------------------------------------------------------------------
    def init(self):
        self.filename = ""
        self.xmin = 0.0
        self.ymin = 0.0
        self.zmin = -10.0

        self.xmax = 10.0
        self.ymax = 10.0
        self.zmax = 3.0

        self._xstep = 1.0
        self._ystep = 1.0

        self.xn = 5
        self.yn = 5

        self.points = []  # probe points
        self.matrix = []  # 2D matrix with Z coordinates
        self.zeroed = False  # if probe was zeroed at any location
        self.start = False  # start collecting probes
        self.saved = False

    # ----------------------------------------------------------------------
    def clear(self):
        del self.points[:]
        del self.matrix[:]
        self.zeroed = False
        self.start = False
        self.saved = False

    # ----------------------------------------------------------------------
    def isEmpty(self):
        return len(self.matrix) == 0

    # ----------------------------------------------------------------------
    def makeMatrix(self):
        del self.matrix[:]
        for j in range(self.yn):
            self.matrix.append([0.0] * (self.xn))

    # ----------------------------------------------------------------------
    # Load autolevel information from file
    # ----------------------------------------------------------------------
    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        self.clear()
        self.saved = True

        def read(f):
            while True:
                line = f.readline()
                assert line, "Read an empty line, please check file IO settings"
                line = line.strip()
                if line:
                    return map(float, line.split())

        f = open(self.filename)
        self.xmin, self.xmax, self.xn = read(f)
        self.ymin, self.ymax, self.yn = read(f)
        self.zmin, self.zmax, feed = read(f)
        self.vars["prbfeed"] = feed

        self.xn = max(2, int(self.xn))
        self.yn = max(2, int(self.yn))

        self.makeMatrix()
        self.xstep()
        self.ystep()

        self.start = True
        try:
            for j in range(self.yn):
                for i in range(self.xn):
                    self.add(*read(f))
        except Exception:
            raise
        f.close()

    # ----------------------------------------------------------------------
    # Save level information to file
    # ----------------------------------------------------------------------
    def save(self, filename=None):
        if filename is None:
            filename = self.filename

        fn, ext = os.path.splitext(filename)
        ext = ext.lower()

        f = open(filename, "w")
        if ext != ".xyz":
            self.filename = filename
            f.write(f"{self.xmin:g} {self.xmax:g} {int(self.xn)}\n")
            f.write(f"{self.ymin:g} {self.ymax:g} {int(self.yn)}\n")
            f.write(f"{self.zmin:g} {self.zmax:g} {self.vars['prbfeed']:g}\n")
            f.write("\n\n")
        for j in range(self.yn):
            y = self.ymin + self._ystep * j
            for i in range(self.xn):
                x = self.xmin + self._xstep * i
                f.write(f"{x:g} {y:g} {self.matrix[j][i]:g}\n")
            f.write("\n")
        f.close()
        self.saved = True

    # ----------------------------------------------------------------------
    # Save level information as STL file
    # ----------------------------------------------------------------------
    def saveAsSTL(self, filename=None):
        if filename is not None:
            self.filename = filename

        with open(self.filename, "wb") as fp:
            writer = Binary_STL_Writer(fp)
            for j in range(self.yn - 1):
                y1 = self.ymin + self._ystep * j
                y2 = self.ymin + self._ystep * (j + 1)
                for i in range(self.xn - 1):
                    x1 = self.xmin + self._xstep * i
                    x2 = self.xmin + self._xstep * (i + 1)
                    v1 = [x1, y1, self.matrix[j][i]]
                    v2 = [x2, y1, self.matrix[j][i + 1]]
                    v3 = [x2, y2, self.matrix[j + 1][i + 1]]
                    v4 = [x1, y2, self.matrix[j + 1][i]]
                    writer.add_face([v1, v2, v3, v4])
            writer.close()

    # ----------------------------------------------------------------------
    # Return step
    # ----------------------------------------------------------------------
    def xstep(self):
        self._xstep = (self.xmax - self.xmin) / float(self.xn - 1)
        return self._xstep

    # ----------------------------------------------------------------------
    def ystep(self):
        self._ystep = (self.ymax - self.ymin) / float(self.yn - 1)
        return self._ystep

    # ----------------------------------------------------------------------
    # Return the code needed to scan margins for autoleveling
    # ----------------------------------------------------------------------
    def scanMargins(self):
        lines = []
        lines.append(f"G0 X{self.xmin:.4f} Y{self.ymin:.4f}")
        lines.append(f"G0 X{self.xmin:.4f} Y{self.ymax:.4f}")
        lines.append(f"G0 X{self.xmax:.4f} Y{self.ymax:.4f}")
        lines.append(f"G0 X{self.xmax:.4f} Y{self.ymin:.4f}")
        lines.append(f"G0 X{self.xmin:.4f} Y{self.ymin:.4f}")
        return lines

    # ----------------------------------------------------------------------
    # Return the code needed to scan for autoleveling
    # ----------------------------------------------------------------------
    def scan(self):
        self.clear()
        self.start = True
        self.makeMatrix()
        x = self.xmin
        xstep = self._xstep
        lines = [
            f"G0Z{self.vars['safe']:.4f}",
            f"G0X{self.xmin:.4f}Y{self.ymin:.4f}",
        ]
        for j in range(self.yn):
            y = self.ymin + self._ystep * j
            for i in range(self.xn):
                lines.append(f"G0Z{self.zmax:.4f}")
                lines.append(f"G0X{x:.4f}Y{y:.4f}")
                lines.append("%wait")  # added for smoothie
                lines.append(
                    f"{self.vars['prbcmd']}Z{self.zmin:.4f}"
                    f"F{self.vars['prbfeed']:g}"
                )
                lines.append("%wait")  # added for smoothie
                x += xstep
            x -= xstep
            xstep = -xstep
        lines.append(f"G0Z{self.zmax:.4f}")
        lines.append(f"G0X{self.xmin:.4f}Y{self.ymin:.4f}")
        return lines

    # ----------------------------------------------------------------------
    # Add a probed point to the list and the 3D matrix
    # ----------------------------------------------------------------------
    def add(self, x, y, z):
        if not self.start:
            return
        i = round((x - self.xmin) / self._xstep)
        if i < 0.0 or i > self.xn:
            return

        j = round((y - self.ymin) / self._ystep)
        if j < 0.0 or j > self.yn:
            return

        rem = abs(x - (i * self._xstep + self.xmin))
        if rem > self._xstep / 10.0:
            return

        rem = abs(y - (j * self._ystep + self.ymin))
        if rem > self._ystep / 10.0:
            return

        try:
            self.matrix[int(j)][int(i)] = z
            self.points.append([x, y, z])
        except IndexError:
            pass

        if len(self.points) >= self.xn * self.yn:
            self.start = False

    # ----------------------------------------------------------------------
    # Make z-level relative to the location of (x,y,0)
    # ----------------------------------------------------------------------
    def setZero(self, x, y):
        del self.points[:]
        if self.isEmpty():
            self.zeroed = False
            return
        zero = self.interpolate(x, y)
        self.xstep()
        self.ystep()
        for j, row in enumerate(self.matrix):
            y = self.ymin + self._ystep * j
            for i in range(len(row)):
                x = self.xmin + self._xstep * i
                row[i] -= zero
                self.points.append([x, y, row[i]])
        self.zeroed = True

    # ----------------------------------------------------------------------
    def interpolate(self, x, y):
        ix = (x - self.xmin) / self._xstep
        jy = (y - self.ymin) / self._ystep
        i = int(math.floor(ix))
        j = int(math.floor(jy))

        if i < 0:
            i = 0
        elif i >= self.xn - 1:
            i = self.xn - 2

        if j < 0:
            j = 0
        elif j >= self.yn - 1:
            j = self.yn - 2

        a = ix - i
        b = jy - j
        a1 = 1.0 - a
        b1 = 1.0 - b

        return (
            a1 * b1 * self.matrix[j][i]
            + a1 * b * self.matrix[j + 1][i]
            + a * b1 * self.matrix[j][i + 1]
            + a * b * self.matrix[j + 1][i + 1]
        )

    # ----------------------------------------------------------------------
    # Split line into multiple segments correcting for Z if needed
    # return only end points
    # ----------------------------------------------------------------------
    def splitLine(self, x1, y1, z1, x2, y2, z2):
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        if abs(dx) < 1e-10:
            dx = 0.0
        if abs(dy) < 1e-10:
            dy = 0.0
        if abs(dz) < 1e-10:
            dz = 0.0

        if dx == 0.0 and dy == 0.0:
            return [(x2, y2, z2 + self.interpolate(x2, y2))]

        # Length along projection on X-Y plane
        rxy = math.sqrt(dx * dx + dy * dy)
        dx /= rxy  # direction cosines along XY plane
        dy /= rxy
        dz /= rxy  # add correction for the slope in Z, versus the travel in XY

        i = int(math.floor((x1 - self.xmin) / self._xstep))
        j = int(math.floor((y1 - self.ymin) / self._ystep))
        if dx > 1e-10:
            tx = (
                float(i + 1) * self._xstep + self.xmin - x1
            ) / dx  # distance to next cell
            tdx = self._xstep / dx
        elif dx < -1e-10:
            # distance to next cell
            tx = (float(i) * self._xstep + self.xmin - x1) / dx
            tdx = -self._xstep / dx
        else:
            tx = 1e10
            tdx = 0.0

        if dy > 1e-10:
            ty = (
                float(j + 1) * self._ystep + self.ymin - y1
            ) / dy  # distance to next cell
            tdy = self._ystep / dy
        elif dy < -1e-10:
            # distance to next cell
            ty = (float(j) * self._ystep + self.ymin - y1) / dy
            tdy = -self._ystep / dy
        else:
            ty = 1e10
            tdy = 0.0

        segments = []
        rxy *= 0.999999999  # just reduce a bit to avoid precision errors
        while tx < rxy or ty < rxy:
            if tx == ty:
                t = tx
                tx += tdx
                ty += tdy
            elif tx < ty:
                t = tx
                tx += tdx
            else:
                t = ty
                ty += tdy
            x = x1 + t * dx
            y = y1 + t * dy
            z = z1 + t * dz
            segments.append((x, y, z + self.interpolate(x, y)))

        segments.append((x2, y2, z2 + self.interpolate(x2, y2)))
        return segments


# =============================================================================
# contains a list of machine points vs position in the gcode
# calculates the transformation matrix (rotation + translation) needed
# to adjust the gcode to match the workpiece on the machine
# =============================================================================
class Orient:
    # -----------------------------------------------------------------------
    def __init__(self):
        self.markers = []  # list of points pairs (xm, ym, x, y)
        self.paths = []
        self.errors = []
        self.filename = ""
        self.clear()

    # -----------------------------------------------------------------------
    def clear(self, item=None):
        if item is None:
            self.clearPaths()
            del self.markers[:]
        else:
            del self.paths[item]
            del self.markers[item]

        self.phi = 0.0
        self.xo = 0.0
        self.yo = 0.0
        self.valid = False
        self.saved = False

    # -----------------------------------------------------------------------
    def clearPaths(self):
        del self.paths[:]

    # -----------------------------------------------------------------------
    def add(self, xm, ym, x, y):
        self.markers.append((xm, ym, x, y))
        self.valid = False
        self.saved = False

    # -----------------------------------------------------------------------
    def addPath(self, path):
        self.paths.append(path)

    # -----------------------------------------------------------------------
    def __getitem__(self, i):
        return self.markers[i]

    # -----------------------------------------------------------------------
    def __len__(self):
        return len(self.markers)

    # -----------------------------------------------------------------------
    # Return the rotation angle phi in radians and the offset (xo,yo)
    # or none on failure
    # Transformation equation is the following
    #
    #    Xm = R * X + T
    #
    #    Xm = [xm ym]^t
    #    X  = [x y]^t
    #
    #
    #       / cosf  -sinf \   / c  -s \
    #   R = |             | = |       |
    #       \ sinf   cosf /   \ s   c /
    #
    # Assuming that the machine is squared. We could even solve it for
    # a skewed machine, but then the arcs have to be converted to
    # ellipses...
    #
    #   T = [xo yo]^t
    #
    # The overdetermined system (equations) to solve are the following
    #      c*x + s*(-y) + xo      = xm
    #      s*x + c*y    + yo      = ym
    #  <=> c*y + s*y         + yo = ym
    #
    # We are solving for the unknowns c,s,xo,yo
    #
    #       /  x1  -y1  1 0 \ / c  \    / xm1 \
    #       |  y1   x1  0 1 | | s  |    | ym1 |
    #       |  x2  -y2  1 0 | | xo |    | xm2 |
    #       |  y2   x2  0 1 | \ yo /  = | ym2 |
    #          ...                   ..
    #       |  xn  -yn  1 0 |           | xmn |
    #       \  yn   xn  0 1 /           \ ymn /
    #
    #               A            X    =    B
    #
    # Constraints:
    #   1. orthogonal system   c^2 + s^2 = 1
    #   2. no aspect ratio
    #
    # -----------------------------------------------------------------------
    def solve(self):
        self.valid = False
        if len(self.markers) < 2:
            raise Exception("Too few markers")
        A = []
        B = []
        for xm, ym, x, y in self.markers:
            A.append([x, -y, 1.0, 0.0])
            B.append([xm])
            A.append([y, x, 0.0, 1.0])
            B.append([ym])

        # The solution of the overdetermined system A X = B
        try:
            c, s, self.xo, self.yo = solveOverDetermined(Matrix(A), Matrix(B))
        except Exception:
            raise Exception("Unable to solve system")

        # Normalize the coefficients
        r = sqrt(c * c + s * s)  # length should be 1.0
        if abs(r - 1.0) > 0.1:
            raise Exception("Resulting system is too skew")

        self.phi = atan2(s, c)

        if abs(self.phi) < TOLERANCE:
            self.phi = 0.0  # rotation

        self.valid = True
        return self.phi, self.xo, self.yo

    # -----------------------------------------------------------------------
    # @return minimum, average and maximum error
    # -----------------------------------------------------------------------
    def error(self):
        # Type errors
        minerr = 1e9
        maxerr = 0.0
        sumerr = 0.0

        c = cos(self.phi)
        s = sin(self.phi)

        del self.errors[:]

        for i, (xm, ym, x, y) in enumerate(self.markers):
            dx = c * x - s * y + self.xo - xm
            dy = s * x + c * y + self.yo - ym
            err = sqrt(dx**2 + dy**2)
            self.errors.append(err)

            minerr = min(minerr, err)
            maxerr = max(maxerr, err)
            sumerr += err

        return minerr, sumerr / float(len(self.markers)), maxerr

    # -----------------------------------------------------------------------
    # Convert gcode to machine coordinates
    # -----------------------------------------------------------------------
    def gcode2machine(self, x, y):
        c = cos(self.phi)
        s = sin(self.phi)
        return c * x - s * y + self.xo, s * x + c * y + self.yo

    # -----------------------------------------------------------------------
    # Convert machine to gcode coordinates
    # -----------------------------------------------------------------------
    def machine2gcode(self, x, y):
        c = cos(self.phi)
        s = sin(self.phi)
        x -= self.xo
        y -= self.yo
        return c * x + s * y, -s * x + c * y

    # ----------------------------------------------------------------------
    # Load orient information from file
    # ----------------------------------------------------------------------
    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        self.clear()
        self.saved = True

        f = open(self.filename)
        for line in f:
            self.add(*map(float, line.split()))
        f.close()

    # ----------------------------------------------------------------------
    # Save orient information to file
    # ----------------------------------------------------------------------
    def save(self, filename=None):
        if filename is not None:
            self.filename = filename
        f = open(self.filename, "w")
        for xm, ym, x, y in self.markers:
            f.write(f"{xm:g} {ym:g} {x:g} {y:g}\n")
        f.close()
        self.saved = True


# =============================================================================
# Command operations on a CNC
# =============================================================================
class CNC:
    inch = False
    lasercutter = False
    laseradaptive = False
    acceleration_x = 25.0  # mm/s^2
    acceleration_y = 25.0  # mm/s^2
    acceleration_z = 25.0  # mm/s^2
    feedmax_x = 3000
    feedmax_y = 3000
    feedmax_z = 2000
    travel_x = 300
    travel_y = 300
    travel_z = 60
    accuracy = 0.01  # sagitta error during arc conversion
    digits = 4
    startup = "G90"
    stdexpr = False  # standard way of defining expressions with []
    comment = ""  # last parsed comment
    developer = False
    drozeropad = 0
    vars = {
        "prbx": 0.0,
        "prby": 0.0,
        "prbz": 0.0,
        "prbcmd": "G38.2",
        "prbfeed": 10.0,
        "errline": "",
        "wx": 0.0,
        "wy": 0.0,
        "wz": 0.0,
        "wa": 0.0,
        "wb": 0.0,
        "wc": 0.0,
        "mx": 0.0,
        "my": 0.0,
        "mz": 0.0,
        "ma": 0.0,
        "mb": 0.0,
        "mc": 0.0,
        "wcox": 0.0,
        "wcoy": 0.0,
        "wcoz": 0.0,
        "wcoa": 0.0,
        "wcob": 0.0,
        "wcoc": 0.0,
        "curfeed": 0.0,
        "curspindle": 0.0,
        "_camwx": 0.0,
        "_camwy": 0.0,
        "G": [],
        "TLO": 0.0,
        "motion": "G0",
        "WCS": "G54",
        "plane": "G17",
        "feedmode": "G94",
        "distance": "G90",
        "arc": "G91.1",
        "units": "G20",
        "cutter": "",
        "tlo": "",
        "program": "M0",
        "spindle": "M5",
        "coolant": "M9",
        "tool": 0,
        "feed": 0.0,
        "rpm": 0.0,
        "planner": 0,
        "rxbytes": 0,
        "OvFeed": 100,  # Override status
        "OvRapid": 100,
        "OvSpindle": 100,
        "_OvChanged": False,
        "_OvFeed": 100,  # Override target values
        "_OvRapid": 100,
        "_OvSpindle": 100,
        "diameter": 3.175,  # Tool diameter
        "cutfeed": 1000.0,  # Material feed for cutting
        "cutfeedz": 500.0,  # Material feed for cutting
        "safe": 3.0,
        "state": "",
        "pins": "",
        "msg": "",
        "stepz": 1.0,
        "surface": 0.0,
        "thickness": 5.0,
        "stepover": 40.0,
        "PRB": None,
        "TLO": 0.0,
        "version": "",
        "controller": "",
        "running": False,
        # "enable6axisopt" : 0,
    }

    drillPolicy = 1  # Expand Canned cycles
    toolPolicy = 1  # Should be in sync with ProbePage
    # 0 - send to grbl
    # 1 - skip those lines
    # 2 - manual tool change (WCS)
    # 3 - manual tool change (TLO)
    # 4 - manual tool change (No Probe)

    toolWaitAfterProbe = True  # wait at tool change position after probing
    appendFeed = False  # append feed on every G1/G2/G3 commands to be used
    # for feed override testing
    # FIXME will not be needed after Grbl v1.0

    # ----------------------------------------------------------------------
    def __init__(self):
        self.initPath()
        self.resetAllMargins()

    # ----------------------------------------------------------------------
    # Update G variables from "G" string
    # ----------------------------------------------------------------------
    def updateG(self):
        for g in self.vars["G"]:
            if g[0] == "F":
                self.vars["feed"] = float(g[1:])
            elif g[0] == "S":
                self.vars["rpm"] = float(g[1:])
            elif g[0] == "T":
                self.vars["tool"] = int(g[1:])
            else:
                var = MODAL_MODES.get(g)
                if var is not None:
                    self.vars[var] = g

    # ----------------------------------------------------------------------
    def __getitem__(self, name):
        return self.vars[name]

    # ----------------------------------------------------------------------
    def __setitem__(self, name, value):
        self.vars[name] = value

    # ----------------------------------------------------------------------
    def loadConfig(self,):  # config):
        section = "CNC"
        self.inch = bool(int(gconfig.get(section, "units", fallback=False)))
        self.lasercutter = bool(int(
            gconfig.get(section, "lasercutter", fallback=False)))
        self.laseradaptive = bool(int(
            gconfig.get(section, "laseradaptive", fallback=False)))
        self.enable6axisopt = bool(int(
            gconfig.get(section, "enable6axisopt", fallback=False)))
        self.doublesizeicon = bool(int(
            gconfig.get(section, "doublesizeicon", fallback=False)))

        self.acceleration_x = float(
            gconfig.get(section, "acceleration_x", fallback="25.0"))
        self.acceleration_y = float(
            gconfig.get(section, "acceleration_y", fallback="25.0"))
        self.acceleration_z = float(
            gconfig.get(section, "acceleration_z", fallback="25.0"))
        self.feedmax_x = float(
            gconfig.get(section, "feedmax_x", fallback="3000.0"))
        self.feedmax_y = float(
            gconfig.get(section, "feedmax_y", fallback="3000.0"))
        self.feedmax_z = float(
            gconfig.get(section, "feedmax_z", fallback="2000.0"))
        self.travel_x = float(
            gconfig.get(section, "travel_x", fallback="300.0"))
        self.travel_y = float(
            gconfig.get(section, "travel_y", fallback="300.0"))
        self.travel_z = float(
            gconfig.get(section, "travel_z", fallback="60.0"))

        self.acceleration_a = float(
            gconfig.get(section, "acceleration_a", fallback="0.0"))
        self.acceleration_b = float(
            gconfig.get(section, "acceleration_b", fallback="0.0"))
        self.acceleration_c = float(
            gconfig.get(section, "acceleration_c", fallback="0.0"))
        self.feedmax_a = float(
            gconfig.get(section, "feedmax_a", fallback="0.0"))
        self.feedmax_b = float(
            gconfig.get(section, "feedmax_b", fallback="0.0"))
        self.feedmax_c = float(
            gconfig.get(section, "feedmax_c", fallback="0.0"))
        self.travel_a = float(
            gconfig.get(section, "travel_a", fallback="0.0"))
        self.travel_b = float(
            gconfig.get(section, "travel_b", fallback="0.0"))
        self.travel_c = float(
            gconfig.get(section, "travel_c", fallback="0.0"))
        self.accuracy = float(
            gconfig.get(section, "accuracy", fallback="0.001"))
        self.digits = int(
            gconfig.get(section, "round", fallback="4"))
        self.drozeropad = int(
            gconfig.get(section, "drozeropad", fallback="0"))

        self.startup = gconfig.get(section, "startup", fallback="G90")
        self.header = gconfig.get(section, "header", fallback=None)
        self.footer = gconfig.get(section, "footer", fallback=None)

        if self.inch:
            self.acceleration_x /= 25.4
            self.acceleration_y /= 25.4
            self.acceleration_z /= 25.4
            self.feedmax_x /= 25.4
            self.feedmax_y /= 25.4
            self.feedmax_z /= 25.4
            self.travel_x /= 25.4
            self.travel_y /= 25.4
            self.travel_z /= 25.4
            # a,b,c are in degrees no conversion required

        section = "Error"
        if self.drillPolicy == 1:
            ERROR_HANDLING["G98"] = 1
            ERROR_HANDLING["G99"] = 1

        for cmd, value in gconfig.items(section):
            try:
                ERROR_HANDLING[cmd.upper()] = int(value)
            except Exception:
                pass

    # ----------------------------------------------------------------------
    @staticmethod
    def saveConfig(config):
        pass

    # ----------------------------------------------------------------------
    def initPath(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if x is None:
            self.x = self.xval = self.vars["wx"] or 0
        else:
            self.x = self.xval = x
        if y is None:
            self.y = self.yval = self.vars["wy"] or 0
        else:
            self.y = self.yval = y
        if z is None:
            self.z = self.zval = self.vars["wz"] or 0
        else:
            self.z = self.zval = z
        if a is None:
            self.a = self.aval = self.vars["wa"] or 0
        else:
            self.a = self.aval = a
        if b is None:
            self.b = self.bval = self.vars["wb"] or 0
        else:
            self.b = self.bval = b
        if c is None:
            self.c = self.cval = self.vars["wc"] or 0
        else:
            self.c = self.cval = c

        self.ival = self.jval = self.kval = 0.0
        self.uval = self.vval = self.wval = 0.0
        self.dx = self.dy = self.dz = 0.0
        self.di = self.dj = self.dk = 0.0
        self.rval = 0.0
        self.pval = 0.0
        self.qval = 0.0
        self.unit = 1.0
        self.mval = 0
        self.lval = 1
        self.tool = 0
        self._lastTool = None

        self.absolute = True  # G90/G91     absolute/relative motion
        self.arcabsolute = False  # G90.1/G91.1 absolute/relative arc
        self.retractz = True  # G98/G99     retract to Z or R
        self.gcode = None
        self.plane = XY
        self.feed = 0  # Actual gcode feed rate (not to confuse with cutfeed
        self.totalLength = 0.0
        self.totalTime = 0.0

    # ----------------------------------------------------------------------
    def resetEnableMargins(self):
        # Selected blocks margin
        self.vars["xmin"] = self.vars["ymin"] = self.vars["zmin"] = 1000000.0
        self.vars["xmax"] = self.vars["ymax"] = self.vars["zmax"] = -1000000.0

    # ----------------------------------------------------------------------
    def resetAllMargins(self):
        self.resetEnableMargins()
        # All blocks margin
        self.vars["axmin"] = self.vars["aymin"] = self.vars["azmin"] = 1000000.0
        self.vars["axmax"] = self.vars["aymax"] = self.vars["azmax"] = -1000000.0

    # ----------------------------------------------------------------------
    def isMarginValid(self):
        return (
            self.vars["xmin"] <= self.vars["xmax"]
            and self.vars["ymin"] <= self.vars["ymax"]
            and self.vars["zmin"] <= self.vars["zmax"]
        )

    # ----------------------------------------------------------------------
    def isAllMarginValid(self):
        return (
            self.vars["axmin"] <= self.vars["axmax"]
            and self.vars["aymin"] <= self.vars["aymax"]
            and self.vars["azmin"] <= self.vars["azmax"]
        )

    # ----------------------------------------------------------------------
    # Number formating
    # ----------------------------------------------------------------------
    def fmt(self, c, v, d=None):
        if d is None:
            d = self.digits
        # Don't know why, but in some cases floats are not truncated by
        # format string unless rounded
        # I guess it's vital idea to round them rather than truncate anyway!
        v = round(v, d)
        return (f"{c}{v:>{d}f}").rstrip("0").rstrip(".")

    # ----------------------------------------------------------------------
    # FIXME: self.gcode() is shadowed by self.gcode variable
    # TODO: Move functions to module level, rather then leaf in class
    def gcode_generate(self, g, pairs):
        s = "g{} {}".format(
            g,
            ' '.join([f"{c[0]}{round(v, self.digits):g}" for c, v in pairs])
        )
        return s

    # ----------------------------------------------------------------------
    def _gcode(self, g, **args):
        s = f"g{int(g)} {' '.join([self.fmt(n, v) for n, v in args.items()])}"
        return s

    # ----------------------------------------------------------------------
    def _gotoABC(self, g, x=None, y=None, z=None, a=None, b=None, c=None, **args):
        s = f"g{int(g)}"
        if x is not None:
            s += " " + self.fmt("x", x)
        if y is not None:
            s += " " + self.fmt("y", y)
        if z is not None:
            s += " " + self.fmt("z", z)
        if a is not None:
            s += " " + self.fmt("a", a)
        if b is not None:
            s += " " + self.fmt("b", b)
        if c is not None:
            s += " " + self.fmt("c", c)
        for n, v in args.items():
            s += " " + self.fmt(n, v)
        return s

    def _goto(self, g, x=None, y=None, z=None, **args):
        s = f"g{int(g)}"
        if x is not None:
            s += " " + self.fmt("x", x)
        if y is not None:
            s += " " + self.fmt("y", y)
        if z is not None:
            s += " " + self.fmt("z", z)
        for n, v in args.items():
            s += " " + self.fmt(n, v)
        return s

    # ----------------------------------------------------------------------
    def grapidABC(self, x=None, y=None, z=None, a=None, b=None, c=None, **args):
        return self._gotoABC(0, x, y, z, a, b, c, **args)

    def grapid(self, x=None, y=None, z=None, **args):
        return self._goto(0, x, y, z, **args)

    # ----------------------------------------------------------------------
    def glineABC(self, x=None, y=None, z=None, a=None, b=None, c=None, **args):
        return self._gotoABC(1, x, y, z, a, b, c, **args)

    def gline(self, x=None, y=None, z=None, **args):
        return self._goto(1, x, y, z, **args)

    # ----------------------------------------------------------------------
    def glinev(self, g, v, feed=None):
        pairs = to_zip("xyz", v)
        if feed is not None:
            pairs.append(("f", feed))
        # FIXME: self.gcode() is shadowed by self.gcode variable
        return self.gcode_generate(g, pairs)

    # ----------------------------------------------------------------------
    def garcv(self, g, v, ijk):
        # FIXME: self.gcode() is shadowed by self.gcode variable
        return self.gcode_generate(g, to_zip("xyz", v) + to_zip("ij", ijk[:2]))

    # ----------------------------------------------------------------------
    def garc(self, g, x=None, y=None, z=None, i=None, j=None, k=None, **args):
        s = f"g{int(g)}"
        if x is not None:
            s += " " + self.fmt("x", x)
        if y is not None:
            s += " " + self.fmt("y", y)
        if z is not None:
            s += " " + self.fmt("z", z)
        if i is not None:
            s += " " + self.fmt("i", i)
        if j is not None:
            s += " " + self.fmt("j", j)
        if k is not None:
            s += " " + self.fmt("k", k)
        for n, v in args.items():
            s += " " + self.fmt(n, v)
        return s

    # ----------------------------------------------------------------------
    # Enter to material or start the laser
    # ----------------------------------------------------------------------
    def zenter(self, z, d=None):
        if self.lasercutter:
            if self.laseradaptive:
                return "m4"
            else:
                return "m3"
        else:
            return (f"g1 {self.fmt('z', z, d)} "
                    f"{self.fmt('f', self.vars['cutfeedz'])}")

    # ----------------------------------------------------------------------
    def zexit(self, z, d=None):
        if self.lasercutter:
            return "m5"
        else:
            return f"g0 {self.fmt('z', z, d)}"

    # ----------------------------------------------------------------------
    # gcode to go to z-safe
    # Exit from material or stop the laser
    # ----------------------------------------------------------------------
    def zsafe(self):
        return self.zexit(self.vars["safe"])

    # ----------------------------------------------------------------------
    # @return line in broken a list of commands, None if empty or comment
    # ----------------------------------------------------------------------
    @staticmethod
    def parseLine(line):
        # skip empty lines
        if len(line) == 0 or line[0] in ("%", "(", "#", ";"):
            return None

        # remove comments
        line = PARENPAT.sub("", line)
        line = SEMIPAT.sub("", line)

        # process command
        # strip all spaces
        line = line.replace(" ", "")

        # Insert space before each command
        line = CMDPAT.sub(r" \1", line).lstrip()
        return line.split()

    # ----------------------------------------------------------------------
    # @return line,comment
    #   line broken in a list of commands,
    #       None,"" if empty or comment
    #       else compiled expressions,""
    # ----------------------------------------------------------------------
    def compileLine(self, line, space=False):
        line = line.strip()
        if not line:
            return None
        if line[0] == "$":
            return line

        # to accept #nnn variables as _nnn internally
        line = line.replace("#", "_")
        self.comment = ""

        # execute literally the line after the first character
        if line[0] == "%":
            # special command
            pat = AUXPAT.match(line.strip())
            if pat:
                cmd = pat.group(1)
                args = pat.group(2)
            else:
                cmd = None
                args = None
            if cmd == "%wait":
                return (WAIT,)
            elif cmd == "%msg":
                if not args:
                    args = None
                return (MSG, args)
            elif cmd == "%update":
                return (UPDATE, args)
            elif line.startswith("%if running") and not self.vars["running"]:
                # ignore if running lines when not running
                return None
            else:
                try:
                    return compile(line[1:], "", "exec")
                except Exception as e:
                    print("Compile line error: \n")
                    print(e)
                    return None

        # most probably an assignment like  #nnn = expr
        if line[0] == "_":
            try:
                return compile(line, "", "exec")
            except Exception:
                # FIXME show the error!!!!
                return None

        # commented line
        if line[0] == ";":
            self.comment = line[1:].strip()
            return None

        out = []  # output list of commands
        braket = 0  # bracket count []
        paren = 0  # parenthesis count ()
        expr = ""  # expression string
        cmd = ""  # cmd string
        inComment = False  # inside inComment
        for i, ch in enumerate(line):
            if ch == "(":
                # comment start?
                paren += 1
                inComment = braket == 0
                if not inComment:
                    expr += ch
            elif ch == ")":
                # comment end?
                paren -= 1
                if not inComment:
                    expr += ch
                if paren == 0 and inComment:
                    inComment = False
            elif ch == "[":
                # expression start?
                if not inComment:
                    if self.stdexpr:
                        ch = "("
                    braket += 1
                    if braket == 1:
                        if cmd:
                            out.append(cmd)
                            cmd = ""
                    else:
                        expr += ch
                else:
                    self.comment += ch
            elif ch == "]":
                # expression end?
                if not inComment:
                    if self.stdexpr:
                        ch = ")"
                    braket -= 1
                    if braket == 0:
                        try:
                            out.append(compile(expr, "", "eval"))
                        except Exception:
                            # FIXME show the error!!!!
                            pass
                        expr = ""
                    else:
                        expr += ch
                else:
                    self.comment += ch
            elif ch == "=":
                # check for assignments (FIXME very bad)
                if not out and braket == 0 and paren == 0:
                    for i in " ()-+*/^$":
                        if i in cmd:
                            cmd += ch
                            break
                    else:
                        try:
                            return compile(line, "", "exec")
                        except Exception:
                            # FIXME show the error!!!!
                            return None
            elif ch == ";":
                # Skip everything after the semicolon on normal lines
                if not inComment and paren == 0 and braket == 0:
                    self.comment += line[i + 1:]
                    break
                else:
                    expr += ch

            elif braket > 0:
                expr += ch

            elif not inComment:
                if ch == " ":
                    if space:
                        cmd += ch
                else:
                    cmd += ch

            elif inComment:
                self.comment += ch

        if cmd:
            out.append(cmd)

        # return output commands
        if len(out) == 0:
            return None
        if len(out) > 1:
            return out
        return out[0]

    # ----------------------------------------------------------------------
    # Break line into commands
    # ----------------------------------------------------------------------
    @staticmethod
    def breakLine(line):
        if line is None:
            return None
        # Insert space before each command
        line = CMDPAT.sub(r" \1", line).lstrip()
        return line.split()

    # ----------------------------------------------------------------------
    # Create path for one g command
    # ----------------------------------------------------------------------
    def motionStart(self, cmds):
        self.mval = 0  # reset m command
        for cmd in cmds:
            c = cmd[0].upper()
            try:
                value = float(cmd[1:])
            except Exception:
                value = 0

            if c == "X":
                self.xval = value * self.unit
                if not self.absolute:
                    self.xval += self.x
                self.dx = self.xval - self.x

            elif c == "Y":
                self.yval = value * self.unit
                if not self.absolute:
                    self.yval += self.y
                self.dy = self.yval - self.y

            elif c == "Z":
                self.zval = value * self.unit
                if not self.absolute:
                    self.zval += self.z
                self.dz = self.zval - self.z

            elif c == "A":
                self.aval = value * self.unit

            elif c == "F":
                self.feed = value * self.unit

            elif c == "G":
                gcode = int(value)
                decimal = int(round((value - gcode) * 10))

                # Execute immediately
                if gcode in (4, 10, 53):
                    pass  # do nothing but don't record to motion
                elif gcode == 17:
                    self.plane = XY

                elif gcode == 18:
                    self.plane = XZ

                elif gcode == 19:
                    self.plane = YZ

                elif gcode == 20:  # Switch to inches
                    if self.inch:
                        self.unit = 1.0
                    else:
                        self.unit = 25.4

                elif gcode == 21:  # Switch to mm
                    if self.inch:
                        self.unit = 1.0 / 25.4
                    else:
                        self.unit = 1.0

                elif gcode == 80:
                    # turn off canned cycles
                    self.gcode = None
                    self.dz = 0
                    self.zval = self.z

                elif gcode == 90:
                    if decimal == 0:
                        self.absolute = True
                    elif decimal == 1:
                        self.arcabsolute = True

                elif gcode == 91:
                    if decimal == 0:
                        self.absolute = False
                    elif decimal == 1:
                        self.arcabsolute = False

                elif gcode in (93, 94, 95):
                    self.vars["feedmode"] = gcode

                elif gcode == 98:
                    self.retractz = True

                elif gcode == 99:
                    self.retractz = False

                else:
                    self.gcode = gcode

            elif c == "I":
                self.ival = value * self.unit
                if self.arcabsolute:
                    self.ival -= self.x

            elif c == "J":
                self.jval = value * self.unit
                if self.arcabsolute:
                    self.jval -= self.y

            elif c == "K":
                self.kval = value * self.unit
                if self.arcabsolute:
                    self.kval -= self.z

            elif c == "L":
                self.lval = int(value)

            elif c == "M":
                self.mval = int(value)

            elif c == "N":
                pass

            elif c == "P":
                self.pval = value

            elif c == "Q":
                self.qval = value * self.unit

            elif c == "R":
                self.rval = value * self.unit

            elif c == "T":
                self.tool = int(value)

            elif c == "U":
                self.uval = value * self.unit

            elif c == "V":
                self.vval = value * self.unit

            elif c == "W":
                self.wval = value * self.unit

    # ----------------------------------------------------------------------
    # Return center x,y,z,r for arc motions 2,3 and set self.rval
    # ----------------------------------------------------------------------
    def motionCenter(self):
        if self.rval > 0.0:
            if self.plane == XY:
                x = self.x
                y = self.y
                xv = self.xval
                yv = self.yval
            elif self.plane == XZ:
                x = self.x
                y = self.z
                xv = self.xval
                yv = self.zval
            else:
                x = self.y
                y = self.z
                xv = self.yval
                yv = self.zval

            ABx = xv - x
            ABy = yv - y
            Cx = 0.5 * (x + xv)
            Cy = 0.5 * (y + yv)
            AB = math.sqrt(ABx**2 + ABy**2)
            try:
                OC = math.sqrt(self.rval**2 - AB**2 / 4.0)
            except Exception:
                OC = 0.0
            if self.gcode == 2:
                OC = -OC  # CW
            if AB != 0.0:
                return Cx - OC * ABy / AB, Cy + OC * ABx / AB
            else:
                # Error!!!
                return x, y
        else:
            # Center
            xc = self.x + self.ival
            yc = self.y + self.jval
            zc = self.z + self.kval
            self.rval = math.sqrt(self.ival**2 + self.jval**2 + self.kval**2)

            if self.plane == XY:
                return xc, yc
            elif self.plane == XZ:
                return xc, zc
            else:
                return yc, zc

    # ----------------------------------------------------------------------
    # Create path for one g command
    # ----------------------------------------------------------------------
    def motionPath(self):
        xyz = []

        # Execute g-code
        if self.gcode in (0, 1):  # fast move or line
            if (
                self.xval - self.x != 0.0
                or self.yval - self.y != 0.0
                or self.zval - self.z != 0.0
            ):
                xyz.append((self.x, self.y, self.z))
                xyz.append((self.xval, self.yval, self.zval))

        elif self.gcode in (2, 3):  # CW=2,CCW=3 circle
            xyz.append((self.x, self.y, self.z))
            uc, vc = self.motionCenter()

            gcode = self.gcode
            if self.plane == XY:
                u0 = self.x
                v0 = self.y
                w0 = self.z
                u1 = self.xval
                v1 = self.yval
                w1 = self.zval
            elif self.plane == XZ:
                u0 = self.x
                v0 = self.z
                w0 = self.y
                u1 = self.xval
                v1 = self.zval
                w1 = self.yval
                gcode = 5 - gcode  # flip 2-3 when XZ plane is used
            else:
                u0 = self.y
                v0 = self.z
                w0 = self.x
                u1 = self.yval
                v1 = self.zval
                w1 = self.xval
            phi0 = math.atan2(v0 - vc, u0 - uc)
            phi1 = math.atan2(v1 - vc, u1 - uc)
            try:
                sagitta = 1.0 - self.accuracy / self.rval
            except ZeroDivisionError:
                sagitta = 0.0
            if sagitta > 0.0:
                df = 2.0 * math.acos(sagitta)
                df = min(df, math.pi / 4.0)
            else:
                df = math.pi / 4.0

            if gcode == 2:
                if phi1 >= phi0 - 1e-10:
                    phi1 -= 2.0 * math.pi
                ws = (w1 - w0) / (phi1 - phi0)
                phi = phi0 - df
                while phi > phi1:
                    u = uc + self.rval * math.cos(phi)
                    v = vc + self.rval * math.sin(phi)
                    w = w0 + (phi - phi0) * ws
                    phi -= df
                    if self.plane == XY:
                        xyz.append((u, v, w))
                    elif self.plane == XZ:
                        xyz.append((u, w, v))
                    else:
                        xyz.append((w, u, v))
            else:
                if phi1 <= phi0 + 1e-10:
                    phi1 += 2.0 * math.pi
                ws = (w1 - w0) / (phi1 - phi0)
                phi = phi0 + df
                while phi < phi1:
                    u = uc + self.rval * math.cos(phi)
                    v = vc + self.rval * math.sin(phi)
                    w = w0 + (phi - phi0) * ws
                    phi += df
                    if self.plane == XY:
                        xyz.append((u, v, w))
                    elif self.plane == XZ:
                        xyz.append((u, w, v))
                    else:
                        xyz.append((w, u, v))

            xyz.append((self.xval, self.yval, self.zval))

        elif self.gcode == 4:  # Dwell
            self.totalTime = self.pval

        elif self.gcode in (81, 82, 83, 85, 86, 89):  # Canned cycles
            # FIXME Assuming only on plane XY
            if self.absolute:
                # FIXME is it correct?
                self.lval = 1
                if self.retractz:
                    clearz = max(self.rval, self.z)
                else:
                    clearz = self.rval
                drill = self.zval
            else:
                clearz = self.z + self.rval
                drill = clearz + self.dz

            x, y, z = self.x, self.y, self.z
            xyz.append((x, y, z))
            if z != clearz:
                z = clearz
                xyz.append((x, y, z))
            for _line in range(self.lval):
                # Rapid move parallel to XY
                x += self.dx
                y += self.dy
                xyz.append((x, y, z))

                # Rapid move parallel to clearz
                if self.z > clearz:
                    xyz.append((x, y, clearz))

                # Drill to z
                xyz.append((x, y, drill))

                # Move to original position
                z = clearz
                xyz.append((x, y, z))  # ???

        return xyz

    # ----------------------------------------------------------------------
    # move to end position
    # ----------------------------------------------------------------------
    def motionEnd(self):
        if self.gcode in (0, 1, 2, 3):
            self.x = self.xval
            self.y = self.yval
            self.z = self.zval
            self.dx = 0
            self.dy = 0
            self.dz = 0

            if self.gcode >= 2:  # reset at the end
                self.rval = self.ival = self.jval = self.kval = 0.0

        elif self.gcode in (28, 30, 92):
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.dx = 0
            self.dy = 0
            self.dz = 0

        # FIXME L is not taken into account for repetitions!!!
        elif self.gcode in (81, 82, 83):
            # FIXME Assuming only on plane XY
            if self.absolute:
                self.lval = 1
                if self.retractz:
                    retract = max(self.rval, self.z)
                else:
                    retract = self.rval
                drill = self.zval
            else:
                retract = self.z + self.rval
                drill = retract + self.dz

            self.x += self.dx * self.lval
            self.y += self.dy * self.lval
            self.z = retract

            self.xval = self.x
            self.yval = self.y
            self.dx = 0
            self.dy = 0
            self.dz = drill - retract

    # ----------------------------------------------------------------------
    # Doesn't work correctly for G83 (peck drilling)
    # ----------------------------------------------------------------------
    def pathLength(self, block, xyz):
        # For XY plane
        p = xyz[0]
        length = 0.0
        for i in xyz:
            length += math.sqrt(
                (i[0] - p[0]) ** 2 + (i[1] - p[1]) ** 2 + (i[2] - p[2]) ** 2
            )
            p = i

        if self.gcode == 0:
            # FIXME calculate the correct time with the feed direction
            # and acceleration
            block.time += length / self.feedmax_x
            self.totalTime += length / self.feedmax_x
            block.rapid += length
        elif ((self.gcode == 1 or self.gcode == 2 or self.gcode == 3)
              and self.feed > 0):
            block.time += length / self.feed
            self.totalTime += length / self.feed
        else:
            try:
                if self.vars["feedmode"] == 94:
                    # Normal mode
                    t = length / self.feed
                elif self.vars["feedmode"] == 93:
                    # Inverse mode
                    t = length * self.feed
                block.time += t
                self.totalTime += t
            except Exception:
                pass
            block.length += length

        self.totalLength += length

    # ----------------------------------------------------------------------
    def pathMargins(self, block):
        if block.enable:
            self.vars["xmin"] = min(self.vars["xmin"], block.xmin)
            self.vars["ymin"] = min(self.vars["ymin"], block.ymin)
            self.vars["zmin"] = min(self.vars["zmin"], block.zmin)
            self.vars["xmax"] = max(self.vars["xmax"], block.xmax)
            self.vars["ymax"] = max(self.vars["ymax"], block.ymax)
            self.vars["zmax"] = max(self.vars["zmax"], block.zmax)

        self.vars["axmin"] = min(self.vars["axmin"], block.xmin)
        self.vars["aymin"] = min(self.vars["aymin"], block.ymin)
        self.vars["azmin"] = min(self.vars["azmin"], block.zmin)
        self.vars["axmax"] = max(self.vars["axmax"], block.xmax)
        self.vars["aymax"] = max(self.vars["aymax"], block.ymax)
        self.vars["azmax"] = max(self.vars["azmax"], block.zmax)

    # ----------------------------------------------------------------------
    # Instead of the current code, override with the custom user lines
    # @param program a list of lines to execute
    # @return the new list of lines
    # ----------------------------------------------------------------------
    def compile(self, program):
        lines = []
        for j, line in enumerate(program):
            newcmd = []
            cmds = self.compileLine(line)
            if cmds is None:
                continue
            if isinstance(cmds, str):
                cmds = self.breakLine(cmds)
            else:
                # either CodeType or tuple, list[] append it as is
                lines.append(cmds)
                continue

            for cmd in cmds:
                c = cmd[0]
                try:
                    value = float(cmd[1:])
                except Exception:
                    value = 0.0
                if c.upper() in ("F", "X", "Y", "Z", "I", "J", "K", "R", "P"):
                    cmd = self.fmt(c, value)
                else:
                    opt = ERROR_HANDLING.get(cmd.upper(), 0)
                    if opt == SKIP:
                        cmd = None

                if cmd is not None:
                    newcmd.append(cmd)
            lines.append("".join(newcmd))
        return lines

    # ----------------------------------------------------------------------
    # code to change manually tool
    # ----------------------------------------------------------------------
    def toolChange(self, tool=None):
        if tool is not None:
            # Force a change
            self.tool = tool
            self._lastTool = None

        # check if it is the same tool
        if self.tool is None or self.tool == self._lastTool:
            return []

        # create the necessary code
        lines = []
        # remember state and populate variables,
        # FIXME: move to ./controllers/_GenericController.py
        lines.append(
            "$g"
        )
        lines.append("m5")  # stop spindle
        lines.append("%wait")
        lines.append("%_x,_y,_z = wx,wy,wz")  # remember position
        lines.append("g53 g0 z[toolchangez]")
        lines.append("g53 g0 x[toolchangex] y[toolchangey]")
        lines.append("%wait")

        if self.comment:
            lines.append(
                f"%msg Tool change T{int(self.tool):02} ({self.comment})")
        else:
            lines.append(f"%msg Tool change T{int(self.tool):02}")
        lines.append("m0")  # feed hold

        if self.toolPolicy < 4:
            lines.append("g53 g0 x[toolprobex] y[toolprobey]")
            lines.append("g53 g0 z[toolprobez]")

            # fixed WCS
            if self.vars["fastprbfeed"]:
                prb_reverse = {"2": "4", "3": "5", "4": "2", "5": "3"}
                self.vars["prbcmdreverse"] = (
                    self.vars["prbcmd"][:-1]
                    + prb_reverse[self.vars["prbcmd"][-1]]
                )
                currentFeedrate = self.vars["fastprbfeed"]
                while currentFeedrate > self.vars["prbfeed"]:
                    lines.append("%wait")
                    lines.append(
                        f"g91 [prbcmd] {self.fmt('f', currentFeedrate)} "
                        f"z[toolprobez-mz-tooldistance]"
                    )
                    lines.append("%wait")
                    lines.append(
                        f"[prbcmdreverse] {self.fmt('f', currentFeedrate)} "
                        f"z[toolprobez-mz]"
                    )
                    currentFeedrate /= 10
            lines.append("%wait")
            lines.append(
                "g91 [prbcmd] f[prbfeed] z[toolprobez-mz-tooldistance]")

            if self.toolPolicy == 2:
                # Adjust the current WCS to fit to the tool
                # FIXME could be done dynamically in the code
                p = WCS.index(self.vars["WCS"]) + 1
                lines.append(f"g10l20p{int(p)} z[toolheight]")
                lines.append("%wait")

            elif self.toolPolicy == 3:
                # Modify the tool length, update the TLO
                lines.append("g4 p1")  # wait a sec to get the probe info
                lines.append("%wait")
                lines.append("%global TLO; TLO=prbz-toolmz")
                lines.append("g43.1z[TLO]")
                lines.append("%update TLO")

            lines.append("g53 g0 z[toolchangez]")
            lines.append("g53 g0 x[toolchangex] y[toolchangey]")

        if self.toolWaitAfterProbe:
            lines.append("%wait")
            lines.append("%msg Restart spindle")
            lines.append("m0")  # feed hold

        # restore state
        lines.append("g90")  # restore mode
        lines.append("g0 x[_x] y[_y]")  # ... x,y position
        lines.append("g0 z[_z]")  # ... z position
        lines.append("f[feed] [spindle]")  # ... feed and spindle
        lines.append("g4 p5")  # wait 5s for spindle to speed up

        # remember present tool
        self._lastTool = self.tool
        return lines

    # ----------------------------------------------------------------------
    # code to expand G80-G89 macro code - canned cycles
    # example:
    # code to expand G83 code - peck drilling cycle
    # format:   (G98 / G99 opt.) G83 X~ Y~ Z~ A~ R~ L~ Q~
    # example:  N150 G98 G83 Z-1.202 R18. Q10. F50.
    #           ...
    #           G80
    # Notes: G98, G99, Z, R, Q, F are unordered parameters
    # ----------------------------------------------------------------------
    def macroGroupG8X(self):
        lines = []
        # FIXME Assuming only on plane XY
        if self.absolute:
            # FIXME is it correct?
            self.lval = 1
            if self.retractz:
                clearz = max(self.rval, self.z)
            else:
                clearz = self.rval
            drill = self.zval
            retract = self.rval
        else:
            clearz = self.z + self.rval
            retract = clearz
            drill = clearz + self.dz

        if self.gcode == 83:  # peck drilling
            peck = self.qval
        else:
            peck = 100000.0  # a large value

        x, y, z = self.x, self.y, self.z
        if z < clearz:
            z = clearz
            lines.append(self.grapid(z=z / self.unit))

        for _line in range(self.lval):
            # Rapid move parallel to XY
            x += self.dx
            y += self.dy
            lines.append(self.grapid(x / self.unit, y / self.unit))

            # Rapid move parallel to retract
            zstep = max(drill, retract - peck)
            while z > drill:
                if z != retract:
                    z = retract
                    lines.append(self.grapid(z=z / self.unit))

                z = max(drill, zstep)
                zstep -= peck

                # Drill to z
                lines.append(
                    self.gline(z=z / self.unit, f=self.feed / self.unit))

            # 82=dwell, 86=boring-stop, 89=boring-dwell
            if self.gcode in (82, 86, 89):
                lines.append(self._gcode(4, p=self.pval))

                if self.gcode == 86:
                    lines.append("M5")  # stop spindle???

            # Move to original position
            if self.gcode in (85, 89):  # boring cycle
                z = retract
                lines.append(
                    self.gline(z=z / self.unit, f=self.feed / self.unit))

            z = clearz
            lines.append(self.grapid(z=z / self.unit))

            if self.gcode == 86:
                lines.append("M3")  # restart spindle???
        return lines


# =============================================================================
# Block of g-code commands. A gcode file is represented as a list of blocks
# - Commands are grouped as (non motion commands Mxxx)
# - Basic shape from the first rapid move command to the last rapid z raise
#   above the working surface
#
# Inherits from list and contains:
#   - a list list of gcode lines
#   - (imported shape)
# =============================================================================
class Block(list):
    def __init__(self, name=None):
        # Copy constructor
        if isinstance(name, Block):
            self.copy(name)
            return
        self._name = name
        self.enable = True  # Enabled/Visible in drawing
        self.expand = False  # Expand in editor
        self.color = None  # Custom color for path
        self._path = []  # canvas drawing paths
        self.sx = self.sy = self.sz = 0  # start  coordinates
        # (entry point first non rapid motion)
        self.ex = self.ey = self.ez = 0  # ending coordinates
        self.resetPath()

    # ----------------------------------------------------------------------
    def copy(self, src):
        self._name = src._name
        self.enable = src.enable
        self.expand = src.expand
        self.color = src.color
        self[:] = src[:]
        self._path = []
        self.sx = src.sx
        self.sy = src.sy
        self.sz = src.sz
        self.ex = src.ex
        self.ey = src.ey
        self.ez = src.ez

    # ----------------------------------------------------------------------
    def name(self):
        return self._name is None and "block" or self._name

    # ----------------------------------------------------------------------
    # @return name without the operation
    # ----------------------------------------------------------------------
    def nameNop(self):
        name = self.name()
        pat = OPPAT.match(name)
        if pat is None:
            return name
        else:
            return pat.group(1).strip()

    # ----------------------------------------------------------------------
    # Tests if block contains operation type
    # ----------------------------------------------------------------------
    def operationTest(self, op, name=None):
        if name is None:
            name = self.name()
        pat = OPPAT.match(name)
        if pat is not None:
            ops = pat.group(2)
            ops = re.split(r"\W+", ops)
            if op in ops:
                return True
        return False

    # ----------------------------------------------------------------------
    # Get block operation value
    # ----------------------------------------------------------------------
    def operationGet(self, op, name=None):
        if name is None:
            name = self.name()
        pat = OPPAT.match(name)
        if pat is not None:
            ops = pat.group(2)
            ops = re.split(",", ops)
            for opp in ops:
                t = re.split(":", opp)
                if t[0] == op:
                    return t[1]
        return None

    # ----------------------------------------------------------------------
    # Tests if block contains operation on inside of the part (-1),
    #      outside (1), or can't decide (0)
    # ----------------------------------------------------------------------
    def operationSide(self, name=None):
        if self.operationTest("pocket", name):
            return -1
        if (self.operationTest("in", name)
                and not self.operationTest("out", name)):
            return -1
        if (self.operationTest("out", name)
                and not self.operationTest("in", name)):
            return 1
        return 0

    # ----------------------------------------------------------------------
    # @return the new name with an operation (static)
    # ----------------------------------------------------------------------
    @staticmethod
    def operationName(name, operation, remove=None):
        pat = OPPAT.match(name)
        if pat is None:
            return f"{name} [{operation}]"
        else:
            name = pat.group(1).strip()
            ops = pat.group(2).split(",")
            if ":" in operation:
                oid, opt = operation.split(":")
            else:
                oid = operation
                opt = None

            found = False
            for i, o in enumerate(ops):
                if ":" in o:
                    o, c = o.split(":")
                    try:
                        c = int(c)
                    except Exception:
                        c = 1
                else:
                    c = 1

                if remove and o in remove:
                    ops[i] = ""
                if not found and o == oid:
                    if opt is not None or c is None:
                        ops[i] = operation
                    else:
                        ops[i] = f"{oid}:{int(c + 1)}"
                    found = True

            # remove all empty
            ops = list(filter(lambda x: x != "", ops))

            if not found:
                ops.append(operation)

            return f"{name} [{','.join(ops)}]"

    # ----------------------------------------------------------------------
    # Add a new operation to the block's name
    # ----------------------------------------------------------------------
    def addOperation(self, operation, remove=None):
        self._name = Block.operationName(self.name(), operation, remove)

    # ----------------------------------------------------------------------
    def header(self):
        e = (
            self.expand
            and Unicode.BLACK_DOWN_POINTING_TRIANGLE
            or Unicode.BLACK_RIGHT_POINTING_TRIANGLE
        )
        v = self.enable and Unicode.BALLOT_BOX_WITH_X or Unicode.BALLOT_BOX
        try:
            return f"{e} {v} {self.name()} - [{len(self)}]"
        except UnicodeDecodeError:
            return " ".join([
                f"{e} {v} {self.name().decode('ascii', 'replace')} -",
                f"[{int(len(self))}]"
            ])  # TODO: is this OK?

    # ----------------------------------------------------------------------
    def write_header(self):
        header = ""
        header += f"(Block-name: {self.name()})\n"
        header += f"(Block-expand: {int(self.expand)})\n"
        header += f"(Block-enable: {int(self.enable)})\n"
        if self.color:
            header += f"(Block-color: {self.color})\n"
        return header

    def write(self, f):
        f.write(self.write_header())
        for line in self:
            if self.enable:
                f.write(f"{line}\n")
            else:
                f.write(
                    f"(Block-X: {line.replace('(', '[').replace(')', ']')})\n")

    # ----------------------------------------------------------------------
    # Return a dump object for pickler
    # ----------------------------------------------------------------------
    def dump(self):
        return self.name(), self.enable, self.expand, self.color, self

    # ----------------------------------------------------------------------
    # Create a block from a dump object from unpickler
    # ----------------------------------------------------------------------
    @staticmethod
    def load(obj):
        name, enable, expand, color, code = obj
        block = Block(name)
        block.enable = enable
        block.expand = expand
        block.color = color
        block.extend(code)
        return block

    # ----------------------------------------------------------------------
    def append(self, line):
        if line.startswith("(Block-"):
            pat = BLOCKPAT.match(line)
            if pat:
                name, value = pat.groups()
                value = value.strip()
                if name == "name":
                    self._name = value
                    return
                elif name == "expand":
                    self.expand = bool(int(value))
                    return
                elif name == "enable":
                    self.enable = bool(int(value))
                    return
                elif name == "tab":
                    # Handled elsewhere
                    return
                elif name == "color":
                    self.color = value
                    return
                elif name == "X":  # uncomment
                    list.append(
                        self, value.replace("[", "(").replace("]", ")"))
                    return
        if self._name is None and ("id:" in line) and ("End" not in line):
            pat = IDPAT.match(line)
            if pat:
                self._name = pat.group(1)
        list.append(self, line)

    # ----------------------------------------------------------------------
    def resetPath(self):
        del self._path[:]
        self.xmin = self.ymin = self.zmin = 1000000.0
        self.xmax = self.ymax = self.zmax = -1000000.0
        self.length = 0.0  # cut length
        self.rapid = 0.0  # rapid length
        self.time = 0.0

    # ----------------------------------------------------------------------
    def hasPath(self):
        return bool(self._path)

    # ----------------------------------------------------------------------
    def addPath(self, p):
        self._path.append(p)

    # ----------------------------------------------------------------------
    def path(self, item):
        try:
            return self._path[item]
        except Exception:
            return None

    # ----------------------------------------------------------------------
    def startPath(self, x, y, z):
        self.sx = x
        self.sy = y
        self.sz = z

    # ----------------------------------------------------------------------
    def endPath(self, x, y, z):
        self.ex = x
        self.ey = y
        self.ez = z

    # ----------------------------------------------------------------------
    def pathMargins(self, xyz):
        self.xmin = min(self.xmin, min(i[0] for i in xyz))
        self.ymin = min(self.ymin, min(i[1] for i in xyz))
        self.zmin = min(self.zmin, min(i[2] for i in xyz))
        self.xmax = max(self.xmax, max(i[0] for i in xyz))
        self.ymax = max(self.ymax, max(i[1] for i in xyz))
        self.zmax = max(self.zmax, max(i[2] for i in xyz))


globCNC = CNC()
