# Instructions:
Working Directory Structure must be:
```
root\
  \...
  \___NoneModFolders
  \_NoneModFolders
  \NoneModFolders
  \__Vehicles
  \__Gameplay
  \__Weapons
  \...
```
Folders not prefixed with 2 underscores will be ignored.
Go in `_ModScan.py` and change the Regex Rule of `RE_DIR` to target your directory setups.

`_ModScan_Install` to install python dependency package used by the script.

`_ModScan_Run` to start the python script.

# Script Functions (Python Interactive Console)

`ppaths()`
* lists all mods that has a potential version conflict, this show up in different colors
* lists all files that falls under the same mod ID but has different file names
* use `ppaths(sortkey=MID)` to sort the mods based on Mod ID instead of the mod names
* very useful in finding mods where the file name has changed between versions
* useful global var for sorting: PTH, DIR, NAM, MID, EXT (or VER, HSH but I don't see the reason to sort with version or hash among many different mods)

`paths()`
* returns the list of mods where the name is the same but has multiple different versions

`clean(paths())`
* automatically put all old versions of any mods with the same filename into `\__CLEAN`

`getmods(input_value)`
* returns list of mod(s) based on `input_value` - which can be `9999` (integer Mod ID), `"keyword"` (string, mod name, etc), or `["veh", "type-66", "bike"]` (list of strings)

`build_content()`
* if you have 7-ZIP installed, this function scans what files are inside each `zip/7z/rar` containers and generates a JSON file to list them all
* eventually this can be used to pre-determine file-level mod conflict before installing any mods
* takes a while to execute, single threaded, not very useful at the moment but if you need a complete list of contents of all mods, you can have it

`lsarc(filepath)`
* this will list all files inside of a single `zip/7z/rar` container given the path of it

`scan()`
* this rescans the directory for any changes

`modds(DB)`
* `DB` is a global variable used to store information of all mods during scan
* this function can be used to list all mods by `folder | Mod ID | version | filename | hash`
* a side product during early debugging

`modds(filter(key, term))`
* using the same `sortkey=MID` for `key` in filter will let user list mods by `term`
* example usage: `modds(filter(NAM, 'fire'))` finds all mods with the word `fire` in their file name
* a side product during early debugging

`link(ModID)`
* open browser to the mod page on nexus based on the ModID
