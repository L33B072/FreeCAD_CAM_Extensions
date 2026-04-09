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
- Works with any CAM operation that has Base geometry
- **Note:** Due to FreeCAD's internal path optimization, this may not always affect the final toolpath order

### 3. Split Profile Tool ⭐ **Recommended for Order Control**
- **Guaranteed cutting order control** - Split a Profile into separate operations
- **One operation per base geometry** - Each geometry becomes its own Profile operation
- **Complete control** - Operations run in sequence, no optimization or reordering
- **Inherits all settings** - Each new operation copies settings from the original
- **Auto-naming** - Operations named Profile_001, Profile_002, etc.
- **Like Fusion 360's workflow** - Similar to creating individual contour operations
- **Most reliable solution** - When you need exact control over cutting sequence

### 4. Advanced Toolpath Linking Controls (Planned)
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
6. The operation will be recomputed

**Note:** Due to FreeCAD's internal path optimization, the toolpath order may still be optimized. For guaranteed order control, use the **Split Profile Tool** instead.

### Split Profile Tool ⭐ **For Guaranteed Order Control**
1. Create a Profile operation with multiple base geometries
2. **Arrange the base geometries in your desired order** using the Reorder Tool first (if needed)
3. Select the Profile operation in the tree
4. Go to **CAM → Extensions → Split Profile into Separate Operations**
5. Review the list of base geometries that will be split
6. Choose options:
   - **Delete original Profile** (recommended - checked by default)
   - **Auto-rename operations** (creates Profile_001, Profile_002, etc.)
   - **Save and reopen document** (optional - ensures operations are immediately editable)
7. Click **Split Profile**
8. Done! Each base geometry is now a separate Profile operation in sequence

**Note:** Due to FreeCAD's internal operation initialization, newly split operations may not be fully editable (can't open task panel) until the document is saved and reopened. Check the "Save and reopen document" option to do this automatically, or manually save and reopen after splitting.

**Why use split?** Each operation runs independently in order with NO automatic reordering or optimization. You get complete control, just like creating individual contour operations in Fusion 360.

**Pro tip:** The operations are inserted in the Job at the same position as the original Profile, maintaining your workflow order.

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
