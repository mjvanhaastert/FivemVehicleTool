# FiveM Vehicle Tool

FiveM Vehicle Tool scans a folder that contains many separate vehicle resources and converts them into one organized `Vehicles` resource.

The output structure is:

```text
Vehicles/
  <category>/
    stream/
    meta/
  fxmanifest.lua
```

It automatically:
- Detects vehicle categories (from `vehicles.meta` when possible)
- Moves stream assets (`.yft`, `.ytd`, etc.) into category stream folders
- Moves meta files into category meta folders
- Prefixes meta filenames with the vehicle name to prevent filename collisions
- Generates one central `Vehicles/fxmanifest.lua`

## Requirements

- Python 3.10+ (recommended)
- Windows/Linux/macOS

## Installation

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. (Optional but recommended) Create and activate a virtual environment.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Start the Application

Run:

```bash
python main.py
```

The PyQt desktop interface will open.

## How to Use

1. **Select Input Folder**
   - Choose the folder that contains your existing FiveM vehicle resources.
   - Each resource should normally contain `fxmanifest.lua` or `__resource.lua`.

2. **Select Output Folder**
   - Choose where the tool should create the unified `Vehicles` folder.
   - Example result path: `D:/exports/Vehicles`.

3. **Scan**
   - Click **Scan** to detect all vehicle resources.
   - The tool reads stream/meta files and tries to detect category from `vehicles.meta`.

4. **(Optional) Override Categories**
   - Click **Categories override** to manually assign category values for incorrectly detected or unknown vehicles.

5. **Choose Options**
   - **Dry-run**: simulate organizing without writing files.
   - **Backup**: create a zip backup of the source before writing.

6. **Run Organizer**
   - Use **Dry-run preview** first if you want to verify.
   - Use **Organize** to write output files.

## Output Details

After organizing, you will get:

- `Vehicles/<category>/stream/*` for stream/model files
- `Vehicles/<category>/meta/*` for meta/xml files
- `Vehicles/fxmanifest.lua` containing all data file registrations

### Example

```text
Vehicles/
  super/
    stream/
      ferrari_f40.yft
      ferrari_f40.ytd
    meta/
      ferrari_f40_vehicles.meta
      ferrari_f40_handling.meta
      ferrari_f40_carcols.meta
  sports/
    stream/
    meta/
  fxmanifest.lua
```

## Notes

- If multiple stream files have the same name, the tool uses safe renaming to avoid overwrites.
- If category cannot be detected, vehicles are placed in `_unknown`.
- If no recognized meta type is detected for a file, it is still copied but may not get a `data_file` entry in `fxmanifest.lua`.

## Troubleshooting

- If the app does not start, verify:
  - `python --version`
  - `pip install -r requirements.txt` completed without errors
- If scan finds no resources:
  - Confirm each resource has `fxmanifest.lua` or `__resource.lua`
  - Confirm you selected the correct input root folder
