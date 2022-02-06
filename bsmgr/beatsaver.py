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
from zipfile import BadZipFile, ZipFile

import requests

from .core.exceptions import BeatSaverApiError, ModelError
from .core.models import BsPlaylist, BsMap


class BeatSaverApi:
    """Container for methods interacting with the BeatSaver API."""

    def __init__(self) -> None:
        """Create the API handler."""
        self.base_url = "https://api.beatsaver.com/"

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
            raise BeatSaverApiError("playlist data invalid") from exc

    def get_song_by_key(self, key: str) -> BsMap:
        """Download the metadata of a custom level referenced by key."""
        response = self._get_beatsaver_url(self._format_song_url(key))
        try:
            lvl = BsMap.from_json(response)
            return lvl
        except ModelError as exc:
            raise BeatSaverApiError("custom level data invalid") from exc

    def download_map_from_url(self, bsmap: BsMap) -> BsMap:
        """Download zipped custom level data referenced by url."""
        response = self._get_beatsaver_url(bsmap.url)
        try:
            with BytesIO(response) as content:
                lvl = ZipFile(content)  # pylint: disable=consider-using-with
            return bsmap.add_content(lvl)
        except BadZipFile as exc:
            raise BeatSaverApiError("content is not a valid zipfile") from exc

    def _get_beatsaver_url(self, url: str) -> bytes:
        """Return response content of Beat Saver GET request to url."""
        if not url.startswith(self.base_url):
            raise BeatSaverApiError("invalid beatsaver url", url)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.HTTPError as exc:
            if response.status_code == 404:
                err = "unable to locate song on Beat Saver"
            else:
                err = f"Beat Saver returned status code {response.status_code}"
            raise BeatSaverApiError(err, url) from exc
        except requests.ConnectionError as exc:
            raise BeatSaverApiError("unable to connect to Beat Saver") from exc

    def _format_playlist_url(self, key: str) -> str:
        """Return download url for a playlist referenced by key."""
        return f"{self.base_url}/playlists/id/{key}/download"

    def _format_song_url(self, key: str) -> str:
        """Return download url for a custom level referenced by key."""
        return f"{self.base_url}/maps/id/{key}"


if __name__ == '__main__':
    api = BeatSaverApi()
    playlist = api.get_playlist_by_key(1056)
    # print(repr(playlist))
    # playlist.write_json(".beatsaber")
