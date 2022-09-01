import os
import configparser
import gettext

from globalConstants import (
    __prg__,
    __prgpath__,
    __iniSystem__,
    __iniUser__,
    __LANGUAGES__,
    __controllerpath__,
    __pluginpath__,
    __pagespath__,
    __framespath__,
    __groupspath__,
    __localespath__,
    _maxRecent,
)

"""
This replaces Utils.config and all according functions

Usage:
from globalConfig import config as gconfig

Utils.loadConfiguration   ->   gconfig.load_configuration
Utils.saveConfiguration   ->   gconfig.save_configuration
Utils.cleanConfiguration  ->   gconfig.clean_configuration
Utils.addSection          ->   gconfig.add_section_if_new
Utils.getStr              ->   gconfig.getstr
Utils.getUtf              ->   gconfig.getstr
Utils.getInt              ->   gconfig.getint
Utils.getFloat            ->   gconfig.getfloat
Utils.getBool             ->   gconfig.getbool
Utils.getFont             ->   gconfig.getfont
Utils.setFont             ->   gconfig.setfont
Utils.setBool             ->   gconfig.setbool
Utils.setStr              ->   gconfig.setstr
Utils.setUtf              ->   gconfig.setstr
Utils.setInt              ->   gconfig.setstr
Utils.setFloat            ->   gconfig.setstr
Utils.addRecent           ->   gconfig.addrecent
Utils.getRecent           ->   gconfig.getrecent

Utils.language            ->   gconfig.getlanguage
                               gconfig.setlanguage
Utils.LANGUAGES           ->   globalConstants.__LANGUAGES__

"""
_FONT_SECTION = "Font"

# language = ""

gettext.install(True, localedir=None)


def _search_controllers():
    import glob
    # import traceback

    controllers = {}
    for f in glob.glob(f"{__controllerpath__}/*.py"):
        name, _ = os.path.splitext(os.path.basename(f))
        if name[0] == "_":
            continue
        controllers[name] = f
        # try:
        #     exec(f"import {name}")
        #     self.controllers[name] = eval(f"{name}.Controller(self)")
        # except (ImportError, AttributeError):
        #     typ, val, tb = sys.exc_info()
        #     traceback.print_exception(typ, val, tb)
    return(controllers)


def _search_py_modules(path):
    import glob

    modules = {}
    for f in glob.glob(f"{path}/*.py"):
        name, _ = os.path.splitext(os.path.basename(f))
        if name[0] == "_":
            continue
        module = f.removeprefix(f"{__prgpath__}/")
        module = module.removesuffix(".py").replace("/", ".")
        modules[name] = module
    return(modules)


def _search_plugins():
    import glob
    # import traceback

    plugins = {}
    for f in glob.glob(f"{__prgpath__}/plugins/*.py"):
        name, _ = os.path.splitext(os.path.basename(f))
        if name[0] == "_":
            continue
        plugins[name] = f
        # try:
        #     exec(f"import {name}")
        #     self.controllers[name] = eval(f"{name}.Controller(self)")
        # except (ImportError, AttributeError):
        #     typ, val, tb = sys.exc_info()
        #     traceback.print_exception(typ, val, tb)
    return(plugins)


# -----------------------------------------------------------------------------
# Return a font from a string
# -----------------------------------------------------------------------------
def make_font(name, value=None):
    import tkinter.font as tkfont
    from tkinter import TclError
    try:
        font = tkfont.Font(name=name, exists=True)
    except TclError:
        font = tkfont.Font(name=name)
        font.delete_font = False
    except AttributeError:
        return None

    if value is None:
        return font

    if isinstance(value, tuple):
        font.configure(family=value[0])
        try:
            font.configure(size=value[1])
        except Exception:
            pass
        try:
            font.configure(weight=value[2])
        except Exception:
            pass
        try:
            font.configure(slant=value[3])
        except Exception:
            pass
    return font


# New class to provide config for everyone
# FIXME: create single instance of this and pass it to all parts of application
class _Config(configparser.ConfigParser):
    def __init__(self):
        configparser.ConfigParser.__init__(self)
        # FIXME: This is here to debug the fact that config is sometimes
        #        instantiated twice
        self._user_ini = __iniUser__
        print("new-config", __prg__, self)

    def set_userini(self, ini_file):
        self._user_ini = ini_file

    # -------------------------------------------------------------------------
    # Load configuration
    # -------------------------------------------------------------------------
    def load_configuration(self, system_only=False):
        # global _errorReport, language
        from globalVariables import glob_error_report, glob_language
        ini_files = [__iniSystem__]
        if not system_only:
            ini_files.append(self._user_ini)
        try:
            self.read(ini_files)
        except Exception:
            glob_error_report = self.getint("Connection", "errorreport", 1)

        self.initiate_translation()
        self.define_colors()
        self.search_py_modules()

    def define_colors(self):
        self.add_section("_colors")
        self.set('_colors', "GLOBAL_CONTROL_BACKGROUND", "White")
        self.set('_colors', "GLOBAL_FONT_COLOR", "White")

        # FIXME: Add color definition here!!
        pass

    def initiate_translation(self):
        """If locales are set, than the translation is initiated.
           With the initialization all strings in the _() format will be taken
           from the translation files.
        """
        language = self.getstr(__prg__, "language")
        # No translation needed if 'en' is selected!
        if language == 'en':
            return

        if not language:
            # import locale
            # loc = locale.getlocale()
            # print(f"default language: {loc}")
            # if loc not in __LANGUAGES__:
            #     loc = "_".split(loc)[0]
            # if loc in __LANGUAGES__:
            #     language = loc
            # else:
            #     return
            return  # FIXME: Check wether locale shall be used as default?
        lang = gettext.translation(
            __prg__,
            __localespath__,
            languages=[language]
        )
        lang.install()

    def search_py_modules(self):
        """Serch for all optional python modules like plugins, widgets, ...
        """
        # Find available controllers -----------------------------------------
        controllers = _search_py_modules(__controllerpath__)
        self.add_section("_controllers")
        for name, path in controllers.items():
            self.set('_controllers', name, path)
        # Find available gui elements ----------------------------------------
        modules = _search_py_modules(__pagespath__)
        self.add_section("_guipages")
        for name, path in modules.items():
            self.set('_guipages', name, path)
        modules = _search_py_modules(__framespath__)
        self.add_section("_guiframes")
        for name, path in modules.items():
            self.set('_guiframes', name, path)
        modules = _search_py_modules(__groupspath__)
        self.add_section("_guigroups")
        for name, path in modules.items():
            self.set('_guigroups', name, path)
        # Find available plugins ---------------------------------------------
        modules = _search_py_modules(__pluginpath__)
        self.add_section("_plugins")
        for name, path in modules.items():
            self.set('_plugins', name, path)

    # -------------------------------------------------------------------------
    # Print the full configuration to stdout
    # -------------------------------------------------------------------------
    def print_configuration(self):
        for s in self.sections():
            print("-" * 30)
            print(s)
            for name, value in self.items(s):
                print(name, value)

    # -------------------------------------------------------------------------
    # Remove items that are the same as in the default ini
    # and Save configuration file
    # -------------------------------------------------------------------------
    def save_configuration(self):
        import copy
        from configparser import NoOptionError, NoSectionError
        newconfig = copy.deepcopy(self)  # Remember config
        config = configparser.ConfigParser()
        config.read(__iniSystem__)

        # Remove options that are in default ini
        for section in self.sections():
            for item, value in self.items(section):
                try:
                    new = config.get(section, item)
                    if value == new:
                        newconfig.remove_option(section, item)
                except (NoOptionError, NoSectionError):
                    pass

        # Remove internal options
        for section in newconfig.sections():
            if section[0] == '_':
                newconfig.remove_section(section)

        f = open(self._user_ini, "w")
        newconfig.write(f)
        f.close()

    # -------------------------------------------------------------------------
    # add section if it doesn't exist
    # -------------------------------------------------------------------------
    def add_section_if_new(self, section):
        if not self.has_section(section):
            self.add_section(section)

    # -------------------------------------------------------------------------
    def getstr(self, section, name, default=""):
        try:
            return self.get(section, name)
        except Exception:
            return default

    # -------------------------------------------------------------------------
    def getutf(self, section, name, default=""):
        try:
            return self.get(section, name)
        except Exception:
            return default

    # -------------------------------------------------------------------------
    def getint(self, section, name, default=0):
        try:
            return int(self.get(section, name))
        except Exception:
            return default

    # -------------------------------------------------------------------------
    def getfloat(self, section, name, default=0.0):
        try:
            return float(self.get(section, name))
        except Exception:
            return default

    # # -----------------------------------------------------------------------
    def getbool(self, section, name, default=False):
        try:
            return bool(int(self.get(section, name)))
        except Exception:
            return default

    # -------------------------------------------------------------------------
    # Get font from configuration
    # -------------------------------------------------------------------------
    def getfont(self, name, default=None):
        try:
            value = self.get(_FONT_SECTION, name)
        except Exception:
            value = None

        if not value:
            font = make_font(name, default)
            self.setfont(name, font)
            return font

        if isinstance(value, str):
            value = tuple(value.split(","))

        if isinstance(value, tuple):
            font = make_font(name, value)
            if font is not None:
                return font
        return value

    # -------------------------------------------------------------------------
    # Set font in configuration
    # -------------------------------------------------------------------------
    def setfont(self, name, font):
        if font is None:
            return
        if isinstance(font, str):
            self.set(_FONT_SECTION, name, font)
        elif isinstance(font, tuple):
            self.set(_FONT_SECTION, name, ",".join(map(str, font)))
        else:
            self.set(
                _FONT_SECTION,
                name,
                f"{font.cget('family')},{font.cget('size')},"
                + f"{font.cget('weight')}",
            )

    # -------------------------------------------------------------------------
    def getrecent(self, recent):
        try:
            return self.get("File", f"recent.{int(recent)}")
        except configparser.NoOptionError:
            return None

    # -------------------------------------------------------------------------
    def setbool(self, section, name, value):
        self.set(section, name, str(int(value)))

    # -------------------------------------------------------------------------
    def setstr(self, section, name, value):
        self.set(section, name, str(value))

    # -------------------------------------------------------------------------
    # Add Recent
    # -------------------------------------------------------------------------
    def addrecent(self, filename):
        try:
            sfn = str(os.path.abspath(filename))
        except UnicodeEncodeError:
            sfn = filename

        last = _maxRecent - 1
        for i in range(_maxRecent):
            rfn = self.getrecent(i)
            if rfn is None:
                last = i - 1
                break
            if rfn == sfn:
                if i == 0:
                    return
                last = i - 1
                break

        # Shift everything by one
        for i in range(last, -1, -1):
            self.set("File", f"recent.{i + 1}", self.getrecent(i))
        self.set("File", "recent.0", sfn)

    def setlanguage(self, lang):
        self.setstr(__prg__, "language", lang)
        pass

    def getlanguage(self):
        language = self.getstr(__prg__, "language")
        return __LANGUAGES__.get(language, "")

    def getcontrollers(self, name=None):
        if name is None:
            controllers = {}
            for key, value in self.items("_controllers"):
                controllers[key] = value
            return controllers
        try:
            return self.getstr("_controllers", name)
        except Exception:
            return None

    def getcontrollerslist(self):
        controllers = {}
        for key, value in self.items("_controllers"):
            controllers[key] = value
        return sorted(controllers.keys())

    def getplugins(self):
        plugins = {}
        for key, value in self.items("_plugins"):
            plugins[key] = value
        return plugins


config = _Config()
