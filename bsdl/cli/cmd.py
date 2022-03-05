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

"""CLI command functions for beatsaber-playlist-manager."""

from logging import Logger
from pathlib import Path
from typing import Any, List, Optional

from ..core.exceptions import BeatSaberError, BeatSaverApiError, ModelError
from ..core.models import BsInvalidLocal, BsPlaylist, PlaylistItem, CustomLevel
from ..beatsaver import BeatSaverApi
from ..local import BeatSaberManager
from .utils import BplListPrinter, LvlListPrinter


class CliCommands(BeatSaberManager):
    """Container for functions corresponding to cli commands."""

    def __init__(self, beatsaber_directory: Path, logger: Logger) -> None:
        """Initialize command namespace with given local manager."""
        super().__init__(beatsaber_directory)
        self.api = BeatSaverApi()
        self.log = logger

    def bpl_lvl_sync(self, remove: bool) -> None:
        """Print (optionally remove) custom levels not in a playlist."""
        self.log.info("Retrieving Levels That Are Not Part of Any Playlist")
        lvl_list = self.get_custom_levels()
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            err_msg = "Skipping Song Removal" if remove else None
            self.log_bpl_warn(bpl_errs, err_msg)
            remove = False
        for lvl in lvl_list:
            if any(bpl.contains_song(lvl) for bpl in bpl_list):
                continue
            self.log.info("%s", lvl)
            if remove:
                try:
                    self.remove_custom_level(lvl)
                    self.log.info("%s: Removed Level", lvl)
                except BeatSaberError as exc:
                    self.log_exc("Can't Remove Level", lvl, exc)

    def bpl_install(self, bpl_list: List[str], kind: str, force: bool) -> None:
        """Install given playlists under specified parameters."""
        self.log.info("Installing %s Playlist(s) From %s", len(bpl_list), kind)
        for bpl_ref in bpl_list:
            try:
                if kind == "keys":
                    bpl = self.api.get_playlist_by_key(bpl_ref)
                elif kind == "files":
                    filepath = Path(bpl_ref)
                    bpl = BsPlaylist.from_json(filepath.read_bytes())
                else:
                    bpl = self.api.get_playlist_from_url(bpl_ref)
                if not force and self.get_playlist_by_key(bpl.key) is not None:
                    self.log.warning("%s: Found Existing Playlist", bpl)
                    continue
                self.log.info("%s: Installing Playlist", bpl)
                self.install_playlist(bpl)
                self._install_playlist_songs(bpl)
            except BeatSaberError as exc:
                self.log_exc("Can't Install Playlist", bpl_ref, exc)
            except BeatSaverApiError as exc:
                self.log_exc("Can't Install Playlist", bpl_ref, exc)
            except ModelError as exc:
                self.log_exc("Can't Construct Playlist", bpl_ref, exc)
            except OSError as exc:
                self.log_exc("Can't Read Playlist", bpl_ref, exc.args[0])

    def bpl_list(self, outdated: bool) -> None:
        """Print information about all installed playlists."""
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            self.log_bpl_warn(bpl_errs)
        printer = BplListPrinter(outdated)
        for bpl in bpl_list:
            if outdated:
                try:
                    remote_bpl = self.api.get_playlist_by_key(bpl.key)
                    is_outdated = remote_bpl.checksum != bpl.checksum
                    printer.append(bpl, is_outdated)
                    continue
                except BeatSaverApiError as exc:
                    self.log_exc("Can't Download Playlist", bpl, exc)
            printer.append(bpl)
        printer.print()

    def bpl_remove(self, bpl_list: List[str], kind: str, keep: bool) -> None:
        """Remove playlist and optionally all songs unique to it."""
        self.log.info("Removing %s Playlist(s) From %s", len(bpl_list), kind)
        local_bpls, bpl_errs = self.get_playlists()
        if bpl_errs:
            err_msg = "Skipping Song Removal" if not keep else None
            self.log_bpl_warn(bpl_errs, err_msg)
            keep = True
        for bpl_ref in bpl_list:
            if kind == "files":
                try:
                    filepath = Path(bpl_ref).resolve()
                    bpl = BsPlaylist.from_json(filepath.read_bytes(), filepath)
                except ModelError as exc:
                    self.log_exc("Can't Construct Playlist", bpl_ref, exc)
                    continue
                except OSError as exc:
                    self.log_exc("Can't Read Playlist File", bpl_ref, exc)
                    continue
            else:
                bpl = self.get_playlist_by_key(bpl_ref)
                if bpl is None:
                    self.log.error("%s: Can't Find Playlist With Key", bpl_ref)
                    continue
            self.log.info("%s: Removing Playlist", bpl)
            try:
                self.remove_playlist(bpl)
            except BeatSaberError as exc:
                self.log_exc("Can't Uninstall Playlist", bpl, exc)
                continue
            if not keep:
                self._remove_lvls_not_in_bpls(
                    bpl_items=bpl.songs,
                    bpl_list=[b for b in local_bpls if b.key != bpl.key]
                )

    def bpl_upgrade(
        self, remove: bool, bpl_list: Optional[List[str]] = None
    ) -> None:
        """Check if playlists are outdated & install latest version."""
        if bpl_list is not None:
            self.log.info("Upgrading %s Playlists", len(bpl_list))
            bpls = []
            for bpl_ref in bpl_list:
                local_bpl = self.get_playlist_by_key(bpl_ref)
                if local_bpl is None:
                    self.log.warning("%s: Can't Find Playlist", bpl_ref)
                    continue
                bpls.append(local_bpl)
        else:
            self.log.info("Upgrading All Playlists")
            bpls, bpl_errs = self.get_playlists()
            if bpl_errs:
                self.log_bpl_warn(bpl_errs)
        for bpl in bpls:
            self.log.info("%s: Upgrading Playlist", bpl)
            try:
                remote_bpl = self.api.get_playlist_from_url(bpl.url)
            except BeatSaverApiError as exc:
                self.log_exc("Can't Check Playlist", bpl, exc)
                continue
            if remote_bpl.checksum == bpl.checksum:
                self.log.warning("%s: Skipping Playlist: Not Outdated", bpl)
                continue
            self.log.info("%s: Installing Playlist", bpl)
            try:
                self.install_playlist(remote_bpl)
            except BeatSaberError as exc:
                self.log_exc("Can't Install Playlist:", bpl, exc)
                continue
            self._install_playlist_songs(remote_bpl)
            if remove:
                self._remove_lvls_not_in_bpls(bpl_items=bpl.songs)

    def lvl_install(self, lvl_list: List[str], kind: str, force: bool) -> None:
        """Install given levels under specified parameters."""
        self.log.info("Installing %s Levels From %s", len(lvl_list), kind)
        for lvl_ref in lvl_list:
            try:
                if kind == "keys":
                    lvl = self.api.get_song_by_key(lvl_ref)
                else:
                    lvl = self.api.get_song_from_url(lvl_ref)
            except BeatSaverApiError as exc:
                self.log_exc("Can't Fetch Level Data", lvl_ref, exc)
                continue
            self.log.info("%s: Installing Level", lvl)
            if not force and self.get_custom_level_by_key(lvl.key) is not None:
                self.log.warning("%s: Level Is Already Installed", lvl)
                continue
            try:
                self.log.info("%s: Downloading Level", lvl)
                lvl_map = self.api.download_map_from_url(lvl)
                self.log.info("%s: Extracting Level Data", lvl)
                self.install_custom_level(lvl_map)
            except BeatSaverApiError as exc:
                self.log_exc("Can't Download Level Data", lvl_ref, exc)
            except BeatSaberError as exc:
                self.log_exc("Can't Extract Level Data", lvl_ref, exc)

    def lvl_list(self, check_bpls: bool) -> None:
        """Print information about all installed custom levels."""
        lvl_list = self.get_custom_levels()
        bpl_list, bpl_errs = self.get_playlists()
        if check_bpls and bpl_errs:
            self.log_bpl_warn(bpl_errs)
        printer = LvlListPrinter(check_bpls)
        for lvl in lvl_list:
            if check_bpls:
                printer.append(
                    lvl,
                    [bpl.title for bpl in bpl_list if bpl.contains_song(lvl)]
                )
            else:
                printer.append(lvl)
        printer.print()

    def lvl_remove(self, lvl_list: List[str], kind: str, force: bool) -> None:
        """Remove a custom level."""
        self.log.info("Removing %s Levels From %s", len(lvl_list), kind)
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            self.log_bpl_warn(bpl_errs)
        for lvl_ref in lvl_list:
            try:
                if kind == "files":
                    lvl_dir = Path(lvl_ref).resolve()
                    if not lvl_dir.is_dir():
                        raise BeatSaberError("directory doesn't exist")
                    lvl = CustomLevel(lvl_dir)
                else:
                    lvl = self.get_custom_level_by_key(lvl_ref)
                    if lvl is None:
                        raise BeatSaberError("level is not installed")
            except BeatSaberError as exc:
                self.log_exc("Can't Locate Level", lvl_ref, exc)
                continue
            self.log.info("%s: Removing Level", lvl)
            if not force and any(bpl.contains_song(lvl) for bpl in bpl_list):
                self.log_lvl_skip(lvl)
                continue
            try:
                self.remove_custom_level(lvl)
            except BeatSaberError as exc:
                self.log_exc("Can't Remove Level", lvl_ref, exc)

    def _install_playlist_songs(self, bpl: BsPlaylist) -> None:
        """Install all songs of given playlist."""
        for lvl in bpl.songs:
            try:
                if self.get_custom_level_by_key(lvl.key) is not None:
                    self.log.info("%s: Level Is Already Installed", lvl)
                    continue
                self.log.info("%s: Starting Download", lvl)
                lvl_data = self.api.get_song_by_key(lvl.key)
                custom_lvl = self.api.download_map_from_url(lvl_data)
                self.log.info("%s: Installing Level", lvl)
                self.install_custom_level(custom_lvl)
            except BeatSaberError as exc:
                self.log_exc("Can't Install Level", lvl, exc)
            except BeatSaverApiError as exc:
                self.log_exc("Can't Download Level", lvl, exc)

    def _remove_lvls_not_in_bpls(
        self, force: bool = False,
        lvl_list: Optional[List[CustomLevel]] = None,
        bpl_items: Optional[List[PlaylistItem]] = None,
        bpl_list: Optional[List[BsPlaylist]] = None
    ) -> None:
        """Remove given levels if they are not in a playlist."""
        if lvl_list is None and bpl_items is not None:
            lvl_list = self._bpl_items_to_lvls(bpl_items)
        elif lvl_list is None and bpl_items is None:
            lvl_list = self.get_custom_levels()
        elif lvl_list is not None and bpl_items is not None:
            lvl_list += self._bpl_items_to_lvls(bpl_items)
        if bpl_list is None:
            bpl_list, bpl_errs = self.get_playlists()
            if bpl_errs:
                self.log_bpl_warn(bpl_errs)
                if not force:
                    self.log.error("Aborting Removal Because It Isn't Forced")
                    return
        for lvl in lvl_list:
            self.log.info("%s: Removing level", lvl)
            if any(bpl.contains_song(lvl) for bpl in bpl_list) and not force:
                self.log_lvl_skip(lvl)
                continue
            try:
                self.remove_custom_level(lvl)
            except BeatSaberError as exc:
                self.log_exc("Can't Remove Level", lvl, exc)

    def _bpl_items_to_lvls(self, bpl: List[PlaylistItem]) -> List[CustomLevel]:
        """Retrieve all playlist levels that are installed locally."""
        lvl_list = []
        for song in bpl:
            self.log.info("%s: Looking For Level", song)
            lvl = self.get_custom_level_by_key(song.key)
            if lvl is None:
                self.log.warning("%s: Can't Locate Level", song)
                continue
            lvl_list.append(lvl)
        return lvl_list

    def log_lvl_skip(self, lvl: CustomLevel) -> None:
        """Log warning that a level in a playlist won't be removed."""
        self.log.warning("%s: Aborting Removal: Found Level in Playlists", lvl)

    def log_bpl_warn(self, err: List[BsInvalidLocal], msg: Any = None) -> None:
        """Log warning for invalid bpls and debug a representation."""
        if msg is not None:
            self.log.warning("%s: Can't Read %s Playlists", msg, len(err))
        else:
            self.log.warning("Can't Read %s Playlists", len(err))
        self.log.debug("%r", err)

    def log_exc(self, msg: str, ident: Any, exc: Any) -> None:
        """Log a message at error and exception info at debug level."""
        self.log.error("%s: %s: %s", ident, msg, exc)
        self.log.debug("Exception(s) That Caused the Above Error:", exc_info=1)
