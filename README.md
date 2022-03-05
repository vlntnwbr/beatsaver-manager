# Beat Saber Custom Level and Playlist Manager ![Tests-badge][pl-tests]
Command Line Interface to install, remove and update custom Beat Saber levels
using the [BeatSaver][beatsaver] API.

## Installation

## Command Line Interface (CLI)
```
bsdl [-h] [--beatsaber <dir>] [--log-level <level>] <command> ...
```
The command line interface provides the main entry point `bsdl`. It has two
arguments that can be specified. They are also available for all other commands
the application provides.

The `--beatsaber` argument specifies the installation directory of the Beat
Saber game, e.g.: "C:\Program Files (x86)\Steam\steamapps\common\Beat Saber"

If the argument isn't set the application tries to read the value from the
environment variable `BEATSABER`. If neither the environment variable nor the
command line argument are set running the application will result in an error.

## Configuration
To avoid having to always specify the Beat Saber installation directory when
calling the application it is advisable to set the environment variable
`$BEATSABER` to contain the path to the Beat Saber installation.

However, the `--beatsaber` argument takes precedence over the value in the
environment variable. If the argument is set, the value from the environment
variable is not used. This makes it easy to manage multiple Beat Saber
installations (e.g. Steam and Oculus).

The following commands can be used to set that environment variable to the
given example location value. To use the command for a different path replace
the filepath part with the one you want. Make sure the path is surrounded by
quotation marks " ". On Windows a correctly formatted path to a folder can be
copied by holding Shift while right-clicking a folder and selecting the option
"Copy as Path".

### Set Steam Directory
- Example Location: `C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels`
```
[System.Environment]::SetEnvironmentVariable("BEATSABER_TEST", "C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels", [System.EnvironmentVariableTarget]::User)
```

### Set Oculus Directory
- Example Location: `C:\Program Files\Oculus\Software\Software\hyperbolic-magnetism-beat-saber\Beat Saber_Data\CustomLevels`
```
[System.Environment]::SetEnvironmentVariable("BEATSABER", "C:\Program Files\Oculus\Software\Software\hyperbolic-magnetism-beat-saber\Beat Saber_Data\CustomLevels", [System.EnvironmentVariableTarget]::User)
```



## Managing Playlists
```
usage: bsdl bpl [-h] <command> ...

positional arguments:
  <command>
    install   install playlist and download missing songs
              (use '-h' option for details)
    list      list all locally installed playlists
              (use '-h' option for details)
    rm        remove a playlist and all its unique songs
              (use '-h' option for details)
    upgrade   install newer version of all outdated local playlists
              (use '-h' option for details)
    sync      list all installed custom levels not in a playlist
              (behaves like 'lvl sync') (use '-h' option for details)
```

## Installing Playlists
```
bsdl bpl install [-h] [--keys] [--files] [-f] playlist [playlist ...]
```
This command installs one or more playlists which can be referenced by either
their BeatSaver key, the full BeatSaver URL or a path to an already downloaded
bplist file from Beat Saver.

During installation all songs in that playlist that are not already installed
are downloaded and installed from Beat Saver.

If a referenced playlist is already installed this specific playlist is skipped
unless the `-f, --force` argument is set. Be aware that this argument applies
to ALL playlists that are referenced.


### Install a playlist via URL
```
bsdl bpl install https://beatsaver.com/playlists/1710
```
The above command will install the playlist [Rammstein][bpl_rammstein] and
download all its songs that aren't already installed. The Beat Saber
installation directory is read from the environment variable. If it isn't set
the application will not run. If the playlist is already installed it won't be
downloaded again.

### Install a playlist via BeatSaver Key
```
bsdl --beatsaber "C:\Beat Saber" bpl install --keys 2218
```
The above command will install the playlist [Cyberpunk 2077][bpl_cyberpunk]
and download all its songs that aren't already installed. The Beat Saber
installation directory is given as "C:\Beat Saber". If that directory doesn't
exist or is write-protected the application will not run. If the playlist is
already installed it won't be downloaded again.

### Install a playlist via local file
```
bsdl bpl install --files "~/Downloads/BeatSaver - Sabaton.bplist"
```
Assume you have downloaded the playlist [Sabaton][bpl_sabaton] to the default
Windows Downloads directory without changing the filename. The above command
will install the playlist  and download all its songs that aren't already
installed. The Beat Saber installation directory is read from the environment
variable. If it isn't set the application will not run. If one of the files
does not contain valid BeatSaver Playlist data the playlist is skipped. If
the playlist is already installed it won't be downloaded again.

### Forcefully install a playlist that is already installed
```
bsdl bpl install -f https://beatsaver.com/playlists/1710
```
```
bsdl bpl install --force https://beatsaver.com/playlists/1710
```
Both above commands are equivalent and behave exactly the same as the one
described in Example 1. The only difference being that the playlist and all
songs not already installed are always downloaded overwriting any potential
existing playlist file.

## Listing Installed Playlists
```
bsdl bpl list [-h] [--outdated]
```


### Display all installed playlists
```
bsdl bpl list
```
The above command will display a table containing the title and Beat Saver key
of all installed playlists. The Beat Saber installation directory is read from
the environment variable. If it isn't set the application will not run. If no
levels are installed nothing is displayed unless the log is set to debug level.

### Display all installed playlists and check if they're outdated
```
bsdl bpl list --outdated
```
The above command behaves like the one in Example 1 but every playlist is
compared to its corresponding version on BeatSaver. A third column is added to
the table which will contain an "x" if the versions are different. This means
the application considers it to be outdated and [upgradable][_toc_bpl_sync].

## Removing Installed Playlists
```
bsdl bpl rm [-h] [--keep-songs] [--files] playlist [playlist ...]
```
This command removes one or more installed playlists which can be referenced by
either their BeatSaver key or the path to the bplist file. By default this also
removes all songs of a playlist unless that song is part of another playlist.
If the option `--keep-songs` is set no songs will be removed. Be aware that
this option applies to ALL referenced playlists. 


### Remove a playlist via key
```
bsdl bpl rm 1710
```
The above command will remove the playlist [Rammstein][bpl_rammstein] and all
songs that are unique to it. The Beat Saber installation directory is read from
the environment variable. If it isn't set the application will not run.

### Remove a playlist via filepath
```
bsdl bpl rm --files "C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Playlists\beatsaver-2218.bplist"
```
The above command will remove the playlist [Cyberpunk 2077][bpl_cyberpunk] and
all songs that are unique to it. The Beat Saber installation directory is read
from the environment variable. If it isn't set the application will not run.

### Remove a playlist keeping all the songs
```
bsdl bpl rm --keep-songs 1710
```
The above command will remove the playlist [Rammstein][bpl_rammstein] but will
not remove its songs. The Beat Saber installation directory is read from the
environment variable. If it isn't set the application will not run.

## Synchronizing Playlists and Levels
```
bsdl bpl sync [-h] [--remove]
```
This command will display all installed levels that are not part in a playlist.
If the option `--remove` is set, all of those levels will be removed.

This command behaves exactly like [bsdl lvl sync][_toc_lvl_sync]


### List all songs that aren't in a playlist
```
bsdl bpl sync
```
The above command will log all installed levels that aren't referenced as a
song in any installed playlist. The Beat Saber installation directory is read
from the environment variable. If it isn't set the application will not run.

### List all songs that aren't in a playlist and delete them
```
bsdl bpl sync --remove
```
The above command will log and remove all installed levels that aren't
referenced as a song in any installed playlist. The Beat Saber installation
directory is read from the environment variable. If it isn't set the
application will not run.

## Upgrading Installed Playlists
```
bsdl bpl upgrade [-h] [--remove-songs] [--bpl <key> [<key> ...]]
```
This command determines all installed playlists and checks whether there is a
difference between the installed version and the one found on BeatSaver. If the
`--remove-songs` option is set . Using the `--bpl` option
makes it possible to reference installed playlists by their BeatSaver key. If
that option is checked only the referenced playlists are upgraded.


### Upgrade a specific playlist
```
bsdl bpl upgrade --bpl 1072
```
The above command will check if there is a difference between the installed
version of the playlist [Sabaton][bpl_sabaton] and the one found on BeatSaver.
If the playlist is not installed nothing is done. The Beat Saber installation
directory is read from the environment variable. If it isn't set the
application will not run.

### Upgrade all outdated playlists
```
bsdl bpl upgrade
```
The above command will determine all installed playlists and check whether
there is a difference between the installed version and the one found on
BeatSaver. The Beat Saber installation directory is read from the environment
variable. If it isn't set the application will not run.

### Upgrade all outdated playlists and remove their songs
```
bsdl bpl upgrade --remove-songs
```
The above command will determine all installed playlists and check whether
there is a difference between the installed version and the one found on
BeatSaver. All songs that are no longer in the playlist are removed unless they
are part of a another playlist. The Beat Saber installation directory is read
from the environment variable. If it isn't set the application will not run.

## Managing Custom Levels
```
usage: bsdl lvl [-h] <command> ...

positional arguments:
  <command>
    install   install a custom level locally
              (use '-h' option for details)
    list      list all installed custom levels
              (use '-h' option for details)
    rm        remove a custom level not in a playlist
              (use '-h' option for details)
    sync      list all installed custom levels not in a playlist
              (behaves like 'bpl sync') (use '-h' option for details)

options:
  -h, --help  show this help message and exit

--log-level argument defaults to 'info' and can also be set with
the environment variable $BSDL_LOG_LEVEL

--beatsaber argument defaults to environment variable $BEATSABER
If the variable is not set, the argument MUST be provided
```

## Installing Custom Levels
```
bsdl lvl install [-h] [--keys] [-f] level [level ...]
```
This command installs one or more levels which can be referenced by either
their BeatSaver key or the full BeatSaver URL.

If a referenced level is already installed this specific playlist is skipped
unless the `-f, --force` argument is set. Be aware that this argument applies
to ALL levels that are referenced.


### Install a Level via URL
```
bsdl lvl install https://beatsaver.com/maps/7707
```
The above command will install the level
[Ludwig Göransson - The Mandalorian Theme][lvl_mando]. If the level is already
installed it won't be downloaded again. The Beat Saber installation directory
is read from the environment variable. If it isn't set the application will not
run.

### Install a Level via BeatSaver Key
```
bsdl lvl install --keys 5257
```
The above command will install the level [Bonfire - Knife Party][lvl_bonfire].
If the level is already installed it won't be downloaded again. The Beat Saber
installation directory is read from the environment variable. If it isn't set
the application will not run.

### Forcefully install a level that is already installed
```
bsdl lvl install -f https://beatsaver.com/maps/7707
```
```
bsdl lvl install --force https://beatsaver.com/maps/7707
```
The above commands are equivalent and behave like the one in Example 1. The
only difference being that the level is always downloaded overwriting any
potential existing version.

## Listing Installed Levels
```
bsdl lvl list [-h] [--check-playlists]
```


### Display all installed levels
```
bsdl lvl list
```
The above command will display a table containing the title and Beat Saver key
of all installed levels. The Beat Saber installation directory is read from the
environment variable. If it isn't set the application will not run. If no
levels are installed nothing is displayed unless the log is set to debug level.

### Display all installed levels and their playlist(s)
```
bsdl lvl list --check-playlists
```
The above command behaves like the one in Example 1 but a third column
containing the names of playlists that contain the song is added to the table.

## Removing Installed Levels
```
bsdl lvl rm [-h] [-f] [--files] level [level ...]
```
This command removes one or more installed levels which can be referenced by
either their BeatSaver key or the path to the directory that contains the level
data. If a level is referenced as a song in any installed playlist the removal
is skipped unless the `-f, --force` option is set. Be aware that this option
applies to ALL referenced levels. A referenced level that is not installed is
also skipped.


### Remove a level via its BeatSaver key
```
bsdl lvl rm 7707
```
The above command will remove the level
[Ludwig Göransson - The Mandalorian Theme][lvl_mando] if it is installed and
not part of any playlist. The Beat Saber installation directory is read from
the environment variable. If it isn't set the application will not run.

### Remove a level via its directory path
```
bsdl lvl rm "C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels\5257 (Bonfire - Funrankable)"
```
The above command will remove the level [Bonfire - Knife Party][lvl_bonfire] if
it is installed and not part of any playlist. The Beat Saber installation
directory is read from the environment variable. If it isn't set the
application will not run.

### Forcefully remove a level ignoring whether it's in a playlist
```
bsdl lvl rm -f 7707
```
```
bsdl lvl rm --force 7707
```
The above commands are equivalent and behave like the one in Example 1. The
only difference being that the level is removed even if it is in a playlist.

## Synchronizing Levels and Playlists
```
bsdl lvl sync [-h] [--remove]
```
This command will display all installed levels that are not part in a playlist.
If the option `--remove` is set, all of those levels will be removed.

This command behaves exactly like [bsdl bpl sync][_toc_bpl_sync]


### List all songs that aren't in a playlist
```
bsdl lvl sync
```
The above command will log all installed levels that aren't referenced as a
song in any installed playlist. The Beat Saber installation directory is read
from the environment variable. If it isn't set the application will not run.

### List all songs that aren't in a playlist and delete them
```
bsdl lvl sync --remove
```
The above command will log and remove all installed levels that aren't
referenced as a song in any installed playlist. The Beat Saber installation
directory is read from the environment variable. If it isn't set the
application will not run.

## Future Improvements
- Support for BeatSaver One-Click installation.

## Encountered a Bug?
Feel free to [open an issue][new-issue] if you encountered bugs or have other
ideas that aren't yet listed in the [backlog][issues].


 <!--- References --->
[pl-tests]: https://github.com/vlntnwbr/beatsaver-manager/workflows/Tests/badge.svg
[beatsaver]: https://beatsaver.com

[bpl_rammstein]: https://beatsaver.com/playlists/1710
[bpl_cyberpunk]: https://beatsaver.com/playlists/2218
[bpl_sabaton]: https://beatsaver.com/playlists/1052
[lvl_mando]: https://beatsaver.com/maps/7707
[lvl_bonfire]: https://beatsaver.com/maps/5257


[new-issue]: https://github.com/vlntnwbr/beatsaver-manager/issues/new/choose
[issues]: https://github.com/vlntnwbr/beatsaver-manager/issues

[_toc_bpl_install]: #installing-playlists
[_toc_bpl_list]: #listing-installed-playlists
[_toc_bpl_rm]: #removing-installed-playlists
[_toc_bpl_sync]: #synchronizing-playlists-and-levels
[_toc_bpl_upgrade]: #upgrading-installed-playlists
[_toc_lvl_install]: #installing-custom-levels
[_toc_lvl_list]: #listing-installed-levels
[_toc_lvl_rm]: #removing-installed-levels
[_toc_lvl_sync]: #synchronizing-levels-and-playlists