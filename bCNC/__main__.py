#!/usr/bin/env python3

import os
import sys
import argparse

from globalConstants import (
    __prg__,
    __version__,
    __libpath__,
    __pluginpath__,
    __controllerpath__,
    _maxRecent,
)

from globalConfig import config as gconfig


PRGPATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(1, __libpath__)
sys.path.insert(1, __pluginpath__)
sys.path.insert(1, __controllerpath__)

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


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""

    parser = argparse.ArgumentParser(
        prog=__prg__,
        description=f"{__prg__} - a CAM tool and g-code sender",
        epilog="If restart is requested, exits with code 23",
    )

    parser.add_argument("file", type=str,
                        nargs='*',
                        help="Path to a g-Code file")
    parser.add_argument("--version", action="version",
                        version=__version__)
    developer = parser.add_mutually_exclusive_group()
    developer.add_argument("-d", action="store_true",
                           help="Enable developer features")
    developer.add_argument("-D", action="store_true",
                           help="Disable developer features")
    parser.add_argument("-f", "--fullscreen", action="store_true",
                        help="Enable fullscreen mode")
    parser.add_argument("-g", type=str,
                        help="Set the default geometry")
    parser.add_argument("-i", "--ini",
                        help="Alternative ini file for testing")
    parser.add_argument("-l", "--list", action="store_true",
                        help="List all recently opened files")
    parser.add_argument("-r", "--recent", action="store_true",
                        help="Load the most recent file opened")
    # NOTE: R is not available in original arguments
    # parser.add_argument("-R", action="store_true",
    #                     help="Load the recent file matching the argument")
    # NOTE: pendant options are ignored in original parser
    # pendant = parser.add_mutually_exclusive_group()
    # pendant.add_argument("-p", "--pendant",
    #                      # metavar="path_to_ini_file",
    #                      help="Open pendant to specified port")
    # pendant.add_argument("-P", action="store_true",
    #                      help="Do not start pendant")
    ser = parser.add_mutually_exclusive_group()
    ser.add_argument("-s", "--serial", type=str,
                     help="Open serial port specified")
    ser.add_argument("-S", action="store_true",
                     help="Do not open serial port")
    parser.add_argument("-b", "--baud", type=int,
                        help="Set the baud rate")
    parser.add_argument("--run", action="store_true",
                        help="Directly run the file once loaded")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    arguments = parser.parse_args()

    return arguments


def select_recent_file():
    import Utils

    # display list of recent files
    maxlen = 10
    for i in range(_maxRecent):
        try:
            filename = gconfig.getrecent(i)
        except Exception:
            continue
        maxlen = max(maxlen, len(os.path.basename(filename)))

    sys.stdout.write("Recent files:\n")
    num_recent = 0
    for i in range(_maxRecent):
        filename = gconfig.getrecent(i)
        num_recent = i
        if filename is None:
            break
        d = os.path.dirname(filename)
        fn = os.path.basename(filename)
        sys.stdout.write(f"  {i + 1:2d}: {fn:<{maxlen}}  {d}\n")

    sys.stdout.write("\nSelect one: \n")
    try:
        r = int(sys.stdin.readline()) - 1
    except Exception:
        r = -1
    if r < 0 or r > num_recent:
        sys.stderr.write(
            f"\nERROR: Only integers from 1 to {num_recent+1} "
            + "are allowed! \n")
        sys.exit(1)

    return r


# -----------------------------------------------------------------------------
def main() -> int:
    import bmain
    import tkExtra
    import Utils
    import Updates
    from CNC import CNC
    try:
        import serial
    except ImportError:
        serial = None
        print("testing mode, could not import serial")

    exit_code = 0

    args = get_arguments()

    recent = args.recent
    run = args.run
    fullscreen = args.fullscreen

    if args.ini:
        gconfig.set_userini(args.ini)

    gconfig.load_configuration()

    # DEBUG: print the entire config
    gconfig.print_configuration()

    CNC.developer = args.d

    r = -1
    if args.recent:
        print("resent")
        r = 0
    elif args.list:
        r = select_recent_file()

    if r >= 0:
        try:
            recent = gconfig.getrecent(r)
        except Exception:
            sys.stderr.write(
                "\nERROR: There is no recent file available!\n")
            sys.exit(1)

    application = bmain.Application(className=f"  {__prg__}  ")

    palette = {"background": application.cget("background")}

    color_count = 0
    custom_color_count = 0
    for color_name in (
        "background",
        "foreground",
        "activeBackground",
        "activeForeground",
        "disabledForeground",
        "highlightBackground",
        "highlightColor",
        "selectBackground",
        "selectForeground",
    ):
        color2 = gconfig.getstr("Color", "global." + color_name.lower(), None)
        color_count += 1
        if (color2 is not None) and (color2.strip() != ""):
            palette[color_name] = color2.strip()
            custom_color_count += 1

            if color_count == 0:
                tkExtra.GLOBAL_CONTROL_BACKGROUND = color2
            elif color_count == 1:
                tkExtra.GLOBAL_FONT_COLOR = color2

    if custom_color_count > 0:
        print("Changing palette")
        application.tk_setPalette(**palette)

    if fullscreen:
        application.attributes("-fullscreen", True)

    for fn in args.file:
        application.load(fn)
    if recent:
        application.load(recent)

    if serial is None:
        application.showSerialError()

    if Updates.need2Check():
        application.checkUpdates()

    if run:
        application.run()

    try:
        application.mainloop()
    except KeyboardInterrupt:
        application.quit()

    application.close()
    gconfig.save_configuration()
    Utils.delIcons()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
