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
        
        # Prepare list of items to split
        # Each item is (base_object, feature_name)
        self.split_items = []
        
        for base_item in self.operation.Base:
            obj = base_item[0]
            features = base_item[1]
            # If multiple features in one base item, split them individually
            for feature in features:
                self.split_items.append((obj, feature))
        
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
        info_text = f"This will create {len(self.split_items)} separate Profile operations,\n"
        info_text += "one for each base geometry, in the current order.\n\n"
        info_text += "Each operation will inherit all settings from the original."
        info = QtGui.QLabel(info_text)
        layout.addWidget(info)
        
        layout.addSpacing(10)
        
        # List of base geometries that will be split
        list_label = QtGui.QLabel("<b>Base geometries to split:</b>")
        layout.addWidget(list_label)
        
        self.list_widget = QtGui.QListWidget()
        for i, split_item in enumerate(self.split_items):
            obj = split_item[0]
            feature = split_item[1]
            item_text = f"{i+1}. {obj.Label} - {feature}"
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
        
        self.save_reopen_checkbox = QtGui.QCheckBox("Save and reopen document after split (ensures full editability)")
        self.save_reopen_checkbox.setChecked(False)
        self.save_reopen_checkbox.setToolTip("Due to FreeCAD internals, operations may not be fully editable until document is saved and reopened.\nCheck this to do it automatically.")
        options_layout.addWidget(self.save_reopen_checkbox)
        
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
        
        # Debug: Show what's in Base
        FreeCAD.Console.PrintMessage(f"\n=== Split Profile Debug Info ===\n")
        FreeCAD.Console.PrintMessage(f"Operation: {self.operation.Label}\n")
        FreeCAD.Console.PrintMessage(f"Split items count: {len(self.split_items)}\n")
        FreeCAD.Console.PrintMessage(f"=================================\n\n")
        
        if not self.operation or len(self.split_items) < 2:
            self.status_label.setText("✗ Profile must have at least 2 base geometries to split")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            return
        
        try:
            doc = FreeCAD.ActiveDocument
            doc.openTransaction("Split Profile Operation")
            
            # Find the parent Job using FreeCAD's utility function
            import PathScripts.PathUtils as PathUtils
            job = PathUtils.findParentJob(self.operation)
            
            if not job:
                raise Exception("Could not find parent Job for Profile operation")
            
            # Get the original operation's position in the Job's Operations Group
            operations_group = job.Operations.Group
            if self.operation not in operations_group:
                raise Exception(f"Operation '{self.operation.Label}' is not in Job's Operations group")
            
            original_index = operations_group.index(self.operation)
            
            # Create separate Profile operations
            new_operations = []
            base_name = self.operation.Label if not self.rename_checkbox.isChecked() else self.operation.Label.rstrip('0123456789_')
            
            FreeCAD.Console.PrintMessage(f"\nSplitting Profile '{self.operation.Label}' into {len(self.split_items)} operations...\n")
            
            for i, split_item in enumerate(self.split_items):
                obj = split_item[0]
                feature = split_item[1]
                
                # Create new Profile operation
                import Path.Op.Profile as PathProfile
                new_op = PathProfile.Create('Profile', obj=None, parentJob=job)
                
                # Set the base geometry (just this one feature)
                # Base format: [(object, (feature_name,))]
                new_op.Base = [(obj, (feature,))]
                
                # Copy all properties from original
                self.copyProperties(self.operation, new_op)
                
                # Explicitly ensure ArcFeedRatePercent is copied (if it exists)
                # This handles cases where the property might not exist on new_op yet
                if hasattr(self.operation, 'ArcFeedRatePercent'):
                    if not hasattr(new_op, 'ArcFeedRatePercent'):
                        # Add the property if it doesn't exist
                        try:
                            new_op.addProperty(
                                "App::PropertyPercent",
                                "ArcFeedRatePercent",
                                "Path",
                                "Feed rate percentage for arc moves (G2/G3). Set to 100% for normal speed, lower values slow down arcs."
                            )
                        except:
                            pass  # Property might already exist
                    # Copy the value
                    try:
                        new_op.ArcFeedRatePercent = self.operation.ArcFeedRatePercent
                        FreeCAD.Console.PrintMessage(f"    ✓ ArcFeedRatePercent: {self.operation.ArcFeedRatePercent}%\n")
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"    Warning: Could not copy ArcFeedRatePercent: {e}\n")
                
                # Set the name
                if self.rename_checkbox.isChecked():
                    new_op.Label = f"{base_name}_{i+1:03d}"
                else:
                    new_op.Label = f"{self.operation.Label}_{i+1}"
                
                # Ensure ViewObject is properly set up for editing
                if hasattr(new_op, 'ViewObject') and new_op.ViewObject:
                    # Set properties that might affect editability
                    try:
                        new_op.ViewObject.Proxy = self.operation.ViewObject.Proxy
                    except:
                        pass
                
                new_operations.append(new_op)
                FreeCAD.Console.PrintMessage(f"  Created: {new_op.Label} for {obj.Label}-{feature}\n")
            
            # Manage the operations in the Job's Operations group
            # Note: Create() should auto-add operations to job.Operations.Group
            operations_group = list(job.Operations.Group)
            
            # If the original should be deleted, remove it from the group
            if self.delete_original_checkbox.isChecked():
                if self.operation in operations_group:
                    operations_group.remove(self.operation)
                    # Update the index since we removed the original
                    # (operations are already created and may be auto-added after the original)
            
            # Ensure all new operations are in the correct position
            # They should have been auto-added by Create(), but let's verify and reorder if needed
            for i, new_op in enumerate(new_operations):
                if new_op in operations_group:
                    # Remove it so we can insert at the correct position
                    operations_group.remove(new_op)
                # Insert at the appropriate position
                insert_pos = original_index + i
                if insert_pos > len(operations_group):
                    operations_group.append(new_op)
                else:
                    operations_group.insert(insert_pos, new_op)
            
            # Update the Job's Operations group
            job.Operations.Group = operations_group
            
            # Delete the original operation from the document if requested
            if self.delete_original_checkbox.isChecked():
                doc.removeObject(self.operation.Name)
                FreeCAD.Console.PrintMessage(f"  Deleted original: {self.operation.Label}\n")
            
            # Force path regeneration - recompute multiple times to ensure proper generation
            FreeCAD.Console.PrintMessage("  Regenerating toolpaths...\n")
            for op in new_operations:
                op.touch()  # Mark as needing recompute
                op.recompute()
            
            job.recompute()
            doc.recompute()
            
            # Second recompute to ensure paths are fully generated
            for op in new_operations:
                try:
                    # Force execute to regenerate path
                    if hasattr(op, 'Proxy') and hasattr(op.Proxy, 'execute'):
                        op.Proxy.execute(op)
                    # Touch path-related properties to force regeneration
                    if hasattr(op, 'Path'):
                        op.Path.touch()
                    op.recompute()
                except Exception as e:
                    FreeCAD.Console.PrintWarning(f"  Warning: Could not fully regenerate path for {op.Label}: {e}\n")
            
            # Final document recompute
            job.recompute()
            doc.recompute()
            
            # Ensure view objects are updated
            for op in new_operations:
                if hasattr(op, 'ViewObject'):
                    op.ViewObject.signalChangeIcon()
            
            FreeCADGui.updateGui()
            
            # Force a soft "refresh" by saving internal state
            # This mimics what happens when you close/reopen the file
            try:
                for op in new_operations:
                    # Force the operation to save and restore its internal state
                    if hasattr(op, 'Proxy') and hasattr(op.Proxy, 'onDocumentRestored'):
                        op.Proxy.onDocumentRestored(op)
                    # Ensure the operation is fully set up
                    if hasattr(op, 'Proxy') and hasattr(op.Proxy, 'setEdit'):
                        pass  # Don't actually open for edit, just ensure the method exists
                FreeCAD.Console.PrintMessage("  Applied state refresh for editability\n")
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"  Note: Could not apply full state refresh: {e}\n")
            doc.commitTransaction()
            
            # Handle save and reopen if requested
            if self.save_reopen_checkbox.isChecked():
                FreeCAD.Console.PrintMessage("  Saving and reopening document to ensure full editability...\n")
                doc_path = doc.FileName
                
                # If document hasn't been saved yet, prompt user to save
                if not doc_path:
                    FreeCAD.Console.PrintWarning("  Document must be saved first to use auto-reopen feature\n")
                    msg = f"✓ Successfully split into {len(new_operations)} Profile operations!\n"
                    msg += "(Save and reopen document manually to make operations fully editable)"
                    if self.delete_original_checkbox.isChecked():
                        msg += "\n(Original operation deleted)"
                    self.status_label.setText(msg)
                    self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
                else:
                    # Save the document
                    doc.save()
                    FreeCAD.Console.PrintMessage(f"  Document saved: {doc_path}\n")
                    
                    # Close and reopen
                    FreeCAD.closeDocument(doc.Name)
                    FreeCAD.openDocument(doc_path)
                    FreeCAD.Console.PrintMessage("  Document reopened - operations are now fully editable\n")
                    
                    # Don't show status or close panel since document was reloaded
                    return
            
            # Success message
            msg = f"✓ Successfully split into {len(new_operations)} Profile operations!"
            if self.delete_original_checkbox.isChecked():
                msg += "\n(Original operation deleted)"
            
            # Add note about editability if not auto-reopening
            if not self.save_reopen_checkbox.isChecked():
                msg += "\n\nNote: If operations aren't fully editable, save and reopen the document."
            
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            
            FreeCAD.Console.PrintMessage(f"✓ Profile split complete!\n")
            if not self.save_reopen_checkbox.isChecked():
                FreeCAD.Console.PrintMessage("  (If operations aren't editable, save and reopen document)\n\n")
            
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
        # Properties to skip (these are set automatically or shouldn't be copied)
        skip_properties = [
            'Base', 'Label', 'Path', 'Shape',
            'State', 'ViewObject', 'Document', 'Name', 'FullName',
            'Id', 'MemSize', 'Module', 'TypeId', 'Proxy', 'OpValues',
            'Group', 'InList', 'OutList', 'Parents'
        ]
        
        # Get all properties from the source
        source_properties = source.PropertiesList
        
        FreeCAD.Console.PrintMessage(f"  Copying {len(source_properties)} properties...\n")
        copied_count = 0
        
        # First, handle expressions - get the source's expression engine
        source_expressions = {}
        if hasattr(source, 'ExpressionEngine'):
            for expr_tuple in source.ExpressionEngine:
                prop_name = expr_tuple[0]
                expr_value = expr_tuple[1]
                source_expressions[prop_name] = expr_value
        
        # Copy each property
        for prop_name in source_properties:
            # Skip properties in the skip list
            if prop_name in skip_properties:
                continue
            
            # Only copy if both source and target have this property
            if hasattr(source, prop_name) and hasattr(target, prop_name):
                try:
                    # Check if this property has an expression in the source
                    if prop_name in source_expressions:
                        # Source has an expression - copy the expression to target
                        target.setExpression(prop_name, source_expressions[prop_name])
                        copied_count += 1
                        if prop_name in ['StepDown', 'FinalDepth', 'StartDepth', 'Direction', 'Side', 'ToolController']:
                            FreeCAD.Console.PrintMessage(f"    ✓ {prop_name}: {source_expressions[prop_name]} (expression)\n")
                    else:
                        # Source has NO expression (literal value) - clear any expression on target and set literal value
                        # First, clear any existing expression on the target
                        if hasattr(target, 'ExpressionEngine'):
                            for target_expr in target.ExpressionEngine:
                                if target_expr[0] == prop_name:
                                    target.setExpression(prop_name, None)  # Clear the expression
                                    break
                        
                        # Now set the literal value from source
                        source_value = getattr(source, prop_name)
                        setattr(target, prop_name, source_value)
                        copied_count += 1
                        
                        # Log important properties
                        if prop_name in ['StepDown', 'FinalDepth', 'StartDepth', 'Direction', 'Side', 'ToolController']:
                            FreeCAD.Console.PrintMessage(f"    ✓ {prop_name}: {source_value} (literal value)\n")
                        
                except Exception as e:
                    # Property might be read-only or have other restrictions
                    FreeCAD.Console.PrintWarning(f"    Warning: Could not copy {prop_name}: {e}\n")
        
        FreeCAD.Console.PrintMessage(f"  Successfully copied {copied_count} properties\n")
    
    def accept(self):
        """Called when the panel is closed"""
        FreeCADGui.Control.closeDialog()
    
    def reject(self):
        """Called when cancel is clicked"""
        FreeCADGui.Control.closeDialog()
    
    def getStandardButtons(self):
        """Define which buttons to show"""
        return QtGui.QDialogButtonBox.Close
