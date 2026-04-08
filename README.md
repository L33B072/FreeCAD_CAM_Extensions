# FreeCAD CAM Extensions

Enhanced features for FreeCAD's CAM (Path) workbench.

## Features

### 1. Operation Variables Viewer
- Displays all CAM Operation Variables (OpFinalDepth, OpStartDepth, OpToolDiameter, etc.)
- Shows SetupSheet properties and values
- Integrated into the CAM workbench - accessible from any CAM operation
- Real-time display of current variable values
- Searchable/filterable table
- Right-click to copy variable names for use in expressions
- Makes it easy to see and understand available variables for expressions

### 2. Base Geometry Reorder Tool
- **Control toolpath sequence** - Reorder base geometries in Profile, Pocket, and other operations
- **Drag-and-drop interface** - Simply drag items to reorder them
- **Quick buttons** - Move items up/down or to top/bottom with one click
- **Visual feedback** - See exactly which geometry will be processed in which order
- **Like Fusion 360's "Keep order as selected"** - FreeCAD now has similar functionality!
- Works with any CAM operation that has Base geometry

### 3. Advanced Toolpath Linking Controls (Planned)
- Enhanced control over toolpath linking behavior
- Coming soon

## Installation

### Method 1: Via Addon Manager (Recommended)
1. Open FreeCAD
2. Go to **Tools → Addon Manager**
3. Search for "CAM Extensions"
4. Click Install

### Method 2: Manual Installation
1. Download or clone this repository
2. Copy the entire folder to your FreeCAD Mod directory:
   - **Windows (FreeCAD 1.0+)**: `C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\v1-1\Mod\` (note: version number in path)
   - **Linux**: `~/.FreeCAD/Mod/`
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
3. Restart FreeCAD

## Usage

### Operation Variables Viewer
1. Open a FreeCAD document with a CAM Job
2. Switch to the CAM workbench
3. Go to **CAM → Extensions → Show Operation Variables**
4. View all available operation variables, SetupSheet properties, and their current values
5. Use the search box to filter variables
6. Right-click to copy variable names for use in expressions

### Base Geometry Reorder Tool
1. Create a CAM operation (Profile, Pocket, etc.) with multiple base geometries
2. Select the operation in the tree (or just have it in your document)
3. Go to **CAM → Extensions → Reorder Base Geometry**
4. **Reorder the geometries:**
   - **Drag and drop** items to reorder them
   - Or use the **Move Up/Down/Top/Bottom** buttons
5. Click **Apply New Order** to update the operation
6. The toolpath will be recomputed in the new order!

**Pro tip:** The order in the list (top to bottom) is the order the tool will visit each geometry.

## Requirements

- FreeCAD 1.0 or later
- CAM (Path) workbench enabled

## Development

This addon is under active development. Contributions and feedback are welcome!

## License

MIT License - See LICENSE file for details

## Author

**L33B072**
- GitHub: https://github.com/L33B072

## Links

- Repository: https://github.com/L33B072/FreeCAD_CAM_Extensions
- Issues: https://github.com/L33B072/FreeCAD_CAM_Extensions/issues
- FreeCAD: https://www.freecad.org/
