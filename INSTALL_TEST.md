# Installation and Testing Guide

## Quick Installation for Development

### Step 1: Copy to FreeCAD Mod Directory

Copy the entire `FreeCAD_CAM_Extensions` folder to your FreeCAD Mod directory:

**Windows (FreeCAD 1.0+):**
```
C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\v1-1\Mod\FreeCAD_CAM_Extensions
```
Note: The directory name changes with FreeCAD version (v0-21, v1-0, v1-1, etc.)

**Windows (FreeCAD 0.21 and earlier):**
```
C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\Mod\FreeCAD_CAM_Extensions
```

**Linux:**
```
~/.FreeCAD/Mod/FreeCAD_CAM_Extensions
```

**macOS:**
```
~/Library/Application Support/FreeCAD/Mod/FreeCAD_CAM_Extensions
```

### Step 2: Restart FreeCAD

Close and reopen FreeCAD for the addon to load.

### Step 3: Test the Installation

1. Open FreeCAD
2. Open the Python console (View → Panels → Python console)
3. Type the following to verify the addon loaded:
   ```python
   import FreeCADGui
   FreeCADGui.listWorkbenches()
   ```
   You should see "CAMExtensionsWorkbench" in the list.

### Step 4: Test the Operation Variables Viewer

#### Option A: Using the CAM Extensions Menu
1. Open or create a FreeCAD document
2. Switch to CAM workbench (if you have a CAM job)
3. Go to menu: **CAM Extensions → Show Operation Variables**
4. A panel should appear showing available variables

#### Option B: Using Python Console
```python
# In FreeCAD Python console
from FreeCAD_CAM_Extensions import CAMExtensions_Commands
FreeCADGui.runCommand('CAM_ShowOperationVariables')
```

## Verifying the Installation

### Check 1: Module Import
```python
import sys
import os

# Check if addon is in path
mod_path = os.path.join(FreeCAD.getUserAppDataDir(), 'Mod', 'FreeCAD_CAM_Extensions')
print(f"Looking for addon at: {mod_path}")
print(f"Exists: {os.path.exists(mod_path)}")

# Try importing the modules
try:
    from FreeCAD_CAM_Extensions import OperationVariablesPanel
    print("✓ OperationVariablesPanel imported successfully")
except Exception as e:
    print(f"✗ Failed to import OperationVariablesPanel: {e}")

try:
    from FreeCAD_CAM_Extensions import CAMExtensions_Commands
    print("✓ CAMExtensions_Commands imported successfully")
except Exception as e:
    print(f"✗ Failed to import CAMExtensions_Commands: {e}")
```

### Check 2: Command Registration
```python
# Verify command is registered
import FreeCADGui
if 'CAM_ShowOperationVariables' in FreeCADGui.listCommands():
    print("✓ Command CAM_ShowOperationVariables is registered")
else:
    print("✗ Command not found")
```

## Common Issues

### Issue: "No module named FreeCAD_CAM_Extensions"
**Solution:** Make sure the folder is named exactly `FreeCAD_CAM_Extensions` and is in the Mod directory.

### Issue: "Workbench not showing up"
**Solution:** 
1. Check the Python console for error messages
2. Verify all .py files are in the correct location
3. Restart FreeCAD completely

### Issue: Variables show as "N/A"
**Solution:** This is normal if no CAM job is open. Create a CAM job to see actual values.

## Creating a Test CAM Job

To test with actual values:

1. Create a new document
2. Insert a cube: Part → Cube
3. Switch to Path/CAM workbench
4. Create a new job: Path → Job
5. Select the cube as the base object
6. Add an operation (e.g., Path → Profile)
7. Now run: **CAM Extensions → Show Operation Variables**
8. You should see actual values for the variables

## Development Tips

### Editing the Code
When developing:
1. Make changes to the files in the Mod directory
2. Restart FreeCAD to reload the addon
3. Or use this to reload without restarting:
   ```python
   import importlib
   from FreeCAD_CAM_Extensions import OperationVariablesPanel, CAMExtensions_Commands
   importlib.reload(OperationVariablesPanel)
   importlib.reload(CAMExtensions_Commands)
   ```

### Debugging
Enable debug output in the Python console:
```python
import FreeCAD
FreeCAD.Console.PrintLog("Debug info here\n")
```

## Next Steps

Once the Operation Variables viewer is working, we can:
1. Integrate it as a tab in the Job Edit task panel (more advanced)
2. Add the toolpath linking controls feature
3. Package for distribution via FreeCAD Addon Manager
