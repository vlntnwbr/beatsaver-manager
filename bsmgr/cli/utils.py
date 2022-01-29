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
    _SubParsersAction as SubParser
from pathlib import Path


class CommandLineInterface:
    """Namespace for building the command line argument parser."""

    def __init__(self) -> None:
        """Initialize the main parser and add subcommand parsers."""
        self.help_msg = "(use '-h' option for details)"
        self.formatter = RawDescriptionHelpFormatter
        self.epilog = "\n".join((
            "--beatsaber argument defaults to environment variable $BEATSABER",
            "If the variable is not set, the argument MUST be provided"
        ))
        self.parser = ArgumentParser(
            prog="bsmgr",
            description="manager for custom Beat Saber playlists and levels.",
            epilog=self.epilog,
            formatter_class=self.formatter
        )
        self.parser.add_argument(
            "--beatsaber",
            help="path to directory where Beat Saber is installed",
            default=os.getenv("BEATSABER"),
            type=Path,
            metavar="PATH"
        )
        main = self.parser.add_subparsers(
            dest="command", required=True, metavar="COMMAND"
        )
        bpl = self.add_parser(main, "bpl", "manage Beat Saber playlists")
        self.bpl = bpl.add_subparsers(
            dest="subcommand", required=True, metavar="COMMAND"
        )
        lvl = self.add_parser(main, "lvl", "manage Beat Saber custom levels")
        self.lvl = lvl.add_subparsers(
            dest="subcommand", required=True, metavar="COMMAND"
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
            help="set this to treat all playlist arguments as beatsaver keys"
        )
        bpl.add_argument(
            "--files", action="store_true",
            help="set this to treat all playlist arguments as paths to files"
        )
        self.add_pos_arg(
            bpl, "playlist",
            "one (or more) beatsaver url(s) for playlist(s) to be installed"
        )

    def _bpl_list(self) -> None:
        """Set up 'bpl list' command."""
        bpl = self.add_bpl_cmd("list", "list all locally installed playlists")
        bpl.add_argument(
            "--outdated", action="store_true",
            help="set this to only display outdated playlists"
        )
        bpl.add_argument(
            "--detail", action="store_true",
            help="set this to display playlists in a detailed table"
        )

    def _bpl_remove(self) -> None:  # TODO
        """Set up 'bpl remove' command."""
        bpl = self.add_bpl_cmd(
            "rm", "remove a playlist and all its unique songs"
        )
        bpl.add_argument(
            "--keep-songs", action="store_true",
            help="set this to skip deletion of playlist songs"
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

    def _lvl_install(self) -> None:
        """Set up 'lvl install' command."""
        lvl = self.add_lvl_cmd("install", "install a custom level locally")
        lvl.add_argument(
            "--keys", action="store_true",
            help="set this to treat all level arguments as BeatSaver keys"
        )
        lvl.add_argument(
            "--files", action="store_true",
            help="set this to treat all level arguments as paths to zip files"
        )
        self.add_pos_arg(
            lvl, "level",
            "one (or more) beatsaver url(s) for level(s) to be installed"
        )

    def _lvl_list(self) -> None:
        """Set up 'lvl list' command."""
        lvl = self.add_lvl_cmd("list", "list all installed custom levels")
        lvl.add_argument(
            "--check-playlists", action="store_true",
            help="set this to check whether each song is in a playlist"
        )

    def _lvl_remove(self) -> None:  # TODO
        """Set up 'lvl remove' command."""
        lvl = self.add_lvl_cmd("rm", "remove a custom level not in a playlist")
        lvl.add_argument(
            "-f", "--force", action="store_true",
            help="forces deletion of all given levels even if in a playlist"
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
        """Return parser object after adding all subcommands."""
        cli = cls()
        cli._bpl_install()
        cli._bpl_list()
        # cli._bpl_remove()  # TODO
        cli._bpl_upgrade()
        cli._lvl_install()
        cli._lvl_list()
        # cli._lvl_remove()  # TODO
        cli._bpl_lvl_sync()
        return cli.parser


if __name__ == '__main__':
    parser = CommandLineInterface.setup()
    args = parser.parse_args()
    print(args)