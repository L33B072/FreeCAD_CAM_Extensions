# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""Operation Variables Panel - Display CAM operation variables"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class OperationVariablesPanel:
    """Task panel for displaying CAM operation variables"""
    
    def __init__(self, job=None):
        """Initialize the panel
        
        Args:
            job: The CAM Job object to inspect for variables
        """
        self.job = job
        self.form = self.createUI()
        self.populateVariables()
    
    def createUI(self):
        """Create the user interface"""
        # Main widget
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        
        # Title label
        title = QtGui.QLabel("<b>CAM Operation Variables</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        if self.job:
            info = QtGui.QLabel(f"Job: {self.job.Label}")
        else:
            info = QtGui.QLabel("No active CAM Job - showing available variable names")
        layout.addWidget(info)
        
        # Search box
        search_layout = QtGui.QHBoxLayout()
        search_label = QtGui.QLabel("Filter:")
        self.search_box = QtGui.QLineEdit()
        self.search_box.setPlaceholderText("Type to filter variables...")
        self.search_box.textChanged.connect(self.filterVariables)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Table for variables
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Variable", "Value", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        # Enable copying from table
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showContextMenu)
        
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_button = QtGui.QPushButton("Refresh Values")
        refresh_button.clicked.connect(self.populateVariables)
        layout.addWidget(refresh_button)
        
        # Help text
        help_text = QtGui.QLabel(
            "<i>Tip: Right-click a variable to copy its name for use in expressions</i>"
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        return widget
    
    def getOperationVariables(self):
        """Get dictionary of CAM operation variables
        
        Returns:
            dict: Dictionary mapping variable names to (value, description) tuples
        """
        variables = {}
        
        # Define the standard CAM operation variables
        # These are the variables available in expressions within CAM operations
        standard_vars = {
            'OpFinalDepth': ('Final depth of the operation', None),
            'OpStartDepth': ('Starting depth of the operation', None),
            'OpStockZMin': ('Minimum Z of the stock', None),
            'OpStockZMax': ('Maximum Z of the stock', None),
            'OpToolDiameter': ('Diameter of the current tool', None),
            'OpToolRadius': ('Radius of the current tool', None),
            'OpToolFluteLength': ('Flute length of the current tool', None),
            'OpToolShankDiameter': ('Shank diameter of the current tool', None),
            'OpStepDown': ('Step down increment', None),
            'OpStepOver': ('Step over percentage', None),
            'OpVertFeed': ('Vertical feed rate (plunge)', None),
            'OpHorizFeed': ('Horizontal feed rate', None),
            'OpVertRapid': ('Vertical rapid rate', None),
            'OpHorizRapid': ('Horizontal rapid rate', None),
            'OpClearanceHeight': ('Clearance height', None),
            'OpSafeHeight': ('Safe height', None),
            'OpStartX': ('Start X position', None),
            'OpStartY': ('Start Y position', None),
            'OpEndX': ('End X position', None),
            'OpEndY': ('End Y position', None),
        }
        
        # If we have a job, try to get actual values
        if self.job:
            # Try to get stock dimensions
            if hasattr(self.job, 'Stock'):
                stock = self.job.Stock
                if hasattr(stock, 'Shape') and stock.Shape:
                    bbox = stock.Shape.BoundBox
                    standard_vars['OpStockZMin'] = (f'Stock Z min', f"{bbox.ZMin:.3f} mm")
                    standard_vars['OpStockZMax'] = (f'Stock Z max', f"{bbox.ZMax:.3f} mm")
            
            # Try to get tool information from operations
            for op in self.job.Group:
                if hasattr(op, 'ToolController'):
                    tc = op.ToolController
                    if tc and hasattr(tc, 'Tool'):
                        tool = tc.Tool
                        if hasattr(tool, 'Diameter'):
                            standard_vars['OpToolDiameter'] = ('Tool diameter', f"{tool.Diameter:.3f} mm")
                            standard_vars['OpToolRadius'] = ('Tool radius', f"{tool.Diameter/2:.3f} mm")
                        if hasattr(tool, 'FluteLength'):
                            standard_vars['OpToolFluteLength'] = ('Tool flute length', f"{tool.FluteLength:.3f} mm")
                        if hasattr(tool, 'ShankDiameter'):
                            standard_vars['OpToolShankDiameter'] = ('Tool shank diameter', f"{tool.ShankDiameter:.3f} mm")
                        # Only need to check first operation with a tool
                        break
                
                # Try to get operation-specific values
                if hasattr(op, 'FinalDepth'):
                    standard_vars['OpFinalDepth'] = ('Final depth', f"{op.FinalDepth.Value:.3f} mm")
                if hasattr(op, 'StartDepth'):
                    standard_vars['OpStartDepth'] = ('Start depth', f"{op.StartDepth.Value:.3f} mm")
                if hasattr(op, 'StepDown'):
                    standard_vars['OpStepDown'] = ('Step down', f"{op.StepDown.Value:.3f} mm")
                if hasattr(op, 'ClearanceHeight'):
                    standard_vars['OpClearanceHeight'] = ('Clearance height', f"{op.ClearanceHeight.Value:.3f} mm")
                if hasattr(op, 'SafeHeight'):
                    standard_vars['OpSafeHeight'] = ('Safe height', f"{op.SafeHeight.Value:.3f} mm")
        
        # Build the variables dictionary
        for var_name, (description, value) in standard_vars.items():
            if value is None:
                value = "N/A (no active operation)"
            variables[var_name] = (value, description)
        
        # Add SetupSheet variables
        setupsheet_vars = self.getSetupSheetVariables()
        variables.update(setupsheet_vars)
        
        return variables
    
    def getSetupSheetVariables(self):
        """Get variables from the SetupSheet
        
        Returns:
            dict: Dictionary mapping variable names to (value, description) tuples
        """
        variables = {}
        
        if not self.job:
            return variables
        
        # Try to find SetupSheet in the job
        setupsheet = None
        if hasattr(self.job, 'SetupSheet'):
            setupsheet = self.job.SetupSheet
        
        if not setupsheet:
            # Try to find it in the job's group
            for obj in self.job.Group:
                if hasattr(obj, 'TypeId') and 'Spreadsheet' in obj.TypeId:
                    setupsheet = obj
                    break
        
        if not setupsheet:
            return variables
        
        # Read all cells from the SetupSheet
        # SetupSheet typically has aliases in column A and values in column B
        try:
            # Get all cells with aliases
            if hasattr(setupsheet, 'cells'):
                cells = setupsheet.cells
                for cell in cells:
                    # Check if cell has an alias
                    alias = setupsheet.getAlias(cell)
                    if alias:
                        # Get the value
                        content = setupsheet.getContents(cell)
                        display_value = setupsheet.get(cell)
                        
                        # Format the description
                        description = f"SetupSheet: {cell}"
                        
                        # Format the value
                        if display_value:
                            value = str(display_value)
                        else:
                            value = str(content) if content else "N/A"
                        
                        # Add to variables dictionary
                        variables[alias] = (value, description)
            
            # Alternative method: iterate through known cells
            elif hasattr(setupsheet, 'getCellFromAlias'):
                # Try common SetupSheet variables
                common_aliases = [
                    'ClearanceHeightOffset', 'SafeHeightOffset',
                    'StartDepth', 'FinalDepth', 'StepDown',
                    'HorizRapid', 'VertRapid', 'HorizFeed', 'VertFeed',
                    'ToolDiameter', 'ToolNumber'
                ]
                
                for alias in common_aliases:
                    try:
                        cell = setupsheet.getCellFromAlias(alias)
                        if cell:
                            content = setupsheet.get(cell)
                            if content is not None:
                                description = f"SetupSheet: {cell}"
                                variables[alias] = (str(content), description)
                    except:
                        continue
                        
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Error reading SetupSheet: {e}\n")
        
        return variables
    
    def populateVariables(self):
        """Populate the table with variables"""
        variables = self.getOperationVariables()
        
        # Clear existing rows
        self.table.setRowCount(0)
        
        # Add rows for each variable
        for var_name in sorted(variables.keys()):
            value, description = variables[var_name]
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Variable name
            name_item = QtGui.QTableWidgetItem(var_name)
            name_item.setFont(QtGui.QFont("Courier"))
            self.table.setItem(row, 0, name_item)
            
            # Value
            value_item = QtGui.QTableWidgetItem(str(value))
            self.table.setItem(row, 1, value_item)
            
            # Description
            desc_item = QtGui.QTableWidgetItem(description)
            self.table.setItem(row, 2, desc_item)
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
        
        # Store all variables for filtering
        self.all_variables = variables
    
    def filterVariables(self, text):
        """Filter the variables table based on search text"""
        text = text.lower()
        
        for row in range(self.table.rowCount()):
            var_name = self.table.item(row, 0).text().lower()
            description = self.table.item(row, 2).text().lower()
            
            # Show row if text matches variable name or description
            should_show = text in var_name or text in description
            self.table.setRowHidden(row, not should_show)
    
    def showContextMenu(self, position):
        """Show context menu for table"""
        menu = QtGui.QMenu()
        
        copy_name_action = menu.addAction("Copy Variable Name")
        copy_value_action = menu.addAction("Copy Value")
        menu.addSeparator()
        copy_row_action = menu.addAction("Copy Row")
        
        action = menu.exec_(self.table.mapToGlobal(position))
        
        current_row = self.table.currentRow()
        if current_row >= 0:
            if action == copy_name_action:
                var_name = self.table.item(current_row, 0).text()
                QtGui.QApplication.clipboard().setText(var_name)
                FreeCAD.Console.PrintMessage(f"Copied: {var_name}\n")
            elif action == copy_value_action:
                value = self.table.item(current_row, 1).text()
                QtGui.QApplication.clipboard().setText(value)
                FreeCAD.Console.PrintMessage(f"Copied value: {value}\n")
            elif action == copy_row_action:
                var_name = self.table.item(current_row, 0).text()
                value = self.table.item(current_row, 1).text()
                description = self.table.item(current_row, 2).text()
                row_text = f"{var_name}\t{value}\t{description}"
                QtGui.QApplication.clipboard().setText(row_text)
                FreeCAD.Console.PrintMessage(f"Copied row\n")
    
    def accept(self):
        """Called when OK button is clicked"""
        FreeCADGui.Control.closeDialog()
        return True
    
    def reject(self):
        """Called when Cancel button is clicked"""
        FreeCADGui.Control.closeDialog()
        return True
    
    def getStandardButtons(self):
        """Define which buttons to show"""
        return QtGui.QDialogButtonBox.Close
