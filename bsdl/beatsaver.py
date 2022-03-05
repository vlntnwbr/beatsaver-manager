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

"""Beatsaver API functionality for beatsaber-playlist-manager."""

from io import BytesIO
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

import requests

from .core.exceptions import BeatSaverApiError, ModelError
from .core.models import BsPlaylist, BsMap


class BeatSaverApi:
    """Container for methods interacting with the BeatSaver API."""

    def __init__(self) -> None:
        """Create the API handler."""
        self.base_url = "https://api.beatsaver.com/"
        self.valid_netlocs = (
            "beatsaver.com",
            "api.beatsaver.com",
            "eu.cdn.beatsaver.com"
        )

    def get_playlist_by_key(self, key: str) -> BsPlaylist:
        """Download a playlist referenced by key."""
        return self.get_playlist_from_url(self._format_playlist_url(key))

    def get_playlist_from_url(self, url: str) -> BsPlaylist:
        """Download a playlist referenced by url."""
        response = self._get_beatsaver_url(url)
        try:
            bplist = BsPlaylist.from_json(response)
            return bplist
        except ModelError as exc:
            raise BeatSaverApiError(f"playlist data invalid: {exc}") from exc

    def get_song_by_key(self, key: str) -> BsMap:
        """Download the metadata of a custom level referenced by key."""
        return self.get_song_from_url(self._format_song_url(key))

    def get_song_from_url(self, url: str) -> BsMap:
        """Download the metadata of a custom level referenced by url."""
        response = self._get_beatsaver_url(url)
        try:
            lvl = BsMap.from_json(response)
            return lvl
        except ModelError as exc:
            raise BeatSaverApiError(f"level data invalid: {exc}") from exc

    def download_map_from_url(self, bsmap: BsMap) -> BsMap:
        """Download zipped custom level data referenced by url."""
        response = self._get_beatsaver_url(bsmap.url)
        try:
            return bsmap.add_content(ZipFile(BytesIO(response)))
        except BadZipFile as exc:
            raise BeatSaverApiError("level data is not a valid zip") from exc

    def _get_beatsaver_url(self, url: str) -> bytes:
        """Return response content of Beat Saver GET request to url."""
        url = self.get_valid_beatsaber_url(url)
        try:
            bsr = requests.get(url)
            bsr.raise_for_status()
            return bsr.content
        except requests.RequestException as exc:
            if isinstance(exc, requests.HTTPError) and bsr.status_code == 404:
                err = "can't find item on BeatSaver: "
            elif isinstance(exc, requests.HTTPError):
                err = "invalid response from BeatSaver: "
            elif isinstance(exc, requests.Timeout):
                err = "connection to BeatSaver timed out: "
            elif isinstance(exc, requests.ConnectionError):
                err = "can't connect to BeatSaver: "
            else:
                err = "an unexpected error occurred connecting to BeatSaver: "
            raise BeatSaverApiError(err + url) from exc

    def _format_playlist_url(self, key: str) -> str:
        """Return download url for a playlist referenced by key."""
        return f"{self.base_url}/playlists/id/{key}/download"

    def _format_song_url(self, key: str) -> str:
        """Return download url for a custom level referenced by key."""
        return f"{self.base_url}/maps/id/{key}"

    def get_valid_beatsaber_url(self, url: str) -> str:
        """Check url for valid BeatSaver netloc and return API url."""
        split_url = urlsplit(url)
        if split_url.netloc in self.valid_netlocs[1:]:
            return url
        if split_url.netloc == self.valid_netlocs[0]:
            err_msg = "invalid BeatSaver url path: " + url
            try:
                kind, key = split_url.path[1:].split("/")
                if kind == "maps":
                    return self._format_song_url(key)
                if kind == "playlists":
                    return self._format_playlist_url(key)
                raise BeatSaverApiError(err_msg)
            except ValueError as exc:
                raise BeatSaverApiError(err_msg) from exc
        raise BeatSaverApiError("url does not point to BeatSaver: " + url)
