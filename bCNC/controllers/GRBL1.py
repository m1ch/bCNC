# GRBL 1.0+ motion controller plugin

from cnc import globCNC
from sender import globSender
from gcode import globGCode
from _GenericController import SPLITPAT
from _GenericGRBL import _GenericGRBL

OV_FEED_100 = chr(0x90)  # Extended override commands
OV_FEED_i10 = chr(0x91)
OV_FEED_d10 = chr(0x92)
OV_FEED_i1 = chr(0x93)
OV_FEED_d1 = chr(0x94)

OV_RAPID_100 = chr(0x95)
OV_RAPID_50 = chr(0x96)
OV_RAPID_25 = chr(0x97)

OV_SPINDLE_100 = chr(0x99)
OV_SPINDLE_i10 = chr(0x9A)
OV_SPINDLE_d10 = chr(0x9B)
OV_SPINDLE_i1 = chr(0x9C)
OV_SPINDLE_d1 = chr(0x9D)

OV_SPINDLE_STOP = chr(0x9E)

OV_FLOOD_TOGGLE = chr(0xA0)
OV_MIST_TOGGLE = chr(0xA1)


class Controller(_GenericGRBL):
    def __init__(self):
        self.gcode_case = 0
        self.has_override = True

    def jog(self, direction):
        globSender.sendGCode(f"$J=G91 {direction} F100000")
        # XXX is F100000 correct?

    def overrideSet(self):
        globCNC.vars["_OvChanged"] = False  # Temporary
        # Check feed
        diff = globCNC.vars["_OvFeed"] - globCNC.vars["OvFeed"]
        if diff == 0:
            pass
        elif globCNC.vars["_OvFeed"] == 100:
            globSender.serial_write(OV_FEED_100)
        elif diff >= 10:
            globSender.serial_write(OV_FEED_i10)
            globCNC.vars["_OvChanged"] = diff > 10
        elif diff <= -10:
            globSender.serial_write(OV_FEED_d10)
            globCNC.vars["_OvChanged"] = diff < -10
        elif diff >= 1:
            globSender.serial_write(OV_FEED_i1)
            globCNC.vars["_OvChanged"] = diff > 1
        elif diff <= -1:
            globSender.serial_write(OV_FEED_d1)
            globCNC.vars["_OvChanged"] = diff < -1
        # Check rapid
        target = globCNC.vars["_OvRapid"]
        current = globCNC.vars["OvRapid"]
        if target == current:
            pass
        elif target == 100:
            globSender.serial_write(OV_RAPID_100)
        # FIXME: GRBL protocol does not specify 75% override command at all
        elif target == 75:
            globSender.serial_write(
                OV_RAPID_50
            )
        elif target == 50:
            globSender.serial_write(OV_RAPID_50)
        elif target == 25:
            globSender.serial_write(OV_RAPID_25)
        # Check Spindle
        diff = globCNC.vars["_OvSpindle"] - globCNC.vars["OvSpindle"]
        if diff == 0:
            pass
        elif globCNC.vars["_OvSpindle"] == 100:
            globSender.serial_write(OV_SPINDLE_100)
        elif diff >= 10:
            globSender.serial_write(OV_SPINDLE_i10)
            globCNC.vars["_OvChanged"] = diff > 10
        elif diff <= -10:
            globSender.serial_write(OV_SPINDLE_d10)
            globCNC.vars["_OvChanged"] = diff < -10
        elif diff >= 1:
            globSender.serial_write(OV_SPINDLE_i1)
            globCNC.vars["_OvChanged"] = diff > 1
        elif diff <= -1:
            globSender.serial_write(OV_SPINDLE_d1)
            globCNC.vars["_OvChanged"] = diff < -1

    def parseBracketAngle(self, line, cline):
        globSender.sio_status = False
        fields = line[1:-1].split("|")
        globCNC.vars["pins"] = ""

        # Report if state has changed
        if (
            globCNC.vars["state"] != fields[0]
            or globSender.runningPrev != globSender.running
        ):
            globSender.controllerStateChange(fields[0])
        globSender.runningPrev = globSender.running

        self.displayState(fields[0])

        for field in fields[1:]:
            word = SPLITPAT.split(field)
            if word[0] == "MPos":
                try:
                    globCNC.vars["mx"] = float(word[1])
                    globCNC.vars["my"] = float(word[2])
                    globCNC.vars["mz"] = float(word[3])
                    globCNC.vars["wx"] = round(
                        globCNC.vars["mx"]
                        - globCNC.vars["wcox"], globCNC.digits
                    )
                    globCNC.vars["wy"] = round(
                        globCNC.vars["my"]
                        - globCNC.vars["wcoy"], globCNC.digits
                    )
                    globCNC.vars["wz"] = round(
                        globCNC.vars["mz"]
                        - globCNC.vars["wcoz"], globCNC.digits
                    )
                    if len(word) > 4:
                        globCNC.vars["ma"] = float(word[4])
                        globCNC.vars["wa"] = round(
                            globCNC.vars["ma"]
                            - globCNC.vars["wcoa"], globCNC.digits
                        )
                    if len(word) > 5:
                        globCNC.vars["mb"] = float(word[5])
                        globCNC.vars["wb"] = round(
                            globCNC.vars["mb"]
                            - globCNC.vars["wcob"], globCNC.digits
                        )
                    if len(word) > 6:
                        globCNC.vars["mc"] = float(word[6])
                        globCNC.vars["wc"] = round(
                            globCNC.vars["mc"]
                            - globCNC.vars["wcoc"], globCNC.digits
                        )
                    globSender._posUpdate = True
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "F":
                try:
                    globCNC.vars["curfeed"] = float(word[1])
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "FS":
                try:
                    globCNC.vars["curfeed"] = float(word[1])
                    globCNC.vars["curspindle"] = float(word[2])
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "Bf":
                try:
                    globCNC.vars["planner"] = int(word[1])
                    globCNC.vars["rxbytes"] = int(word[2])
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "Ov":
                try:
                    globCNC.vars["OvFeed"] = int(word[1])
                    globCNC.vars["OvRapid"] = int(word[2])
                    globCNC.vars["OvSpindle"] = int(word[3])
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "WCO":
                try:
                    globCNC.vars["wcox"] = float(word[1])
                    globCNC.vars["wcoy"] = float(word[2])
                    globCNC.vars["wcoz"] = float(word[3])

                    if len(word) > 4:
                        globCNC.vars["wcoa"] = float(word[4])
                    if len(word) > 5:
                        globCNC.vars["wcob"] = float(word[5])
                    if len(word) > 6:
                        globCNC.vars["wcoc"] = float(word[6])
                except (ValueError, IndexError):
                    globCNC.vars["state"] = \
                        f"Garbage receive {word[0]}: {line}"
                    globSender.log.put(
                        (globSender.MSG_RECEIVE, globCNC.vars["state"]))
                    break
            elif word[0] == "Pn":
                try:
                    globCNC.vars["pins"] = word[1]
                    if "S" in word[1]:
                        if (globCNC.vars["state"] == "Idle"
                                and not globSender.running):
                            print("Stream requested by CYCLE START "
                                  + "machine button")
                            globSender.event_generate("<<Run>>", when="tail")
                        else:
                            print(
                                "Ignoring machine stream request, "
                                + "because of state: ",
                                globCNC.vars["state"],
                                globSender.running,
                            )
                except (ValueError, IndexError):
                    break

        # Machine is Idle buffer is empty stop waiting and go on
        if (
            globSender.sio_wait
            and not cline
            and fields[0] not in ("Run", "Jog", "Hold")
        ):
            globSender.sio_wait = False
            globSender._gcount += 1

    def parseBracketSquare(self, line):
        word = SPLITPAT.split(line[1:-1])
        if word[0] == "PRB":
            globCNC.vars["prbx"] = float(word[1])
            globCNC.vars["prby"] = float(word[2])
            globCNC.vars["prbz"] = float(word[3])
            globGCode.probe.add(
                globCNC.vars["prbx"] - globCNC.vars["wcox"],
                globCNC.vars["prby"] - globCNC.vars["wcoy"],
                globCNC.vars["prbz"] - globCNC.vars["wcoz"],
            )
            globSender._probeUpdate = True
            globCNC.vars[word[0]] = word[1:]
        if word[0] == "G92":
            globCNC.vars["G92X"] = float(word[1])
            globCNC.vars["G92Y"] = float(word[2])
            globCNC.vars["G92Z"] = float(word[3])
            if len(word) > 4:
                globCNC.vars["G92A"] = float(word[4])
            if len(word) > 5:
                globCNC.vars["G92B"] = float(word[5])
            if len(word) > 6:
                globCNC.vars["G92C"] = float(word[6])
            globCNC.vars[word[0]] = word[1:]
            globSender._gUpdate = True
        if word[0] == "G28":
            globCNC.vars["G28X"] = float(word[1])
            globCNC.vars["G28Y"] = float(word[2])
            globCNC.vars["G28Z"] = float(word[3])
            globCNC.vars[word[0]] = word[1:]
            globSender._gUpdate = True
        if word[0] == "G30":
            globCNC.vars["G30X"] = float(word[1])
            globCNC.vars["G30Y"] = float(word[2])
            globCNC.vars["G30Z"] = float(word[3])
            globCNC.vars[word[0]] = word[1:]
            globSender._gUpdate = True
        elif word[0] == "GC":
            globCNC.vars["G"] = word[1].split()
            globCNC.updateG()
            globSender._gUpdate = True
        elif word[0] == "TLO":
            globCNC.vars[word[0]] = word[1]
            globSender._probeUpdate = True
            globSender._gUpdate = True
        else:
            globCNC.vars[word[0]] = word[1:]
