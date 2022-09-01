""" This is just for testing purposes of the GUI.
    Running this file will open the GUI without any functionality.

"""

# Add test init here!

import os
import sys

PRGPATH = os.path.abspath(os.path.dirname(__file__))
print(os.path.abspath(f"{os.path.dirname(__file__)}{os.sep}.."))
sys.path.insert(1, os.path.abspath(
    f"{os.path.dirname(__file__)}{os.sep}../lib"))
sys.path.insert(1, os.path.abspath(f"{os.path.dirname(__file__)}{os.sep}.."))

if __name__ == "__main__":
    from globalConfig import config as gconfig
    gconfig.load_configuration()
    import app

    application = app.maingui()

    try:
        application.mainloop()
    except KeyboardInterrupt:
        application.quit()

    # application.close()
