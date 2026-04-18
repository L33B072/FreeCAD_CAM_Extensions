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

### 2. Split Profile Tool ⭐ **Recommended for Order Control**
- **Guaranteed cutting order control** - Split a Profile into separate operations
- **One operation per base geometry** - Each geometry becomes its own Profile operation
- **Complete control** - Operations run in sequence, no optimization or reordering
- **Inherits all settings** - Each new operation copies settings from the original
- **Auto-naming** - Operations named Profile_001, Profile_002, etc.
- **Like Fusion 360's workflow** - Similar to creating individual contour operations
- **Most reliable solution** - When you need exact control over cutting sequence
- **Reorder in tree** - After splitting, simply drag operations in the tree to change cutting order

### 3. Arc Feed Rate Control
- **Independent arc speed control** - Set different feed rates for arc moves (G2/G3) vs linear moves (G1)
- **ArcFeedRatePercent property** - Added to all Profile operations automatically
- **Per-operation control** - Each Profile can have its own arc feed rate percentage
- **Default: 100%** - No change to feed rate unless you modify it
- **Better finish on curves** - Slow down on tight radius cuts for improved quality
- **Material-specific** - Foam, wood, plastics may benefit from slower arc speeds
- **Works with Split Profile** - Each split operation can have different arc speeds
- **Visible in G-code** - Feed rates are explicitly output for verification

**How it works:**
- Set ArcFeedRatePercent to 60 for 60% speed on arcs
- Linear moves (G1) run at normal feed rate
- Arc moves (G2/G3) run at reduced feed rate
- Combines with Mach4 CV mode for smooth cornering

### 4. Production Array ⭐ **NEW - Design for Manufacturing**
- **Create multiple parts as separate Bodies** - Design once, array many times
- **Parametric workflow** - Edit master sketch, all copies update (coming soon: auto-refresh)
- **Separate Bodies for CAM** - Each array instance is its own Body, ready for individual toolpaths
- **Flexible grid layouts** - Linear (1D) or rectangular (2D) arrays
- **Smart spacing** - Enter gap between parts, tool automatically adds part size
- **Integrated extrusion** - Array AND pad in one step
- **Auto-naming** - Bodies named Part_001, Part_002, etc.
- **Like Fusion 360's Rectangular Pattern** - But creates actual separate Bodies

**Perfect for:**
- Multiple identical parts on one sheet (cabinet parts, drawer fronts, etc.)
- Production runs requiring material optimization
- Batch manufacturing workflows
- Any time you need to cut multiples of the same part

**How it works:**
1. Create a sketch with your part profile (e.g., 2" × 20" rectangle)
2. Select the sketch → Production Array command
3. Set count (e.g., 6 parts in X direction, 1 in Y = linear array)
4. Set gap (e.g., 1.0 inch) - part size is added automatically
5. ☑ Check "Add part size to spacing" (checked by default)
6. Set extrusion depth (e.g., 0.5 inches)
7. Click Create Array
8. Result: 6 separate Bodies with 1" gap between them!

**Example:** 2" × 20" parts with 1" gap:
- Gap X: 1.0 in → Effective spacing: 3.0 in (2" part + 1" gap)
- 6 parts fit on 17" width: 0", 3", 6", 9", 12", 15"

**Advanced:** Uncheck "Add part size to spacing" to manually control center-to-center distances.

**Coming soon:** Auto-refresh to update all array Bodies when master sketch changes

### 6. Sketcher Parametric Array ⭐ **NEW - True Parametric Sketch Arrays**
- **Fully parametric rectangular arrays** - Create arrays directly in sketches with automatic size propagation
- **Smart spacing** - Geometry-aware spacing: edge-to-edge for polygons, center-to-center for circles
- **Automatic updates** - Change base geometry size, all copies update automatically via constraints
- **Live preview** - See total array dimensions before creating
- **Toolbar access** - Add to custom toolbar for quick access (see installation below)
- **Professional workflow** - Perfect for hole patterns, bolt circles, repeated features

**How it works:**
1. Enter sketch edit mode (double-click a sketch)
2. Create your base geometry (rectangle, circle, polygon, etc.)
3. Run Parametric Array command (via toolbar macro)
4. Set rows, columns, and gap spacing
5. Array is created with smart constraints
6. **Change base geometry** → All copies update automatically! 🎯

**Smart spacing behavior:**
- **Circles/Arcs:** Gap = center-to-center distance
- **Polygons/Lines:** Gap = edge-to-edge distance (facing edges)
- **Mixed geometry:** Handled intelligently based on geometry type

**Perfect for:**
- Bolt hole patterns
- Ventilation grilles
- Repeated cutouts or features
- Any sketch pattern that needs to stay synchronized with base geometry

### 7. Advanced Toolpath Linking Controls (Planned)
- Enhanced control over toolpath linking behavior
- Coming soon

## Project Vision

**FreeCAD for Production Manufacturing**

This extension suite bridges the gap between FreeCAD's excellent design capabilities and real-world production CNC workflows. While FreeCAD CAM is powerful for one-off parts and hobby machines, production manufacturing requires:
- **Multi-part sheet optimization** - Multiple parts per sheet for material efficiency
- **Parametric arrays** - Design once, manufacture many, update globally
- **Batch processing** - Efficient workflows for repeated production runs
- **Complete toolpath control** - Predictable, reliable cutting sequences

### Project Structure

The extensions are organized into focused modules:

```
FreeCAD_CAM_Extensions/
├── cam/                    # CAM-specific tools
│   ├── ArcFeedRatePatch.py
│   ├── SplitProfilePanel.py
│   ├── OperationVariablesPanel.py
│   └── BaseGeometryReorderPanel.py
├── design/                 # Design-for-production tools (coming soon)
│   └── Parametric arrays, nesting, sheet layout
├── common/                 # Shared utilities
│   └── Common UI components and helpers
└── CAMExtensions_Commands.py
```

**Current Focus:** CAM toolpath control and optimization  
**Next Phase:** Parametric arrays and sheet nesting for production workflows

## Installation

### Method 1: Via Addon Manager (Recommended)
1. Open FreeCAD
2. Go to **Tools → Addon Manager**
3. Search for "CAM Extensions"
4. Click Install

### Method 2: Manual Installation

#### Step 1: Install the Extension
1. Download or clone this repository
2. **Option A - Automated (Windows):**
   - Open PowerShell in the repository folder
   - Run: `.\deploy_to_freecad.ps1`
   - This automatically copies all files to the correct location
3. **Option B - Manual:**
   - Copy the entire folder to your FreeCAD Mod directory:
     - **Windows (FreeCAD 1.0+)**: `C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\v1-1\Mod\FreeCAD_CAM_Extensions`
     - **Linux**: `~/.FreeCAD/Mod/FreeCAD_CAM_Extensions`
     - **macOS**: `~/Library/Application Support/FreeCAD/Mod/FreeCAD_CAM_Extensions`
4. Restart FreeCAD

#### Step 2: Install Sketcher Array Macro (Optional - for Toolbar Access)

To add the Sketcher Parametric Array to your toolbar:

1. **Copy the macro file:**
   - **Windows:** Copy `ParametricArray.FCMacro` to: `C:\Users\[YourUsername]\AppData\Roaming\FreeCAD\v1-1\Macro\`
   - **Linux:** Copy to `~/.FreeCAD/Macro/`
   - **macOS:** Copy to `~/Library/Preferences/FreeCAD/Macro/`

2. **Copy the icon file:**
   - Copy `Resources/icons/ProductionArray.svg` to the same Macro folder

3. **Restart FreeCAD**

4. **Set the macro icon:**
   - Go to **Tools → Customize...**
   - Click the **Macros** tab
   - Find `ParametricArray` in the list
   - Click the **Icon** button
   - Navigate to your FreeCAD Macro folder
   - Select **ProductionArray.svg**
   - Click **Open**

5. **Add to toolbar:**
   - Still in **Tools → Customize...**, switch to the **Toolbars** tab
   - Click **New...** to create a custom toolbar (name it "Sketch Tools" or similar)
   - Switch back to the **Macros** tab
   - Select `ParametricArray`
   - Click the **→** button to add it to your toolbar
   - Click **Close**

**Detailed instructions:** See `ADD_TO_TOOLBAR.md` in the repository for complete step-by-step guide with screenshots.

**Alternative access:** You can also run the command from the Python console while in sketch edit mode:
```python
FreeCADGui.runCommand('Sketcher_ParametricArray')
```

## Usage

### Operation Variables Viewer
1. Open a FreeCAD document with a CAM Job
2. Switch to the CAM workbench
3. Go to **CAM → Extensions → Show Operation Variables**
4. View all available operation variables, SetupSheet properties, and their current values
5. Use the search box to filter variables
6. Right-click to copy variable names for use in expressions

### Split Profile Tool ⭐ **For Guaranteed Order Control**
1. Create a Profile operation with multiple base geometries
2. Select the Profile operation in the tree
3. Go to **CAM → Extensions → Split Profile into Separate Operations**
4. Review the list of base geometries that will be split
5. Choose options:
   - **Delete original Profile** (recommended - checked by default)
   - **Auto-rename operations** (creates Profile_001, Profile_002, etc.)
   - **Save and reopen document** (optional - ensures operations are immediately editable)
6. Click **Split Profile**
7. Done! Each base geometry is now a separate Profile operation in sequence
8. **To reorder:** Simply drag the operations in the tree to change cutting order

**Note:** Due to FreeCAD's internal operation initialization, newly split operations may not be fully editable (can't open task panel) until the document is saved and reopened. Check the "Save and reopen document" option to do this automatically, or manually save and reopen after splitting.

**Why use split?** Each operation runs independently in order with NO automatic reordering or optimization. You get complete control, just like creating individual contour operations in Fusion 360.

**Pro tip:** The operations are inserted in the Job at the same position as the original Profile, maintaining your workflow order.

### Production Array ⭐
1. Create a sketch with your part profile (design ONE part)
2. Exit the sketch
3. Select the sketch in the tree
4. Go to **CAM → Extensions → Design Tools → Production Array**
5. **Choose spacing mode:**
   - **Gap Spacing** (default): Specify the gap between parts
   - **Overall Spacing**: Specify total distance from first to last part
6. Configure the array:
   - **Count X**: Number of copies in X direction (e.g., 6 for 6 parts)
   - **Count Y**: Number of copies in Y direction (1 = linear array, >1 = rectangular grid)
   - **Spacing mode options:**
     - **Gap Spacing mode:**
       - **Gap X**: Edge-to-edge gap between parts (e.g., 1.0 inches)
       - **Gap Y**: Edge-to-edge gap between parts in Y direction
       - **Add part size to spacing**: Auto-adds part dimensions to gap (checked by default)
     - **Overall Spacing mode:**
       - **Overall X**: Total distance from first to last part (e.g., 20.0 inches)
       - **Overall Y**: Total distance from first to last part (e.g., 96.0 inches)
       - Program calculates: spacing = (overall - part_size) / (count - 1)
       - First part edge at 0, last part edge at overall distance
   - **Pad Depth**: Extrusion depth for each body (e.g., 0.5 inches)
   - **Reverse Direction**: Check to extrude in opposite direction
   - **Keep master sketch visible**: Keep original sketch in tree
   - **Auto-rename bodies**: Name bodies as Part_001, Part_002, etc.
7. Click **Create Array**
8. Result: A **ProductionArray** feature object appears in the tree!

**✨ NEW: Fully Parametric!**
- **Edit master sketch** → Array automatically regenerates with new geometry! 🎯
- **Double-click ProductionArray** in tree → Edit all parameters (count, spacing, depth, etc.)
- **Change any parameter** → Bodies automatically regenerate
- **All parameters visible** in Property Editor (Data tab)
- **Fully integrated** with FreeCAD's undo/redo system

**Example Parametric Workflow:**
1. Create array of 30 parts (3×10)
2. Edit master sketch → change a dimension → FreeCAD recomputes → all 30 bodies update automatically! ✨
3. Double-click ProductionArray object → change count to 5×12 (60 parts) → Click "Update Array"
4. Old 30 bodies deleted, 60 new ones created!

**Using the array for CAM:**
- Each Body can have its own CAM operation
- Select all Bodies → Create Profile operation → Generates toolpaths for all parts
- Or create individual operations per Body for maximum control
- Use Split Profile on the resulting operation if needed

**Examples:**

*Example 1: Gap Spacing (default)*
- Part: 2" × 20" rectangle
- Gap X: 1.0 in, Gap Y: 1.0 in
- "Add part size to spacing": ✓ (checked)
- Count: 3 × 10
- **Result**: Parts separated by 1" gaps (effective spacing: 3" × 21")

*Example 2: Overall Spacing*
- Part: 2" × 20" rectangle (sketch at origin, extends to 2"×20")
- Overall X: 20.0 in, Overall Y: 96.0 in
- Count X: 5, Count Y: 10
- **Calculation**: 
  - Part width: 2", Part length: 20"
  - Spacing X = (20" - 2") / (5 - 1) = 18" / 4 = 4.5"
  - Spacing Y = (96" - 20") / (10 - 1) = 76" / 9 = 8.444"
- **Result**: First part at origin (0,0), last part edge at (20", 96")
  - Part 1: 0" to 2" (left edge to right edge)
  - Part 2: 4.5" to 6.5"
  - Part 3: 9" to 11"
  - Part 4: 13.5" to 15.5"
  - Part 5: 18" to 20" ✓

*Example 3: Linear array on 24" sheet*
- Part: 3" × 10" rectangle
- Overall X: 24.0 in
- Count X: 6, Count Y: 1
- **Calculation**: 
  - Part width: 3"
  - Spacing = (24" - 3") / (6 - 1) = 21" / 5 = 4.2"
- **Result**: 6 parts with first edge at 0" and last edge at 24"
  - Part positions: 0", 4.2", 8.4", 12.6", 16.8", 21"
  - Part edges: 0"-3", 4.2"-7.2", 8.4"-11.4", 12.6"-15.6", 16.8"-19.8", 21"-24" ✓

**When to use which mode:**
- **Gap Spacing**: When you care about the gap between parts (e.g., for cutting clearance, material separation)
- **Overall Spacing**: When you need to fit parts into a fixed area (e.g., material sheet size, machine work envelope)

### Sketcher Parametric Array ⭐
1. **Open a sketch** for editing (double-click a sketch in the tree, or create a new one)
2. **Create your base geometry:**
   - Draw a rectangle, circle, polygon, or any sketch geometry
   - This is the "master" that will be arrayed
3. **Select the geometry** you want to array (click on it)
4. **Run the Parametric Array command:**
   - Click your custom toolbar button (if you installed the macro)
   - OR run from Python console: `FreeCADGui.runCommand('Sketcher_ParametricArray')`
5. **Configure the array** in the dialog:
   - **Rows**: Number of copies in vertical direction (e.g., 3)
   - **Columns**: Number of copies in horizontal direction (e.g., 5)
   - **Column Gap**: Spacing between columns
   - **Row Gap**: Spacing between rows
6. **Preview the total dimensions** shown at the bottom of the dialog
7. Click **Create Array**
8. **Result:** Array is created with parametric constraints!

**✨ Fully Parametric Behavior:**
- Change the base geometry size (e.g., resize the rectangle)
- **All copies update automatically** via constraints! 🎯
- Edit the gap spacing by modifying the constraints in the sketch
- Everything stays synchronized

**Smart Spacing Examples:**

*Example 1: Rectangle Array (edge-to-edge)*
- Base: 2" × 3" rectangle
- Columns: 4, Rows: 3
- Column Gap: 0.5", Row Gap: 0.5"
- **Behavior:** Gap measures from right edge of one rectangle to left edge of next
- **Total width:** 2" + 0.5" + 2" + 0.5" + 2" + 0.5" + 2" = 10.5"
- **Resize base to 3" × 3"** → Total width becomes 14.5" automatically!

*Example 2: Circle Array (center-to-center)*
- Base: 1" diameter circle
- Columns: 6, Rows: 1 (linear pattern)
- Column Gap: 2.5"
- **Behavior:** Gap measures from center of one circle to center of next
- **Total width:** (6-1) × 2.5" = 12.5" (span between first and last centers)
- **Change diameter to 2"** → Spacing stays 2.5" center-to-center automatically!

*Example 3: Bolt Hole Pattern*
- Create one bolt hole (circle)
- Array: 4 columns × 3 rows
- Column gap: 4", Row gap: 3"
- Later: **Change hole diameter** from 0.25" to 0.375" → All 12 holes update instantly!

**Tips:**
- **Mixed geometry:** If you select multiple types (circles + rectangles), the tool intelligently handles each type
- **Live preview:** The dialog shows total array dimensions before you create it
- **Validation:** The tool checks for potential overlaps and warns you
- **Undo/Redo:** Fully integrated with FreeCAD's undo system

**Perfect for:**
- Mounting hole patterns
- Ventilation grilles  
- Repeated features in sheet metal
- Bolt circles
- Any parametric pattern that needs to adapt to design changes

### Arc Feed Rate Control
1. Create or select a Profile operation
2. Look in the **Data** tab in the **Property Editor**
3. Find the **ArcFeedRatePercent** property (under "Path" section)
4. Set the percentage (default is 100%):
   - **100%** - Arcs run at same speed as linear moves (normal behavior)
   - **60%** - Arcs run at 60% of the Profile's feed rate (good for tight curves)
   - **40%** - Arcs run at 40% of the Profile's feed rate (delicate materials)
   - **25%** - Arcs run at 25% of the Profile's feed rate (very tight radius or fragile material)
5. Generate toolpath and post-process
6. Check the G-code - you'll see different F values on G2/G3 commands vs G1 commands

**When to use:**
- Tight radius features that need better finish quality
- Foam cutting where arc speed needs to be slower
- Materials that tend to burn or melt on curves
- Any time you want independent control of arc vs linear speeds

**Example:**
- Profile set to 500 in/min horizontal feed rate
- ArcFeedRatePercent set to 60%
- Result: G1 moves at 500 in/min, G2/G3 moves at 300 in/min

**Works with Split Profile:** When you split a Profile, each new operation gets its own ArcFeedRatePercent property, so different parts of your cut can have different arc speeds!

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
