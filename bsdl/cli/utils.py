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

"""Utilities for beatsaber-playlist-manager command line interface."""

import os

from argparse import ArgumentParser, RawDescriptionHelpFormatter, \
    ArgumentTypeError as ArgError, _SubParsersAction as SubParser
from pathlib import Path
from typing import Iterable

from ..core.models import BsPlaylist, CustomLevel
from ..core.utils import LOG_LEVELS


def valid_log_level(level: str) -> str:
    """Raise ArgumentTypeError if levelname is not a valid log level."""
    if level not in (valid_keys := LOG_LEVELS):
        choices = ", ".join(f"'{lvl}'" for lvl in valid_keys)
        msg = f"invalid choice: '{level}' (choose from {choices})"
        raise ArgError(msg)
    return level


def valid_beatsaber_dir(path: str) -> Path:
    """Return absolute path if it points to existing directory."""
    if path == "NOT_SET":
        raise ArgError("BEATSABER environment variable is not set")
    arg_path = Path(path).resolve()
    if not arg_path.is_dir():
        raise ArgError(f"Beat Saber directory '{arg_path}' does not exist.")
    return arg_path


class CommandLineInterface:
    """Namespace for building the command line argument parser."""

    def __init__(self) -> None:
        """Initialize the main parser and add subcommand parsers."""
        self.help_msg = "(use '-h' option for details)"
        self.formatter = RawDescriptionHelpFormatter
        self.epilog = "\n".join((
            "--log-level argument defaults to 'info' and can also be set with",
            "the environment variable $BSDL_LOG_LEVEL", "",
            "--beatsaber argument defaults to environment variable $BEATSABER",
            "If the variable is not set, the argument MUST be provided"
        ))
        self.parser = ArgumentParser(
            prog="bsdl",
            description="manager for custom Beat Saber playlists and levels.",
            epilog=self.epilog,
            formatter_class=self.formatter
        )
        self.parser.add_argument(
            "--beatsaber",
            help="path to directory where Beat Saber is installed",
            default=os.getenv("BEATSABER", "NOT_SET"),
            type=valid_beatsaber_dir,
            metavar="<dir>"
        )
        self.parser.add_argument(
            "--log-level",
            help=f"set the logging level ({', '.join(LOG_LEVELS.keys())})",
            choices=LOG_LEVELS.keys(),
            default=os.getenv("BSDL_LOG_LEVEL", "info"),
            type=valid_log_level,
            metavar="<level>"
        )
        main = self.parser.add_subparsers(
            dest="command", required=True, metavar="<command>"
        )
        bpl = self.add_parser(main, "bpl", "manage Beat Saber playlists")
        self.bpl = bpl.add_subparsers(
            dest="subcommand", required=True, metavar="<command>"
        )
        lvl = self.add_parser(main, "lvl", "manage Beat Saber custom levels")
        self.lvl = lvl.add_subparsers(
            dest="subcommand", required=True, metavar="<command>"
        )

    def add_bpl_cmd(self, cmd: str, msg: str) -> ArgumentParser:
        """Add a subcommand to the 'bpl' command."""
        return self.add_parser(self.bpl, cmd, msg)

    def add_lvl_cmd(self, cmd: str, msg: str) -> ArgumentParser:
        """Add a subcommand to the 'lvl' command."""
        return self.add_parser(self.lvl, cmd, msg)

    def add_parser(
        self, parent: SubParser, cmd: str, msg: str
    ) -> ArgumentParser:
        """Add a parser for the given parent command."""
        return parent.add_parser(
            cmd, epilog=self.epilog, formatter_class=self.formatter,
            help=f"{msg} {self.help_msg}"
        )

    def _bpl_install(self) -> None:
        """Set up 'bpl install' command."""
        bpl = self.add_bpl_cmd(
            "install", "install playlist and download missing songs"
        )
        bpl.add_argument(
            "--keys", action="store_true",
            help="set this to treat all playlist arguments as BeatSaver keys"
        )
        bpl.add_argument(
            "--files", action="store_true",
            help="set this to treat all playlist arguments as filepaths"
        )
        bpl.add_argument(
            "-f", "--force", action="store_true",
            help="set this to force install, overwriting any existing playlist"
        )
        self.add_pos_arg(
            bpl, "playlist",
            "one (or more) BeatSaver url(s) for playlist(s) to be installed"
        )

    def _bpl_list(self) -> None:
        """Set up 'bpl list' command."""
        bpl = self.add_bpl_cmd("list", "list all locally installed playlists")
        bpl.add_argument(
            "--outdated", action="store_true",
            help="set this to only display outdated playlists"
        )

    def _bpl_remove(self) -> None:
        """Set up 'bpl remove' command."""
        bpl = self.add_bpl_cmd(
            "rm", "remove a playlist and all its unique songs"
        )
        bpl.add_argument(
            "--keep-songs", action="store_true",
            help="set this to skip deletion of playlist songs"
        )
        bpl.add_argument(
            "--files", action="store_true",
            help="set this to treat all playlist arguments as filepaths"
        )
        self.add_pos_arg(
            bpl, "playlist",
            "one (or more) BeatSaver playlist keys for playlists to be removed"
        )

    def _bpl_upgrade(self) -> None:
        """Set up 'bpl upgrade' command."""
        bpl = self.add_parser(
            self.bpl, "upgrade",
            "install newer version of all outdated local playlists"
        )
        bpl.add_argument(
            "--remove-songs", action="store_true",
            help="set this to remove songs that were unique to playlists"
        )
        bpl.add_argument(
            "--bpl", help="only upgrade the local playlists with these keys",
            nargs="+", metavar="<key>", dest="playlist"
        )

    def _lvl_install(self) -> None:
        """Set up 'lvl install' command."""
        lvl = self.add_lvl_cmd("install", "install a custom level locally")
        lvl.add_argument(
            "--keys", action="store_true",
            help="set this to treat all level arguments as BeatSaver keys"
        )
        lvl.add_argument(
            "-f", "--force", action="store_true",
            help="set this to force install, overwriting any existing level"
        )
        self.add_pos_arg(
            lvl, "level",
            "one (or more) BeatSaver url(s) for level(s) to be installed"
        )

    def _lvl_list(self) -> None:
        """Set up 'lvl list' command."""
        lvl = self.add_lvl_cmd("list", "list all installed custom levels")
        lvl.add_argument(
            "--check-playlists", action="store_true",
            help="set this to check whether each song is in a playlist"
        )

    def _lvl_remove(self) -> None:
        """Set up 'lvl remove' command."""
        lvl = self.add_lvl_cmd("rm", "remove a custom level not in a playlist")
        lvl.add_argument(
            "-f", "--force", action="store_true",
            help="forces deletion of all given levels even if in a playlist"
        )
        lvl.add_argument(
            "--files", action="store_true",
            help="set this to treat all level arguments as directory paths"
        )
        self.add_pos_arg(
            lvl, "level",
            "one (or more) BeatSaver key for custom level to be removed"
        )

    def _bpl_lvl_sync(self) -> None:
        """Set up 'bpl sync' and 'lvl sync' commands."""
        for subparser, other in ((self.bpl, "lvl"), (self.lvl, "bpl")):
            sync = self.add_parser(subparser, "sync", (
                "list all installed custom levels not in a playlist "
                f"(behaves like '{other} sync')"
            ))
            sync.add_argument(
                "--remove", action="store_true",
                help="set this to remove all songs not in a playlist"
            )

    @staticmethod
    def add_pos_arg(parent: ArgumentParser, cmd: str, msg: str) -> None:
        """Add an argument with '+' nargs to given parser."""
        parent.add_argument(cmd, nargs="+", help=msg)

    @classmethod
    def setup(cls) -> ArgumentParser:
        """Return parser object after setting up all subcommands."""
        cli = cls()
        cli._bpl_install()
        cli._bpl_list()
        cli._bpl_remove()
        cli._bpl_upgrade()
        cli._lvl_install()
        cli._lvl_list()
        cli._lvl_remove()
        cli._bpl_lvl_sync()
        return cli.parser


class TablePrinter:
    """Base class for printing a list as a table."""

    def __init__(self) -> None:
        """Create the Printer."""
        self.col_title = "TITLE"
        self.col_key = "KEY"
        self.table_row = ""
        self.printing_table = []
        self.default_len = len(self.printing_table)

    def print(self) -> None:
        """Print all rows of printing table."""
        if len(self.printing_table) == self.default_len:
            return
        print("\n" + "\n".join(self.printing_table))

    def add_row(self, row: str) -> None:
        """Append a row to the printing table."""
        self.printing_table.append(row)


class LvlListPrinter(TablePrinter):
    """Container for collecting and printing installed custom levels."""

    def __init__(self, check_bpls: bool) -> None:
        """Create the printer with or without playlist column."""
        self.bpl_check = check_bpls
        self.col_playlists = "PLAYLISTS"
        super().__init__()
        self._init_printing_table()

    def append(self, lvl: CustomLevel, bpls: Iterable[str] = ()) -> None:
        """Append a table row for a custom level the printing table."""
        if self.bpl_check:
            self._add_bpl_row(lvl.key, lvl.name, ", ".join(bpls))
        else:
            self._add_lvl_row(lvl.key, lvl.name)

    def _init_printing_table(self) -> None:
        """Format table row and add head of printing table."""
        if self.bpl_check:
            self.table_row = "| {:6} | {:80} | {:24} |"
            self._add_bpl_row(self.col_key, self.col_title, self.col_playlists)
            self._add_bpl_row("-" * 6, "-" * 80, "-" * 24)
        else:
            self.table_row = "| {:6} | {:107} |"
            self._add_lvl_row(self.col_key, self.col_title)
            self._add_lvl_row("-" * 6, "-" * 107)
        self.default_len = len(self.printing_table)

    def _add_bpl_row(self, key: str, title: str, playlists: str) -> None:
        """Append a row with playlist column to printing table."""
        self.add_row(self.table_row.format(key, title, playlists))

    def _add_lvl_row(self, key: str, title: str) -> None:
        """Append a row without playlist column to printing table."""
        self.add_row(self.table_row.format(key, title))


class BplListPrinter(TablePrinter):
    """Container for collecting and printing installed playlists."""

    def __init__(self, outdated: bool) -> None:
        """Create printer with or without outdated column."""
        self.outdated = outdated
        self.col_old = "OUTDATED"
        super().__init__()
        self._init_printing_table()

    def append(self, bpl: BsPlaylist, outdated: bool = False) -> None:
        """Append row for a playlist to printing table."""
        if self.outdated:
            self._add_outdated_row(bpl.key, bpl.title, "x" if outdated else "")
        else:
            self._add_standard_row(bpl.key, bpl.title)

    def _init_printing_table(self) -> None:
        """Format table row and add head of printing table."""
        if self.outdated:
            self.table_row = "| {:4} | {:98} | {:^8} |"
            self._add_outdated_row(self.col_key, self.col_title, self.col_old)
            self._add_outdated_row("-" * 4, "-" * 98, "-" * 8)
        else:
            self.table_row = "| {:4} | {:109} |"
            self._add_standard_row(self.col_key, self.col_title)
            self._add_standard_row("-" * 4, "-" * 109)
        self.default_len = len(self.printing_table)

    def _add_outdated_row(self, key: str, name: str, outdated: str) -> None:
        """Append a row with outdated column to printing table."""
        self.add_row(self.table_row.format(key, name, outdated))

    def _add_standard_row(self, key: str, name: str) -> None:
        """Append a row without outdated column to printing table."""
        self.add_row(self.table_row.format(key, name))
