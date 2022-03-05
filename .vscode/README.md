# Debug Configurations
| Test Playlist    | BeatSaver                           | Initial Level              | Key  |
| ---------------- | ----------------------------------- | -------------------------- | ---- |
| _test1 <=> 3351  | [Web][_test1_web] [API][_test1_api] | DEUTSCHLAND - Rammstein    | 42ea |
| _test2 <=> 3444  | [Web][_test2_web] [API][_test2_api] | Eskimo Callboy - Hypa Hypa | b741 |
| _test1 <=> 3445  | [Web][_test3_web] [API][_test3_api] | Bonfire - Knife Party      | 5257 |

| Test Level                               | Key   | BeatSaver                           |
| ---------------------------------------- | ----- | ----------------------------------- |
| Ludwig Göransson - The Mandalorian Theme | 7707  | [Web][_mando_web] [API][_mando_api] |
| Power Glove - Knife Party                | 44f4  | [Web][_power_web] [API][_power_api] |
| Mick Gordon - Icon of Sin                | 11ed6 | [Web][_icon_web] [API][_icon_api]   |
| Skyrim Theme - Song of the Dragonborn    | 147e  | [Web][_tesv_web] [API][_tesv_api]   |

## bsdl bpl install

### Install Playlists From URLs
```
bsdl bpl install _test3_web https://vweber.eu _test1_api
```
**Expected Results**
1. Playlist _test3 is installed successfully
2. The playlist is skipped because the URL is invalid
3. Playlist _test1 is installed successfully

### Install Playlist From BeatSaver Keys
```
bsdl bpl install --keys 3445 abcd 3444
```
**Expected Results**
1. Playlist _test3 is skipped because it is already installed
2. Playlist is skipped because it isn't found on BeatSaver
3. Playlist _test2 is installed successfully

### Forcefully Install Playlists From Local Files
```
bsdl bpl install --force --files _err.bplist 3351.bplist
```
**Expected Results**
1. Playlist is skipped because the JSON is missing the 'title' key
2. Playlist _test1 is is overwritten 

## bsdl bpl list

### List All Installed Playlists Without Outdated Column
```
bsdl bpl list
```
***Expected Results**
- A table with all Titles and Keys of installed playlists is printed to the console

### List All Installed Playlists With Outdated Column
**Preparation**
1. Change the Description of playlist: _test2
```
bsdl bpl list --outdated
```
***Expected Results**
- A table with all Titles and Keys of installed playlists is printed to the console
- Additionally a third column will indicate whether a playlist is outdated
- The playlist _test2 will be recognized as outdated

## bsdl bpl remove

### Remove Playlists From BeatSaver Keys
```
bsdl bpl rm 2218 3351
```
***Expected Results**
1. Playlist is skipped because it isn't installed
2. Playlist "_test1" and level "DEUTSCHLAND - Rammstein" are removed

### Remove Playlists Via Filepath
```
bsdl bpl rm --files _no_exist.bplist .beatsaber/Playlists/beatsaver-3444.bplist
```
***Expected Results**
1. Playlist is skipped because it doesn't exist
2. Playlist "_test2" and level "Exkimo Callboy - Hypa Hypa" are removed

### Remove a Playlist But Keep All The Songs
```
bsdl bpl rm --keep-songs 3445
```
***Expected Results**
1. Playlist "_test3" but not level "Bonfire - Knife Party" is removed

## bsdl bpl sync

### List All Songs That Are Not Part Of a Playlist
```
bsdl bpl sync
```
**Expected Results**
1. Level "Bonfire - Knife Party" is displayed but not removed

### List All Songs That Are Not Part Of a Playlist And Remove Them
```
bsdl bpl sync --remove
```
**Expected Results**
1. Level "Bonfire - Knife Party" is displayed and removed

## bsdl bpl upgrade

### Upgrade Specific Playlists
**Preparation**
```
cp .beatsaber/.test_data/beatsaver-3444.bplist .beatsaber/Playlists/
cp .beatsaber/.test_data/beatsaver-3445.bplist .beatsaber/Playlists/
```
```
bsdl bpl upgrade --bpl 3351 3444
```
**Expected Results**
1. Playlist "_test1" is skipped because it isn't installed
2. Playlist _test2 and level "Eskimo Callboy - Hypa Hypa" are installed
3. Playlist _test3 is not upgraded and its file does not list any songs

### Upgrade All Outdated Playlists
**Preparation**
```
cp .beatsaber/.test_data/beatsaver-3445.bplist .beatsaber/Playlists/
```
- Move "Eskimo Callboy - Hypa Hypa" from "_test2" to "_test3"
- Move "Bonfire - Knife Party" from "_test3" to "_test2"
```
bsdl bpl upgrade
```
**Expected Results**
1. Playlist "_test1" and level "DEUTSCHLAND - Rammstein" are installed
2. Playlist "_test2" is installed and level "Bonfire - Knife Party" is skipped
3. Playlist "_test3" is installed and level "Eskimo Callboy - Hypa Hypa" is found

### Upgrade All Outdated Playlists And Remove Their Songs
**Preparation**
- Remove level "Bonfire - Knife Party" from playlist "_test2"
```
bsdl bpl upgrade --remove-songs
```
- ...
**Expected Results**
1. ---

**Cleanup**
- Playlist "_test1" shall only contain the level "DEUTSCHLAND - Rammstein"
- Playlist "_test2" shall only contain the level "Eskimo Callboy - Hypa Hypa"
- Playlist "_test3" shall only contain the level "Bonfire - Knife Party"

## bsdl lvl install

### Install Levels From URLs
```
bsdl lvl install _mando_web https://vweber.eu _power_api
```
**Expected Results**
1. Level "Ludwig Görransson - The Mandalorian Theme" is installed
2. Level is skipped because the URL is invalid
3. Level "Power Glove - Knife Party" is installed

### Install Levels From BeatSaver Keys
```
bsdl lvl install 44f4 11ed6 abcdefgh
```
**Expected Results**
1. Level "Power Glove - Knife Party" is skipped because it is already installed
2. Level "Mick Gordon - Icon of Sin" is installed
3. Level is skipped because it's not found on BeatSaver

### Forcefully Install a Level That Is Already Installed
```
bsdl lvl install --force 44f4
```
**Expected Results**
1. Level "Power Glove - Knife Party" is installed

## bsdl lvl list

### List All Installed Songs
```
bsdl lvl list
```
**Expected Results**
- A table with all Titles and Keys of installed levels is printed to the console

### List All Installed Songs And The Playlists They Are a Part Of
```
bsdl lvl list --check-playlists
```
**Expected Results**
- A table with all Titles and Keys of installed levels is printed to the console
- Additionally a third column will list the playlists a song is part of
- For all previously installed testing levels the playlist column is empty

## bsdl lvl remove

### Remove levels via their BeatSaver key
```
bsdl lvl rm 147e 5257 44f4
```
**Expected Result**
1. Level "Skyrim Theme - Song of the Dragonborn" is skipped because it's not installed
2. Level "Bonfire - Knife Party" is skipped because it's part of a playlist
3. Level "Power Glove - Knife Party" is removed

### Remove Levels From Their Directory Path
```
bsdl lvl rm --files ^
  ".beatsaber/Beat Saber_Data/CustomLevels/44f4 (Power Glove - Knife Party - LittleAsi)" ^
  ".beatsaber/Beat Saber_Data/CustomLevels/5257 (Bonfire - Knife Party - Funrankable)" ^
  ".beatsaber/Beat Saber_Data/CustomLevels/11ed6 (Mick Gordon - Icon of Sin - Foow17)"
```
1. Level "Power Glove - Knife Party" is skipped because it's not installed
2. Level "Bonfire - Knife Party" is skipped because it's part of a playlist
3. Level "Mick Gordon - Icon of Sin" is removed

### Forcefully Remove a Level That Is Part Of a Playlist
```
bsdl lvl rm --force 5257
```
**Expected Result**
- Level "Bonfire - Knife Party" is removed

## bsdl lvl sync

### List All Songs That Are Not Part Of a Playlist
```
bsdl lvl sync
```
**Expected Results**
1. Level "Ludwig Göransson - The Mandalorian Theme" is displayed but not removed

### List All Songs That Are Not Part Of a Playlist And Remove Them
```
bsdl lvl sync --remove
```
**Expected Results**
1. Level "Ludwig Göransson - The Mandalorian Theme" is displayed and removed

<!--- References ------------------------------------------------------------->
[_test1_web]: https://beatsaver.com/playlists/3351
[_test1_api]: https://api.beatsaver.com/playlists/id/3351
[_test2_web]: https://beatsaver.com/playlists/3444
[_test2_api]: https://api.beatsaver.com/playlists/id/3444
[_test3_web]: https://beatsaver.com/playlists/3445
[_test3_api]: https://api.beatsaver.com/playlists/id/3445

[_mando_web]: https://beatsaver.com/maps/7707
[_mando_api]: https://api.beatsaver.com/maps/id/7707
[_power_web]: https://beatsaver.com/maps/44f4
[_power_api]: https://api.beatsaver.com/maps/id/44f4
[_icon_web]: https://beatsaver.com/maps/11ed6
[_icon_api]: https://api.beatsaver.com/maps/id/11ed6
[_tesv_web]: https://beatsaver.com/maps/147e
[_tesv_api]: https://api.beatsaver.com/maps/id/147e
