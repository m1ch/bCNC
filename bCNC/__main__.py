#!/usr/bin/env python3

import os
import sys
import getopt

PRGPATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PRGPATH)
sys.path.append(os.path.join(PRGPATH, "lib"))
sys.path.append(os.path.join(PRGPATH, "plugins"))
sys.path.append(os.path.join(PRGPATH, "controllers"))


def main():
    try:
        import bmain
    except ImportError:
        sys.stderr.write("\n\nERROR: bmain.py not found\n")
        sys.exit()

    # Parse arguments
    try:
        optlist, args = getopt.getopt(
            sys.argv[1:],
            "?b:dDfhi:g:rlpPSs:",
            [
                "help",
                "ini=",
                "fullscreen",
                "recent",
                "list",
                "pendant=",
                "serial=",
                "baud=",
                "run",
            ],
        )
    except getopt.GetoptError:
        bmain.usage(1)

    bmain.main(optlist, args)


sys.stdout.write("=" * 80 + "\n")
sys.stdout.write(
    "WARNING: bCNC was resently ported to only support \n"
    + "python3.8 and newer.\n"
)
sys.stdout.write(
    "Most things seem to work reasonably well.\n"
)
sys.stdout.write(
    "Please report any issues to: "
    + "https://github.com/vlachoudis/bCNC/issues\n"
)
sys.stdout.write("=" * 80 + "\n")

main()
