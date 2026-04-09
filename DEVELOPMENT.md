# Development Workflow

This repository is the **source of truth** for the FreeCAD CAM Extensions.

## Directory Structure

- **Git Repository (Source)**: `c:\FreeCAD_CAM_Extensions\`
- **Active FreeCAD Extension**: `%APPDATA%\FreeCAD\v1-1\Mod\FreeCAD_CAM_Extensions\`

## Development Workflow

### 1. Edit files in the Git repository
Edit any Python files, README, etc. in `c:\FreeCAD_CAM_Extensions\`

### 2. Deploy changes to FreeCAD
Run the deployment script:
```powershell
cd c:\FreeCAD_CAM_Extensions
.\deploy_to_freecad.ps1
```

Or manually copy files:
```powershell
Copy-Item c:\FreeCAD_CAM_Extensions\*.py "$env:APPDATA\FreeCAD\v1-1\Mod\FreeCAD_CAM_Extensions\" -Force
```

### 3. Test in FreeCAD
- Restart FreeCAD completely to load the new code
- Test your changes

### 4. Commit to Git
```bash
cd c:\FreeCAD_CAM_Extensions
git add .
git commit -m "Your commit message"
git push
```

## Quick Deploy Command
```powershell
.\deploy_to_freecad.ps1
```

## Notes
- Always edit in the **Git repository** (`c:\FreeCAD_CAM_Extensions`)
- FreeCAD loads from **AppData Mod directory** 
- Must restart FreeCAD to see changes
- The deploy script copies all Python and documentation files automatically
