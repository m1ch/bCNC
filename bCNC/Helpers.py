""" This file is a collection of simple helper functions. It was necessary to
remove them from other files, since there were circular imports.
XXX: This file might be removed, once the circular imports are cleared.
"""

import os
import sys
from globalConstants import __prgpath__

__all__ = (
    "to_zip",
)

__prg__ = "bCNC"
prgpath = os.path.abspath(os.path.dirname(__file__))
if getattr(sys, "frozen", False):
    # When being bundled by pyinstaller, paths are different
    print("Running as pyinstaller bundle!", sys.argv[0])
    prgpath = os.path.abspath(os.path.dirname(sys.argv[0]))


def to_zip(*args, **kwargs):
    return list(zip(*args, **kwargs))


# TODO: Define function that returns available serials
def get_serial_ports():
    import serial
    # import serial.tools.list_ports
    # return [comport.device for comport in serial.tools.list_ports.comports()]
    comports = serial.tools.list_ports.comports
    print([comport.description for comport in comports()])
    print([comport.description for comport in comports()])
    print([comport.hwid for comport in comports()])
    print([comport.name for comport in comports()])
    print([comport.pid for comport in comports()])
    print([comport.device_path for comport in comports()])
    print([comport.device for comport in comports()])
    print([comport.interface for comport in comports()])
    print([comport.location for comport in comports()])
    print([comport.manufacturer for comport in comports()])


def import_dynamic(name):
    # FIXME: update as described in
    #        https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_controllers():
    import glob
    import traceback
    for f in glob.glob(f"{__prgpath__}/controllers/*.py"):
        name, _ = os.path.splitext(os.path.basename(f))
        if name[0] == "_":
            continue
        try:
            exec(f"import {name}")
            self.controllers[name] = eval(f"{name}.Controller(self)")
        except (ImportError, AttributeError):
            typ, val, tb = sys.exc_info()
            traceback.print_exception(typ, val, tb)
    pass


def get_plugins():
    pass
