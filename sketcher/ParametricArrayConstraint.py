# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Parametric Array Constraint for Sketcher - Creates parametric rectangular arrays"""

import FreeCAD
import FreeCADGui
import Part
import Sketcher
from PySide import QtCore, QtGui
import json


class ParametricArrayConstraint:
    """Manages parametric rectangular arrays in sketches"""
    
    @staticmethod
    def get_array_data(sketch):
        """Get array metadata from sketch"""
        if not hasattr(sketch, 'ArrayData'):
            return {}
        try:
            return json.loads(sketch.ArrayData)
        except:
            return {}
    
    @staticmethod
    def set_array_data(sketch, data):
        """Store array metadata in sketch"""
        # Add custom property if it doesn't exist
        if not hasattr(sketch, 'ArrayData'):
            sketch.addProperty("App::PropertyString", "ArrayData", "Arrays", "Parametric array metadata")
            sketch.setEditorMode("ArrayData", 1)  # Read-only in UI
        sketch.ArrayData = json.dumps(data)
    
    @staticmethod
    def get_next_array_id(sketch):
        """Get next available array ID"""
        data = ParametricArrayConstraint.get_array_data(sketch)
        if not data:
            return "Array001"
        
        max_num = 0
        for array_id in data.keys():
            if array_id.startswith("Array"):
                try:
                    num = int(array_id[5:])
                    max_num = max(max_num, num)
                except:
                    pass
        return f"Array{max_num + 1:03d}"
    
    @staticmethod
    def copy_internal_constraints(sketch, base_indices, grid, rows, cols):
        """Copy SHAPE constraints (not size) that are internal to the base geometry to all array copies
        
        This copies only structural constraints like Coincident, Horizontal, Vertical, etc.
        Size constraints (Distance, Equal, Radius) are NOT copied - instead, Equal constraints
        will be added to link copy sizes to base, making the array truly parametric.
        
        Args:
            sketch: The sketch object
            base_indices: List of base geometry indices
            grid: 2D array of geometry indices [row][col] = [geo_indices]
            rows, cols: Array dimensions
        
        Returns:
            int: Number of constraints copied
        """
        base_set = set(base_indices)
        constraint_count = 0
        
        # Define which constraint types to copy (SHAPE constraints only)
        shape_constraints = {'Coincident', 'Horizontal', 'Vertical', 'Parallel', 'Perpendicular'}
        
        # Find all constraints that involve ONLY base geometry AND are shape constraints
        internal_constraints = []
        for i, constraint in enumerate(sketch.Constraints):
            # Skip size constraints - we'll use Equal constraints instead
            if constraint.Type not in shape_constraints:
                continue
            
            # Get geometry indices involved in this constraint
            involved_geos = set()
            
            if constraint.First >= 0:
                involved_geos.add(constraint.First)
            if hasattr(constraint, 'Second') and constraint.Second >= 0:
                involved_geos.add(constraint.Second)
            if hasattr(constraint, 'Third') and constraint.Third >= 0:
                involved_geos.add(constraint.Third)
            
            # Check if all involved geometry is in our base set
            if involved_geos and involved_geos.issubset(base_set):
                internal_constraints.append(constraint)
                FreeCAD.Console.PrintMessage(f"  Found internal constraint: {constraint.Type}\n")
        
        # For each array copy position (excluding base at 0,0)
        for row in range(rows):
            for col in range(cols):
                if row == 0 and col == 0:
                    continue  # Skip base position
                
                # Create a mapping from base indices to copy indices for this position
                index_map = {}
                for i, base_idx in enumerate(base_indices):
                    copy_idx = grid[row][col][i]
                    index_map[base_idx] = copy_idx
                
                # Copy each internal constraint with remapped indices
                for constraint in internal_constraints:
                    try:
                        # Get the constraint type
                        c_type = constraint.Type
                        
                        # Create appropriate constraint based on type (SHAPE constraints only)
                        if c_type == 'Coincident':
                            # Coincident requires two geometry indices and point positions
                            if constraint.First in index_map and constraint.Second in index_map:
                                new_constraint = Sketcher.Constraint('Coincident',
                                    index_map[constraint.First], constraint.FirstPos,
                                    index_map[constraint.Second], constraint.SecondPos)
                                sketch.addConstraint(new_constraint)
                                constraint_count += 1
                        
                        elif c_type == 'Horizontal':
                            # Horizontal requires one geometry index
                            if constraint.First in index_map:
                                new_constraint = Sketcher.Constraint('Horizontal', index_map[constraint.First])
                                sketch.addConstraint(new_constraint)
                                constraint_count += 1
                        
                        elif c_type == 'Vertical':
                            # Vertical requires one geometry index
                            if constraint.First in index_map:
                                new_constraint = Sketcher.Constraint('Vertical', index_map[constraint.First])
                                sketch.addConstraint(new_constraint)
                                constraint_count += 1
                        
                        elif c_type == 'Parallel':
                            # Parallel requires two geometry indices
                            if constraint.First in index_map and constraint.Second in index_map:
                                new_constraint = Sketcher.Constraint('Parallel',
                                    index_map[constraint.First], index_map[constraint.Second])
                                sketch.addConstraint(new_constraint)
                                constraint_count += 1
                        
                        elif c_type == 'Perpendicular':
                            # Perpendicular requires two geometry indices
                            if constraint.First in index_map and constraint.Second in index_map:
                                new_constraint = Sketcher.Constraint('Perpendicular',
                                    index_map[constraint.First], index_map[constraint.Second])
                                sketch.addConstraint(new_constraint)
                                constraint_count += 1
                        
                        else:
                            FreeCAD.Console.PrintWarning(f"  Unsupported constraint type: {c_type}\n")
                        
                    except Exception as e:
                        FreeCAD.Console.PrintWarning(f"Could not copy constraint {c_type}: {e}\n")
        
        if constraint_count > 0:
            FreeCAD.Console.PrintMessage(f"Copied {constraint_count} shape constraints to array copies\n")
        else:
            FreeCAD.Console.PrintMessage("No shape constraints found in base geometry\n")
        
        return constraint_count
    
    @staticmethod
    def create_array(sketch, base_geometry_indices, rows, cols, row_spacing, col_spacing):
        """Create a new parametric array
        
        Args:
            sketch: The sketch object
            base_geometry_indices: List of geometry indices to array
            rows: Number of rows
            cols: Number of columns
            row_spacing: GAP between rows in mm (not center-to-center)
            col_spacing: GAP between columns in mm (not center-to-center)
        
        Returns:
            array_id: ID of created array
        """
        array_id = ParametricArrayConstraint.get_next_array_id(sketch)
        
        # Calculate bounding box size of base geometry
        bbox_width, bbox_height = ParametricArrayConstraint.get_geometry_bounding_size(sketch, base_geometry_indices)
        
        # Calculate actual center-to-center distances
        # Spacing is the GAP between geometry, so add the geometry size
        actual_col_spacing = bbox_width + col_spacing
        actual_row_spacing = bbox_height + row_spacing
        
        FreeCAD.Console.PrintMessage(f"Base geometry size: {bbox_width:.2f} × {bbox_height:.2f} mm\n")
        FreeCAD.Console.PrintMessage(f"Gap: {col_spacing:.2f} × {row_spacing:.2f} mm\n")
        FreeCAD.Console.PrintMessage(f"Center-to-center: {actual_col_spacing:.2f} × {actual_row_spacing:.2f} mm\n")
        
        # Store array metadata (store both gap and actual spacing)
        data = ParametricArrayConstraint.get_array_data(sketch)
        data[array_id] = {
            'base_indices': base_geometry_indices,
            'rows': rows,
            'cols': cols,
            'row_spacing': row_spacing,  # User-specified gap
            'col_spacing': col_spacing,  # User-specified gap
            'actual_row_spacing': actual_row_spacing,  # Calculated center-to-center
            'actual_col_spacing': actual_col_spacing,  # Calculated center-to-center
            'copy_indices': []  # Will be filled as we create copies
        }
        
        # Create array copies
        copy_indices = []
        for row in range(rows):
            for col in range(cols):
                # Skip the (0,0) position - that's the original
                if row == 0 and col == 0:
                    continue
                
                offset_x = col * actual_col_spacing
                offset_y = row * actual_row_spacing
                
                # Copy each base geometry element
                for base_idx in base_geometry_indices:
                    base_geo = sketch.Geometry[base_idx]
                    
                    # Create NEW geometry with offset (don't modify copied geometry)
                    geo_type = base_geo.TypeId
                    
                    if geo_type == "Part::GeomCircle":
                        new_geo = Part.Circle()
                        new_geo.Radius = base_geo.Radius
                        new_geo.Center = FreeCAD.Vector(
                            base_geo.Center.x + offset_x,
                            base_geo.Center.y + offset_y,
                            base_geo.Center.z
                        )
                    elif geo_type == "Part::GeomArcOfCircle":
                        new_geo = Part.ArcOfCircle()
                        new_geo.Radius = base_geo.Radius
                        new_geo.Center = FreeCAD.Vector(
                            base_geo.Center.x + offset_x,
                            base_geo.Center.y + offset_y,
                            base_geo.Center.z
                        )
                        # For arcs, we need to set the angle range
                        new_geo.FirstParameter = base_geo.FirstParameter
                        new_geo.LastParameter = base_geo.LastParameter
                    elif geo_type == "Part::GeomLineSegment":
                        new_geo = Part.LineSegment()
                        new_geo.StartPoint = FreeCAD.Vector(
                            base_geo.StartPoint.x + offset_x,
                            base_geo.StartPoint.y + offset_y,
                            base_geo.StartPoint.z
                        )
                        new_geo.EndPoint = FreeCAD.Vector(
                            base_geo.EndPoint.x + offset_x,
                            base_geo.EndPoint.y + offset_y,
                            base_geo.EndPoint.z
                        )
                    elif geo_type == "Part::GeomPoint":
                        new_geo = Part.Point()
                        new_geo.X = base_geo.X + offset_x
                        new_geo.Y = base_geo.Y + offset_y
                        new_geo.Z = base_geo.Z
                    else:
                        # Fall back to copy method for unsupported types
                        FreeCAD.Console.PrintWarning(f"Copying {geo_type} using .copy() method - may not work correctly\n")
                        new_geo = base_geo.copy()
                        # Try to offset if it has common properties
                        if hasattr(new_geo, 'Center'):
                            new_geo.Center = FreeCAD.Vector(
                                new_geo.Center.x + offset_x,
                                new_geo.Center.y + offset_y,
                                new_geo.Center.z
                            )
                        elif hasattr(new_geo, 'StartPoint'):
                            new_geo.StartPoint = FreeCAD.Vector(
                                new_geo.StartPoint.x + offset_x,
                                new_geo.StartPoint.y + offset_y,
                                new_geo.StartPoint.z
                            )
                            if hasattr(new_geo, 'EndPoint'):
                                new_geo.EndPoint = FreeCAD.Vector(
                                    new_geo.EndPoint.x + offset_x,
                                    new_geo.EndPoint.y + offset_y,
                                    new_geo.EndPoint.z
                                )
                    
                    # Add to sketch (preserve construction status)
                    is_construction = sketch.getConstruction(base_idx)
                    new_idx = sketch.addGeometry(new_geo, is_construction)
                    copy_indices.append(new_idx)
        
        # Create constraint grid to track geometry indices by position
        # Build a 2D array: grid[row][col] = [list of geometry indices]
        grid = [[[] for _ in range(cols)] for _ in range(rows)]
        
        # Fill grid with base geometry at (0,0)
        for base_idx in base_geometry_indices:
            grid[0][0].append(base_idx)
        
        # Fill grid with copied geometry
        copy_idx = 0
        for row in range(rows):
            for col in range(cols):
                if row == 0 and col == 0:
                    continue  # Skip base position
                for _ in base_geometry_indices:
                    grid[row][col].append(copy_indices[copy_idx])
                    copy_idx += 1
        
        # Copy shape constraints (not size) to maintain geometry relationships
        FreeCAD.Console.PrintMessage("Copying shape constraints (Coincident, H/V, etc.) to array copies...\n")
        internal_constraint_count = ParametricArrayConstraint.copy_internal_constraints(
            sketch, base_geometry_indices, grid, rows, cols
        )
        
        # Add parametric constraints for array spacing
        constraint_indices = []
        FreeCAD.Console.PrintMessage("Adding parametric constraints...\n")
        
        # Add horizontal constraints (between columns in each row)
        # Only use the FIRST geometry element as reference point to avoid redundancy
        # (Internal constraints make all elements move together as a rigid body)
        for row in range(rows):
            for col in range(cols - 1):
                # Use only the first geometry element in each cell as reference
                geo_idx_left = grid[row][col][0]
                geo_idx_right = grid[row][col + 1][0]
                
                # Determine point type for constraint (center for circles, start point for lines)
                geo_left = sketch.Geometry[geo_idx_left]
                point_type = ParametricArrayConstraint.get_constraint_point_type(geo_left)
                
                # DistanceX constraint
                constraint = Sketcher.Constraint('DistanceX', 
                                                geo_idx_left, point_type,
                                                geo_idx_right, point_type,
                                                actual_col_spacing)
                constraint_idx = sketch.addConstraint(constraint)
                constraint_indices.append(constraint_idx)
        
        # Add vertical constraints (between rows in each column)
        # Only use the FIRST geometry element as reference point to avoid redundancy
        for col in range(cols):
            for row in range(rows - 1):
                # Use only the first geometry element in each cell as reference
                geo_idx_top = grid[row][col][0]
                geo_idx_bottom = grid[row + 1][col][0]
                
                geo_top = sketch.Geometry[geo_idx_top]
                point_type = ParametricArrayConstraint.get_constraint_point_type(geo_top)
                
                # DistanceY constraint
                constraint = Sketcher.Constraint('DistanceY',
                                                geo_idx_top, point_type,
                                                geo_idx_bottom, point_type,
                                                actual_row_spacing)
                constraint_idx = sketch.addConstraint(constraint)
                constraint_indices.append(constraint_idx)
        
        FreeCAD.Console.PrintMessage(f"Added {len(constraint_indices)} spacing constraints\n")
        
        # Add position locking constraints for first row and column
        # This anchors the array copies relative to base geometry position
        # Locks array regardless of where base is positioned in sketch
        position_constraint_count = 0
        
        # Get reference point from base geometry
        base_geo_idx = grid[0][0][0]  # First geometry in base cell
        base_geo = sketch.Geometry[base_geo_idx]
        
        # Use appropriate point based on geometry type
        if base_geo.TypeId in ["Part::GeomCircle", "Part::GeomArcOfCircle"]:
            base_point_type = 3  # Center point
        else:
            base_point_type = 1  # Start point for lines
        
        # Lock first row (all columns except base) to same Y position as base
        # DistanceY = 0 means same horizontal line
        for col in range(1, cols):  # Skip col 0 (base)
            copy_geo_idx = grid[0][col][0]  # First geometry in cell
            copy_geo = sketch.Geometry[copy_geo_idx]
            
            # Use appropriate point based on geometry type
            if copy_geo.TypeId in ["Part::GeomCircle", "Part::GeomArcOfCircle"]:
                copy_point_type = 3  # Center point
            else:
                copy_point_type = 1  # Start point for lines
            
            try:
                # DistanceY = 0 means same Y coordinate (horizontal alignment)
                constraint = Sketcher.Constraint('DistanceY', 
                                                base_geo_idx, base_point_type,
                                                copy_geo_idx, copy_point_type,
                                                0.0)
                c_idx = sketch.addConstraint(constraint)
                constraint_indices.append(c_idx)
                position_constraint_count += 1
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Could not add Y position lock: {e}\n")
        
        # Lock first column (all rows except base) to same X position as base
        # DistanceX = 0 means same vertical line
        for row in range(1, rows):  # Skip row 0 (base)
            copy_geo_idx = grid[row][0][0]  # First geometry in cell
            copy_geo = sketch.Geometry[copy_geo_idx]
            
            # Use appropriate point based on geometry type
            if copy_geo.TypeId in ["Part::GeomCircle", "Part::GeomArcOfCircle"]:
                copy_point_type = 3  # Center point
            else:
                copy_point_type = 1  # Start point for lines
            
            try:
                # DistanceX = 0 means same X coordinate (vertical alignment)
                constraint = Sketcher.Constraint('DistanceX',
                                                base_geo_idx, base_point_type,
                                                copy_geo_idx, copy_point_type,
                                                0.0)
                c_idx = sketch.addConstraint(constraint)
                constraint_indices.append(c_idx)
                position_constraint_count += 1
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Could not add X position lock: {e}\n")
        
        if position_constraint_count > 0:
            FreeCAD.Console.PrintMessage(f"Added {position_constraint_count} position lock constraints\n")
        
        # Add size constraints (Equal constraints to base geometry)
        # This makes the array truly parametric - changing base size updates all copies
        # Equal constraints link copy sizes to base, allowing parametric behavior
        # For multi-element shapes (rectangles), only add Equal to ONE element per orientation
        # to avoid redundancy (shape constraints propagate the sizing)
        FreeCAD.Console.PrintMessage("Adding Equal constraints for parametric sizing...\n")
        size_constraint_count = 0
        
        # Track which orientations we've already constrained per copy position
        # For rectangles: need 1 horizontal + 1 vertical
        # For circles: need 1 radius
        
        for row in range(rows):
            for col in range(cols):
                if row == 0 and col == 0:
                    continue  # Skip base position
                
                # Track what we've constrained for this copy position
                has_horizontal_equal = False
                has_vertical_equal = False
                has_circle_equal = False
                
                position_idx = row * cols + col - 1  # -1 because we skipped (0,0)
                copy_offset = position_idx * len(base_geometry_indices)
                
                # For each base geometry element
                for base_position, base_idx in enumerate(base_geometry_indices):
                    base_geo = sketch.Geometry[base_idx]
                    geo_type = base_geo.TypeId
                    copy_idx = copy_indices[copy_offset + base_position]
                    
                    # Determine if we should add Equal constraint
                    should_add_equal = False
                    
                    if geo_type in ["Part::GeomCircle", "Part::GeomArcOfCircle"]:
                        # For circles, always add Equal (need radius match)
                        if not has_circle_equal:
                            should_add_equal = True
                            has_circle_equal = True
                    
                    elif geo_type == "Part::GeomLineSegment":
                        # For lines, check if it's horizontal or vertical
                        # Look through sketch constraints to find orientation
                        is_horizontal = False
                        is_vertical = False
                        
                        for constraint in sketch.Constraints:
                            if constraint.First == base_idx:
                                if constraint.Type == 'Horizontal':
                                    is_horizontal = True
                                    break
                                elif constraint.Type == 'Vertical':
                                    is_vertical = True
                                    break
                        
                        # Add Equal only if we haven't added one for this orientation yet
                        if is_horizontal and not has_horizontal_equal:
                            should_add_equal = True
                            has_horizontal_equal = True
                        elif is_vertical and not has_vertical_equal:
                            should_add_equal = True
                            has_vertical_equal = True
                        elif not is_horizontal and not is_vertical:
                            # Line with no orientation constraint - add Equal
                            should_add_equal = True
                    
                    # Add the constraint if needed
                    if should_add_equal:
                        try:
                            constraint = Sketcher.Constraint('Equal', base_idx, copy_idx)
                            c_idx = sketch.addConstraint(constraint)
                            constraint_indices.append(c_idx)
                            size_constraint_count += 1
                        except Exception as e:
                            FreeCAD.Console.PrintWarning(f"Could not add Equal constraint: {e}\n")
        
        if size_constraint_count > 0:
            FreeCAD.Console.PrintMessage(f"Added {size_constraint_count} Equal constraints (parametric sizing)\n")
        
        # Store array metadata (no marker point - not needed)
        data[array_id]['copy_indices'] = copy_indices
        data[array_id]['constraint_indices'] = constraint_indices
        
        ParametricArrayConstraint.set_array_data(sketch, data)
        
        FreeCAD.Console.PrintMessage(f"Created {array_id}: {rows}x{cols} = {rows*cols} copies\n")
        return array_id
    
    @staticmethod
    def get_geometry_center(sketch, indices):
        """Get center point of geometry elements"""
        points = []
        for idx in indices:
            geo = sketch.Geometry[idx]
            if hasattr(geo, 'Center'):
                points.append(geo.Center)
            elif hasattr(geo, 'StartPoint'):
                points.append(geo.StartPoint)
                if hasattr(geo, 'EndPoint'):
                    points.append(geo.EndPoint)
        
        if not points:
            return FreeCAD.Vector(0, 0, 0)
        
        avg_x = sum(p.x for p in points) / len(points)
        avg_y = sum(p.y for p in points) / len(points)
        return FreeCAD.Vector(avg_x, avg_y, 0)
    
    @staticmethod
    def get_geometry_bounding_size(sketch, indices):
        """Get bounding box dimensions of geometry elements
        
        Returns:
            tuple: (width, height) in mm
        """
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for idx in indices:
            geo = sketch.Geometry[idx]
            
            if hasattr(geo, 'Center') and hasattr(geo, 'Radius'):
                # Circle or arc
                min_x = min(min_x, geo.Center.x - geo.Radius)
                max_x = max(max_x, geo.Center.x + geo.Radius)
                min_y = min(min_y, geo.Center.y - geo.Radius)
                max_y = max(max_y, geo.Center.y + geo.Radius)
            elif hasattr(geo, 'StartPoint') and hasattr(geo, 'EndPoint'):
                # Line
                min_x = min(min_x, geo.StartPoint.x, geo.EndPoint.x)
                max_x = max(max_x, geo.StartPoint.x, geo.EndPoint.x)
                min_y = min(min_y, geo.StartPoint.y, geo.EndPoint.y)
                max_y = max(max_y, geo.StartPoint.y, geo.EndPoint.y)
            elif hasattr(geo, 'X') and hasattr(geo, 'Y'):
                # Point
                min_x = min(min_x, geo.X)
                max_x = max(max_x, geo.X)
                min_y = min(min_y, geo.Y)
                max_y = max(max_y, geo.Y)
        
        width = max_x - min_x if max_x > min_x else 0
        height = max_y - min_y if max_y > min_y else 0
        
        return (width, height)
    
    @staticmethod
    def get_constraint_point_type(geometry):
        """Get the point type for constraints based on geometry type
        
        Returns:
            int: Point type for Sketcher constraints
                 0 = point itself
                 1 = start point
                 2 = end point
                 3 = center point
        """
        geo_type = geometry.TypeId
        if geo_type in ["Part::GeomCircle", "Part::GeomArcOfCircle"]:
            return 3  # Center point
        elif geo_type == "Part::GeomLineSegment":
            return 1  # Start point
        elif geo_type == "Part::GeomPoint":
            return 0  # Point itself
        else:
            return 1  # Default to start point
    
    @staticmethod
    def update_array(sketch, array_id, rows=None, cols=None, row_spacing=None, col_spacing=None):
        """Update an existing array"""
        data = ParametricArrayConstraint.get_array_data(sketch)
        
        if array_id not in data:
            FreeCAD.Console.PrintError(f"Array {array_id} not found\n")
            return False
        
        array_info = data[array_id]
        
        # Update parameters if provided
        if rows is not None:
            array_info['rows'] = rows
        if cols is not None:
            array_info['cols'] = cols
        if row_spacing is not None:
            array_info['row_spacing'] = row_spacing
        if col_spacing is not None:
            array_info['col_spacing'] = col_spacing
        
        # Delete old copies and constraints
        old_copies = array_info.get('copy_indices', [])
        old_constraints = array_info.get('constraint_indices', [])
        old_marker = array_info.get('marker_index')
        
        # Delete constraints first
        for idx in reversed(sorted(old_constraints)):
            try:
                sketch.delConstraint(idx)
            except:
                pass
        
        # Delete geometry (copies)
        for idx in reversed(sorted(old_copies)):  # Delete from end to avoid index shifting
            try:
                sketch.delGeometry(idx)
            except:
                pass
        
        # Delete marker
        if old_marker is not None:
            try:
                sketch.delGeometry(old_marker)
            except:
                pass
        
        # Recreate array (this will create new copy_indices)
        base_indices = array_info['base_indices']
        rows = array_info['rows']
        cols = array_info['cols']
        row_spacing = array_info['row_spacing']
        col_spacing = array_info['col_spacing']
        
        # Remove old array data
        del data[array_id]
        ParametricArrayConstraint.set_array_data(sketch, data)
        
        # Recreate
        ParametricArrayConstraint.create_array(sketch, base_indices, rows, cols, row_spacing, col_spacing)
        
        return True
    
    @staticmethod
    def delete_array(sketch, array_id):
        """Delete an array and leave geometry as independent"""
        data = ParametricArrayConstraint.get_array_data(sketch)
        
        if array_id not in data:
            FreeCAD.Console.PrintError(f"Array {array_id} not found\n")
            return False
        
        array_info = data[array_id]
        
        # Delete constraints to break array relationship
        constraint_indices = array_info.get('constraint_indices', [])
        for idx in reversed(sorted(constraint_indices)):
            try:
                sketch.delConstraint(idx)
            except:
                pass
        
        # Delete marker
        marker_idx = array_info.get('marker_index')
        if marker_idx is not None:
            try:
                sketch.delGeometry(marker_idx)
            except:
                pass
        
        # Remove array from metadata (copies remain as independent geometry)
        del data[array_id]
        ParametricArrayConstraint.set_array_data(sketch, data)
        
        FreeCAD.Console.PrintMessage(f"Deleted {array_id} - geometry is now independent\n")
        return True
    
    @staticmethod
    def find_array_by_geometry(sketch, geo_index):
        """Find which array (if any) a geometry element belongs to
        
        Returns:
            tuple: (array_id, role) where role is 'base', 'copy', or 'marker'
                   Returns (None, None) if not part of any array
        """
        data = ParametricArrayConstraint.get_array_data(sketch)
        
        for array_id, array_info in data.items():
            # Check if it's a base element
            if geo_index in array_info.get('base_indices', []):
                return (array_id, 'base')
            
            # Check if it's a copy
            if geo_index in array_info.get('copy_indices', []):
                return (array_id, 'copy')
            
            # Check if it's the marker
            if geo_index == array_info.get('marker_index'):
                return (array_id, 'marker')
        
        return (None, None)
    
    @staticmethod
    def get_array_info(sketch, array_id):
        """Get array information by ID
        
        Returns:
            dict: Array info or None if not found
        """
        data = ParametricArrayConstraint.get_array_data(sketch)
        return data.get(array_id)
