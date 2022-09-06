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
    __toolspath__,
    __pluginpath__,
    __pagespath__,
    __framespath__,
    __groupspath__,
    __iconpath__,
    __imagepath__,
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


def _search_files(path, recursive=False, type=None):
    import glob

    files = []

    path = [path]

    p = f"{path.pop(0)}/*"
    if recursive:
        p = f"{p}*/*"
    if type:
        p = f"{p}.{type}"
    for f in glob.glob(p, recursive=recursive):
        if os.path.isdir(f):
            continue
        name, ext = os.path.splitext(os.path.basename(f))
        ext = ext[1:] if ext[0] == "." else ext
        f_ = {
            "dir": os.path.dirname(os.path.abspath(f)),
            "basename": os.path.basename(f),
            "name": name,
            "ext": ext,
            "full": f,
        }
        files.append(f_)

    return files


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


# FIXME: Icons need description and dicts in class!
# from PIL import ImageTk, Image
# myimg = ImageTk.PhotoImage(Image.open('myimage.png'))
class _Icon():
    __icons = {}

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        icons = self.__icons
        icons[key] = value

    def keys(self):
        icons = self.__icons
        return icons.keys()

    def get(self, key, default=None):
        import tkinter as tk
        icons = self.__icons
        if key not in icons:
            return default
        if isinstance(icons[key], str):
            icons[key] = tk.PhotoImage(file=icons[key])
            if config.getbool("CNC", "doublesizeicon"):
                icons[key] = icons[key].zoom(2, 2)
        return icons[key]


class _Image():
    __images = {}

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        images = self.__images
        images[key] = value

    def keys(self):
        images = self.__images
        return images.keys()

    def get(self, key, default=None):
        import tkinter as tk
        images = self.__images
        if key not in images:
            return default
        if isinstance(images[key], str):
            images[key] = tk.PhotoImage(file=images[key])
            if config.getbool("CNC", "doublesizeicon"):
                images[key] = images[key].zoom(2, 2)
        return images[key]


# New class to provide config for everyone
# FIXME: create single instance of this and pass it to all parts of application
class _Config(configparser.ConfigParser):
    machines = {}

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
        # from globalVariables import glob_error_report, glob_language
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
        self.search_images()
        self.parse_machines()

        self.check_configuration()

    def check_configuration(self):
        """ Check the sanity of the configuration and raise an exception
            if not.
        """
        from pydoc import locate
        # self.add_section("_enabled_pages")
        active_groups = []
        active_pannels = []
        self.active_pages = []

        for page in self[__prg__]["ribbon"].split(" "):
            if page[-1] == ">":
                page = page[:-1]
            # FIXME: Add check if page exist
            self.active_pages.append(page)
            if f"{page}.ribbon" not in self[__prg__]:
                pass  # FIXME: Raise an exception!
            groups = self[__prg__][f"{page}.ribbon"].split(" ")
            if f"{page}.page" not in self[__prg__]:
                pass  # FIXME: Raise an exception!
            panels = self[__prg__][f"{page}.page"].split(" ")

            while groups:
                g = groups.pop()
                if g not in self["_guigroups"]:
                    print(f"ERROR: {g}, from {page} was not found in groups!")
                    continue  # FIXME: Raise an exception!
                if g in active_groups:
                    continue
                active_groups.append(g)
                module_path = self["_guigroups"][g]
                module = locate(module_path)
                try:
                    groups.extend(module.required_groups)
                except AttributeError:
                    pass
                try:
                    panels.extend(module.required_frames)
                except AttributeError:
                    pass

            while panels:
                p = panels.pop()
                if p[-1] == "*":
                    p = p[:-1]
                if p not in self["_guiframes"]:
                    print(f"ERROR: {g}, from {page} was not found in frames!")
                    continue  # FIXME: Raise an exception!
                elif p not in active_pannels:
                    active_pannels.append(p)

        self.active_groups = active_groups
        self.active_pannels = active_pannels

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
        """Search for all optional python modules like plugins, widgets, ...
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
        # Find available tools -----------------------------------------------
        modules = _search_py_modules(__toolspath__)
        self.add_section("_tools")
        for name, path in modules.items():
            self["_tools"][name] = path
        # Find available plugins ---------------------------------------------
        modules = _search_py_modules(__pluginpath__)
        self.add_section("_plugins")
        for name, path in modules.items():
            self.set('_plugins', name, path)

    def search_images(self):
        """ Search for icons and images in the project
        """
        global icon
        for ext in ["gif", "png"]:
            ico = _search_files(__iconpath__, type=ext)
            for x in ico:
                icon[x["name"]] = x["full"]

        global image
        for ext in ["gif", "png"]:
            img = _search_files(__imagepath__, type=ext)
            for x in img:
                image[x["name"]] = x["full"]

    def parse_machines(self):
        """ Parse the machine settings to the internal format
        """
        machines = self.machines
        for key, value in self["Machines"].items():
            if key == "last_used":
                continue
            name, key = key.split(".")
            if name not in self.machines:
                machines[name] = {"axis": {},
                                  "table": {}}
                machines[name]["axis"]["names"] = []
                for a in self["Machines"][f"{name}.axis"][1:-1].split(","):
                    machines[name]["axis"][a] = {}
                    machines[name]["axis"]["names"].append(a)
            if value.startswith("[") and value.endswith("]"):
                if key == "axis":
                    continue
                if "," in value:
                    value = value[1:-1].split(",")
                elif "-" in value:
                    machines[name][key] = {}
                    machines[name][key]["min"], machines[name][key]["max"] = \
                        value[1:-1].split("-")
                    continue
                else:
                    value = value[1:-1]
            else:
                machines[name][key] = value
                continue
            if key == "table" and len(value) == 2:
                machines[name][key]["x"] = value[0]
                machines[name][key]["y"] = value[1]
            elif key == "leftfront" and len(value) == 2:
                machines[name]["table"]["x_off"] = value[0]
                machines[name]["table"]["y_off"] = value[1]
            elif len(value) == len(machines[name]["axis"]["names"]):
                for i in range(len(machines[name]["axis"]["names"])):
                    a = machines[name]["axis"]["names"][i]
                    machines[name]["axis"][a][key] = value[i]
            else:
                machines[name][key] = value

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
            return self[section].getboolean(name)
        except ValueError:
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
icon = _Icon()
image = _Image()
