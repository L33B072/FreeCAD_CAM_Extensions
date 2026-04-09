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

# Import and apply patches
import ArcFeedRatePatch

# Note: ProfileOrderPatch is experimental and not currently used
# import ProfileOrderPatch

FreeCAD.Console.PrintMessage("CAM Extensions loaded - commands registered\n")

# Apply arc feed rate patch to add property to Profile operations
if ArcFeedRatePatch.apply_arc_feed_rate_patch():
    FreeCAD.Console.PrintMessage("CAM Extensions: Arc feed rate patch applied successfully\n")
else:
    FreeCAD.Console.PrintWarning("CAM Extensions: Arc feed rate patch failed to apply\n")

# Note: Profile order patch is disabled in favor of the Split Profile tool
# if ProfileOrderPatch.apply_profile_order_patch():
#     FreeCAD.Console.PrintMessage("CAM Extensions: Profile order patch applied successfully\n")
# else:
#     FreeCAD.Console.PrintWarning("CAM Extensions: Profile order patch failed to apply\n")


# Extend the CAM workbench to add our commands
class CAMWorkbenchExtension:
    """Extension to add commands to the CAM workbench"""
    
    def __init__(self):
        # Try different possible names for the CAM/Path workbench
        cam_wb_names = ["Path", "PathWorkbench", "CAM", "CAMWorkbench"]
        self.cam_wb = None
        
        for name in cam_wb_names:
            try:
                self.cam_wb = FreeCADGui.getWorkbench(name)
                if self.cam_wb:
                    FreeCAD.Console.PrintMessage(f"CAM Extensions: Found CAM workbench as '{name}'\n")
                    self.extend_cam_workbench()
                    break
            except:
                continue
        
        if not self.cam_wb:
            FreeCAD.Console.PrintMessage("CAM Extensions: Will extend CAM workbench when it's activated\n")
    
    def extend_cam_workbench(self):
        """Add our commands to the CAM workbench menus and toolbars"""
        try:
            # Store the original Initialize method
            original_initialize = self.cam_wb.Initialize
            
            # Define new Initialize that calls original + adds our stuff
            def new_initialize():
                original_initialize()
                
                # Add our commands to CAM workbench
                cam_extensions_list = [
                    "CAM_ShowOperationVariables",
                    "CAM_ReorderBaseGeometry",
                    "CAM_SplitProfile"
                ]
                
                # Add to a submenu in the CAM menu
                self.cam_wb.appendMenu(["&CAM", "E&xtensions"], cam_extensions_list)
                
                # Add to toolbar
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
    FreeCAD.Console.PrintWarning(f"CAM Extensions initialization: {e}\n")
