""" Main Frame and initialization of the GUI
"""
# import os
# import sys
import tkinter as tk
from tkinter import ttk
from typing import Final

# from gui.app import RIBBON_HIDDEN


# _BACKGROUND_DISABLE = "#A6A2A0"
# _BACKGROUND = "#E6E2E0"
# # _BACKGROUND_GROUP = "#B6B2B0"

# _BACKGROUND_GROUP2 = "#B0C0C0"
# _BACKGROUND_GROUP3 = "#A0C0A0"
# _BACKGROUND_GROUP4 = "#B0C0A0"

# _FOREGROUND_GROUP = "White"
# _ACTIVE_COLOR = "LightYellow"
# _LABEL_SELECT_COLOR = "#C0FFC0"

# Spacing:
RIBBON_HEIGHT: Final = 103
RIBBON_LABEL_HEIGHT: Final = 16

# Fonts:
TABFONT: Final = ("Sans", "-14", "bold")
FONT: Final = ("Sans", "-11")

# Colors:
FONT_COLOR_DARK: Final = "Black"
FONT_COLOR_BRIGHT: Final = "White"
FONT_COLOR_PANNEL_COLAPSE: Final = "DarkBlue"
BACKGROUND_TOPBAR: Final = "#A6A2A0"
BACKGROUND_ACTIVE: Final = "LightYellow"
ACTIVE_COLOR: Final = BACKGROUND_ACTIVE
BACKGROUND_RIBBON: Final = "#E6E2E0"
BACKGROUND_RIBBON_GROUP: Final = "#B6B2B0"
BACKGROUND_RIBBON_LABEL: Final = "#B6B2B0"
FOREGROUND_RIBBON_LABEL: Final = "White"
BACKGROUND_RIBBON_SELECTED: Final = "#C0FFC0"
BACKGROUND_STATUSBAR: Final = "#B6B2B0"
BACKGROUND_PANEL: Final = BACKGROUND_RIBBON
FOREGROUND_PANEL: Final = "DarkBlue"

STATECOLOR = {
    "Idle": "Yellow",
    "Run": "LightGreen",
    "Alarm": "Red",
    "Jog": "Green",
    "Home": "Green",
    "Check": "Magenta2",
    "Sleep": "LightBlue",
    "Hold": "Orange",
    "Hold:0": "Orange",
    "Hold:1": "OrangeRed",
    "Queue": "OrangeRed",
    "Door": "Red",
    "Door:0": "OrangeRed",
    "Door:1": "Red",
    "Door:2": "Red",
    "Door:3": "OrangeRed",
    "Connected": "Yellow",
    "Not connected": "OrangeRed",
    "Default": "LightYellow",
}


def load_styles():
    style = ttk.Style()

    ###########################################################################
    # Default
    ###########################################################################
    style.configure('TFrame',
                    # background=BACKGROUND_RIBBON,
                    borderwidth=0,
                    relief='flat')
    style.configure('TButton',
                    # background=BACKGROUND_RIBBON,
                    borderwidth=1,
                    relief='raised',
                    padding=(0, 0, 0, 0),
                    border=1)
    style.map('TButton', background=[
        ('active', BACKGROUND_ACTIVE)])
    style.configure('TEntry',
                    background="White",
                    borderwidth=1,
                    relief='sunken',
                    padding=(0, 0, 0, 0),
                    border=1)
    style.map('TButton', background=[
        ('active', BACKGROUND_ACTIVE)])


    # style.theme_use('classic')

    style.configure('StatusBar.TFrame',
                    background=BACKGROUND_STATUSBAR,
                    borderwidth=1,
                    relief='sunken')
    style.configure('StatusBar.TLabel',
                    foreground="DarkRed",
                    # background='red',
                    borderwidth=1,
                    relief='sunken')

    #     self.config(
    #     relief="flat",
    #     activebackground=_ACTIVE_COLOR,
    #     font=_FONT,
    #     borderwidth=1,
    #     highlightthickness=0,
    #     padx=2,
    #     pady=0,
    # )

    ###########################################################################
    # Top Bar
    ###########################################################################
    style.configure('TopBar.TFrame',
                    background=BACKGROUND_TOPBAR,
                    borderwidth=1,
                    relief='flat')
    style.configure('TopBar.TButton',
                    background=BACKGROUND_TOPBAR,
                    borderwidth=0,
                    relief='flat',
                    padding=(0, 0, 0, 0),
                    border=0)
    style.map('TopBar.TButton', background=[
        ('active', BACKGROUND_ACTIVE)])
    style.configure('Tabs.Toolbutton',
                    font=TABFONT,
                    indicator=False,
                    compound="left",
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_TOPBAR,
                    border=BACKGROUND_RIBBON_GROUP,
                    borderwidth=0,
                    padx=5,
                    width=7,
                    relief='flat')
    style.map(
        'Tabs.Toolbutton',
        foreground=[
            ('disabled', 'white'),
            ('selected', FONT_COLOR_DARK),
            ('!selected', FONT_COLOR_DARK)],
        background=[
            ('active', BACKGROUND_ACTIVE),
            ('disabled', 'black'),
            ('selected', BACKGROUND_RIBBON),
            ('!selected', BACKGROUND_TOPBAR)],
        relief=[
            ('disabled', 'flat'),
            ('selected', 'raised'),
            ('!selected', 'flat'),
            ('active', 'flat')],
    )

    ###########################################################################
    # Ribbon
    ###########################################################################
    style.configure('Ribbon.TFrame',
                    background=BACKGROUND_RIBBON,
                    borderwidth=0,
                    padding=(0, 0, 0, 0),
                    relief='raised')
    style.configure('Ribbon.TSeparator',
                    background=BACKGROUND_RIBBON,
                    # foreground="DarkRed",
                    borderwidth=0,
                    relief='groove',
                    padding=(2, 2, 0, 0))
    style.configure('RibbonGroup.TFrame',
                    background=BACKGROUND_RIBBON,
                    borderwidth=0,
                    relief='flat')
    style.configure('RibbonGroup.TButton',
                    font=FONT,
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_RIBBON,
                    borderwidth=0,
                    relief='flat',
                    padding=[0, 0, 0, 0],
                    border=0)
    style.map('RibbonGroup.TButton', background=[
        ('active', BACKGROUND_ACTIVE)])
    style.configure('RibbonGroup.TButton.label',
                    anchor="w")
    style.configure('RibbonGroup.TRadiobutton',
                    font=FONT,
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_RIBBON,
                    relief='flat',
                    padding=[0, 0, 0, 0],
                    indicator=False,
                    indicatorcolor=BACKGROUND_RIBBON,
                    indicatorbackground=BACKGROUND_RIBBON,
                    indicatormargin=[0, 0, 0, 0],
                    indicatorrelief='flat',
                    borderwidth=0,
                    border=0)
    style.map('RibbonGroup.TRadiobutton',
              background=[
                  ('active', BACKGROUND_ACTIVE),
                  ('selected', BACKGROUND_RIBBON_SELECTED)],
              )
    style.configure('RibbonGroup.Toolbutton',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_RIBBON,
                    border=BACKGROUND_RIBBON,
                    borderwidth=0,
                    padding=[2, 2, 1, 1],
                    relief='flat')
    style.map('RibbonGroup.Toolbutton',
              background=[
                  ('active', BACKGROUND_ACTIVE),
                  ('selected', BACKGROUND_RIBBON_SELECTED)],
              )
    style.configure('RibbonGroup.TCheckbutton',
                    font=FONT,
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_RIBBON,
                    relief='flat',
                    padding=[0, 0, 0, 0],
                    indicatorcolor=BACKGROUND_RIBBON,
                    indicatorbackground=BACKGROUND_RIBBON,
                    indicatormargin=[0, 0, 0, 0],
                    indicatorrelief='flat',
                    borderwidth=0,
                    border=0)
    style.map('RibbonGroup.TCheckbutton',
              background=[
                  ('active', BACKGROUND_ACTIVE),
                  ('selected', BACKGROUND_RIBBON_SELECTED)],
              )
    style.configure('RibbonGroup.TMenubutton',
                    font=FONT,
                    foreground=FONT_COLOR_DARK,
                    background=BACKGROUND_RIBBON,
                    relief='flat',
                    padding=[0, 0, 0, 0],
                    borderwidth=0,
                    border=0)
    style.configure('RibbonGroup.TLabel',
                    font=FONT,
                    background=BACKGROUND_RIBBON,
                    relief='flat',
                    padding=(0, 0, 0, 0),
                    border=0)
    style.configure('Bottom.RibbonGroup.TButton',
                    background=BACKGROUND_RIBBON_LABEL,
                    foreground=FOREGROUND_RIBBON_LABEL)
    style.configure('Bottom.RibbonGroup.TFrame',
                    background=BACKGROUND_RIBBON_LABEL,
                    foreground=FOREGROUND_RIBBON_LABEL,
                    borderwidth=1,
                    relief='flat')
    style.configure('Bottom.RibbonGroup.TLabel',
                    background=BACKGROUND_RIBBON_LABEL,
                    foreground=FOREGROUND_RIBBON_LABEL,
                    relief='flat',
                    padding=(0, 0, 0, 0),
                    border=0)

    ###########################################################################
    # Left side panel
    ###########################################################################
    style.configure('Panel.TFrame',
                    # background=BACKGROUND_PANEL,
                    borderwidth=0,
                    padding=(0, 0, 0, 0),
                    relief='flat')
    style.configure('Panel.TLabelFrame.Label',
                    # background=BACKGROUND_PANEL,
                    foreground=FOREGROUND_PANEL,
                    borderwidth=0,
                    padding=(0, 0, 0, 0),
                    relief='flat')
    style.configure('Panel.TButton',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground=FONT_COLOR_DARK,
                    borderwidth=1,
                    padding=1,
                    relief='raised')
    style.configure('Connected.Panel.TButton',
                    background="LightGreen")
    style.map(
        'Connected.Panel.TButton',
        background=[('active', "LightGreen",)],)
    style.configure('Unconnected.Panel.TButton',
                    background="Salmon")
    style.map(
        'Unconnected.Panel.TButton',
        background=[('active', "Salmon",)],)
    style.configure('Panel.TCheckbutton',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground=FONT_COLOR_DARK,
                    borderwidth=1,
                    padding=(2, 1),
                    relief='raised')
    style.configure('Panel.TEntry',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    background="White",
                    foreground=FONT_COLOR_DARK,
                    borderwidth=0,
                    padding=1,
                    justify="right",
                    relief='flat')
    style.configure('Control.Panel.TLabel',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    padx=3,
                    pady=3,
                    ipadx=10,
                    ipady=1,
                    # width=7,
                    )
    style.configure('Control.Panel.TCombobox',
                    font=FONT,
                    indicator=False,
                    # background=BACKGROUND_PANEL,
                    padx=3,
                    pady=3,
                    ipadx=10,
                    ipady=1,
                    # width=7,
                    )
    style.configure('Control.Panel.TButton',
                    font=TABFONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    padx=3,
                    pady=3,
                    ipadx=10,
                    ipady=1,
                    # width=7,
                    )
    style.map(
        'Control.Panel.TButton',
        background=[
            ('active', BACKGROUND_ACTIVE), ],
        # relief=[
        #     ('disabled', 'flat'),
        #     ('selected', 'raised'),
        #     ('!selected', 'flat'),
        #     ('active', 'flat')],
    )

    style.configure('Collapsible.TCheckbutton',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground=FONT_COLOR_PANNEL_COLAPSE,
                    borderwidth=0,
                    padding=0,
                    relief='flat')
    style.configure('Collapsible.TButton',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground=FONT_COLOR_PANNEL_COLAPSE,
                    borderwidth=0,
                    padding=0,
                    relief='flat')
    style.configure('Collapsible.TLabel',
                    font=FONT,
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground=FONT_COLOR_PANNEL_COLAPSE,
                    borderwidth=0,
                    padding=0,
                    relief='flat')

    style.configure('Workspaces.Panel.TButton',
                    font="Helvetica,14",
                    indicator=False,
                    compound="left",
                    # background=BACKGROUND_PANEL,
                    foreground="DarkRed",
                    borderwidth=1,
                    padding=1,
                    relief='raised')

    style.configure('StateBtn.TButton',
                    font=("Helvetica", 12, "bold"),
                    indicator=False,
                    compound="left",
                    background=STATECOLOR['Not connected'],
                    borderwidth=1,
                    padding=1,
                    relief='raised')
    for key, color in STATECOLOR.items():
        key = key.replace(":", "_").replace(" ", "_")
        stl = f"{key}.StateBtn.TButton"
        style.configure(stl,
                        background=color)
        style.map(
            stl,
            background=[('active', color,)],)

    ###########################################################################
    # Status Bar
    ###########################################################################
    style.configure('StatusBar.TLabel',
                    # background=BACKGROUND_RIBBON_LABEL,
                    foreground="DarkRed",
                    relief='sunken',
                    width=12,
                    padding=(0, 0, 0, 0),
                    border=0)

    ###########################################################################
    # Dialogs
    ###########################################################################
    style.configure('Dialog.TFrame',
                    background="#707070",
                    borderwidth=2,
                    relief="sunken",)
    style.configure('Dialog.TLabelFrame.Label',
                    foreground="DarkRed",
                    borderwidth=0,
                    padding=(0, 0, 0, 0),
                    relief='flat')
    style.configure('Dialog.TButton',
                    borderwidth=1,
                    indicator=False,
                    relief='raised',
                    padding=1,)
    style.configure('Dialog.TLabel',
                    background="#707070",
                    foreground="#ffffff",
                    relief='raised',
                    padding=(0, 0, 0, 0),
                    border=0)
    style.configure('Text1.Dialog.TLabel',
                    relief='flat',
                    font="Helvetica -10",
                    justify="left",)
    style.configure('Blue.Text1.Dialog.TLabel',
                    foreground="DarkBlue",)
    style.configure('Text2.Dialog.TLabel',
                    relief='flat',
                    font="Helvetica -12",
                    justify="left",)

    ###########################################################################
    # Tooltip
    ###########################################################################
    style.configure('Tooltip.TLabel',
                    background="LightYellow",
                    foreground="Black",
                    font=("Helvetica", "-12"),
                    padding=(3, 3, 3, 0),
                    border=0)
