# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Production Array Feature - Parametric array feature object"""

import FreeCAD
import FreeCADGui
import Part
from PySide import QtCore, QtGui
import os


class ProductionArrayFeature:
    """FeaturePython object for parametric production arrays"""
    
    def __init__(self, obj):
        """Initialize the feature with properties"""
        obj.Proxy = self
        
        # Master sketch reference - use LinkGlobal to allow referencing sketches inside Bodies
        obj.addProperty("App::PropertyLinkGlobal", "MasterSketch", "Base",
                       "Master sketch to array")
        
        # Array configuration
        obj.addProperty("App::PropertyInteger", "CountX", "Array",
                       "Number of copies in X direction").CountX = 3
        obj.addProperty("App::PropertyInteger", "CountY", "Array",
                       "Number of copies in Y direction").CountY = 1
        
        # Spacing mode
        obj.addProperty("App::PropertyEnumeration", "SpacingMode", "Array",
                       "Spacing calculation mode")
        obj.SpacingMode = ["Gap", "Overall"]
        obj.SpacingMode = "Gap"
        
        # Gap spacing parameters
        obj.addProperty("App::PropertyLength", "GapX", "Gap Spacing",
                       "Gap between parts in X direction").GapX = "1.0 in"
        obj.addProperty("App::PropertyLength", "GapY", "Gap Spacing",
                       "Gap between parts in Y direction").GapY = "1.0 in"
        obj.addProperty("App::PropertyBool", "AddPartSize", "Gap Spacing",
                       "Add part size to gap spacing").AddPartSize = True
        
        # Overall spacing parameters
        obj.addProperty("App::PropertyLength", "OverallX", "Overall Spacing",
                       "Total distance in X direction").OverallX = "20.0 in"
        obj.addProperty("App::PropertyLength", "OverallY", "Overall Spacing",
                       "Total distance in Y direction").OverallY = "96.0 in"
        
        # Extrusion parameters
        obj.addProperty("App::PropertyLength", "PadDepth", "Extrusion",
                       "Extrusion depth").PadDepth = "0.5 in"
        obj.addProperty("App::PropertyBool", "Reversed", "Extrusion",
                       "Reverse extrusion direction").Reversed = False
        
        # Options
        obj.addProperty("App::PropertyBool", "KeepMasterVisible", "Options",
                       "Keep master sketch visible").KeepMasterVisible = True
        obj.addProperty("App::PropertyBool", "AutoRename", "Options",
                       "Auto-rename bodies as Part_001, etc.").AutoRename = True
        
        # Internal tracking
        obj.addProperty("App::PropertyLinkList", "GeneratedBodies", "Internal",
                       "List of generated bodies")
        
        obj.setEditorMode("GeneratedBodies", 1)  # Read-only
        
    def onChanged(self, obj, prop):
        """Handle property changes"""
        # When MasterSketch changes, trigger recompute
        if prop == "MasterSketch" and hasattr(obj, "MasterSketch") and obj.MasterSketch:
            pass  # Will recompute automatically
            
    def execute(self, obj):
        """Generate/regenerate the array"""
        if not obj.MasterSketch:
            FreeCAD.Console.PrintWarning("ProductionArray: No master sketch assigned\n")
            return
            
        FreeCAD.Console.PrintMessage(f"\n=== Regenerating Production Array ===\n")
        FreeCAD.Console.PrintMessage(f"Master Sketch: {obj.MasterSketch.Label}\n")
        
        # Delete old bodies
        self.delete_old_bodies(obj)
        
        # Generate new bodies
        self.generate_bodies(obj)
        
        # Hide/show master sketch
        if hasattr(obj.MasterSketch, 'Visibility'):
            obj.MasterSketch.Visibility = obj.KeepMasterVisible
        
        FreeCAD.Console.PrintMessage(f"=== Array Regenerated Successfully ===\n\n")
        
    def delete_old_bodies(self, obj):
        """Delete all previously generated bodies"""
        if not hasattr(obj, 'GeneratedBodies'):
            return
            
        doc = obj.Document
        
        bodies_to_delete = []
        
        # Collect bodies that still exist
        for body in obj.GeneratedBodies:
            if body and body.Document:  # Check if body still exists
                bodies_to_delete.append(body)
        
        if not bodies_to_delete:
            return
            
        FreeCAD.Console.PrintMessage(f"  Deleting {len(bodies_to_delete)} old bodies\n")
        
        # Delete children FIRST (Pad and Sketch inside each Body)
        # This prevents them from escaping to document root
        for body in bodies_to_delete:
            try:
                children = body.Group if hasattr(body, 'Group') else []
                for child in children:
                    try:
                        doc.removeObject(child.Name)
                    except:
                        pass
            except:
                pass
        
        # Remove bodies from ProductionArray Group BEFORE deleting them
        # Otherwise they become "pending delete" and may escape
        current_group = list(obj.Group)
        for body in bodies_to_delete:
            if body in current_group:
                current_group.remove(body)
        obj.Group = current_group
        
        # Now delete the bodies themselves
        for body in bodies_to_delete:
            try:
                doc.removeObject(body.Name)
            except:
                pass
        
        obj.GeneratedBodies = []
        
    def generate_bodies(self, obj):
        """Generate the array of bodies"""
        doc = obj.Document
        sketch = obj.MasterSketch
        
        count_x = obj.CountX
        count_y = obj.CountY
        pad_depth = obj.PadDepth.Value  # In mm
        reversed_pad = obj.Reversed
        
        # Calculate spacing based on mode
        if obj.SpacingMode == "Gap":
            spacing_x = obj.GapX.Value  # mm
            spacing_y = obj.GapY.Value  # mm
            
            # Add part size if requested
            if obj.AddPartSize:
                bbox = self.get_sketch_bounding_box(sketch)
                if bbox:
                    part_size_x = bbox['max_x'] - bbox['min_x']
                    part_size_y = bbox['max_y'] - bbox['min_y']
                    spacing_x += part_size_x
                    spacing_y += part_size_y
                    FreeCAD.Console.PrintMessage(f"Part size: {part_size_x:.2f}mm × {part_size_y:.2f}mm\n")
                    FreeCAD.Console.PrintMessage(f"Effective spacing: {spacing_x:.2f}mm × {spacing_y:.2f}mm\n")
        else:
            # Overall spacing mode
            overall_x = obj.OverallX.Value  # mm
            overall_y = obj.OverallY.Value  # mm
            
            # Get part size
            bbox = self.get_sketch_bounding_box(sketch)
            if bbox:
                part_size_x = bbox['max_x'] - bbox['min_x']
                part_size_y = bbox['max_y'] - bbox['min_y']
                FreeCAD.Console.PrintMessage(f"Part size: {part_size_x:.2f}mm × {part_size_y:.2f}mm\n")
            else:
                part_size_x = 0.0
                part_size_y = 0.0
            
            # Calculate spacing
            if count_x > 1:
                spacing_x = (overall_x - part_size_x) / (count_x - 1)
            else:
                spacing_x = 0.0
                
            if count_y > 1:
                spacing_y = (overall_y - part_size_y) / (count_y - 1)
            else:
                spacing_y = 0.0
            
            FreeCAD.Console.PrintMessage(f"Overall distance: {overall_x:.2f}mm × {overall_y:.2f}mm\n")
            FreeCAD.Console.PrintMessage(f"Calculated spacing: {spacing_x:.2f}mm × {spacing_y:.2f}mm\n")
        
        FreeCAD.Console.PrintMessage(f"Grid: {count_x} × {count_y} = {count_x * count_y} bodies\n")
        
        # Create bodies first - use obj.newObject to create them directly inside the ProductionArray container
        bodies_created = []
        body_index = 1
        
        for iy in range(count_y):
            for ix in range(count_x):
                # Create new body directly inside the ProductionArray (not at document root)
                body = obj.newObject('PartDesign::Body', 'Body')
                
                # Auto-rename if requested
                if obj.AutoRename:
                    body.Label = f'Part_{body_index:03d}'
                
                bodies_created.append(body)
                body_index += 1
        
        # Bodies are already in the Group by virtue of being created with obj.newObject()
        # Store the list for tracking and deletion
        obj.GeneratedBodies = bodies_created
        
        # Now create features in each body
        body_index = 1
        for iy in range(count_y):
            for ix in range(count_x):
                body = bodies_created[(iy * count_x) + ix]
                
                # Calculate offset
                offset_x = ix * spacing_x
                offset_y = iy * spacing_y
                
                # Create sketch in body
                new_sketch = body.newObject('Sketcher::SketchObject', 'Sketch')
                
                # Leave sketch unattached - just position it in XY plane at origin
                # This allows geometry to use absolute coordinates
                new_sketch.Placement = FreeCAD.Placement()
                
                # Copy geometry from master sketch with offset
                self.copy_sketch_geometry(sketch, new_sketch, offset_x, offset_y)
                
                # Force sketch to recompute and generate Shape
                new_sketch.recompute()
                
                # Solve the sketch constraints
                new_sketch.solve()
                
                # Create Pad
                pad = body.newObject("PartDesign::Pad", "Pad")
                pad.Profile = new_sketch
                pad.Length = abs(pad_depth)  # Length is always positive
                pad.Reversed = reversed_pad  # Direction controlled by Reversed flag
                
                # Force pad to recompute
                pad.recompute()
                
                # Set the Tip to the Pad (tells Body what feature to display)
                body.Tip = pad
                
                # Recompute THIS body immediately to finalize the Pad before moving on
                # This prevents FreeCAD from creating orphaned Pads at document root
                body.recompute()
                
                FreeCAD.Console.PrintMessage(f"  Created {body.Label} at ({offset_x:.1f}, {offset_y:.1f})\n")
                body_index += 1
        
    def get_sketch_bounding_box(self, sketch):
        """Get bounding box of sketch"""
        if not hasattr(sketch, 'Geometry') or len(sketch.Geometry) == 0:
            return None
        
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for geo in sketch.Geometry:
            points = []
            
            if hasattr(geo, 'StartPoint'):
                points.append(geo.StartPoint)
            if hasattr(geo, 'EndPoint'):
                points.append(geo.EndPoint)
            if hasattr(geo, 'Center'):
                center = geo.Center
                if hasattr(geo, 'Radius'):
                    radius = geo.Radius
                    points.append(FreeCAD.Vector(center.x - radius, center.y - radius, center.z))
                    points.append(FreeCAD.Vector(center.x + radius, center.y + radius, center.z))
                else:
                    points.append(center)
            
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
    
    def copy_sketch_geometry(self, source_sketch, target_sketch, offset_x, offset_y):
        """Copy geometry from source to target with offset"""
        for geo in source_sketch.Geometry:
            new_geo = geo.copy()
            
            # Apply offset based on geometry type
            # For arcs/circles: offset center
            if hasattr(new_geo, 'Center'):
                new_geo.Center = FreeCAD.Vector(
                    new_geo.Center.x + offset_x,
                    new_geo.Center.y + offset_y,
                    new_geo.Center.z
                )
            
            # For lines/line segments: offset start and end points
            elif hasattr(new_geo, 'StartPoint') and hasattr(new_geo, 'EndPoint'):
                new_geo.StartPoint = FreeCAD.Vector(
                    new_geo.StartPoint.x + offset_x,
                    new_geo.StartPoint.y + offset_y,
                    new_geo.StartPoint.z
                )
                new_geo.EndPoint = FreeCAD.Vector(
                    new_geo.EndPoint.x + offset_x,
                    new_geo.EndPoint.y + offset_y,
                    new_geo.EndPoint.z
                )
            
            # For points
            elif hasattr(new_geo, 'X') and hasattr(new_geo, 'Y'):
                new_geo.X += offset_x
                new_geo.Y += offset_y
            
            target_sketch.addGeometry(new_geo, False)


class ProductionArrayViewProvider:
    """ViewProvider for ProductionArray feature"""
    
    def __init__(self, vobj):
        vobj.Proxy = self
        
    def getIcon(self):
        """Return path to icon"""
        import os
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(addon_dir, "Resources", "icons", "ProductionArray.svg")
        if os.path.exists(icon_path):
            return icon_path
        return None
        
    def attach(self, vobj):
        self.Object = vobj.Object
        
    def updateData(self, obj, prop):
        return
        
    def onChanged(self, vobj, prop):
        return
        
    def doubleClicked(self, vobj):
        """Open panel for editing when double-clicked"""
        from .ProductionArrayPanel import ProductionArrayPanel
        
        obj = vobj.Object
        panel = ProductionArrayPanel(None, feature_object=obj)
        FreeCADGui.Control.showDialog(panel)
        return True
        
    def __getstate__(self):
        return None
        
    def __setstate__(self, state):
        return None


def create_production_array(sketch):
    """Create a new ProductionArray feature
    
    Args:
        sketch: Master sketch to array
        
    Returns:
        ProductionArray feature object
    """
    doc = FreeCAD.ActiveDocument
    
    # Create the feature - use DocumentObjectGroupPython for Group support
    obj = doc.addObject("App::DocumentObjectGroupPython", "ProductionArray")
    ProductionArrayFeature(obj)
    
    # Create view provider
    if FreeCAD.GuiUp:
        ProductionArrayViewProvider(obj.ViewObject)
    
    # Set master sketch
    obj.MasterSketch = sketch
    
    return obj
