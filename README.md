# FreeCAD CAM Extensions

Enhanced features for FreeCAD's CAM (Path) workbench.

## Features

### 1. Operation Variables Viewer (In Development)
- Displays all CAM Operation Variables (OpFinalDepth, OpStartDepth, OpToolDiameter, etc.) in a dedicated tab
- Integrated into the Job Edit Task window
- Real-time display of current variable values
- Makes it easy to see and understand available variables for expressions

### 2. Advanced Toolpath Linking Controls (Planned)
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
   - **Windows**: `C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\Mod\`
   - **Linux**: `~/.FreeCAD/Mod/`
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
3. Restart FreeCAD

## Usage

### Operation Variables Viewer
1. Open a FreeCAD document with a CAM Job
2. Edit a CAM Job (double-click on Job in the tree)
3. Look for the "Variables" tab in the Job Edit task panel
4. View all available operation variables and their current values

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
