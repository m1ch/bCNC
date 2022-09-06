import sys
import os
from typing import Final

# =============================================================================
# General program information
MAJOR_VERSION: Final = 0
MINOR_VERSION: Final = 9
PATCH_VERSION: Final = 15

__author__: Final = "Vasilis Vlachoudis"
__email__: Final = "vvlachoudis@gmail.com"
__version__: Final = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
__date__: Final = "24 June 2022"
__prg__: Final = "bCNC"

__platform_fingerprint__: Final = "({} py{}.{}.{})".format(
    sys.platform,
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro,
)
__title__: Final = f"{__prg__} {__version__} {__platform_fingerprint__}"

__www__: Final = "https://github.com/vlachoudis/bCNC"
__contribute__: Final = (
    "@effer Filippo Rivato\n"
    "@carlosgs Carlos Garcia Saura\n"
    "@dguerizec\n"
    "@buschhardt\n"
    "@MARIOBASZ\n"
    "@harvie Tomas Mudrunka"
)
__credits__: Final = (
    "@1bigpig\n"
    "@chamnit Sonny Jeon\n"
    "@harvie Tomas Mudrunka\n"
    "@onekk Carlo\n"
    "@SteveMoto\n"
    "@willadams William Adams"
)
__translations__: Final = (
    "Dutch - @hypothermic\n"
    "French - @ThierryM\n"
    "German - @feistus, @SteveMoto\n"
    "Italian - @onekk\n"
    "Japanese - @stm32f1\n"
    "Korean - @jjayd\n"
    "Portuguese - @moacirbmn \n"
    "Russian - @minithc\n"
    "Simplified Chinese - @Bluermen\n"
    "Spanish - @carlosgs\n"
    "Traditional Chinese - @Engineer2Designer"
)

# =============================================================================
# Path and special folders

# When being bundled by pyinstaller, paths are different
__prgpath__: Final = os.path.abspath(os.path.dirname(sys.argv[0])) \
    if getattr(sys, "frozen", False) \
    else os.path.abspath(os.path.dirname(__file__))

__localespath__: Final = os.path.join(__prgpath__, "locale")
__libpath__: Final = os.path.join(__prgpath__, "lib")
__pluginpath__: Final = os.path.join(__prgpath__, "plugins")
__toolspath__: Final = os.path.join(__prgpath__, "tools")
__controllerpath__: Final = os.path.join(__prgpath__, "controllers")
__guipath__: Final = os.path.join(__prgpath__, "gui")
__pagespath__: Final = os.path.join(__guipath__, "pages")
__framespath__: Final = os.path.join(__guipath__, "frames")
__groupspath__: Final = os.path.join(__guipath__, "groups")
__iconpath__: Final = os.path.join(__guipath__, "icons")
__imagepath__: Final = os.path.join(__guipath__, "images")


# =============================================================================
# System information
__iniSystem__: Final = os.path.join(__prgpath__, f"{__prg__}.ini")
__iniUser__: Final = os.path.expanduser(f"~/.{__prg__}")
__hisFile__: Final = os.path.expanduser(f"~/.{__prg__}.history")


# =============================================================================
# Language and translation
__LANGUAGES__: Final = {
    "": "<system>",
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
    "ja": "Japanese",
    "kr": "Korean",
    "nl": "Nederlands",
    "pt_BR": "Brazilian - Portuguese",
    "ru": "Russian",
    "zh_cn": "Simplified Chinese",
    "zh_tw": "Traditional Chinese",
}

# =============================================================================
# General
_maxRecent = 10
