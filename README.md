![](https://github.com/TeaCrab/NexusArchiveScanner/blob/master/__title.png?raw=true)
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

## Update 2024-11-17:
### Version strings & symbols in file names are now stripped from mod file identification.
* File names which only differ in symbol, version string & upper/lower case now identifies as the same file under their Mod ID & versions.
* If the mod name, ID and version are all identical but exists in different folders, the file which has the largest hash will be kept during cleaning.
  * If the hash are also the same, the alphabetical first file that's already categorized will be kept

# Script Functions (Python Interactive Console)

`build_content()`
* works only when you have 7-ZIP installed, scans the content of every `zip/7z/rar` file and generates a JSON file to list all content
* groundwork for detecting/automating file level mod conflict checking & a tool for trouble shooting
* takes a while to generate the JSON file if you have a lot of mods

`lsarc(filepath)`
* this will list all files inside of a single `zip/7z/rar` container given the path of it

`link(ModID)`
* open browser to the mod page on nexus based on the ModID
* currently defaults to Cyberpunk 2077

`scan()`
* this scans the directory, useful for refreshing

`paths(filt=None, sortbyname=False)`
* returns the list of mods where the name is the same but has multiple different versions
* if `filt` is a valid string, it only displays mod files which contains the key words in sequence

`ppaths(filt=None, sortbyname=False)`
* same as paths, but:
* lists all mods that has a potential version conflict, this show up in different colors
* lists all files that falls under the same mod ID but has different file names
* very useful in finding mods where the file name has changed between versions

`upaths(filt="__unsorted", sortbyname=False)`
* just a shortcut for listing from a folder which the name contains `__unsorted` keyword

`getmods(input_value)`
* returns list of mod info based on `input_value` - which can be:
  * `9999` (a single integer as Mod ID)
  * `"key words"` (same usage as the `filt` argument in `paths()`)
  * `[999, 1999, 2999]` (list of integer Mod IDs)
  * `{999:{content info}, 1000:...}` (dict containing integer Mod ID as key and Mod info as value)
  * `[{999:{content info}, {1000:...}]` (same as above but a list of)

`fsort(fuzzypath='')`
* `fuzzypath` selects a single folder name in working directory and attempts to load a corresponding text file
* the text file contains a Mod ID on each line, all the files associated with the IDs will be moved into the `fuzzypath` folder
* lists any mods in the text file which doesn't exists in the working directory

`clean(input_value, force=False)`
* `input_value` is the same idea as in `getmods()`
* put all older versions of selected mods' files with the same name into `\__CLEAN` directory
* if `force==True`, all files associated with the selected mods will be put into `\__CLEAN`

`move(input_value, fuzzypath)`
* `input_value` is the same idea as in `getmods()`
* put all files of any selected mods into the `fuzzyfind` directory

`mvvh(input_value)`
* just a shortcut for moving selected mods into `\__Vehicles` folder
