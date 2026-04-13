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
            
            # Import the correct Profile GUI module (FreeCAD 1.1+)
            try:
                from Path.Op.Gui import Profile as ProfileGui
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Successfully imported Path.Op.Gui.Profile\n")
            except ImportError as e:
                FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not import Profile GUI: {e}\n")
                return
            
            from PySide import QtGui
            
            # Patch getForm() to add our widget
            if hasattr(ProfileGui.TaskPanelOpPage, 'getForm'):
                original_getForm = ProfileGui.TaskPanelOpPage.getForm
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Found getForm method, patching...\n")
                
                def patched_getForm(panel_self):
                    # Call original getForm to get the form
                    form = original_getForm(panel_self)
                    
                    try:
                        # Add Arc Feed Rate field to the form
                        layout = form.layout()
                        if layout:
                            # Create horizontal layout for our field
                            arcLayout = QtGui.QHBoxLayout()
                            
                            # Label
                            arcLabel = QtGui.QLabel("Arc Feed Rate:")
                            arcLabel.setToolTip("Feed rate percentage for arc moves (G2/G3).\nSet below 100% to slow down arcs for better finish.")
                            arcLayout.addWidget(arcLabel)
                            
                            # Spinbox
                            arcSpinbox = QtGui.QSpinBox()
                            arcSpinbox.setMinimum(1)
                            arcSpinbox.setMaximum(100)
                            arcSpinbox.setValue(100)
                            arcSpinbox.setSuffix(" %")
                            arcSpinbox.setObjectName("arcFeedRateSpinBox")
                            arcLayout.addWidget(arcSpinbox)
                            arcLayout.addStretch()
                            
                            # Add to form layout
                            layout.addLayout(arcLayout)
                            
                            FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Added Arc Feed Rate field to form\n")
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not add field to form: {e}\n")
                        import traceback
                        traceback.print_exc()
                    
                    return form
                
                ProfileGui.TaskPanelOpPage.getForm = patched_getForm
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: getForm patched successfully\n")
            
            # Patch setFields() to load the value
            if hasattr(ProfileGui.TaskPanelOpPage, 'setFields'):
                original_setFields = ProfileGui.TaskPanelOpPage.setFields
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Found setFields method, patching...\n")
                
                def patched_setFields(panel_self, obj):
                    # Call original setFields
                    original_setFields(panel_self, obj)
                    
                    # Load Arc Feed Rate value
                    try:
                        spinbox = panel_self.form.findChild(QtGui.QSpinBox, "arcFeedRateSpinBox")
                        if spinbox and hasattr(obj, 'ArcFeedRatePercent'):
                            spinbox.setValue(int(obj.ArcFeedRatePercent))
                            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: Loaded ArcFeedRatePercent = {obj.ArcFeedRatePercent}%\n")
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not load Arc Feed Rate: {e}\n")
                
                ProfileGui.TaskPanelOpPage.setFields = patched_setFields
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: setFields patched successfully\n")
            
            # Patch getFields() to save the value
            if hasattr(ProfileGui.TaskPanelOpPage, 'getFields'):
                original_getFields = ProfileGui.TaskPanelOpPage.getFields
                patcher_self = self  # Capture self for use in nested function
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: Found getFields method, patching...\n")
                
                def patched_getFields(panel_self, obj):
                    # Call original getFields
                    original_getFields(panel_self, obj)
                    
                    # Save Arc Feed Rate value
                    try:
                        spinbox = panel_self.form.findChild(QtGui.QSpinBox, "arcFeedRateSpinBox")
                        if spinbox:
                            # Ensure property exists
                            if not hasattr(obj, 'ArcFeedRatePercent'):
                                patcher_self.add_property_to_profile(obj)
                            # Set the value
                            obj.ArcFeedRatePercent = spinbox.value()
                            FreeCAD.Console.PrintMessage(f"ArcFeedRatePatch: Saved ArcFeedRatePercent = {spinbox.value()}%\n")
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"ArcFeedRatePatch: Could not save Arc Feed Rate: {e}\n")
                
                ProfileGui.TaskPanelOpPage.getFields = patched_getFields
                FreeCAD.Console.PrintMessage("ArcFeedRatePatch: getFields patched successfully\n")
            
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
