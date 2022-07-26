""" This file is a collection of simple helper functions. It was necessary to
remove them from other files, since there were circular imports.
XXX: This file might be removed, once the circular imports are cleared.
"""

import os
import gettext
import sys

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

def _(txt):
    return gettext.translation(
        __prg__, os.path.join(prgpath, "locale"), fallback=True
    ).gettext(txt)

def N_(message):
    return message
