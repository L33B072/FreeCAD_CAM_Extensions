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


# Import and register commands immediately (available in all workbenches)
import CAMExtensions_Commands

FreeCAD.Console.PrintMessage("CAM Extensions loaded - commands available in CAM workbench\n")


# Extend the CAM workbench to add our commands
class CAMWorkbenchExtension:
    """Extension to add commands to the CAM workbench"""
    
    def __init__(self):
        # Get the original CAM workbench
        self.cam_wb = FreeCADGui.getWorkbench("PathWorkbench")
        if self.cam_wb:
            self.extend_cam_workbench()
    
    def extend_cam_workbench(self):
        """Add our commands to the CAM workbench menus and toolbars"""
        try:
            # Store the original Initialize method
            original_initialize = self.cam_wb.Initialize
            
            # Define new Initialize that calls original + adds our stuff
            def new_initialize():
                original_initialize()
                
                # Add our commands to CAM workbench
                cam_extensions_list = ["CAM_ShowOperationVariables"]
                
                # Add to a submenu in the CAM menu
                self.cam_wb.appendMenu(["CAM", "E&xtensions"], cam_extensions_list)
                
                # Optionally add to toolbar
                self.cam_wb.appendToolbar("CAM Extensions", cam_extensions_list)
                
                FreeCAD.Console.PrintMessage("CAM Extensions commands added to CAM workbench\n")
            
            # Replace the Initialize method
            self.cam_wb.Initialize = new_initialize
            
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not extend CAM workbench: {e}\n")
            FreeCAD.Console.PrintWarning("Commands are still available via Python console\n")


# Try to extend the CAM workbench
try:
    extension = CAMWorkbenchExtension()
except Exception as e:
    FreeCAD.Console.PrintWarning(f"CAM Extensions: {e}\n")
