# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""FreeCAD CAM Extensions - GUI Initialization"""

import FreeCAD
import FreeCADGui


class CAMExtensionsWorkbench(FreeCADGui.Workbench):
    """CAM Extensions workbench"""
    
    MenuText = "CAM Extensions"
    ToolTip = "Enhanced CAM workbench features"
    Icon = """
        /* XPM */
        static char * cam_ext_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #000000",
        "+	c #0000FF",
        "                ",
        "   .........    ",
        "   .+++++++.    ",
        "   .+.....+.    ",
        "   .+.+++.+.    ",
        "   .+.+.+.+.    ",
        "   .+.+++.+.    ",
        "   .+.....+.    ",
        "   .+++++++.    ",
        "   .++...++.    ",
        "   .+.+++.+.    ",
        "   .+.+.+.+.    ",
        "   .+.+++.+.    ",
        "   .++...++.    ",
        "   .........    ",
        "                "};
        """
    
    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        from . import OperationVariablesPanel
        
        # Import the command classes
        import CAMExtensions_Commands
        
        # List of command names
        self.list = ["CAM_ShowOperationVariables"]
        
        # Create toolbars and menus
        self.appendToolbar("CAM Extensions", self.list)
        self.appendMenu("CAM E&xtensions", self.list)
        
        FreeCAD.Console.PrintMessage("CAM Extensions workbench initialized\n")
    
    def Activated(self):
        """This function is executed when the workbench is activated"""
        return
    
    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return
    
    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen"""
        self.appendContextMenu("CAM Extensions", self.list)
    
    def GetClassName(self):
        """Return workbench classname"""
        return "Gui::PythonWorkbench"


# Add the workbench to FreeCAD
FreeCADGui.addWorkbench(CAMExtensionsWorkbench())
