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

"""Data models for beatsaber-playlist-manager."""

import dataclasses
import json

from pathlib import Path
from typing import Optional, Tuple
from zipfile import ZipFile

from .exceptions import ModelError
from .utils import get_checksum


@dataclasses.dataclass(repr=True)
class Model:
    """Base Class for a data model."""


@dataclasses.dataclass(repr=True)
class BsPlaylistItem(Model):
    """Container for a song in a BeatSaver playlist."""

    key: str
    hash: str
    name: str


@dataclasses.dataclass(repr=True)
class BsPlaylist(Model):
    """Container for playlist data from BeatSaver."""

    checksum: str
    title: str
    author: str
    description: str
    url: str
    songs: Tuple[BsPlaylistItem]
    _json: bytes

    @classmethod
    def from_json(cls, content: bytes):
        """Return instance of class built from json content."""
        try:
            bplist = json.loads(content)
            checksum = get_checksum(content)
            title = bplist["playlistTitle"]
            author = bplist["playlistAuthor"]
            desc = bplist["playlistDescription"]
            url = bplist["customData"]["syncURL"]
            songs = tuple(
                BsPlaylistItem(s["key"], s["hash"], s["songName"])
                for s in bplist["songs"]
            )
            return cls(checksum, title, author, desc, url, songs, content)
        except json.JSONDecodeError as exc:
            raise ModelError("can't parse json data") from exc
        except KeyError as exc:
            raise ModelError("can't read playlist data from json") from exc

    @property
    def song_keys(self) -> Tuple[str]:
        """Return tuple with keys of all songs."""
        return tuple(s.key for s in self.songs)

    def __str__(self) -> str:
        """Return bplist filename for playlist."""
        return f"BeatSaver - {self.title}.bplist"


@dataclasses.dataclass(repr=True)
class BsInvalidLocal(Model):
    """Container for unreadable local Beat Saber playlist or level."""

    path: Path
    exc: Exception


@dataclasses.dataclass(repr=True)
class BsMap(Model):
    """Container for custom map data from BeatSaver."""

    key: str
    name: str
    author: str
    url: str
    content: Optional[ZipFile] = None

    @classmethod
    def from_json(cls, content: bytes):
        """Construct object from JSON."""
        try:
            lvl = json.loads(content)
            key = lvl["id"]
            title = lvl["name"]
            author = lvl["uploader"]["name"]
            url = lvl["downloadURL"]
            return cls(key, title, author, url)
        except json.JSONDecodeError as exc:
            raise ModelError("can't parse json data") from exc
        except KeyError as exc:
            raise ModelError("can't read custom level data from json") from exc

    def add_content(self, content: ZipFile):
        """Return new object with added beatmap data as zipfile."""
        return dataclasses.replace(self, content=content)

    def __str__(self) -> str:
        """Return the map's title made from its key, name and author."""
        return f"{self.key} ({self.name} - {self.author})"


@dataclasses.dataclass(repr=True)
class CustomLevel(Model):
    """Container for locally installed custom level data."""

    directory: Path
    key: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Get custom level key from directory name."""
        self.key = self.directory.name.split(" ")[0]

    def __str__(self) -> str:
        """Return directory name as string representation of level."""
        return self.directory.name
