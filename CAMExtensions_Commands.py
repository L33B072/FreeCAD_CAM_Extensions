# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""CAM Extensions - Command definitions"""

import os
import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class ShowOperationVariablesCommand:
    """Command to show the Operation Variables viewer"""
    
    def GetResources(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'Resources', 'icons', 'CAM_ShowOperationVariables.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Show Operation Variables"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Display CAM operation variables and their values")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        from cam import OperationVariablesPanel
        
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


# Reorder Base Geometry Command - DEPRECATED
# Use Split Profile and reorder operations in the tree instead
# class ReorderBaseGeometryCommand:
#     """Command to reorder base geometries in a CAM operation"""
#     
#     def GetResources(self):
#         return {
#             'Pixmap': 'Draft_PathArray',  # Array/path icon suggesting ordering
#             'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_ReorderBaseGeometry", "Reorder Base Geometry"),
#             'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_ReorderBaseGeometry", "Reorder the base geometries in a CAM operation to control toolpath sequence")
#         }
#     
#     def Activated(self):
#         """Execute when the command is activated"""
#         from cam import BaseGeometryReorderPanel
#         
#         # Get the active document
#         doc = FreeCAD.ActiveDocument
#         if not doc:
#             FreeCAD.Console.PrintError("No active document\n")
#             return
#         
#         # Try to find a selected CAM operation or get one from the user
#         operation = None
#         selection = FreeCADGui.Selection.getSelection()
#         
#         # Check if a CAM operation is selected
#         for obj in selection:
#             if hasattr(obj, 'Base') and obj.TypeId == 'Path::FeaturePython':
#                 operation = obj
#                 break
#         
#         # If no operation selected, try to find operations in the document
#         if not operation:
#             operations = []
#             for obj in doc.Objects:
#                 if hasattr(obj, 'Base') and obj.TypeId == 'Path::FeaturePython':
#                     operations.append(obj)
#             
#             if len(operations) == 0:
#                 FreeCAD.Console.PrintError("No CAM operations with Base geometry found\n")
#                 QtGui.QMessageBox.warning(
#                     None,
#                     "No Operation Found",
#                     "Please select a CAM operation (Profile, Pocket, etc.) with base geometry first."
#                 )
#                 return
#             elif len(operations) == 1:
#                 operation = operations[0]
#             else:
#                 # Multiple operations - ask user to select one
#                 items = [op.Label for op in operations]
#                 item, ok = QtGui.QInputDialog.getItem(
#                     None,
#                     "Select Operation",
#                     "Multiple operations found. Select one:",
#                     items,
#                     0,
#                     False
#                 )
#                 if ok and item:
#                     operation = operations[items.index(item)]
#                 else:
#                     return
#         
#         # Check if operation has base geometry
#         if not hasattr(operation, 'Base') or len(operation.Base) == 0:
#             FreeCAD.Console.PrintWarning(f"Operation {operation.Label} has no base geometry\n")
#             QtGui.QMessageBox.warning(
#                 None,
#                 "No Base Geometry",
#                 f"The selected operation '{operation.Label}' has no base geometry to reorder."
#             )
#             return
#         
#         # Show the reorder panel
#         FreeCAD.Console.PrintMessage(f"Opening reorder panel for {operation.Label} ({len(operation.Base)} items)\n")
#         panel = BaseGeometryReorderPanel.BaseGeometryReorderPanel(operation)
#         FreeCADGui.Control.showDialog(panel)
#     
#     def IsActive(self):
#         """Return True if command should be active"""
#         return FreeCAD.ActiveDocument is not None


class SplitProfileCommand:
    """Command to split a Profile operation into separate operations (one per base geometry)"""
    
    def GetResources(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'Resources', 'icons', 'CAM_SplitProfile.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_SplitProfile", "Split Profile into Separate Operations"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_SplitProfile", "Split a Profile with multiple base geometries into separate Profile operations for complete order control")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        from cam import SplitProfilePanel
        
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
                    # Include ALL profiles - we can auto-discover base geometries if needed
                    operations.append(obj)
            
            if len(operations) == 0:
                FreeCAD.Console.PrintError("No Profile operations found\n")
                QtGui.QMessageBox.warning(
                    None,
                    "No Profile Found",
                    "Please select a Profile operation first.\n\n"
                    "This tool splits a Profile into separate operations (one per base geometry) "
                    "so you have complete control over the cutting order.\n\n"
                    "If your Profile doesn't have explicit base geometries, they will be "
                    "auto-discovered from the Job's Model (bottom faces)."
                )
                return
            elif len(operations) == 1:
                operation = operations[0]
            else:
                # Multiple operations - ask user to select one
                items = []
                for op in operations:
                    base_count = len(op.Base) if hasattr(op, 'Base') else 0
                    if base_count == 0:
                        items.append(f"{op.Label} (no base - will auto-discover)")
                    else:
                        items.append(f"{op.Label} ({base_count} base geometries)")
                
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
        if not hasattr(operation, 'Base'):
            FreeCAD.Console.PrintWarning(f"Profile {operation.Label} has no Base property\n")
            return
        
        # Debug output
        FreeCAD.Console.PrintMessage(f"\n=== Split Profile Debug ===\n")
        FreeCAD.Console.PrintMessage(f"Operation: {operation.Label}\n")
        FreeCAD.Console.PrintMessage(f"Base items count: {len(operation.Base) if operation.Base else 0}\n")
        
        # Count total features across all base items
        total_features = 0
        if operation.Base:
            for i, base_item in enumerate(operation.Base):
                obj = base_item[0]
                features = base_item[1]
                FreeCAD.Console.PrintMessage(f"  Base item {i}: Object={obj.Label}, Features={features} (count={len(features)})\n")
                total_features += len(features)
        
        FreeCAD.Console.PrintMessage(f"Total features before auto-discovery: {total_features}\n")
        
        # Allow operation even if Base is empty - we'll auto-discover in the panel
        if total_features == 0:
            FreeCAD.Console.PrintMessage("No explicit base geometries - will attempt auto-discovery from Job Model\n")
        
        FreeCAD.Console.PrintMessage(f"===========================\n\n")
        
        # Show the split panel (auto-discovery happens in the panel's __init__)
        FreeCAD.Console.PrintMessage(f"Opening split panel for {operation.Label}\n")
        panel = SplitProfilePanel.SplitProfilePanel(operation)
        
        # After panel initialization, check if we have enough to split
        if len(panel.split_items) < 2:
            FreeCAD.Console.PrintWarning(f"Profile {operation.Label} has less than 2 base geometries even after auto-discovery\n")
            item_count = len(panel.split_items)
            QtGui.QMessageBox.warning(
                None,
                "Not Enough Base Geometries",
                f"The selected Profile '{operation.Label}' only has {item_count} base geometry.\n\n"
                "This tool is for splitting Profiles with multiple base geometries.\n\n"
                f"Auto-discovery from the Job Model found {item_count} bottom face(s).\n"
                "You may need to manually set base geometries in the Profile operation."
            )
            return
        
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


class ProductionArrayCommand:
    """Command to create a production array of parts as separate Bodies"""
    
    def GetResources(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'Resources', 'icons', 'ProductionArray.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("ProductionArray", "Production Array"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("ProductionArray", "Create a parametric array of parts as separate Bodies for production manufacturing")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        from design import ProductionArrayPanel
        
        # Get the active document
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document\n")
            return
        
        # Try to find a selected Sketch
        sketch = None
        selection = FreeCADGui.Selection.getSelection()
        
        # Check if a Sketch is selected
        for obj in selection:
            if obj.TypeId == 'Sketcher::SketchObject':
                sketch = obj
                break
        
        # If no sketch selected, try to find sketches in the document
        if not sketch:
            sketches = []
            for obj in doc.Objects:
                if obj.TypeId == 'Sketcher::SketchObject':
                    # Only include sketches that are not already in a Body with a Pad
                    is_in_padded_body = False
                    for parent in obj.InList:
                        if parent.TypeId == 'PartDesign::Body':
                            # Check if this body has a Pad
                            for child in parent.Group:
                                if 'Pad' in child.TypeId:
                                    is_in_padded_body = True
                                    break
                    
                    if not is_in_padded_body:
                        sketches.append(obj)
            
            if len(sketches) == 0:
                FreeCAD.Console.PrintError("No suitable sketches found\n")
                QtGui.QMessageBox.warning(
                    None,
                    "No Sketch Found",
                    "Please select a sketch to create a production array.\n\n"
                    "The sketch should contain the profile of ONE part.\n"
                    "The tool will create multiple copies as separate Bodies."
                )
                return
            elif len(sketches) == 1:
                sketch = sketches[0]
            else:
                # Multiple sketches - ask user to select one
                items = [sk.Label for sk in sketches]
                item, ok = QtGui.QInputDialog.getItem(
                    None,
                    "Select Sketch",
                    "Multiple sketches found. Select the master sketch to array:",
                    items,
                    0,
                    False
                )
                if ok and item:
                    sketch = sketches[items.index(item)]
                else:
                    return
        
        # Check if sketch has geometry
        if not hasattr(sketch, 'Geometry') or len(sketch.Geometry) == 0:
            FreeCAD.Console.PrintWarning(f"Sketch {sketch.Label} has no geometry\n")
            QtGui.QMessageBox.warning(
                None,
                "Empty Sketch",
                f"The selected sketch '{sketch.Label}' has no geometry.\n\n"
                "Please add geometry to the sketch first."
            )
            return
        
        # Show the production array panel
        FreeCAD.Console.PrintMessage(f"Opening Production Array panel for sketch: {sketch.Label}\n")
        panel = ProductionArrayPanel.ProductionArrayPanel(sketch)
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


# Register the commands
FreeCADGui.addCommand('CAM_ShowOperationVariables', ShowOperationVariablesCommand())
# ReorderBaseGeometry removed - use Split Profile and reorder operations in tree instead
# FreeCADGui.addCommand('CAM_ReorderBaseGeometry', ReorderBaseGeometryCommand())
FreeCADGui.addCommand('CAM_SplitProfile', SplitProfileCommand())
FreeCADGui.addCommand('ProductionArray', ProductionArrayCommand())
