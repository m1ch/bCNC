# GRBL <=0.9 motion controller plugin

from cnc import globCNC
from sender import globSender
from gcode import globGCode
from _GenericController import DOLLARPAT, POSPAT, STATUSPAT, TLOPAT
from _GenericGRBL import _GenericGRBL


class Controller(_GenericGRBL):
    def __init__(self):
        self.gcode_case = 0
        self.has_override = False

    def parseBracketAngle(self, line, cline):
        globSender.sio_status = False
        pat = STATUSPAT.match(line)
        if pat:
            if not globSender._alarm:
                globCNC.vars["state"] = pat.group(1)
            globCNC.vars["mx"] = float(pat.group(2))
            globCNC.vars["my"] = float(pat.group(3))
            globCNC.vars["mz"] = float(pat.group(4))
            globCNC.vars["wx"] = float(pat.group(5))
            globCNC.vars["wy"] = float(pat.group(6))
            globCNC.vars["wz"] = float(pat.group(7))
            globCNC.vars["wcox"] = globCNC.vars["mx"] - globCNC.vars["wx"]
            globCNC.vars["wcoy"] = globCNC.vars["my"] - globCNC.vars["wy"]
            globCNC.vars["wcoz"] = globCNC.vars["mz"] - globCNC.vars["wz"]
            globSender._posUpdate = True
            if pat.group(1)[:4] != "Hold" and globSender._msg:
                globSender._msg = None

            # Machine is Idle buffer is empty
            # stop waiting and go on
            if (
                globSender.sio_wait
                and not cline
                and pat.group(1) not in ("Run", "Jog", "Hold")
            ):
                globSender.sio_wait = False
                globSender._gcount += 1
            else:
                globSender.log.put((globSender.MSG_RECEIVE, line))

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
