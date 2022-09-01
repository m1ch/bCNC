# Smoothieboard motion controller plugin

import time

from cnc import globCNC
from sender import globSender
from gcode import globGCode
from _GenericController import DOLLARPAT, POSPAT, TLOPAT, _GenericController


class Controller(_GenericController):
    def __init__(self):
        self.gcode_case = 1
        self.has_override = False

    def executeCommand(self, oline, line, cmd):
        if line[0] in (
            "help",
            "version",
            "mem",
            "ls",
            "cd",
            "pwd",
            "cat",
            "rm",
            "mv",
            "remount",
            "play",
            "progress",
            "abort",
            "reset",
            "dfu",
            "break",
            "config-get",
            "config-set",
            "get",
            "set_temp",
            "get",
            "get",
            "net",
            "load",
            "save",
            "upload",
            "calc_thermistor",
            "thermistors",
            "md5sum",
            "fire",
            "switch",
        ):
            if globSender.serial:
                globSender.serial_write(oline + "\n")
            return True
        return False

    def hardResetPre(self):
        globSender.serial_write(b"reset\n")

    def hardResetAfter(self):
        time.sleep(6)

    def viewBuild(self):
        globSender.serial_write(b"version\n")
        globSender.sendGCode("$I")

    def grblHelp(self):
        globSender.serial_write(b"help\n")

    def parseBracketAngle(self, line, cline):
        # <Idle|MPos:68.9980,-49.9240,40.0000,12.3456|WPos:68.9980,-49.9240,40.0000|F:12345.12|S:1.2>
        ln = line[1:-1]  # strip off < .. >

        # split fields
        lval = ln.split("|")

        # strip off status
        globCNC.vars["state"] = lval[0]

        # strip of rest into a dict of name: [values,...,]
        d = {
            a: [float(y) for y in b.split(",")]
            for a, b in [x.split(":") for x in lval[1:]]
        }
        globCNC.vars["mx"] = float(d["MPos"][0])
        globCNC.vars["my"] = float(d["MPos"][1])
        globCNC.vars["mz"] = float(d["MPos"][2])
        globCNC.vars["wx"] = float(d["WPos"][0])
        globCNC.vars["wy"] = float(d["WPos"][1])
        globCNC.vars["wz"] = float(d["WPos"][2])
        globCNC.vars["wcox"] = globCNC.vars["mx"] - globCNC.vars["wx"]
        globCNC.vars["wcoy"] = globCNC.vars["my"] - globCNC.vars["wy"]
        globCNC.vars["wcoz"] = globCNC.vars["mz"] - globCNC.vars["wz"]
        if "F" in d:
            globCNC.vars["curfeed"] = float(d["F"][0])
        globSender._posUpdate = True

        # Machine is Idle buffer is empty
        # stop waiting and go on
        if (globSender.sio_wait
                and not cline
                and lval[0] not in ("Run", "Jog", "Hold")):
            globSender.sio_wait = False
            globSender._gcount += 1

    def parseBracketSquare(self, line):
        pat = POSPAT.match(line)
        if pat:
            if pat.group(1) == "PRB":
                globCNC.vars["prbx"] = float(pat.group(2))
                globCNC.vars["prby"] = float(pat.group(3))
                globCNC.vars["prbz"] = float(pat.group(4))
                globGCode.probe.add(
                    globCNC.vars["prbx"]
                    + globCNC.vars["wx"]
                    - globCNC.vars["mx"],
                    globCNC.vars["prby"]
                    + globCNC.vars["wy"]
                    - globCNC.vars["my"],
                    globCNC.vars["prbz"]
                    + globCNC.vars["wz"]
                    - globCNC.vars["mz"],
                )
                globSender._probeUpdate = True
            globCNC.vars[pat.group(1)] = [
                float(pat.group(2)),
                float(pat.group(3)),
                float(pat.group(4)),
            ]
        else:
            pat = TLOPAT.match(line)
            if pat:
                globCNC.vars[pat.group(1)] = pat.group(2)
                globSender._probeUpdate = True
            elif DOLLARPAT.match(line):
                globCNC.vars["G"] = line[1:-1].split()
                globCNC.updateG()
                globSender._gUpdate = True
