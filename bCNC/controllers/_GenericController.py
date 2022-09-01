# Generic motion controller definition
# All controller plugins inherit features from this one

import re
import time

from cnc import globCNC, WCS
from sender import globSender

# GRBLv1
SPLITPAT = re.compile(r"[:,]")

# GRBLv0 + Smoothie
STATUSPAT = re.compile(
    r"^<(\w*?),MPos:([+\-]?\d*\.\d*),([+\-]?\d*\.\d*),([+\-]?\d*\.\d*)(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?,WPos:([+\-]?\d*\.\d*),([+\-]?\d*\.\d*),([+\-]?\d*\.\d*)(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?(?:,.*)?>$"
)
POSPAT = re.compile(
    r"^\[(...):([+\-]?\d*\.\d*),([+\-]?\d*\.\d*),([+\-]?\d*\.\d*)(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?(?:,[+\-]?\d*\.\d*)?(:(\d*))?\]$"
)
# FIXME: add example for strings this regexes shall convert

TLOPAT = re.compile(r"^\[(...):([+\-]?\d*\.\d*)\]$")
DOLLARPAT = re.compile(r"^\[G\d* .*\]$")

# Only used in this file
VARPAT = re.compile(r"^\$(\d+)=(\d*\.?\d*) *\(?.*")


class _GenericController:
    def test(self):
        print("test supergen")

    def executeCommand(self, oline, line, cmd):
        return False

    def hardResetPre(self):
        pass

    def hardResetAfter(self):
        pass

    def viewStartup(self):
        pass

    def checkGcode(self):
        pass

    def viewSettings(self):
        pass

    def grblRestoreSettings(self):
        pass

    def grblRestoreWCS(self):
        pass

    def grblRestoreAll(self):
        pass

    def purgeControllerExtra(self):
        pass

    def overrideSet(self):
        pass

    def hardReset(self):
        globSender.busy()
        if globSender.serial is not None:
            self.hardResetPre()
            globSender.openClose()
            self.hardResetAfter()
        globSender.openClose()
        globSender.stopProbe()
        globSender._alarm = False
        globCNC.vars["_OvChanged"] = True  # force a feed change if any
        globSender.notBusy()

    # ----------------------------------------------------------------------
    def softReset(self, clearAlarm=True):
        if globSender.serial:
            globSender.serial_write(b"\030")
        globSender.stopProbe()
        if clearAlarm:
            globSender._alarm = False
        globCNC.vars["_OvChanged"] = True  # force a feed change if any

    # ----------------------------------------------------------------------
    def unlock(self, clearAlarm=True):
        if clearAlarm:
            globSender._alarm = False
        globSender.sendGCode("$X")

    # ----------------------------------------------------------------------
    def home(self, event=None):
        globSender._alarm = False
        globSender.sendGCode("$H")

    def viewStatusReport(self):
        globSender.serial_write(b"?")
        globSender.sio_status = True

    def viewParameters(self):
        globSender.sendGCode("$#")

    def viewState(self):  # Maybe rename to viewParserState() ???
        globSender.sendGCode("$G")

    # ----------------------------------------------------------------------
    def jog(self, direction):
        globSender.sendGCode(f"G91G0{direction}")
        globSender.sendGCode("G90")

    # ----------------------------------------------------------------------
    def goto(self, x=None, y=None, z=None, a=None, b=None, c=None):
        cmd = "G90G0"
        if x is not None:
            cmd += f"X{x:g}"
        if y is not None:
            cmd += f"Y{y:g}"
        if z is not None:
            cmd += f"Z{z:g}"
        if a is not None:
            cmd += f"A{a:g}"
        if b is not None:
            cmd += f"B{b:g}"
        if c is not None:
            cmd += f"C{c:g}"
        globSender.sendGCode(f"{cmd}")

    # ----------------------------------------------------------------------
    def _wcsSet(self, x, y, z, a=None, b=None, c=None):
        p = WCS.index(globCNC.vars["WCS"])
        if p < 6:
            cmd = "G10L20P%d" % (p + 1)
        elif p == 6:
            cmd = "G28.1"
        elif p == 7:
            cmd = "G30.1"
        elif p == 8:
            cmd = "G92"

        pos = ""
        if x is not None and abs(float(x)) < 10000.0:
            pos += "X" + str(x)
        if y is not None and abs(float(y)) < 10000.0:
            pos += "Y" + str(y)
        if z is not None and abs(float(z)) < 10000.0:
            pos += "Z" + str(z)
        if a is not None and abs(float(a)) < 10000.0:
            pos += "A" + str(a)
        if b is not None and abs(float(b)) < 10000.0:
            pos += "B" + str(b)
        if c is not None and abs(float(c)) < 10000.0:
            pos += "C" + str(c)
        cmd += pos
        globSender.sendGCode(cmd)
        self.viewParameters()
        globSender.event_generate(
            "<<Status>>",
            data=(_("Set workspace {} to {}").format(WCS[p], pos))
        )
        globSender.event_generate("<<CanvasFocus>>")

    # ----------------------------------------------------------------------
    def feedHold(self, event=None):
        if event is not None and not globSender.acceptKey(True):
            return
        if globSender.serial is None:
            return
        globSender.serial_write(b"!")
        globSender.serial.flush()
        globSender._pause = True

    # ----------------------------------------------------------------------
    def resume(self, event=None):
        if event is not None and not globSender.acceptKey(True):
            return
        if globSender.serial is None:
            return
        globSender.serial_write(b"~")
        globSender.serial.flush()
        globSender._msg = None
        globSender._alarm = False
        globSender._pause = False

    # ----------------------------------------------------------------------
    def pause(self, event=None):
        if globSender.serial is None:
            return
        if globSender._pause:
            globSender.resume()
        else:
            globSender.feedHold()

    # ----------------------------------------------------------------------
    # Purge the buffer of the controller. Unfortunately we have to perform
    # a reset to clear the buffer of the controller
    # ---------------------------------------------------------------------
    def purgeController(self):
        globSender.serial_write(b"!")
        globSender.serial.flush()
        time.sleep(1)
        # remember and send all G commands
        G = " ".join([x for x in globCNC.vars["G"] if x[0] == "G"])  # remember $G
        TLO = globCNC.vars["TLO"]
        self.softReset(False)  # reset controller
        self.purgeControllerExtra()
        globSender.runEnded()
        globSender.stopProbe()
        if G:
            globSender.sendGCode(G)  # restore $G
        globSender.sendGCode(f"G43.1Z{TLO}")  # restore TLO
        self.viewState()

    # ----------------------------------------------------------------------
    def displayState(self, state):
        state = state.strip()

        # Do not show g-code errors, when machine is already in alarm state
        if (globCNC.vars["state"].startswith("ALARM:")
                and state.startswith("error:")):
            print(f"Supressed: {state}")
            return

        # Do not show alarm without number when we already
        # display alarm with number
        if state == "Alarm" and globCNC.vars["state"].startswith("ALARM:"):
            return

        globCNC.vars["state"] = state

    # ----------------------------------------------------------------------
    def parseLine(self, line, cline, sline):
        if not line:
            return True

        elif line[0] == "<":
            if not globSender.sio_status:
                globSender.log.put((globSender.MSG_RECEIVE, line))
            else:
                self.parseBracketAngle(line, cline)

        elif line[0] == "[":
            globSender.log.put((globSender.MSG_RECEIVE, line))
            self.parseBracketSquare(line)

        elif "error:" in line or "ALARM:" in line:
            globSender.log.put((globSender.MSG_ERROR, line))
            globSender._gcount += 1
            if cline:
                del cline[0]
            if sline:
                globCNC.vars["errline"] = sline.pop(0)
            if not globSender._alarm:
                globSender._posUpdate = True
            globSender._alarm = True
            self.displayState(line)
            if globSender.running:
                globSender._stop = True

        elif line.find("ok") >= 0:
            globSender.log.put((globSender.MSG_OK, line))
            globSender._gcount += 1
            if cline:
                del cline[0]
            if sline:
                del sline[0]

        elif line[0] == "$":
            globSender.log.put((globSender.MSG_RECEIVE, line))
            pat = VARPAT.match(line)
            if pat:
                globCNC.vars[f"grbl_{pat.group(1)}"] = pat.group(2)

        elif line[:4] == "Grbl" or line[:13] == "CarbideMotion":
            globSender.log.put((globSender.MSG_RECEIVE, line))
            globSender._stop = True
            del cline[:]  # After reset clear the buffer counters
            del sline[:]
            globCNC.vars["version"] = line.split()[1]
            # Detect controller
            # FIXME: This overwrites the setup
            # if globSender.controller in ("GRBL0", "GRBL1"):
            #     globSender.controllerSet(
            #         "GRBL%d" % (int(globCNC.vars["version"][0])))

        else:
            # We return false in order to tell that we can't parse this line
            # Sender will log the line in such case
            return False

        # Parsing succesfull
        return True
