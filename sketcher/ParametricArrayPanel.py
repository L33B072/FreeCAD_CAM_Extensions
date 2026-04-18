# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Parametric Array Dialog Panel"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class ParametricArrayPanel:
    """Panel for creating/editing parametric arrays in sketches"""
    
    def __init__(self, sketch, selected_geo_indices, array_id=None):
        """Initialize the panel
        
        Args:
            sketch: The sketch object being edited
            selected_geo_indices: List of selected geometry indices
            array_id: If editing existing array, the array ID
        """
        self.sketch = sketch
        self.selected_geo_indices = selected_geo_indices
        self.array_id = array_id
        self.is_editing = array_id is not None
        self.dialog = None  # Will be set by caller
        
        self.form = self.create_ui()
        
        # If editing, load existing array values
        if self.is_editing:
            self.load_array_values()
    
    def load_array_values(self):
        """Load values from existing array into the dialog"""
        from sketcher import ParametricArrayConstraint
        
        array_info = ParametricArrayConstraint.ParametricArrayConstraint.get_array_info(
            self.sketch, self.array_id
        )
        
        if array_info:
            # Set values (converting mm to inches for spacing)
            self.rows_spin.setValue(array_info['rows'])
            self.cols_spin.setValue(array_info['cols'])
            self.row_spacing_spin.setValue(array_info['row_spacing'] / 25.4)  # mm to inches
            self.col_spacing_spin.setValue(array_info['col_spacing'] / 25.4)  # mm to inches
            self.update_total()
            
            FreeCAD.Console.PrintMessage(f"Loaded {self.array_id}: {array_info['rows']}×{array_info['cols']}\n")
        
    def create_ui(self):
        """Create the UI for the panel"""
        
        # Main widget
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        
        # Title
        if self.is_editing:
            title = QtGui.QLabel(f"<b>Edit Parametric Array - {self.array_id}</b>")
        else:
            title = QtGui.QLabel("<b>Create Parametric Array</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QtGui.QLabel(f"Selected geometry: {len(self.selected_geo_indices)} elements")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        layout.addWidget(self.create_separator())
        
        # Description
        desc = QtGui.QLabel(
            "Creates a parametric rectangular array of the selected geometry.\n\n"
            "<b>Spacing behavior:</b>\n"
            "• Circles/Arcs: Gap = center-to-center distance\n"
            "• Polygons/Lines: Gap = edge-to-edge distance\n\n"
            "Changing base geometry size automatically updates all copies!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #555; font-size: 9pt;")
        layout.addWidget(desc)
        
        layout.addWidget(self.create_separator())
        
        # Array Configuration Group
        config_group = QtGui.QGroupBox("Array Configuration")
        config_layout = QtGui.QFormLayout()
        
        # Rows
        self.rows_spin = QtGui.QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setMaximum(100)
        self.rows_spin.setValue(2)
        self.rows_spin.setToolTip("Number of rows (Y direction)")
        config_layout.addRow("Rows:", self.rows_spin)
        
        # Columns
        self.cols_spin = QtGui.QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setMaximum(100)
        self.cols_spin.setValue(3)
        self.cols_spin.setToolTip("Number of columns (X direction)")
        config_layout.addRow("Columns:", self.cols_spin)
        
        # Row Spacing
        self.row_spacing_spin = QtGui.QDoubleSpinBox()
        self.row_spacing_spin.setMinimum(0.001)
        self.row_spacing_spin.setMaximum(1000.0)
        self.row_spacing_spin.setValue(2.0)
        self.row_spacing_spin.setDecimals(3)
        self.row_spacing_spin.setSuffix(" in")
        self.row_spacing_spin.setToolTip("Gap between rows\nCircles: center-to-center | Polygons: edge-to-edge")
        config_layout.addRow("Row Gap:", self.row_spacing_spin)
        
        # Column Spacing
        self.col_spacing_spin = QtGui.QDoubleSpinBox()
        self.col_spacing_spin.setMinimum(0.001)
        self.col_spacing_spin.setMaximum(1000.0)
        self.col_spacing_spin.setValue(2.0)
        self.col_spacing_spin.setDecimals(3)
        self.col_spacing_spin.setSuffix(" in")
        self.col_spacing_spin.setToolTip("Gap between columns\nCircles: center-to-center | Polygons: edge-to-edge")
        config_layout.addRow("Column Gap:", self.col_spacing_spin)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addWidget(self.create_separator())
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Total count preview
        self.total_label = QtGui.QLabel()
        self.total_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        self.update_total()
        layout.addWidget(self.total_label)
        
        layout.addWidget(self.create_separator())
        
        # Custom buttons
        button_layout = QtGui.QHBoxLayout()
        
        if self.is_editing:
            self.apply_button = QtGui.QPushButton("Update Array")
        else:
            self.apply_button = QtGui.QPushButton("Create Array")
        self.apply_button.setStyleSheet("font-weight: bold; padding: 8px 20px;")
        self.apply_button.setToolTip("Apply array parameters")
        self.apply_button.clicked.connect(self.on_apply_clicked)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel and close without changes")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals to update total
        self.rows_spin.valueChanged.connect(self.update_total)
        self.cols_spin.valueChanged.connect(self.update_total)
        
        return widget
    
    def create_separator(self):
        """Create a horizontal separator line"""
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        return line
    
    def update_total(self):
        """Update the total count display"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        total = rows * cols
        self.total_label.setText(f"Total instances: {rows} × {cols} = {total}")
    
    def on_apply_clicked(self):
        """Called when Apply button is clicked"""
        from sketcher import ParametricArrayConstraint
        
        # Get values from UI (convert inches to mm)
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        row_spacing = self.row_spacing_spin.value() * 25.4  # Convert to mm
        col_spacing = self.col_spacing_spin.value() * 25.4  # Convert to mm
        
        FreeCAD.Console.PrintMessage(f"\n=== Parametric Array ===\n")
        FreeCAD.Console.PrintMessage(f"Rows: {rows}, Columns: {cols}\n")
        FreeCAD.Console.PrintMessage(f"Gap (Row): {self.row_spacing_spin.value()} in ({row_spacing:.3f} mm)\n")
        FreeCAD.Console.PrintMessage(f"Gap (Col): {self.col_spacing_spin.value()} in ({col_spacing:.3f} mm)\n")
        
        try:
            if self.is_editing:
                # Update existing array
                success = ParametricArrayConstraint.ParametricArrayConstraint.update_array(
                    self.sketch, self.array_id, rows, cols, row_spacing, col_spacing
                )
            else:
                # Create new array
                array_id = ParametricArrayConstraint.ParametricArrayConstraint.create_array(
                    self.sketch, self.selected_geo_indices, rows, cols, row_spacing, col_spacing
                )
                success = array_id is not None
            
            if success:
                # Force sketch to recompute
                self.sketch.recompute()
                FreeCAD.Console.PrintMessage("=== Array Complete ===\n\n")
                
                # Close the dialog
                if self.dialog:
                    self.dialog.accept()
            else:
                FreeCAD.Console.PrintError("Failed to create/update array\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error creating array: {e}\n")
            import traceback
            traceback.print_exc()
    
    def on_cancel_clicked(self):
        """Called when Cancel button is clicked"""
        FreeCAD.Console.PrintMessage("Array operation cancelled\n")
        
        # Close the dialog
        if self.dialog:
            self.dialog.reject()
