# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Production Array Panel - Create parametric arrays of parts as separate Bodies"""

import FreeCAD
import FreeCADGui
import Part
import Sketcher
from PySide import QtCore, QtGui


class ProductionArrayPanel:
    """Panel for configuring and creating production arrays"""
    
    def __init__(self, sketch=None, feature_object=None):
        """Initialize the panel
        
        Args:
            sketch: The master sketch to create array from (for new arrays)
            feature_object: Existing ProductionArray feature to edit (for editing)
        """
        self.sketch = sketch
        self.feature_object = feature_object
        self.is_editing = feature_object is not None
        
        # If editing, get sketch from feature
        if self.is_editing:
            self.sketch = feature_object.MasterSketch
        
        # Detect document units
        self.unit_suffix, self.unit_name = self.get_document_units()
        
        self.form = self.create_ui()
    
    def get_document_units(self):
        """Detect the document's unit system
        
        Returns:
            tuple: (suffix_string, unit_name) e.g. (" in", "in") or (" mm", "mm")
        """
        try:
            # Get unit schema from FreeCAD preferences
            # 0 = Standard (mm), 1 = MKS (m), 2 = Imperial (inch), 
            # 3 = Building Euro (mm), 4 = Building US (inch), etc.
            schema = FreeCAD.Units.getSchema()
            
            # Imperial schemes use inches
            if schema in [2, 4, 7]:  # Imperial, Building US, Imperial Civil Engineering
                return (" in", "in")
            else:
                # All other schemes use metric (mm)
                return (" mm", "mm")
                
        except:
            # Default to inches if detection fails (for backwards compatibility)
            FreeCAD.Console.PrintWarning("Could not detect units, defaulting to inches\n")
            return (" in", "in")
        
    def create_ui(self):
        """Create the UI for the panel"""
        
        # Main widget
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        
        # Title
        if self.is_editing:
            title = QtGui.QLabel("<b>Production Array - Edit Parameters</b>")
        else:
            title = QtGui.QLabel("<b>Production Array - Create Multiple Bodies</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info about selected sketch
        sketch_label = self.sketch.Label if self.sketch else "None"
        info = QtGui.QLabel(f"Master Sketch: {sketch_label}")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        layout.addWidget(self.create_separator())
        
        # Spacing Mode Selection
        mode_group = QtGui.QGroupBox("Spacing Mode")
        mode_layout = QtGui.QVBoxLayout()
        
        self.gap_mode_radio = QtGui.QRadioButton("Gap Spacing (specify gap between parts)")
        self.gap_mode_radio.setChecked(True)
        self.gap_mode_radio.setToolTip("Specify the gap between parts (edge-to-edge)")
        mode_layout.addWidget(self.gap_mode_radio)
        
        self.overall_mode_radio = QtGui.QRadioButton("Overall Spacing (specify total distance)")
        self.overall_mode_radio.setToolTip("Specify the total distance from first to last part, program divides evenly")
        mode_layout.addWidget(self.overall_mode_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        layout.addWidget(self.create_separator())
        
        # Array Configuration Group
        config_group = QtGui.QGroupBox("Array Configuration")
        config_layout = QtGui.QFormLayout()
        
        # Count X
        self.count_x_spin = QtGui.QSpinBox()
        self.count_x_spin.setMinimum(1)
        self.count_x_spin.setMaximum(100)
        self.count_x_spin.setValue(3)
        self.count_x_spin.setToolTip("Number of copies in X direction")
        config_layout.addRow("Count X:", self.count_x_spin)
        
        # Spacing X
        self.spacing_x_spin = QtGui.QDoubleSpinBox()
        self.spacing_x_spin.setMinimum(0.0)
        self.spacing_x_spin.setMaximum(1000.0)
        self.spacing_x_spin.setValue(1.0)
        self.spacing_x_spin.setDecimals(3)
        self.spacing_x_spin.setSuffix(self.unit_suffix)
        self.spacing_x_spin.setToolTip("Gap between parts in X direction (part size added automatically if checked below)")
        config_layout.addRow("Gap X:", self.spacing_x_spin)
        
        # Count Y
        self.count_y_spin = QtGui.QSpinBox()
        self.count_y_spin.setMinimum(1)
        self.count_y_spin.setMaximum(100)
        self.count_y_spin.setValue(1)
        self.count_y_spin.setToolTip("Number of copies in Y direction (1 = linear array)")
        config_layout.addRow("Count Y:", self.count_y_spin)
        
        # Spacing Y
        self.spacing_y_spin = QtGui.QDoubleSpinBox()
        self.spacing_y_spin.setMinimum(0.0)
        self.spacing_y_spin.setMaximum(1000.0)
        self.spacing_y_spin.setValue(1.0)
        self.spacing_y_spin.setDecimals(3)
        self.spacing_y_spin.setSuffix(self.unit_suffix)
        self.spacing_y_spin.setToolTip("Gap between parts in Y direction (part size added automatically if checked below)")
        config_layout.addRow("Gap Y:", self.spacing_y_spin)
        
        # Add part size to spacing checkbox
        self.add_part_size_check = QtGui.QCheckBox("Add part size to spacing (edge-to-edge gap)")
        self.add_part_size_check.setChecked(True)
        self.add_part_size_check.setToolTip(
            "When checked: Spacing = gap between parts (part size is added automatically)\n"
            "When unchecked: Spacing = center-to-center distance (you calculate total)"
        )
        config_layout.addRow("", self.add_part_size_check)
        
        # Overall Spacing inputs (hidden by default)
        self.overall_x_spin = QtGui.QDoubleSpinBox()
        self.overall_x_spin.setMinimum(0.0)
        self.overall_x_spin.setMaximum(10000.0)
        self.overall_x_spin.setValue(20.0)
        self.overall_x_spin.setDecimals(3)
        self.overall_x_spin.setSuffix(self.unit_suffix)
        self.overall_x_spin.setToolTip("Total distance from first to last part in X direction")
        self.overall_x_label = QtGui.QLabel("Overall X:")
        config_layout.addRow(self.overall_x_label, self.overall_x_spin)
        
        self.overall_y_spin = QtGui.QDoubleSpinBox()
        self.overall_y_spin.setMinimum(0.0)
        self.overall_y_spin.setMaximum(10000.0)
        self.overall_y_spin.setValue(96.0)
        self.overall_y_spin.setDecimals(3)
        self.overall_y_spin.setSuffix(self.unit_suffix)
        self.overall_y_spin.setToolTip("Total distance from first to last part in Y direction")
        self.overall_y_label = QtGui.QLabel("Overall Y:")
        config_layout.addRow(self.overall_y_label, self.overall_y_spin)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Extrusion Group
        extrude_group = QtGui.QGroupBox("Extrusion")
        extrude_layout = QtGui.QFormLayout()
        
        # Pad depth
        self.pad_depth_spin = QtGui.QDoubleSpinBox()
        self.pad_depth_spin.setMinimum(0.001)
        self.pad_depth_spin.setMaximum(1000.0)
        self.pad_depth_spin.setValue(0.5)
        self.pad_depth_spin.setDecimals(3)
        self.pad_depth_spin.setSuffix(self.unit_suffix)
        self.pad_depth_spin.setToolTip("Extrusion depth for each body")
        extrude_layout.addRow("Pad Depth:", self.pad_depth_spin)
        
        # Reversed checkbox
        self.reversed_check = QtGui.QCheckBox("Reverse Direction")
        self.reversed_check.setToolTip("Extrude in opposite direction")
        extrude_layout.addRow("", self.reversed_check)
        
        extrude_group.setLayout(extrude_layout)
        layout.addWidget(extrude_group)
        
        # Options Group
        options_group = QtGui.QGroupBox("Options")
        options_layout = QtGui.QVBoxLayout()
        
        # Keep master sketch checkbox
        self.keep_master_check = QtGui.QCheckBox("Keep master sketch visible")
        self.keep_master_check.setChecked(True)
        self.keep_master_check.setToolTip("Keep the original sketch in the tree")
        options_layout.addWidget(self.keep_master_check)
        
        # Auto-rename bodies
        self.auto_rename_check = QtGui.QCheckBox("Auto-rename bodies")
        self.auto_rename_check.setChecked(True)
        self.auto_rename_check.setToolTip("Name bodies as Part_001, Part_002, etc.")
        options_layout.addWidget(self.auto_rename_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Summary
        layout.addWidget(self.create_separator())
        self.summary_label = QtGui.QLabel()
        self.summary_label.setStyleSheet("background-color: #e8f4f8; padding: 8px; border-radius: 4px;")
        self.update_summary()
        layout.addWidget(self.summary_label)
        
        # Connect signals to update summary
        self.count_x_spin.valueChanged.connect(self.update_summary)
        self.count_y_spin.valueChanged.connect(self.update_summary)
        
        # Connect mode change signals
        self.gap_mode_radio.toggled.connect(self.on_mode_changed)
        self.overall_mode_radio.toggled.connect(self.on_mode_changed)
        
        # Initialize UI based on default mode
        self.on_mode_changed()
        
        # Load values if editing existing feature
        if self.is_editing:
            self.load_values_from_feature()
        
        # Buttons
        button_layout = QtGui.QHBoxLayout()
        
        if self.is_editing:
            self.create_button = QtGui.QPushButton("Update Array")
        else:
            self.create_button = QtGui.QPushButton("Create Array")
        self.create_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.create_button.clicked.connect(self.create_or_update_array)
        button_layout.addWidget(self.create_button)
        
        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        return widget
    
    def create_separator(self):
        """Create a horizontal separator line"""
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        return line
    
    def on_mode_changed(self):
        """Handle spacing mode change"""
        is_gap_mode = self.gap_mode_radio.isChecked()
        
        # Show/hide gap spacing controls
        self.spacing_x_spin.setVisible(is_gap_mode)
        self.spacing_y_spin.setVisible(is_gap_mode)
        self.add_part_size_check.setVisible(is_gap_mode)
        
        # Show/hide overall spacing controls
        self.overall_x_spin.setVisible(not is_gap_mode)
        self.overall_y_spin.setVisible(not is_gap_mode)
        self.overall_x_label.setVisible(not is_gap_mode)
        self.overall_y_label.setVisible(not is_gap_mode)
        
        # Update label text for Gap/Overall mode
        # Note: Labels are already set correctly above, just ensure they're visible
        
        self.update_summary()
    
    def update_summary(self):
        """Update the summary label with current settings"""
        count_x = self.count_x_spin.value()
        count_y = self.count_y_spin.value()
        total = count_x * count_y
        
        summary = f"<b>Total Bodies to Create: {total}</b><br>"
        summary += f"Grid: {count_x} × {count_y}"
        
        # Add spacing info based on mode
        if self.gap_mode_radio.isChecked():
            gap_x = self.spacing_x_spin.value()
            gap_y = self.spacing_y_spin.value()
            if self.add_part_size_check.isChecked():
                summary += f"<br>Gap: {gap_x}{self.unit_name} × {gap_y}{self.unit_name} (+ part size)"
            else:
                summary += f"<br>Spacing: {gap_x}{self.unit_name} × {gap_y}{self.unit_name}"
        else:
            overall_x = self.overall_x_spin.value()
            overall_y = self.overall_y_spin.value()
            
            # Get part size for accurate spacing calculation
            bbox = self.get_sketch_bounding_box(self.sketch)
            if bbox:
                part_size_x_mm = bbox['max_x'] - bbox['min_x']
                part_size_y_mm = bbox['max_y'] - bbox['min_y']
                
                # Convert to current units
                if self.unit_name == "in":
                    part_size_x = part_size_x_mm / 25.4  # Convert mm to inches
                    part_size_y = part_size_y_mm / 25.4
                else:
                    part_size_x = part_size_x_mm  # Already in mm
                    part_size_y = part_size_y_mm
            else:
                part_size_x = 0.0
                part_size_y = 0.0
            
            # Calculate actual spacing (accounting for part size)
            if count_x > 1:
                calc_x = (overall_x - part_size_x) / (count_x - 1)
                summary += f"<br>Overall X: {overall_x}{self.unit_name} (spacing: {calc_x:.3f}{self.unit_name})"
            if count_y > 1:
                calc_y = (overall_y - part_size_y) / (count_y - 1)
                summary += f"<br>Overall Y: {overall_y}{self.unit_name} (spacing: {calc_y:.3f}{self.unit_name})"
        
        self.summary_label.setText(summary)
    
    def load_values_from_feature(self):
        """Load values from existing feature object into UI"""
        if not self.feature_object:
            return
        
        obj = self.feature_object
        
        # Load array configuration
        self.count_x_spin.setValue(obj.CountX)
        self.count_y_spin.setValue(obj.CountY)
        
        # Load spacing mode
        if obj.SpacingMode == "Gap":
            self.gap_mode_radio.setChecked(True)
        else:
            self.overall_mode_radio.setChecked(True)
        
        # Load gap spacing (convert to current units)
        self.spacing_x_spin.setValue(obj.GapX.getValueAs(self.unit_name))
        self.spacing_y_spin.setValue(obj.GapY.getValueAs(self.unit_name))
        self.add_part_size_check.setChecked(obj.AddPartSize)
        
        # Load overall spacing (convert to current units)
        self.overall_x_spin.setValue(obj.OverallX.getValueAs(self.unit_name))
        self.overall_y_spin.setValue(obj.OverallY.getValueAs(self.unit_name))
        
        # Load extrusion (convert to current units)
        self.pad_depth_spin.setValue(obj.PadDepth.getValueAs(self.unit_name))
        self.reversed_check.setChecked(obj.Reversed)
        
        # Load options
        self.keep_master_check.setChecked(obj.KeepMasterVisible)
        self.auto_rename_check.setChecked(obj.AutoRename)
    
    def create_or_update_array(self):
        """Create new array or update existing one"""
        if self.is_editing:
            self.update_array()
        else:
            self.create_array()
    
    def update_array(self):
        """Update existing ProductionArray feature"""
        if not self.feature_object:
            return
        
        try:
            obj = self.feature_object
            doc = FreeCAD.ActiveDocument
            
            # Open transaction for update
            doc.openTransaction("Update Production Array")
            
            # Update all properties
            obj.CountX = self.count_x_spin.value()
            obj.CountY = self.count_y_spin.value()
            
            # Spacing mode
            if self.gap_mode_radio.isChecked():
                obj.SpacingMode = "Gap"
            else:
                obj.SpacingMode = "Overall"
            
            # Gap spacing
            obj.GapX = f"{self.spacing_x_spin.value()} {self.unit_name}"
            obj.GapY = f"{self.spacing_y_spin.value()} {self.unit_name}"
            obj.AddPartSize = self.add_part_size_check.isChecked()
            
            # Overall spacing
            obj.OverallX = f"{self.overall_x_spin.value()} {self.unit_name}"
            obj.OverallY = f"{self.overall_y_spin.value()} {self.unit_name}"
            
            # Extrusion
            obj.PadDepth = f"{self.pad_depth_spin.value()} {self.unit_name}"
            obj.Reversed = self.reversed_check.isChecked()
            
            # Options
            obj.KeepMasterVisible = self.keep_master_check.isChecked()
            obj.AutoRename = self.auto_rename_check.isChecked()
            
            # Trigger recompute (will regenerate bodies)
            obj.touch()
            doc.recompute()
            
            # Commit transaction
            doc.commitTransaction()
            
            QtGui.QMessageBox.information(
                None,
                "Success",
                f"Production Array updated successfully!\n\n"
                f"Created {obj.CountX * obj.CountY} bodies"
            )
            
            FreeCADGui.Control.closeDialog()
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error updating array: {str(e)}\n")
            import traceback
            FreeCAD.Console.PrintError(traceback.format_exc())
            if doc:
                doc.abortTransaction()
            QtGui.QMessageBox.critical(
                None,
                "Error",
                f"Failed to update array:\n{str(e)}"
            )
    
    def create_array(self):
        """Create new ProductionArray feature"""
        from .ProductionArrayFeature import create_production_array
        
        try:
            doc = FreeCAD.ActiveDocument
            doc.openTransaction("Create Production Array")
            
            # Create the feature object
            obj = create_production_array(self.sketch)
            
            # Set all properties from UI
            obj.CountX = self.count_x_spin.value()
            obj.CountY = self.count_y_spin.value()
            
            # Spacing mode
            if self.gap_mode_radio.isChecked():
                obj.SpacingMode = "Gap"
            else:
                obj.SpacingMode = "Overall"
            
            # Gap spacing
            obj.GapX = f"{self.spacing_x_spin.value()} {self.unit_name}"
            obj.GapY = f"{self.spacing_y_spin.value()} {self.unit_name}"
            obj.AddPartSize = self.add_part_size_check.isChecked()
            
            # Overall spacing
            obj.OverallX = f"{self.overall_x_spin.value()} {self.unit_name}"
            obj.OverallY = f"{self.overall_y_spin.value()} {self.unit_name}"
            
            # Extrusion
            obj.PadDepth = f"{self.pad_depth_spin.value()} {self.unit_name}"
            obj.Reversed = self.reversed_check.isChecked()
            
            # Options
            obj.KeepMasterVisible = self.keep_master_check.isChecked()
            obj.AutoRename = self.auto_rename_check.isChecked()
            
            # Execute to generate bodies (each body is recomputed individually during generation)
            obj.touch()
            doc.recompute()
            
            doc.commitTransaction()
            
            QtGui.QMessageBox.information(
                None,
                "Success",
                f"Created Production Array successfully!\n\n"
                f"Total bodies: {obj.CountX * obj.CountY}\n\n"
                f"To modify:\n"
                f"• Edit the master sketch → array auto-updates\n"
                f"• Double-click ProductionArray → edit parameters"
            )
            
            FreeCADGui.Control.closeDialog()
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error creating array: {str(e)}\n")
            import traceback
            FreeCAD.Console.PrintError(traceback.format_exc())
            if doc:
                doc.abortTransaction()
            QtGui.QMessageBox.critical(
                None,
                "Error",
                f"Failed to create array:\n{str(e)}"
            )
    
    def get_sketch_bounding_box(self, sketch):
        """Get the bounding box of a sketch
        
        Args:
            sketch: The sketch object
            
        Returns:
            dict with min_x, max_x, min_y, max_y or None if no geometry
        """
        if not hasattr(sketch, 'Geometry') or len(sketch.Geometry) == 0:
            return None
        
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for geo in sketch.Geometry:
            # Get points from geometry
            points = []
            
            if hasattr(geo, 'StartPoint'):
                points.append(geo.StartPoint)
            if hasattr(geo, 'EndPoint'):
                points.append(geo.EndPoint)
            if hasattr(geo, 'Center'):
                # For circles/arcs, include center +/- radius
                center = geo.Center
                if hasattr(geo, 'Radius'):
                    radius = geo.Radius
                    points.append(FreeCAD.Vector(center.x - radius, center.y - radius, center.z))
                    points.append(FreeCAD.Vector(center.x + radius, center.y + radius, center.z))
                else:
                    points.append(center)
            
            # Update bounding box
            for point in points:
                min_x = min(min_x, point.x)
                max_x = max(max_x, point.x)
                min_y = min(min_y, point.y)
                max_y = max(max_y, point.y)
        
        if min_x == float('inf'):
            return None
            
        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y
        }
    
    def cancel(self):
        """Cancel the operation"""
        FreeCADGui.Control.closeDialog()
    
    def getStandardButtons(self):
        """Return standard buttons (none - we have custom buttons)"""
        return 0

