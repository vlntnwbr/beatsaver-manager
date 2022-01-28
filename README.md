# Beat Saber Custom Level and Playlist Manager ![Tests-badge][pl-tests]
Command Line Interface to install, remove and update custom Beat Saber levels
using the [BeatSaver][beatsaver] API.

## Installation and Configuration

## Command Line Interface (CLI)

## playlist command

### install
- install a playlist referenced by either key or url
- downloads and extracts all songs that aren't installed already
- optionally install playlist from bplist file

### list
- list all installed playlists
- optionally check if they're upgradeable

### remove
- remove a playlist and all songs unique to that playlist
- optionally keep songs in playlist

### sync
- list all installed songs that aren't in a playlist
- optionally remove them
- behaves exactly the same as 'lvl sync'

### upgrade
- read all installed playlists and compare checksum with data from sync url
- install playlist when local checksum differs from online
- optionally remove all songs that were unique to updated playlist

## lvl command

### install
- install a (list of) songs referenced by either key or url
- downloads and extracts map data if it isn't available yet
- optionally install custom level from local zip file

### list
- list all installed songs
- optionally check if they're in a playlist

### remove
- removes song if it isn't part of a playlist
- optionally force removal (-f)

### sync
- list all installed songs that aren't in a playlist
- optionally remove them
- behaves exactly the same as 'bpl sync'

[pl-tests]: https://github.com/vlntnwbr/beatsaver-manager/workflows/Tests/badge.svg
[beatsaver]: https://beatsaver.com
