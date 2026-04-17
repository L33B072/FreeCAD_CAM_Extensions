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
from PySide import QtGui, QtCore


# Import and register commands immediately (available in all workbenches)
import CAMExtensions_Commands

# Import and register Sketcher commands
from sketcher import ParametricArrayCommands

# Import and apply patches from cam module
from cam import ArcFeedRatePatch

# Note: ProfileOrderPatch is experimental and not currently used
# from cam import ProfileOrderPatch

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
                
                # CAM Tools
                cam_tools_list = [
                    "CAM_ShowOperationVariables",
                    "CAM_SplitProfile"
                ]
                
                # Design Tools
                design_tools_list = [
                    "ProductionArray"
                ]
                
                # Add to submenus in the CAM menu
                self.cam_wb.appendMenu(["&CAM", "E&xtensions", "CAM Tools"], cam_tools_list)
                self.cam_wb.appendMenu(["&CAM", "E&xtensions", "Design Tools"], design_tools_list)
                
                # Add to toolbar (all tools)
                all_tools = cam_tools_list + design_tools_list
                self.cam_wb.appendToolbar("CAM Extensions", all_tools)
                
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


# Observer and Extension classes for Sketcher workbench
class SketcherWorkbenchObserver:
    """Observer to inject menu items when Sketcher workbench is activated"""
    
    def workbenchActivated(self, workbench_name):
        """Called when a workbench is activated"""
        if workbench_name == "SketcherWorkbench":
            self.inject_sketcher_menu()
    
    def inject_sketcher_menu(self):
        """Inject our command into Sketcher's menu structure"""
        try:
            # Get the main window
            mw = FreeCADGui.getMainWindow()
            
            # Find the Sketch menu
            sketch_menu = None
            for action in mw.menuBar().actions():
                if action.text().replace("&", "") == "Sketch":
                    sketch_menu = action.menu()
                    break
            
            if sketch_menu:
                # Add separator and our command
                sketch_menu.addSeparator()
                action = sketch_menu.addAction("Parametric Rectangular Array")
                action.triggered.connect(lambda: FreeCADGui.runCommand('Sketcher_ParametricArray'))
                action.setIcon(FreeCAD.getHomePath() + "Mod/FreeCAD_CAM_Extensions/Resources/icons/Sketcher_ParametricArray.svg")
                FreeCAD.Console.PrintMessage("CAM Extensions: Parametric Array added to Sketch menu\n")
            else:
                FreeCAD.Console.PrintWarning("Could not find Sketch menu\n")
                
            # Try to add toolbar button
            try:
                # Find Sketcher geometries toolbar
                for toolbar in mw.findChildren(QtGui.QToolBar):
                    if "Sketcher geometries" in toolbar.windowTitle():
                        action = toolbar.addAction("Array")
                        action.triggered.connect(lambda: FreeCADGui.runCommand('Sketcher_ParametricArray'))
                        action.setIcon(FreeCAD.getHomePath() + "Mod/FreeCAD_CAM_Extensions/Resources/icons/Sketcher_ParametricArray.svg")
                        action.setToolTip("Parametric Rectangular Array")
                        FreeCAD.Console.PrintMessage("CAM Extensions: Array button added to toolbar\n")
                        break
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Could not add toolbar button: {e}\n")
        
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not inject Sketcher menu: {e}\n")
            import traceback
            traceback.print_exc()


class SketcherWorkbenchExtension:
    """Extension to add parametric array command to the Sketcher workbench"""
    
    def __init__(self):
        # Register a workbench activated observer to inject menu when Sketcher loads
        self.observer = SketcherWorkbenchObserver()
        FreeCADGui.getMainWindow().workbenchActivated.connect(self.observer.workbenchActivated)
        FreeCAD.Console.PrintMessage("CAM Extensions: Sketcher parametric array available\n")


# Initialize Sketcher extension
try:
    sketcher_extension = SketcherWorkbenchExtension()
except Exception as e:
    FreeCAD.Console.PrintWarning(f"Sketcher Extensions initialization: {e}\n")
