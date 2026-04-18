# Adding Parametric Array to Custom Toolbar

The Parametric Array command is registered as `Sketcher_ParametricArray` and is available for use, but doesn't automatically appear in the Tools → Customize dialog.

## Quick Setup: Use the Provided Macro

A macro file `ParametricArray.FCMacro` is included in the repository root.

### Step 1: Copy Files to FreeCAD

Copy both the macro and icon to your FreeCAD Macro folder:

**Windows:**
```powershell
copy ParametricArray.FCMacro "$env:APPDATA\FreeCAD\Macro\"
copy Resources\icons\ProductionArray.svg "$env:APPDATA\FreeCAD\Macro\"
```

**Manual Copy (Windows):**
- Copy `ParametricArray.FCMacro` to: `C:\Users\<YourName>\AppData\Roaming\FreeCAD\Macro\`
- Copy `Resources\icons\ProductionArray.svg` to: `C:\Users\<YourName>\AppData\Roaming\FreeCAD\Macro\`

**Linux/macOS:**
- Macro folder: `~/.FreeCAD/Macro/`

### Step 2: Set the Macro Icon

1. **Restart FreeCAD** (to reload macros)
2. Go to **Tools → Customize...**
3. Click the **Macros** tab
4. Find `ParametricArray` in the macro list
5. Click the **Icon** button (below the macro list)
6. Navigate to `%APPDATA%\FreeCAD\Macro\` (or your FreeCAD Macro folder)
7. Select **ProductionArray.svg**
8. Click **Open**

The icon is now set for the macro!

### Step 3: Add Macro to Custom Toolbar

1. Still in **Tools → Customize...**, switch to the **Toolbars** tab
2. Click **New...** to create a new toolbar (name it "Sketch Tools" or similar)
3. Switch back to the **Macros** tab
4. Select your `ParametricArray` macro
5. Click the **→** arrow to add it to your toolbar
6. Click **Close**

### Step 4: Position Your Toolbar

Your new custom toolbar will appear. You can:
- Drag it to dock it anywhere in the FreeCAD window
- Right-click it to customize further
- Save your layout via **View → Toolbars → Lock Toolbars** (unchecked while arranging)

---

## Alternative: Run from Python Console

When in Sketcher edit mode, you can also run directly from the Python console:

```python
FreeCADGui.runCommand('Sketcher_ParametricArray')
```

## Keyboard Shortcut (Optional)

1. Go to **Tools → Customize...**
2. Click the **Keyboard** tab
3. Search for macros
4. Find your `ParametricArray` macro
5. Click in the "Press new shortcut" box
6. Press your desired key combination (e.g., `Ctrl+Shift+A`)
7. Click **Assign**
8. Click **Close**

Now you can trigger the Parametric Array with your keyboard shortcut!
