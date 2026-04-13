# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""
ArcFeedRatePatch - Add arc feed rate control to Profile operations

This module patches Profile operations to add an "ArcFeedRatePercent" property
that allows users to control the feed rate on arc moves (G2/G3) independently
from linear moves (G1). This is useful for:
- Slowing down on tight radius corners
- Material-specific arc cutting speeds
- Better finish quality on curved features

The post-processor reads this property and applies feed rate reduction to G2/G3 moves.
"""

import FreeCAD
import FreeCADGui
from PySide import QtCore


class ArcFeedRatePatch:
    """Patches Profile operations to add ArcFeedRatePercent property"""
    
    def __init__(self):
        self.patched = False
        
    def apply_patch(self):
        """Apply the patch to Profile operations"""
        try:
            # Add property to existing Profile operations
            self.add_property_to_existing_profiles()
            
            # Patch the Profile creation to add property to new operations
            self.patch_profile_creation()
            
            # Patch the Profile task panel GUI to add input field
            self.patch_profile_task_panel()
            
            self.patched = True
            FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Successfully patched Profile operations\n")
            
            return True
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"ArcFeedRatePatch: Failed to apply patch: {e}\n")
            import traceback
            traceback.print_exc()
            return False
    
    def add_property_to_existing_profiles(self):
        """Add ArcFeedRatePercent property to all existing Profile operations"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            return
        
        added_count = 0
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy') and obj.Proxy.__class__.__name__ == 'ObjectProfile':
                if self.add_property_to_profile(obj):
                    added_count += 1
        
        if added_count > 0:
            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: Added ArcFeedRatePercent to {added_count} existing Profile operations\n")
    
    def add_property_to_profile(self, obj):
        """Add ArcFeedRatePercent property to a single Profile operation"""
        if not hasattr(obj, 'ArcFeedRatePercent'):
            try:
                obj.addProperty(
                    "App::PropertyPercent",
                    "ArcFeedRatePercent",
                    "Path",
                    QtCore.QT_TRANSLATE_NOOP("App::Property", 
                        "Feed rate percentage for arc moves (G2/G3). Set to 100% for normal speed, lower values slow down arcs for better finish on curves.")
                )
                obj.ArcFeedRatePercent = 100  # Default to 100% (no change)
                return True
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not add property to {obj.Label}: {e}\n")
                return False
        return False
    
    def patch_profile_creation(self):
        """Patch Profile operation creation to automatically add ArcFeedRatePercent property"""
        try:
            import Path.Op.Profile as ProfileModule
            
            # Store original __init__ if it exists
            original_init = ProfileModule.ObjectProfile.__init__
            
            def patched_init(proxy_self, obj, *args, **kwargs):
                # Call original init
                result = original_init(proxy_self, obj, *args, **kwargs)
                
                # Add our property
                self.add_property_to_profile(obj)
                
                return result
            
            # Replace __init__
            ProfileModule.ObjectProfile.__init__ = patched_init
            
            FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Patched Profile.__init__ for new operations\n")
            
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not patch Profile creation: {e}\n")
    
    def patch_profile_task_panel(self):
        """Patch Profile task panel to add Arc Feed Rate input field"""
        try:
            FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Attempting to patch Profile task panel...\n")
            
            # Try to import the Profile GUI module
            try:
                from PathScripts import PathProfileGui
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Successfully imported PathProfileGui\n")
            except ImportError as e:
                FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not import PathProfileGui: {e}\n")
                # Try alternative import paths
                try:
                    import PathScripts.PathProfileGui as PathProfileGui
                    FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Successfully imported via alternative path\n")
                except ImportError as e2:
                    FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Alternative import also failed: {e2}\n")
                    return
            
            # Check what's in the module
            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: PathProfileGui attributes: {dir(PathProfileGui)}\n")
            
            # Check if TaskPanel exists
            if not hasattr(PathProfileGui, 'TaskPanel'):
                FreeCAD.Console.PrintWarning("ArcFeedRatePatch: PathProfileGui has no TaskPanel class\n")
                FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: Available classes: {[x for x in dir(PathProfileGui) if not x.startswith('_')]}\n")
                return
            
            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: TaskPanel methods: {[x for x in dir(PathProfileGui.TaskPanel) if not x.startswith('_')]}\n")
            
            from PySide import QtGui
            
            # Store original setupUi if it exists
            if hasattr(PathProfileGui.TaskPanel, 'setupUi'):
                original_setupUi = PathProfileGui.TaskPanel.setupUi
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Found setupUi method, patching...\n")
                
                def patched_setupUi(panel_self):
                    FreeCAD.Console.PrintMessage("ArcFeedRatePatch: patched_setupUi called\n")
                    # Call original setupUi
                    result = original_setupUi(panel_self)
                    
                    # Add our Arc Feed Rate field
                    try:
                        # Find the form layout (usually in panel_self.form)
                        if hasattr(panel_self, 'form') and panel_self.form:
                            form_layout = panel_self.form.layout()
                            
                            if form_layout:
                                # Create a horizontal layout for our field
                                arc_layout = QtGui.QHBoxLayout()
                                
                                # Label
                                arc_label = QtGui.QLabel("Arc Feed Rate:")
                                arc_label.setToolTip("Feed rate percentage for arc moves (G2/G3).\nSet below 100% to slow down arcs for better finish on curves.\nLinear moves (G1) use normal feed rate.")
                                arc_layout.addWidget(arc_label)
                                
                                # Spinbox
                                arc_spinbox = QtGui.QSpinBox()
                                arc_spinbox.setMinimum(1)
                                arc_spinbox.setMaximum(100)
                                arc_spinbox.setValue(100)
                                arc_spinbox.setSuffix(" %")
                                arc_spinbox.setToolTip("Percentage of normal feed rate for arcs (default: 100%)")
                                arc_layout.addWidget(arc_spinbox)
                                
                                # Add stretch to push controls to the left
                                arc_layout.addStretch()
                                
                                # Add to form layout
                                form_layout.addLayout(arc_layout)
                                
                                # Store reference to spinbox
                                panel_self.arcFeedRateSpinBox = arc_spinbox
                                
                                # Load existing value if available
                                if hasattr(panel_self, 'obj') and panel_self.obj:
                                    if hasattr(panel_self.obj, 'ArcFeedRatePercent'):
                                        arc_spinbox.setValue(int(panel_self.obj.ArcFeedRatePercent))
                                
                                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Successfully added Arc Feed Rate field to UI\n")
                            else:
                                FreeCAD.Console.PrintWarning("ArcFeedRatePatch: Could not find form layout\n")
                        else:
                            FreeCAD.Console.PrintWarning("ArcFeedRatePatch: panel_self has no form attribute\n")
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Error adding UI field: {e}\n")
                        import traceback
                        traceback.print_exc()
                    
                    return result
                
                # Replace setupUi
                PathProfileGui.TaskPanel.setupUi = patched_setupUi
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: setupUi patched successfully\n")
            else:
                FreeCAD.Console.PrintWarning("ArcFeedRatePatch: TaskPanel has no setupUi method\n")
            
            # Also patch accept() to save the value
            if hasattr(PathProfileGui.TaskPanel, 'accept'):
                original_accept = PathProfileGui.TaskPanel.accept
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Found accept method, patching...\n")
                
                def patched_accept(panel_self):
                    FreeCAD.Console.PrintMessage("ArcFeedRatePatch: patched_accept called\n")
                    # Save Arc Feed Rate value if spinbox exists
                    if hasattr(panel_self, 'arcFeedRateSpinBox') and hasattr(panel_self, 'obj'):
                        if panel_self.obj:
                            # Ensure property exists
                            if not hasattr(panel_self.obj, 'ArcFeedRatePercent'):
                                self.add_property_to_profile(panel_self.obj)
                            # Set the value from spinbox
                            panel_self.obj.ArcFeedRatePercent = panel_self.arcFeedRateSpinBox.value()
                            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: Set ArcFeedRatePercent to {panel_self.arcFeedRateSpinBox.value()}%\n")
                    
                    # Call original accept
                    return original_accept(panel_self)
                
                # Replace accept
                PathProfileGui.TaskPanel.accept = patched_accept
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: accept patched successfully\n")
            else:
                FreeCAD.Console.PrintWarning("ArcFeedRatePatch: TaskPanel has no accept method\n")
            
            FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Profile task panel GUI patching complete\n")
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"ArcFeedRatePatch: Failed to patch task panel: {e}\n")
            import traceback
            traceback.print_exc()
    
    def remove_patch(self):
        """Remove the patch (not implemented - property is benign if unused)"""
        # Note: We don't actually remove the property since it doesn't hurt anything
        # and provides useful functionality even when the post-processor doesn't use it
        pass


# Global instance
_patch_instance = None


def apply_arc_feed_rate_patch():
    """Apply the Arc Feed Rate patch - called from InitGui.py"""
    global _patch_instance
    
    if _patch_instance is None:
        _patch_instance = ArcFeedRatePatch()
    
    return _patch_instance.apply_patch()


def remove_arc_feed_rate_patch():
    """Remove the Arc Feed Rate patch"""
    global _patch_instance
    
    if _patch_instance:
        _patch_instance.remove_patch()
