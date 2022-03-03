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
from typing import List, Optional

from ..core.exceptions import BeatSaberError, BeatSaverApiError, ModelError
from ..core.models import BsPlaylist, PlaylistItem, CustomLevel
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
        self.log.info("retrieving levels that are not part of any playlist")
        lvl_list = self.get_custom_levels()
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            err = "unable to read %s playlists"
            if remove:
                remove = False
                err = "skipping removal: " + err
            self.log.warning(err, len(bpl_errs))
            self.log.debug("%r", bpl_errs)
        for lvl in lvl_list:
            if any(bpl.contains_song(lvl) for bpl in bpl_list):
                continue
            self.log.info("found %s", lvl.title)
            if remove:
                try:
                    self.remove_custom_level(lvl)
                    self.log.info("removed level")
                except BeatSaberError as exc:
                    self.log.error("unable to remove custom level %s", lvl)
                    self.log.debug("%s", exc, exc_info=1)

    def bpl_install(self, bpl_list: List[str], kind: str, force: bool) -> None:
        """Install given playlists under specified parameters."""
        self.log.info("installing %s playlist(s) from %s", len(bpl_list), kind)
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
                    self.log.warning("found existing playlist: %s", bpl)
                    continue
                self.log.info("installing playlist: %s", bpl)
                self.install_playlist(bpl)
                self._install_playlist_songs(bpl)
            except BeatSaberError as exc:
                self.log.debug("%s", exc, exc_info=1)
            except BeatSaverApiError as exc:
                self.log.debug("%s", exc, exc_info=1)
            except ModelError as exc:
                self.log.debug("%s", exc, exc_info=1)
            except OSError as exc:
                self.log.debug("%s", exc, exc_info=1)

    def bpl_list(self, outdated: bool) -> None:
        """Print information about all installed playlists."""
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            self.log.warning("unable to read %s playlists", len(bpl_errs))
            self.log.debug("%r", bpl_errs)
        printer = BplListPrinter(outdated)
        for bpl in bpl_list:
            if outdated:
                try:
                    remote_bpl = self.api.get_playlist_by_key(bpl.key)
                    is_outdated = remote_bpl.checksum != bpl.checksum
                    printer.append(bpl, is_outdated)
                    continue
                except BeatSaverApiError as exc:
                    self.log.error("can't fetch %s from Beat Saver", bpl)
                    self.log.debug("%r", exc, exc_info=1)
            printer.append(bpl)
        printer.print()

    def bpl_remove(self, bpl_list: List[str], kind: str, keep: bool) -> None:
        """Remove playlist and optionally all songs unique to it."""
        self.log.info("removing %s playlist(s) from %s", len(bpl_list), kind)
        local_bpls, bpl_errs = self.get_playlists()
        if bpl_errs:
            keep = True
            self.log.warning(
                "unable to check %s playlists. Songs won't be removed.",
                len(bpl_errs)
            )
            self.log.debug("%r", bpl_errs)
        for bpl_ref in bpl_list:
            if kind == "files":
                try:
                    filepath = Path(bpl_ref).resolve()
                    bpl = BsPlaylist.from_json(filepath.read_bytes(), filepath)
                except (OSError, ModelError) as exc:
                    self.log.error("unable to read playlist %s", bpl_ref)
                    self.log.debug("%r", exc, exc_info=1)
                    continue
            else:
                bpl = self.get_playlist_by_key(bpl_ref)
                if bpl is None:
                    self.log.error("can't find playlist with key: %s", bpl_ref)
                    continue
            self.log.info("removing playlist %s", bpl)
            try:
                self.remove_playlist(bpl)
            except BeatSaberError as exc:
                self.log.error("cannot uninstall playlist %s", bpl)
                self.log.debug("%r", exc, exc_info=1)
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
            self.log.info("upgrading %s playlists", len(bpl_list))
            bpls = []
            for bpl_ref in bpls:
                local_bpl = self.get_playlist_by_key(bpl_ref)
                if local_bpl is None:
                    self.log.warning("unable to find playlist %s", bpl_ref)
                    continue
                bpls.append(local_bpl)
        else:
            self.log.info("upgrading all playlists")
            bpls, bpl_errs = self.get_playlists()
            if bpl_errs:
                self.log.warning("unable to read %s playlists", len(bpl_errs))
                self.log.debug("%r", bpl_errs)
        for bpl in bpls:
            self.log.info("upgrading playlist: %s", bpl)
            try:
                remote_bpl = self.api.get_playlist_from_url(bpl.url)
            except BeatSaverApiError as exc:
                self.log.error("cannot check playlist: %s", exc.args[0])
                self.log.debug("%r", exc, exc_info=1)
                continue
            if remote_bpl.checksum == bpl.checksum:
                self.log.warning("skipping playlist: it is already up to date")
                continue
            self.log.info("installing playlist")
            try:
                self.install_playlist(remote_bpl)
            except BeatSaberError as exc:
                self.log.error("unable to install playlist")
                self.log.debug("%r", exc, exc_info=1)
                continue
            self._install_playlist_songs(remote_bpl)
            if remove:
                self._remove_lvls_not_in_bpls(bpl_items=bpl.songs)

    def lvl_install(self, lvl_list: List[str], kind: str, force: bool) -> None:
        """Install given levels under specified parameters."""
        self.log.info("installing %s levels from %s", len(lvl_list), kind)
        for lvl_ref in lvl_list:
            try:
                if kind == "keys":
                    lvl = self.api.get_song_by_key(lvl_ref)
                else:
                    lvl = self.api.get_song_from_url(lvl_ref)
            except BeatSaverApiError as exc:
                self.log.error("unable to fetch level data: %s", exc.args[0])
                self.log.debug("%r", exc, exc_info=1)
                continue
            self.log.info("installing level: %s", lvl.name)
            if not force and self.get_custom_level_by_key(lvl.key) is not None:
                self.log.warning("custom level is already installed")
                continue
            try:
                self.log.info("downloading level")
                lvl_map = self.api.download_map_from_url(lvl)
                self.log.info("extracting level data")
                self.install_custom_level(lvl_map)
            except BeatSaverApiError as exc:
                self.log.error("unable to download map data: %s", exc.args[0])
                self.log.debug("%r", exc, exc_info=1)
            except BeatSaberError as exc:
                self.log.error("unable to extract level data: %s", exc.args[0])
                self.log.debug("%r", exc, exc_info=1)

    def lvl_list(self, check_bpls: bool) -> None:
        """Print information about all installed custom levels."""
        lvl_list = self.get_custom_levels()
        bpl_list, bpl_errs = self.get_playlists()
        if check_bpls and bpl_errs:
            self.log.warning("unable to read %s playlists", len(bpl_errs))
            self.log.debug("%r", bpl_errs)
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
        self.log.info("removing %s levels from %s", len(lvl_list), kind)
        bpl_list, bpl_errs = self.get_playlists()
        if bpl_errs:
            self.log.warning("unable to check %s playlists.")
        for lvl_ref in lvl_list:
            try:
                if kind == "files":
                    lvl_dir = Path(lvl_ref).resolve()
                    if not lvl_dir.is_dir():
                        raise BeatSaberError
                    lvl = CustomLevel(lvl_dir)
                else:
                    lvl = self.get_custom_level_by_key(lvl_ref)
                    if lvl is None:
                        raise BeatSaberError
            except BeatSaberError:
                self.log.error("unable to locate level %s", lvl_ref)
                continue
            self.log.info("trying to remove level %s", lvl.title)
            if not force and any(bpl.contains_song(lvl) for bpl in bpl_list):
                self.log.warning("skipping level because it is in playlist(s)")
                continue
            try:
                self.remove_custom_level(lvl)
            except BeatSaberError as exc:
                self.log.error("unable to remove custom level")
                self.log.debug("%r", exc, exc_info=1)

    def _install_playlist_songs(self, bpl: BsPlaylist) -> None:
        """Install all songs of given playlist."""
        for lvl in bpl.songs:
            try:
                self.log.info("%s", lvl)
                if self.get_custom_level_by_key(lvl.key) is not None:
                    self.log.info("level already installed")
                    continue
                self.log.info("level not installed. starting download")
                lvl_data = self.api.get_song_by_key(lvl.key)
                custom_lvl = self.api.download_map_from_url(lvl_data)
                self.log.info("installing level")
                self.install_custom_level(custom_lvl)
            except BeatSaberError as exc:
                self.log.error("can't install level: %s", exc)
                self.log.debug("%s", exc, exc_info=1)
            except BeatSaverApiError as exc:
                self.log.error("can't download level: %s", exc)
                self.log.debug("%s", exc, exc_info=1)

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
                self.log.error(
                    "skipping removal: can't read %s playlists", len(bpl_errs)
                )
                self.log.debug("%r", bpl_errs)
                if not force:
                    return
        for lvl in lvl_list:
            self.log.info("removing level %s", lvl.title)
            if any(bpl.contains_song(lvl) for bpl in bpl_list) and not force:
                self.log.warning("skipping removal: found lvl in playlists")
                continue
            self.log.info("removing level")
            try:
                self.remove_custom_level(lvl)
            except BeatSaberError as exc:
                self.log.error("unable to remove level")
                self.log.debug("%r", exc, exc_info=1)

    def _bpl_items_to_lvls(self, bpl: List[PlaylistItem]) -> List[CustomLevel]:
        """Retrieve all playlist levels that are installed locally."""
        lvl_list = []
        for song in bpl:
            self.log.info("looking for level: %s", song)
            lvl = self.get_custom_level_by_key(song.key)
            if lvl is None:
                self.log.warning("unable to find level: %s", song)
                continue
            lvl_list.append(lvl)
        return lvl_list
