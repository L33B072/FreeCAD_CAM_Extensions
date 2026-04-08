# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Base Geometry Reorder Panel - Reorder base geometries in CAM operations"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class BaseGeometryReorderPanel:
    """Task panel for reordering CAM operation base geometries"""
    
    def __init__(self, operation=None):
        """Initialize the panel
        
        Args:
            operation: The CAM operation with Base geometry to reorder
        """
        self.operation = operation
        self.form = self.createUI()
        self.populateList()
    
    def createUI(self):
        """Create the user interface"""
        # Main widget
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        
        # Title
        title = QtGui.QLabel("<b>Reorder Base Geometry</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Operation info
        if self.operation:
            info = QtGui.QLabel(f"Operation: {self.operation.Label}")
            layout.addWidget(info)
        
        # Instructions
        instructions = QtGui.QLabel(
            "Drag items to reorder, or use the buttons below.\n"
            "The toolpath will process geometry in this order from top to bottom."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # List widget for base geometries
        self.list_widget = QtGui.QListWidget()
        self.list_widget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.list_widget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)
        
        # Buttons for moving items
        button_layout = QtGui.QHBoxLayout()
        
        self.move_top_btn = QtGui.QPushButton("Move to Top")
        self.move_top_btn.clicked.connect(self.moveToTop)
        button_layout.addWidget(self.move_top_btn)
        
        self.move_up_btn = QtGui.QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.moveUp)
        button_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QtGui.QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.moveDown)
        button_layout.addWidget(self.move_down_btn)
        
        self.move_bottom_btn = QtGui.QPushButton("Move to Bottom")
        self.move_bottom_btn.clicked.connect(self.moveBottom)
        button_layout.addWidget(self.move_bottom_btn)
        
        layout.addLayout(button_layout)
        
        # Apply button
        apply_button = QtGui.QPushButton("Apply New Order")
        apply_button.clicked.connect(self.applyOrder)
        apply_button.setStyleSheet("QPushButton { font-weight: bold; background-color: #4CAF50; color: white; padding: 8px; }")
        layout.addWidget(apply_button)
        
        # Info label
        self.info_label = QtGui.QLabel("")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        return widget
    
    def populateList(self):
        """Populate the list with base geometries"""
        if not self.operation or not hasattr(self.operation, 'Base'):
            return
        
        self.list_widget.clear()
        
        for i, base_item in enumerate(self.operation.Base):
            obj = base_item[0]
            features = base_item[1]
            
            # Create list item
            item_text = f"{i+1}. {obj.Label} - {', '.join(features)}"
            list_item = QtGui.QListWidgetItem(item_text)
            
            # Store the base_item data
            list_item.setData(QtCore.Qt.UserRole, base_item)
            
            self.list_widget.addItem(list_item)
        
        self.info_label.setText(f"Total: {len(self.operation.Base)} base geometries")
    
    def moveToTop(self):
        """Move selected item to top"""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(0, item)
            self.list_widget.setCurrentRow(0)
            self.updateNumbers()
    
    def moveUp(self):
        """Move selected item up one position"""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)
            self.updateNumbers()
    
    def moveDown(self):
        """Move selected item down one position"""
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1 and current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)
            self.updateNumbers()
    
    def moveBottom(self):
        """Move selected item to bottom"""
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1 and current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.addItem(item)
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)
            self.updateNumbers()
    
    def updateNumbers(self):
        """Update the numbering in the list after reordering"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            base_item = item.data(QtCore.Qt.UserRole)
            obj = base_item[0]
            features = base_item[1]
            item.setText(f"{i+1}. {obj.Label} - {', '.join(features)}")
    
    def applyOrder(self):
        """Apply the new order to the operation"""
        if not self.operation:
            return
        
        # Get the new order from the list
        new_base = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            base_item = item.data(QtCore.Qt.UserRole)
            new_base.append(base_item)
        
        # Update the operation's Base property
        try:
            # CRITICAL: Set HandleMultipleFeatures to 'Individually' to respect our custom order
            # When set to 'Collectively', FreeCAD optimizes the toolpath order automatically
            # When set to 'Individually', it processes each base geometry in the order specified
            handle_features_changed = False
            if hasattr(self.operation, 'HandleMultipleFeatures'):
                old_value = self.operation.HandleMultipleFeatures
                if old_value != 'Individually':
                    self.operation.HandleMultipleFeatures = 'Individually'
                    handle_features_changed = True
                    FreeCAD.Console.PrintMessage(f"Changed HandleMultipleFeatures from '{old_value}' to 'Individually'\n")
            
            # CRITICAL: Disable UseStartPoint to respect our custom order
            # When UseStartPoint is True, FreeCAD optimizes the toolpath order
            # based on proximity to StartPoint, ignoring Base order
            use_start_point_disabled = False
            if hasattr(self.operation, 'UseStartPoint') and self.operation.UseStartPoint:
                self.operation.UseStartPoint = False
                use_start_point_disabled = True
                FreeCAD.Console.PrintMessage(f"Disabled UseStartPoint to respect custom geometry order\n")
            
            # Set the new Base order
            self.operation.Base = new_base
            
            # Mark the operation as touched to force recomputation
            self.operation.touch()
            
            # Recompute the operation itself
            self.operation.recompute()
            
            # Find and recompute the parent Job if it exists
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, 'Group') and self.operation in obj.Group:
                    if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, '__class__'):
                        # This is likely the Job object
                        FreeCAD.Console.PrintMessage(f"Recomputing parent Job: {obj.Label}\n")
                        obj.touch()
                        obj.recompute()
                        break
            
            # Recompute the entire document
            FreeCAD.ActiveDocument.recompute()
            
            msg = "✓ Order applied! Toolpath follows your custom sequence."
            changes = []
            if handle_features_changed:
                changes.append("HandleMultipleFeatures→Individually")
            if use_start_point_disabled:
                changes.append("UseStartPoint→False")
            if changes:
                msg += f" ({', '.join(changes)})"
            
            self.info_label.setText(msg)
            self.info_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            
            FreeCAD.Console.PrintMessage(f"Base geometry order updated for {self.operation.Label}\n")
            FreeCAD.Console.PrintMessage(f"New order: {[f'{b[0].Label}-{b[1]}' for b in new_base]}\n")
            
        except Exception as e:
            self.info_label.setText(f"✗ Error: {str(e)}")
            self.info_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            FreeCAD.Console.PrintError(f"Error applying order: {str(e)}\n")
            FreeCAD.Console.PrintError(f"Failed to update base geometry order: {e}\n")
    
    def accept(self):
        """Called when OK button is clicked"""
        self.applyOrder()
        FreeCADGui.Control.closeDialog()
        return True
    
    def reject(self):
        """Called when Cancel button is clicked"""
        FreeCADGui.Control.closeDialog()
        return True
    
    def getStandardButtons(self):
        """Define which buttons to show"""
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
