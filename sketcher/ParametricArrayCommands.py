# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Parametric Array Commands for Sketcher Workbench"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class CreateParametricArrayCommand:
    """Command to create a parametric array in a sketch"""
    
    def GetResources(self):
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'Resources', 'icons', 'Sketcher_ParametricArray.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Sketcher_ParametricArray", "Parametric Rectangular Array"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Sketcher_ParametricArray", 
                "Create a parametric rectangular array of selected geometry")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        from sketcher import ParametricArrayPanel
        from sketcher import ParametricArrayConstraint
        
        # Get the active sketch
        sketch = self.get_active_sketch()
        if not sketch:
            FreeCAD.Console.PrintError("No active sketch. Please edit a sketch first.\n")
            return
        
        FreeCAD.Console.PrintMessage(f"Active sketch: {sketch.Label}\n")
        FreeCAD.Console.PrintMessage(f"Sketch has {len(sketch.Geometry)} geometry elements\n")
        
        # Get selected geometry
        selected_geo = self.get_selected_geometry(sketch)
        if not selected_geo:
            FreeCAD.Console.PrintError("No geometry selected. Please select geometry to array or edit.\n")
            QtGui.QMessageBox.warning(
                None,
                "No Selection",
                "Please select geometry in the sketch:\n\n"
                "• To CREATE array: Select geometry to array\n"
                "• To EDIT array: Select any part of an existing array\n\n"
                "Tip: Hold Ctrl to select multiple elements."
            )
            return
        
        # Check if any selected geometry is part of an existing array
        array_id = None
        array_role = None
        for geo_idx in selected_geo:
            found_id, role = ParametricArrayConstraint.ParametricArrayConstraint.find_array_by_geometry(sketch, geo_idx)
            if found_id:
                array_id = found_id
                array_role = role
                break
        
        # Determine mode: Edit or Create
        if array_id:
            FreeCAD.Console.PrintMessage(f"Editing array: {array_id} (selected {array_role} element)\n")
            # Edit mode - get base geometry from array info
            array_info = ParametricArrayConstraint.ParametricArrayConstraint.get_array_info(sketch, array_id)
            panel = ParametricArrayPanel.ParametricArrayPanel(sketch, array_info['base_indices'], array_id)
            dialog_title = f"Edit Array - {array_id}"
        else:
            FreeCAD.Console.PrintMessage(f"Creating new array with {len(selected_geo)} selected elements\n")
            # Create mode
            panel = ParametricArrayPanel.ParametricArrayPanel(sketch, selected_geo)
            dialog_title = "Create Parametric Array"
        
        # Show the panel as a floating dialog (not a task panel, since sketch editor is active)
        # Set parent to FreeCAD main window and keep on top
        main_window = FreeCADGui.getMainWindow()
        dialog = QtGui.QDialog(main_window)
        dialog.setWindowTitle(dialog_title)
        dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        dialog.setLayout(QtGui.QVBoxLayout())
        dialog.layout().addWidget(panel.form)
        
        # Store panel reference so it can close the dialog
        panel.dialog = dialog
        
        # Bring to front and activate
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Show as modal dialog
        dialog.exec_()
    
    def IsActive(self):
        """Return True if command should be active (sketch in edit mode)"""
        return self.get_active_sketch() is not None
    
    def get_active_sketch(self):
        """Get the currently edited sketch, if any"""
        try:
            # Check if we're in sketch edit mode
            if FreeCADGui.ActiveDocument is None:
                return None
            
            edit_obj = FreeCADGui.ActiveDocument.getInEdit()
            if edit_obj is None:
                return None
            
            obj = edit_obj.Object
            if obj.TypeId == 'Sketcher::SketchObject':
                return obj
            
            return None
        except:
            return None
    
    def get_selected_geometry(self, sketch):
        """Get indices of selected geometry in the sketch"""
        try:
            # When sketch is in edit mode, use Sketcher's selection
            selection = FreeCADGui.Selection.getSelectionEx()
            
            geo_indices = []
            
            for sel in selection:
                if sel.Object == sketch:
                    # Get selected sub-elements
                    for sub in sel.SubElementNames:
                        # Geometry elements are named like "Edge1", "Edge2", etc.
                        if sub.startswith('Edge'):
                            try:
                                # Edge numbering starts at 1, geometry index starts at 0
                                # But we need to account for external geometry (negative indices)
                                edge_num = int(sub[4:])
                                geo_idx = edge_num - 1
                                
                                # Only include non-negative indices (actual sketch geometry, not external)
                                if geo_idx >= 0 and geo_idx < len(sketch.Geometry):
                                    if geo_idx not in geo_indices:
                                        geo_indices.append(geo_idx)
                            except:
                                pass
            
            FreeCAD.Console.PrintMessage(f"Found {len(geo_indices)} selected geometry elements: {geo_indices}\n")
            return sorted(geo_indices)
            
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Error getting selected geometry: {e}\n")
            import traceback
            traceback.print_exc()
            return []


# Register command
FreeCADGui.addCommand('Sketcher_ParametricArray', CreateParametricArrayCommand())
