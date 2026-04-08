# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2026 L33B072                                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the MIT License                                 *
# ***************************************************************************

"""CAM Extensions - Command definitions"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui


class ShowOperationVariablesCommand:
    """Command to show the Operation Variables viewer"""
    
    def GetResources(self):
        return {
            'Pixmap': 'Path_Array',  # Using existing icon as placeholder
            'MenuText': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Show Operation Variables"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("CAM_ShowOperationVariables", "Display CAM operation variables and their values")
        }
    
    def Activated(self):
        """Execute when the command is activated"""
        import OperationVariablesPanel
        
        # Get the active document
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document\n")
            return
        
        # Try to find a CAM Job in the document
        job = None
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, '__class__'):
                if 'Job' in obj.Proxy.__class__.__name__:
                    job = obj
                    break
        
        if not job:
            FreeCAD.Console.PrintWarning("No CAM Job found in document. Variables shown will be generic.\n")
        
        # Show the variables panel
        panel = OperationVariablesPanel.OperationVariablesPanel(job)
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Return True if command should be active"""
        return FreeCAD.ActiveDocument is not None


# Register the command
FreeCADGui.addCommand('CAM_ShowOperationVariables', ShowOperationVariablesCommand())
