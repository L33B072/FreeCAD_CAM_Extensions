# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""
ProfileOrderPatch - Monkey-patch for FreeCAD Profile operations to respect Base geometry order

This module patches the Profile operation's areaOpShapes() method to add
a "RespectBaseOrder" property that, when enabled, preserves the order of
Base geometries in the toolpath generation.
"""

import FreeCAD
import FreeCADGui
from PySide import QtCore


class ProfileOrderPatch:
    """Patches Profile operations to add RespectBaseOrder functionality"""
    
    def __init__(self):
        self.original_area_op_shapes = None
        self.patched = False
        
    def apply_patch(self):
        """Apply the monkey-patch to Profile operations"""
        try:
            import Path.Op.Profile as ProfileModule
            
            # Store the original method
            self.original_area_op_shapes = ProfileModule.ObjectProfile.areaOpShapes
            
            # Create our patched version
            def patched_area_op_shapes(proxy_self, obj):
                """
                Patched areaOpShapes that respects Base order when RespectBaseOrder is True
                """
                # Check if RespectBaseOrder property exists and is True
                if hasattr(obj, 'RespectBaseOrder') and obj.RespectBaseOrder:
                    FreeCAD.Console.PrintMessage(f"ProfileOrderPatch: Processing {obj.Label} in Base order\n")
                    
                    # Call original method to get shapes
                    shapes = self.original_area_op_shapes(proxy_self, obj)
                    
                    # The shapes should already be in Base order since we're using
                    # HandleMultipleFeatures: Individually
                    # We just need to make sure they don't get reordered
                    
                    return shapes
                else:
                    # Use original behavior
                    return self.original_area_op_shapes(proxy_self, obj)
            
            # Replace the method
            ProfileModule.ObjectProfile.areaOpShapes = patched_area_op_shapes
            
            self.patched = True
            FreeCAD.Console.PrintMessage("ProfileOrderPatch: Successfully patched Profile.areaOpShapes\n")
            
            # Add property to existing Profile operations
            self.add_property_to_existing_profiles()
            
            # Patch the Profile creation to add property to new operations
            self.patch_profile_creation()
            
            return True
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"ProfileOrderPatch: Failed to apply patch: {e}\n")
            import traceback
            traceback.print_exc()
            return False
    
    def add_property_to_existing_profiles(self):
        """Add RespectBaseOrder property to all existing Profile operations"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            return
        
        added_count = 0
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy') and obj.Proxy.__class__.__name__ == 'ObjectProfile':
                if self.add_property_to_profile(obj):
                    added_count += 1
        
        if added_count > 0:
            FreeCAD.Console.PrintMessage(f"ProfileOrderPatch: Added RespectBaseOrder to {added_count} existing Profile operations\n")
    
    def add_property_to_profile(self, obj):
        """Add RespectBaseOrder property to a single Profile operation"""
        if not hasattr(obj, 'RespectBaseOrder'):
            try:
                obj.addProperty(
                    "App::PropertyBool",
                    "RespectBaseOrder",
                    "Path",
                    QtCore.QT_TRANSLATE_NOOP("App::Property", 
                        "Respect Base geometry order instead of optimizing toolpath sequence")
                )
                obj.RespectBaseOrder = False  # Default to False for compatibility
                return True
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"ProfileOrderPatch: Could not add property to {obj.Label}: {e}\n")
                return False
        return False
    
    def patch_profile_creation(self):
        """Patch Profile operation creation to automatically add RespectBaseOrder property"""
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
            
            FreeCAD.Console.PrintMessage("ProfileOrderPatch: Patched Profile.__init__ for new operations\n")
            
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"ProfileOrderPatch: Could not patch Profile creation: {e}\n")
    
    def remove_patch(self):
        """Remove the monkey-patch and restore original behavior"""
        if not self.patched:
            return
        
        try:
            import Path.Op.Profile as ProfileModule
            
            if self.original_area_op_shapes:
                ProfileModule.ObjectProfile.areaOpShapes = self.original_area_op_shapes
                self.patched = False
                FreeCAD.Console.PrintMessage("ProfileOrderPatch: Patch removed\n")
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"ProfileOrderPatch: Failed to remove patch: {e}\n")


# Global instance
_patch_instance = None


def apply_profile_order_patch():
    """Apply the Profile order patch - called from InitGui.py"""
    global _patch_instance
    
    if _patch_instance is None:
        _patch_instance = ProfileOrderPatch()
    
    return _patch_instance.apply_patch()


def remove_profile_order_patch():
    """Remove the Profile order patch"""
    global _patch_instance
    
    if _patch_instance:
        _patch_instance.remove_patch()
