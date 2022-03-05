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

"""Main entry point for beatsaber-playlist-manager."""

from .cmd import CliCommands
from .utils import CommandLineInterface
from ..core.exceptions import BeatSaberError
from ..core.utils import get_logger


def main() -> None:
    """Parse command line arguments and delegate to command function."""
    cli = CommandLineInterface.setup()
    args = cli.parse_args()
    command, action = args.command, args.subcommand
    logger = get_logger(f"{command}-{action}", args.log_level)
    logger.debug("BEATSABER_DIRECTORY: %s", args.beatsaber)
    try:
        cmd = CliCommands(args.beatsaber, logger)
    except BeatSaberError as exc:
        logger.error("Can't Create Beat Saber Subdirectory: %s", exc)
        logger.debug("%r", exc, exc_info=1)
        return
    if action == "sync":
        cmd.bpl_lvl_sync(args.remove)
    elif command == "bpl":
        if action == "install":
            if args.keys and args.files:
                cli.error("can't set --keys and --files together")
            kind = "keys" if args.keys else "files" if args.files else "urls"
            cmd.bpl_install(args.playlist, kind, args.force)
        elif action == "list":
            cmd.bpl_list(args.outdated)
        elif action == "rm":
            kind = "files" if args.files else "keys"
            cmd.bpl_remove(args.playlist, kind, args.keep_songs)
        elif action == "upgrade":
            cmd.bpl_upgrade(args.remove_songs, args.playlist)
    elif command == "lvl":
        if action == "install":
            kind = "keys" if args.keys else "urls"
            cmd.lvl_install(args.level, kind, args.force)
        elif action == "list":
            cmd.lvl_list(args.check_playlists)
        elif action == "rm":
            kind = "files" if args.files else "keys"
            cmd.lvl_remove(args.level, kind, args.force)


if __name__ == '__main__':
    main()
