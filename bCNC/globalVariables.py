from typing import Final

import cnc

globCNC:Final = cnc.CNC()

# Variables need to be defined later due to circular imports
globGCode = None
globSender = None


def N_(message):
    return message
