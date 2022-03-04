##
#   Copyright (c) 2022 Valentin Weber
#
#   This file is part of the software beatsaver-playlist-manager.
#
#   The software is licensed under the European Union Public License
#   (EUPL) version 1.2 or later. You should have received a copy of
#   the english license text with the software. For your rights and
#   obligations under this license refer to the file LICENSE or visit
#   https://joinup.ec.europa.eu/community/eupl/og_page/eupl to view
#   official translations of the licence in another language of the EU.
##

"""Local BeatSaber functionality for beatsaber-playlist-manager."""

import os
import shutil

from pathlib import Path
from typing import List, Optional, Tuple

from .core.exceptions import BeatSaberError, ModelError
from .core.models import BsMap, BsPlaylist, CustomLevel, BsInvalidLocal


class BeatSaberManager:
    """Base for interacting with a local BeatSaber installation."""

    def __init__(self, directory: Path) -> None:
        """Init manager for BeatSaber installation at given location."""
        self.playlist_ext = ".bplist"
        self.default_songs = (  # Contains levels auto-generated by Mod
            "Jaroslav Beck - Beat Saber (Built in)",
        )
        self.directory = directory
        self.bpl_dir = directory / "Playlists"
        self.custom_lvl_dir = directory / "Beat Saber_Data" / "CustomLevels"
        for bs_dir in (self.bpl_dir, self.custom_lvl_dir):
            try:
                if not bs_dir.is_dir():
                    bs_dir.mkdir(parents=True)
            except FileExistsError as exc:
                err = f"directory path points to an existing file: {bs_dir}"
                raise BeatSaberError(err) from exc
            except PermissionError as exc:
                err = f"access to directory denied: {bs_dir}"
                raise BeatSaberError(err) from exc

    def get_bpl_files(self) -> List[Path]:
        """Return list of all bplist filepaths of given installation."""
        return [
            bpl.resolve() for bpl in self.bpl_dir.iterdir()
            if bpl.is_file() and bpl.suffix == self.playlist_ext
        ]

    def get_playlists(self) -> Tuple[List[BsPlaylist], List[BsInvalidLocal]]:
        """Return list with all playlists of given installation."""
        playlist_files = self.get_bpl_files()
        bplists = []
        invalids = []
        for playlist in playlist_files:
            try:
                content = playlist.read_bytes()
                bplists.append(BsPlaylist.from_json(content, playlist))
            except (OSError, ModelError) as exc:
                invalids.append(BsInvalidLocal(playlist, exc))
        return bplists, invalids

    def get_playlist_names(self) -> List[str]:
        """Return list with all playlist names of given installation."""
        return [bpl.title for bpl in self.get_playlists()[0]]

    def get_playlist_by_key(self, key: str) -> Optional[BsPlaylist]:
        """Return playlist for given key if it exists."""
        for bplist in self.get_playlists()[0]:
            if bplist.key == key:
                return bplist
        return None

    def remove_playlist(self, bpl: BsPlaylist) -> None:
        """Remove given playlist file."""  # pylint: disable=no-self-use
        try:
            bpl.filepath.unlink()
        except OSError as exc:
            err_msg = f"can't remove playlist file: {exc.args[0]}"
            raise BeatSaberError(err_msg) from exc

    def install_playlist(self, bpl: BsPlaylist) -> None:
        """Write JSON playlist content to file in playlist directory."""
        bpl_dest = self.bpl_dir / bpl.filename
        try:
            bpl_dest.write_bytes(bpl.json_raw)
        except OSError as exc:
            err_msg = f"can't write playlist content: {exc.args[0]}"
            raise BeatSaberError(err_msg) from exc

    def get_custom_lvl_dirs(self) -> List[Path]:
        """Return list with all custom level directories."""
        return [
            lvl.resolve() for lvl in self.custom_lvl_dir.iterdir()
            if lvl.is_dir() and lvl.name not in self.default_songs
        ]

    def get_custom_levels(self) -> List[CustomLevel]:
        """Return keys of all installed songs from directory names."""
        return [CustomLevel(lvl) for lvl in self.get_custom_lvl_dirs()]

    def get_custom_level_by_key(self, key: str) -> Optional[CustomLevel]:
        """Return custom level for given key if it exists."""
        for lvl in self.get_custom_levels():
            if not isinstance(lvl, CustomLevel):
                continue
            if lvl.key == key:
                return lvl
        return None

    def remove_custom_level(self, lvl: CustomLevel) -> None:
        """Remove level directory."""  # pylint: disable=no-self-use
        try:
            shutil.rmtree(lvl.directory)
        except OSError as exc:
            err_msg = f"can't remove custom level: {exc.args[0]}"
            raise BeatSaberError(err_msg) from exc

    def install_custom_level(self, lvl: BsMap) -> None:
        """Extract the zipped custom level contents to lvl directory."""
        if lvl.content is None:
            raise BeatSaberError("level has no content")
        lvl_path = self.custom_lvl_dir / lvl.directory
        try:
            lvl.content.extractall(lvl_path)
        except OSError as exc:
            if lvl_path.exists():
                lvl_path.unlink()
            err_msg = f"can't extract level content: {exc.args[0]}"
            raise BeatSaberError(err_msg) from exc


if __name__ == '__main__':
    mgr = BeatSaberManager(Path(os.getenv("BEATSABER")))
    print("\n".join(repr(bpl) for bpl in mgr.get_playlists()))
