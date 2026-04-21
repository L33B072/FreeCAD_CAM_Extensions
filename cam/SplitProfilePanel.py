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


def discoverBottomFaces(job):
    """
    Discover bottom faces of all bodies/solids in the Job's Model.
    
    Finds all faces at the minimum Z level (bottom) for each body.
    Handles bodies with multiple solids by finding all faces at that level.
    
    Returns list of (object, (feature_name,)) tuples suitable for Profile.Base
    """
    if not job or not hasattr(job, 'Model') or not job.Model:
        return []
    
    base_items = []
    
    # Iterate through all bodies in the job's model
    for body in job.Model.Group:
        if not hasattr(body, 'Shape') or not body.Shape.Faces:
            continue
        
        FreeCAD.Console.PrintMessage(f"  Analyzing {body.Label}...\n")
        
        # Find the minimum Z coordinate across all faces
        min_z = float('inf')
        for face in body.Shape.Faces:
            face_z = face.CenterOfMass.z
            if face_z < min_z:
                min_z = face_z
        
        # Tolerance: faces within this distance of min_z are considered "bottom faces"
        # Larger tolerance handles multiple solids at approximately the same level
        z_tolerance = 2.0  # mm (increased tolerance for manufacturing variations)
        
        # Find ALL faces at or near the minimum Z
        bottom_faces = []
        for face_idx, face in enumerate(body.Shape.Faces):
            face_z = face.CenterOfMass.z
            
            # Include all faces within tolerance of minimum Z
            if abs(face_z - min_z) <= z_tolerance:
                bottom_faces.append((face_idx, face_z))
        
        # Add all discovered bottom faces to base items
        for face_idx, face_z in bottom_faces:
            face_name = f"Face{face_idx + 1}"  # FreeCAD uses 1-based indexing
            base_items.append((body, (face_name,)))
            FreeCAD.Console.PrintMessage(f"    Bottom face: {face_name} (Z={face_z:.3f})\n")
        
        # Info message
        if len(bottom_faces) > 1:
            FreeCAD.Console.PrintMessage(f"    Found {len(bottom_faces)} bottom faces (multiple solids or features)\n")
        elif len(bottom_faces) == 0:
            FreeCAD.Console.PrintWarning(f"    Warning: No bottom faces found for {body.Label}\n")
    
    return base_items


class SplitProfilePanel:
    """Panel for splitting a Profile operation into separate operations"""
    
    def __init__(self, operation, auto_discovered=False):
        self.operation = operation
        self.auto_discovered = auto_discovered
        
        # Prepare list of items to split
        # Each item is (base_object, feature_name)
        self.split_items = []
        
        # Check if Base is empty or has only one item
        if not self.operation.Base or len(self.operation.Base) < 1:
            FreeCAD.Console.PrintWarning("Profile operation has no base geometries set. Auto-discovering bottom faces...\n")
            
            # Auto-discover bottom faces
            import PathScripts.PathUtils as PathUtils
            job = PathUtils.findParentJob(self.operation)
            discovered_bases = discoverBottomFaces(job)
            
            if discovered_bases:
                FreeCAD.Console.PrintMessage(f"Discovered {len(discovered_bases)} bottom faces\n")
                # Populate the operation's Base with discovered geometries
                self.operation.Base = discovered_bases
                self.operation.recompute()
                self.auto_discovered = True
            else:
                FreeCAD.Console.PrintError("Could not auto-discover any base geometries\n")
        
        # Build split items list from Base
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
        
        # Auto-discovery notification
        if self.auto_discovered:
            auto_msg = QtGui.QLabel("ℹ️ <i>Base geometries were auto-discovered from Job Model (bottom faces)</i>")
            auto_msg.setWordWrap(True)
            auto_msg.setStyleSheet("QLabel { color: #0066cc; background-color: #e6f2ff; padding: 5px; border-radius: 3px; }")
            layout.addWidget(auto_msg)
            layout.addSpacing(5)
        
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
        
        # Dressup options
        dressup_group = QtGui.QGroupBox("Dressup Operations (Optional)")
        dressup_layout = QtGui.QVBoxLayout()
        
        # Tag dressup checkbox
        self.apply_tags_checkbox = QtGui.QCheckBox("Add Holding Tags to each split operation")
        self.apply_tags_checkbox.setChecked(False)
        self.apply_tags_checkbox.toggled.connect(self.onTagsCheckboxToggled)
        dressup_layout.addWidget(self.apply_tags_checkbox)
        
        # Get document units for default values
        import PathScripts.PathUtils as PathUtils
        job = PathUtils.findParentJob(self.operation)
        units_suffix, units_multiplier = self.getDocumentUnits(job)
        
        # Tag settings (initially hidden)
        self.tag_settings_widget = QtGui.QWidget()
        tag_settings_layout = QtGui.QFormLayout()
        tag_settings_layout.setContentsMargins(20, 5, 5, 5)  # Indent settings
        
        self.tag_width_spin = QtGui.QDoubleSpinBox()
        self.tag_width_spin.setRange(0.001 * units_multiplier, 100.0 * units_multiplier)
        self.tag_width_spin.setValue(5.0 * units_multiplier)  # 5mm or equivalent
        self.tag_width_spin.setDecimals(3)
        self.tag_width_spin.setSuffix(units_suffix)
        tag_settings_layout.addRow("Tag Width:", self.tag_width_spin)
        
        self.tag_height_spin = QtGui.QDoubleSpinBox()
        self.tag_height_spin.setRange(0.001 * units_multiplier, 100.0 * units_multiplier)
        self.tag_height_spin.setValue(2.0 * units_multiplier)  # 2mm or equivalent
        self.tag_height_spin.setDecimals(3)
        self.tag_height_spin.setSuffix(units_suffix)
        tag_settings_layout.addRow("Tag Height:", self.tag_height_spin)
        
        self.tag_angle_spin = QtGui.QDoubleSpinBox()
        self.tag_angle_spin.setRange(30.0, 90.0)
        self.tag_angle_spin.setValue(45.0)
        self.tag_angle_spin.setDecimals(1)
        self.tag_angle_spin.setSuffix("°")
        tag_settings_layout.addRow("Tag Angle:", self.tag_angle_spin)
        
        self.tag_count_spin = QtGui.QSpinBox()
        self.tag_count_spin.setRange(1, 20)
        self.tag_count_spin.setValue(4)
        self.tag_count_spin.setToolTip("Number of tags to auto-generate around each profile")
        tag_settings_layout.addRow("Tags per profile:", self.tag_count_spin)
        
        self.tag_settings_widget.setLayout(tag_settings_layout)
        self.tag_settings_widget.setVisible(False)
        dressup_layout.addWidget(self.tag_settings_widget)
        
        dressup_group.setLayout(dressup_layout)
        layout.addWidget(dressup_group)
        
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
    
    def onTagsCheckboxToggled(self, checked):
        """Toggle visibility of tag settings when checkbox is toggled"""
        self.tag_settings_widget.setVisible(checked)
    
    def getDocumentUnits(self, job):
        """
        Get the document's unit system and return suffix and multiplier.
        
        Returns:
            tuple: (suffix_string, multiplier_from_mm)
                   e.g., (" mm", 1.0) or (" in", 0.0393701)
        """
        # Try to get units from the Job
        if job and hasattr(job, 'Units'):
            units = job.Units
        else:
            # Fallback: check document units
            try:
                units = FreeCAD.ActiveDocument.Units
            except:
                units = 0  # Default to metric
        
        # Units: 0 = Metric (mm), 1 = Imperial (inches)
        if units == 1:  # Imperial
            return (" in", 0.0393701)  # 1mm = 0.0393701 inches
        else:  # Metric (default)
            return (" mm", 1.0)
    
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
            
            # Only manually manage operations group if NOT applying tags
            # If applying tags, the dressup application will handle operation management
            if not self.apply_tags_checkbox.isChecked():
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
            # (Do this before applying dressups so we don't delete wrapped operations)
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
            
            # Apply tag dressups if requested
            if self.apply_tags_checkbox.isChecked():
                FreeCAD.Console.PrintMessage("\n  Applying tag dressups...\n")
                try:
                    # Store references to operations that will be replaced by dressups
                    operations_to_dressup = list(new_operations)
                    dressuped_operations = []
                    
                    for op in operations_to_dressup:
                        dressuped_op = self.applyTagDressup(op, job)
                        if dressuped_op:
                            dressuped_operations.append(dressuped_op)
                    
                    # Update the new_operations list to reference dressups instead of base operations
                    # This ensures the success message and any further processing uses the dressups
                    new_operations = dressuped_operations
                    
                    FreeCAD.Console.PrintMessage(f"  ✓ Applied tags to {len(dressuped_operations)} operations\n")
                except Exception as e:
                    FreeCAD.Console.PrintError(f"  Error applying tag dressups: {e}\n")
                    import traceback
                    traceback.print_exc()
            
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
            
            # Add tag info if applied
            if self.apply_tags_checkbox.isChecked():
                msg += f"\n✓ Tags applied to all operations"
            
            # Add note about editability if not auto-reopening
            if not self.save_reopen_checkbox.isChecked():
                msg += "\n\nNote: If operations aren't fully editable, save and reopen the document."
            
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            
            FreeCAD.Console.PrintMessage(f"✓ Profile split complete!\n")
            if self.apply_tags_checkbox.isChecked():
                FreeCAD.Console.PrintMessage(f"✓ Tags applied to all {len(new_operations)} operations\n")
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
    
    def applyTagDressup(self, base_operation, job):
        """
        Apply tag dressup to a profile operation.
        
        Args:
            base_operation: The Profile operation to wrap with tags
            job: The parent Job object
            
        Returns:
            The created tag dressup operation, or None if failed
        """
        try:
            import Path.Dressup.Tags as PathDressupTag
            import PathScripts.PathUtils as PathUtils
            
            # Create the tag dressup using FreeCAD's standard pattern
            tag_name = f"{base_operation.Label}_Tags"
            FreeCAD.Console.PrintMessage(f"    Creating {tag_name}...\n")
            
            doc = FreeCAD.ActiveDocument
            
            # Create the dressup object
            tag_dressup = doc.addObject("Path::FeaturePython", tag_name)
            
            # Initialize the dressup proxy (this sets up Base property and links)
            PathDressupTag.ObjectTagDressup(tag_dressup, base_operation)
            
            # Verify Base property is set correctly
            if hasattr(tag_dressup, 'Base'):
                FreeCAD.Console.PrintMessage(f"      ✓ Base property set to: {tag_dressup.Base.Label if tag_dressup.Base else 'None'}\n")
            else:
                FreeCAD.Console.PrintWarning(f"      Warning: Base property not found on tag_dressup\n")
            
            # Set up the ViewProvider for proper tree display
            if FreeCAD.GuiUp:
                try:
                    import Path.Dressup.Gui.Tags as PathDressupTagGui
                    # Assign the ViewProvider to ViewObject.Proxy (not just calling the constructor)
                    tag_dressup.ViewObject.Proxy = PathDressupTagGui.PathDressupTagViewProvider(tag_dressup.ViewObject)
                    FreeCAD.Console.PrintMessage(f"      ✓ ViewProvider assigned to ViewObject.Proxy\n")
                except Exception as e:
                    FreeCAD.Console.PrintWarning(f"      Warning: Could not set ViewProvider: {e}\n")
                    import traceback
                    traceback.print_exc()
            
            # Configure tag properties from UI
            # Spinbox values are in document units, but FreeCAD tag properties expect mm
            # Get units info to convert back to mm
            units_suffix, units_multiplier = self.getDocumentUnits(job)
            
            # Convert from user units to mm (divide by multiplier)
            width_mm = self.tag_width_spin.value() / units_multiplier
            height_mm = self.tag_height_spin.value() / units_multiplier
            
            tag_dressup.Width = width_mm
            tag_dressup.Height = height_mm
            tag_dressup.Angle = self.tag_angle_spin.value()
            
            # Generate tag positions
            # We need to generate actual positions, not just set a count
            tag_count = self.tag_count_spin.value()
            
            # Trigger path generation first so we have a path to work with
            tag_dressup.Proxy.execute(tag_dressup)
            
            # Now generate tag positions using the tag dressup's methods
            if hasattr(tag_dressup.Proxy, 'generateTags'):
                try:
                    # Some versions use generateTags method
                    tag_dressup.Proxy.generateTags(tag_dressup, tag_count)
                    FreeCAD.Console.PrintMessage(f"      ✓ Generated {tag_count} tag positions\n")
                except Exception as e:
                    FreeCAD.Console.PrintWarning(f"      Warning: Could not auto-generate tags: {e}\n")
            elif hasattr(tag_dressup, 'Positions'):
                # If no auto-generation, at least initialize empty positions list
                tag_dressup.Positions = []
                FreeCAD.Console.PrintMessage(f"      Note: Tag positions initialized empty (edit manually to add)\n")
            
            # Use FreeCAD's Job.addOperation to properly nest the dressup
            # This handles:
            # - Removing base_operation from Job.Operations.Group
            # - Adding tag_dressup to Job.Operations.Group  
            # - Hiding base_operation's ViewObject
            # - Proper tree nesting
            FreeCAD.Console.PrintMessage(f"      Adding to Job operations...\n")
            
            # Get current operations group
            operations_group = list(job.Operations.Group)
            
            # Find and replace base_operation with tag_dressup
            if base_operation in operations_group:
                base_index = operations_group.index(base_operation)
                operations_group[base_index] = tag_dressup
                
                # Update the Job's operations group
                job.Operations.Group = operations_group
                
                FreeCAD.Console.PrintMessage(f"      ✓ Replaced {base_operation.Label} with {tag_dressup.Label} in Job\n")
            else:
                # Base operation not in group, just add the tag dressup
                operations_group.append(tag_dressup)
                job.Operations.Group = operations_group
                FreeCAD.Console.PrintMessage(f"      ✓ Added {tag_dressup.Label} to Job\n")
            
            # Hide the base operation
            if hasattr(base_operation, 'ViewObject') and base_operation.ViewObject:
                base_operation.ViewObject.Visibility = False
                FreeCAD.Console.PrintMessage(f"      ✓ Base profile hidden\n")
            
            # Verify the operation was added and base was removed
            if tag_dressup in job.Operations.Group:
                FreeCAD.Console.PrintMessage(f"      ✓ Tag dressup in Job operations\n")
            if base_operation not in job.Operations.Group:
                FreeCAD.Console.PrintMessage(f"      ✓ Base profile removed from Job operations\n")
            else:
                FreeCAD.Console.PrintWarning(f"      Warning: Base profile still in Job operations!\n")
            
            # Force tree refresh
            if FreeCAD.GuiUp:
                FreeCADGui.updateGui()
            
            # Recompute to generate the path with tags
            tag_dressup.recompute()
            
            FreeCAD.Console.PrintMessage(f"      ✓ Tags: W={tag_dressup.Width}, H={tag_dressup.Height}, Angle={tag_dressup.Angle}\n")
            
            return tag_dressup
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"    Failed to apply tags to {base_operation.Label}: {e}\n")
            import traceback
            traceback.print_exc()
            return None
    
    def accept(self):
        """Called when the panel is closed"""
        FreeCADGui.Control.closeDialog()
    
    def reject(self):
        """Called when cancel is clicked"""
        FreeCADGui.Control.closeDialog()
    
    def getStandardButtons(self):
        """Define which buttons to show"""
        return QtGui.QDialogButtonBox.Close
