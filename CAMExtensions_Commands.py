# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""CAM Extensions - Command definitions"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class ShowOperationVariablesCommand:
    """Command to show the Operation Variables viewer"""
    
    def GetResources(self):
        return {
            'Pixmap': 'Path_Array',  # Using existing icon as placeholder
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Show Operation Variables"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Display CAM operation variables and their values")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        import OperationVariablesPanel
        
        # Get the active document
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document\n")
            return
        
        # Try to find a CAM Job in the document
        job = None
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, '__class__'):
                if 'Job' in obj.Proxy.__class__.__name__:
                    job = obj
                    break
        
        if not job:
            FreeCAD.Console.PrintWarning("No CAM Job found in document. Variables shown will be generic.\n")
        
        # Show the variables panel
        panel = OperationVariablesPanel.OperationVariablesPanel(job)
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


class ReorderBaseGeometryCommand:
    """Command to reorder base geometries in a CAM operation"""
    
    def GetResources(self):
        return {
            'Pixmap': 'Path_Array',  # Using existing icon as placeholder
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_ReorderBaseGeometry", "Reorder Base Geometry"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_ReorderBaseGeometry", "Reorder the base geometries in a CAM operation to control toolpath sequence")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        import BaseGeometryReorderPanel
        
        # Get the active document
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document\n")
            return
        
        # Try to find a selected CAM operation or get one from the user
        operation = None
        selection = FreeCADGui.Selection.getSelection()
        
        # Check if a CAM operation is selected
        for obj in selection:
            if hasattr(obj, 'Base') and obj.TypeId == 'Path::FeaturePython':
                operation = obj
                break
        
        # If no operation selected, try to find operations in the document
        if not operation:
            operations = []
            for obj in doc.Objects:
                if hasattr(obj, 'Base') and obj.TypeId == 'Path::FeaturePython':
                    operations.append(obj)
            
            if len(operations) == 0:
                FreeCAD.Console.PrintError("No CAM operations with Base geometry found\n")
                QtGui.QMessageBox.warning(
                    None,
                    "No Operation Found",
                    "Please select a CAM operation (Profile, Pocket, etc.) with base geometry first."
                )
                return
            elif len(operations) == 1:
                operation = operations[0]
            else:
                # Multiple operations - ask user to select one
                items = [op.Label for op in operations]
                item, ok = QtGui.QInputDialog.getItem(
                    None,
                    "Select Operation",
                    "Multiple operations found. Select one:",
                    items,
                    0,
                    False
                )
                if ok and item:
                    operation = operations[items.index(item)]
                else:
                    return
        
        # Check if operation has base geometry
        if not hasattr(operation, 'Base') or len(operation.Base) == 0:
            FreeCAD.Console.PrintWarning(f"Operation {operation.Label} has no base geometry\n")
            QtGui.QMessageBox.warning(
                None,
                "No Base Geometry",
                f"The selected operation '{operation.Label}' has no base geometry to reorder."
            )
            return
        
        # Show the reorder panel
        FreeCAD.Console.PrintMessage(f"Opening reorder panel for {operation.Label} ({len(operation.Base)} items)\n")
        panel = BaseGeometryReorderPanel.BaseGeometryReorderPanel(operation)
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


class SplitProfileCommand:
    """Command to split a Profile operation into separate operations (one per base geometry)"""
    
    def GetResources(self):
        return {
            'Pixmap': 'Path_Array',  # Using existing icon as placeholder
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_SplitProfile", "Split Profile into Separate Operations"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_SplitProfile", "Split a Profile with multiple base geometries into separate Profile operations for complete order control")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        import SplitProfilePanel
        
        # Get the active document
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document\n")
            return
        
        # Try to find a selected Profile operation
        operation = None
        selection = FreeCADGui.Selection.getSelection()
        
        # Check if a Profile operation is selected
        for obj in selection:
            if hasattr(obj, 'Proxy') and obj.Proxy.__class__.__name__ == 'ObjectProfile':
                operation = obj
                break
        
        # If no operation selected, try to find Profile operations in the document
        if not operation:
            operations = []
            for obj in doc.Objects:
                if hasattr(obj, 'Proxy') and obj.Proxy.__class__.__name__ == 'ObjectProfile':
                    if hasattr(obj, 'Base') and len(obj.Base) > 1:  # Only profiles with multiple base geometries
                        operations.append(obj)
            
            if len(operations) == 0:
                FreeCAD.Console.PrintError("No Profile operations with multiple base geometries found\n")
                QtGui.QMessageBox.warning(
                    None,
                    "No Profile Found",
                    "Please select a Profile operation with multiple base geometries first.\n\n"
                    "This tool splits a Profile into separate operations (one per base geometry) "
                    "so you have complete control over the cutting order."
                )
                return
            elif len(operations) == 1:
                operation = operations[0]
            else:
                # Multiple operations - ask user to select one
                items = [f"{op.Label} ({len(op.Base)} base geometries)" for op in operations]
                item, ok = QtGui.QInputDialog.getItem(
                    None,
                    "Select Profile to Split",
                    "Multiple Profile operations found. Select one:",
                    items,
                    0,
                    False
                )
                if ok and item:
                    operation = operations[items.index(item)]
                else:
                    return
        
        # Check if operation has multiple base geometries
        if not hasattr(operation, 'Base') or len(operation.Base) < 2:
            FreeCAD.Console.PrintWarning(f"Profile {operation.Label} has less than 2 base geometries\n")
            QtGui.QMessageBox.warning(
                None,
                "Not Enough Base Geometries",
                f"The selected Profile '{operation.Label}' only has {len(operation.Base) if hasattr(operation, 'Base') else 0} base geometry.\n\n"
                "This tool is for splitting Profiles with multiple base geometries."
            )
            return
        
        # Show the split panel
        FreeCAD.Console.PrintMessage(f"Opening split panel for {operation.Label} ({len(operation.Base)} base geometries)\n")
        panel = SplitProfilePanel.SplitProfilePanel(operation)
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


# Register the commands
FreeCADGui.addCommand('CAM_ShowOperationVariables', ShowOperationVariablesCommand())
FreeCADGui.addCommand('CAM_ReorderBaseGeometry', ReorderBaseGeometryCommand())
FreeCADGui.addCommand('CAM_SplitProfile', SplitProfileCommand())
