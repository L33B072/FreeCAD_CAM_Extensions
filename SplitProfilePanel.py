# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""
Split Profile Operation - Split a Profile with multiple base geometries into separate operations

This module provides functionality to split a single Profile operation with multiple
base geometries into multiple Profile operations (one per base geometry), giving
complete control over the cutting order.
"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class SplitProfilePanel:
    """Panel for splitting a Profile operation into separate operations"""
    
    def __init__(self, operation):
        self.operation = operation
        self.form = self.createUI()
        
    def createUI(self):
        """Create the UI for the split profile panel"""
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        
        # Title
        title = QtGui.QLabel(f"<b>Split Profile:</b> {self.operation.Label}")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Info
        info_text = f"This will create {len(self.operation.Base)} separate Profile operations,\n"
        info_text += "one for each base geometry, in the current order.\n\n"
        info_text += "Each operation will inherit all settings from the original."
        info = QtGui.QLabel(info_text)
        layout.addWidget(info)
        
        layout.addSpacing(10)
        
        # List of base geometries that will be split
        list_label = QtGui.QLabel("<b>Base geometries to split:</b>")
        layout.addWidget(list_label)
        
        self.list_widget = QtGui.QListWidget()
        for i, base_item in enumerate(self.operation.Base):
            obj = base_item[0]
            features = base_item[1]
            item_text = f"{i+1}. {obj.Label} - {', '.join(features)}"
            self.list_widget.addItem(item_text)
        layout.addWidget(self.list_widget)
        
        layout.addSpacing(10)
        
        # Options
        options_group = QtGui.QGroupBox("Options")
        options_layout = QtGui.QVBoxLayout()
        
        self.delete_original_checkbox = QtGui.QCheckBox("Delete original Profile operation after split")
        self.delete_original_checkbox.setChecked(True)
        options_layout.addWidget(self.delete_original_checkbox)
        
        self.rename_checkbox = QtGui.QCheckBox("Auto-rename split operations")
        self.rename_checkbox.setChecked(True)
        self.rename_checkbox.setToolTip("Names will be: ProfileName_001, ProfileName_002, etc.")
        options_layout.addWidget(self.rename_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addSpacing(10)
        
        # Split button
        split_button = QtGui.QPushButton("Split Profile")
        split_button.clicked.connect(self.splitProfile)
        layout.addWidget(split_button)
        
        # Status label
        self.status_label = QtGui.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        return widget
    
    def splitProfile(self):
        """Split the Profile operation into separate operations"""
        if not self.operation or len(self.operation.Base) < 2:
            self.status_label.setText("✗ Profile must have at least 2 base geometries to split")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            return
        
        try:
            doc = FreeCAD.ActiveDocument
            doc.openTransaction("Split Profile Operation")
            
            # Find the parent Job
            job = None
            for obj in doc.Objects:
                if hasattr(obj, 'Group') and self.operation in obj.Group:
                    job = obj
                    break
            
            if not job:
                raise Exception("Could not find parent Job for Profile operation")
            
            # Get the original operation's position in the Job's Group
            original_index = job.Group.index(self.operation)
            
            # Create separate Profile operations
            new_operations = []
            base_name = self.operation.Label if not self.rename_checkbox.isChecked() else self.operation.Label.rstrip('0123456789_')
            
            FreeCAD.Console.PrintMessage(f"\nSplitting Profile '{self.operation.Label}' into {len(self.operation.Base)} operations...\n")
            
            for i, base_item in enumerate(self.operation.Base):
                # Create new Profile operation
                import Path.Op.Profile as PathProfile
                new_op = PathProfile.Create('Profile', obj=None, parentJob=job)
                
                # Set the base geometry (just this one)
                new_op.Base = [base_item]
                
                # Copy all properties from original
                self.copyProperties(self.operation, new_op)
                
                # Set the name
                if self.rename_checkbox.isChecked():
                    new_op.Label = f"{base_name}_{i+1:03d}"
                else:
                    new_op.Label = f"{self.operation.Label}_{i+1}"
                
                new_operations.append(new_op)
                FreeCAD.Console.PrintMessage(f"  Created: {new_op.Label} for {base_item[0].Label}-{base_item[1]}\n")
            
            # Check if operations were auto-added to the job (they should be)
            # If not in Job, we'll manually add them at the correct position
            job_group = list(job.Group)
            
            # Remove the original if requested
            if self.delete_original_checkbox.isChecked() and self.operation in job_group:
                job_group.remove(self.operation)
                original_index = original_index  # Position stays the same after removal
            
            # Check which operations need to be added
            for i, new_op in enumerate(new_operations):
                if new_op not in job_group:
                    # Insert at the appropriate position
                    job_group.insert(original_index + i, new_op)
            
            job.Group = job_group
            
            # Delete the original operation from the document if requested
            if self.delete_original_checkbox.isChecked():
                doc.removeObject(self.operation.Name)
                FreeCAD.Console.PrintMessage(f"  Deleted original: {self.operation.Label}\n")
            
            # Recompute
            for op in new_operations:
                op.recompute()
            
            job.recompute()
            doc.recompute()
            doc.commitTransaction()
            
            # Success message
            msg = f"✓ Successfully split into {len(new_operations)} Profile operations!"
            if self.delete_original_checkbox.isChecked():
                msg += "\n(Original operation deleted)"
            
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            
            FreeCAD.Console.PrintMessage(f"✓ Profile split complete!\n\n")
            
            # Close the panel after a brief delay
            QtCore.QTimer.singleShot(2000, self.accept)
            
        except Exception as e:
            doc.abortTransaction()
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            FreeCAD.Console.PrintError(f"Error splitting Profile: {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    def copyProperties(self, source, target):
        """Copy all relevant properties from source to target operation"""
        # List of properties to copy
        properties_to_copy = [
            'Active', 'Direction', 'Side', 'OffsetExtra', 'UseComp',
            'StepDown', 'FinalDepth', 'StartDepth',
            'SafeHeight', 'ClearanceHeight',
            'ToolController', 'CoolantMode',
            'UseStartPoint', 'StartPoint',
            'processHoles', 'processPerimeter', 'processCircles',
            'HandleMultipleFeatures', 'JoinType', 'MiterLimit',
            'SplitArcs', 'Stepover', 'NumPasses'
        ]
        
        for prop in properties_to_copy:
            if hasattr(source, prop) and hasattr(target, prop):
                try:
                    setattr(target, prop, getattr(source, prop))
                except:
                    pass  # Some properties might be read-only
    
    def accept(self):
        """Called when the panel is closed"""
        FreeCADGui.Control.closeDialog()
    
    def reject(self):
        """Called when cancel is clicked"""
        FreeCADGui.Control.closeDialog()
    
    def getStandardButtons(self):
        """Define which buttons to show"""
        return QtGui.QDialogButtonBox.Close
