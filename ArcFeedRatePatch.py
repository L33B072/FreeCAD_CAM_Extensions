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
