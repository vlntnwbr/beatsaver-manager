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
from .utils import get_checksum, get_windows_filename


@dataclasses.dataclass(repr=True)
class Model:
    """Base Class for a data model."""


@dataclasses.dataclass(repr=True)
class CustomLevel(Model):
    """Container for locally installed custom level data."""

    directory: Path
    name: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Set key and title attribute derived from level directory."""
        self.key, name = self.directory.name.split(" ", 1)
        self.name = name[1:-1]

    def __str__(self) -> str:
        """Return directory name as string representation of level."""
        return self.name


@dataclasses.dataclass(repr=True)
class PlaylistItem(Model):
    """Container for a song in a BeatSaver playlist."""

    key: str
    hash: str
    name: str

    def __str__(self) -> str:
        """Return name of song."""
        return self.name


@dataclasses.dataclass(repr=True)
class BsPlaylist(Model):  # pylint: disable=too-many-instance-attributes
    """Container for playlist data from BeatSaver."""

    checksum: str
    title: str
    author: str
    description: str
    url: str
    songs: Tuple[PlaylistItem]
    json_raw: bytes
    filepath: Optional[Path] = None
    key: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Set key attribute parsed from playlist url."""
        self.key = self.url.rsplit("/", 2)[-2]

    @classmethod
    def from_json(cls, raw: bytes, filepath: Optional[Path] = None):
        """Return instance of class built from json content."""
        try:
            bplist = json.loads(raw)
            checksum = get_checksum(raw)
            title = bplist["playlistTitle"]
            author = bplist["playlistAuthor"]
            desc = bplist["playlistDescription"]
            url = bplist["customData"]["syncURL"]
            lvls = tuple(
                PlaylistItem(s["key"], s["hash"], s["songName"])
                for s in bplist["songs"]
            )
            return cls(checksum, title, author, desc, url, lvls, raw, filepath)
        except json.JSONDecodeError as exc:
            raise ModelError("can't parse json data") from exc
        except KeyError as exc:
            raise ModelError("can't read playlist data from json") from exc

    @property
    def song_keys(self) -> Tuple[str]:
        """Return tuple with keys of all songs."""
        return tuple(s.key for s in self.songs)

    @property
    def filename(self) -> str:
        """Return filename from filepath or construct it using key."""
        if self.filepath is not None:
            return self.filepath.name  # pylint: disable=no-member
        return get_windows_filename(f"beatsaver-{self.key}.bplist")

    def __str__(self) -> str:
        """Return title of playlist."""
        return self.title

    def contains_song(self, song: CustomLevel) -> bool:
        """Return true if playlist contains given song."""
        return song.key in self.song_keys


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
            url = lvl["versions"][-1]["downloadURL"]
            return cls(key, title, author, url)
        except json.JSONDecodeError as exc:
            raise ModelError("can't parse json data") from exc
        except KeyError as exc:
            raise ModelError("can't read custom level data from json") from exc

    def add_content(self, content: ZipFile):
        """Return new object with added beatmap data as zipfile."""
        return dataclasses.replace(self, content=content)

    @property
    def directory(self) -> Path:
        """Return the map's relative directory path as: 'key (name)'."""
        return Path(get_windows_filename(f"{self.key} ({self.name})"))

    def __str__(self) -> str:
        """Return the name of the map."""
        return self.name
