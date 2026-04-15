# Repository Restructure - April 15, 2026

## Overview
Reorganized the FreeCAD_CAM_Extensions repository to support expansion into design-for-production tools while maintaining the existing CAM functionality.

## Changes Made

### New Folder Structure
```
FreeCAD_CAM_Extensions/
├── cam/                    # CAM-specific extensions
│   ├── __init__.py
│   ├── ArcFeedRatePatch.py
│   ├── BaseGeometryReorderPanel.py
│   ├── OperationVariablesPanel.py
│   ├── ProfileOrderPatch.py
│   └── SplitProfilePanel.py
├── design/                 # Design-for-production (future)
│   └── __init__.py
├── common/                 # Shared utilities (future)
│   └── __init__.py
├── CAMExtensions_Commands.py  (root)
├── InitGui.py                  (root)
└── Init.py                     (root)
```

### Files Modified

**InitGui.py**
- Changed: `import ArcFeedRatePatch` → `from cam import ArcFeedRatePatch`
- Commented out ProfileOrderPatch import updated to use new path

**CAMExtensions_Commands.py**
- Changed: `import OperationVariablesPanel` → `from cam import OperationVariablesPanel`
- Changed: `import BaseGeometryReorderPanel` → `from cam import BaseGeometryReorderPanel`
- Changed: `import SplitProfilePanel` → `from cam import SplitProfilePanel`

**README.md**
- Added "Project Vision" section
- Added "Project Structure" section with folder diagram
- Positioned as "FreeCAD for Production Manufacturing"

### Files Moved
- `ArcFeedRatePatch.py` → `cam/ArcFeedRatePatch.py`
- `SplitProfilePanel.py` → `cam/SplitProfilePanel.py`
- `ProfileOrderPatch.py` → `cam/ProfileOrderPatch.py`
- `OperationVariablesPanel.py` → `cam/OperationVariablesPanel.py`
- `BaseGeometryReorderPanel.py` → `cam/BaseGeometryReorderPanel.py`

## Rationale

### Why Keep One Repository?
1. Unified "production manufacturing" vision
2. Single installation/deployment workflow
3. Shared infrastructure (commands, deployment, etc.)
4. Parametric arrays directly support CAM production workflows
5. Easier maintenance and testing

### Why This Structure?
- **cam/** - Clear separation of CAM-specific functionality
- **design/** - Future home for parametric arrays, nesting tools
- **common/** - Future shared utilities and UI components
- Allows independent development while maintaining cohesion

## Next Steps

### Immediate
1. Deploy to FreeCAD and test
2. Verify all existing functionality works
3. Commit changes to git

### Near Future - Parametric Array Feature
1. Create `design/ParametricArrayManager.py`
2. Track master sketch and create/update Body instances
3. Add UI panel for array configuration
4. Register commands in CAMExtensions_Commands.py

## Testing Checklist
- [ ] Extension loads without errors
- [ ] Arc Feed Rate patch applies successfully
- [ ] Show Operation Variables command works
- [ ] Reorder Base Geometry command works
- [ ] Split Profile command works
- [ ] All imports resolve correctly
- [ ] No broken functionality from restructure

## Deployment
Run the normal deployment script:
```powershell
cd c:\FreeCAD_CAM_Extensions
.\deploy_to_freecad.ps1
```

Then restart FreeCAD and verify all features work.
