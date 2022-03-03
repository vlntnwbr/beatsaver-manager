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

"""Utilities for beatsaber-playlist-manager."""

import hashlib
import logging

LOG_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }


def get_checksum(content: bytes) -> str:
    """Return sha256 checksum hex of given content."""
    sha_hash = hashlib.sha256(content)
    return sha_hash.hexdigest()


def get_file_checksum(filename: str) -> str:
    """Return sha256 checksum of given file content."""
    with open(filename, "rb") as hash_file:
        content = hash_file.read()
    return get_checksum(content)


def setup_logging(level: str) -> None:
    """Set up logging stream handler with given level."""
    logging.basicConfig(
        format="%(name)s | %(levelname)-8s |  %(message)s",
        level=LOG_LEVELS[level.lower()]
    )


if __name__ == '__main__':
    setup_logging("DEBUG")
    loggers = (
        "bpl-install", "bpl-list", "bpl-remove", "bpl-sync", "bpl-upgrade",
        "lvl-install", "lvl-list", "lvl-remove", "lvl-sync"
    )
    for logname in loggers:
        log = logging.getLogger(logname)
        log.debug("Hello There")
        log.info("General Kenobi")
        log.warning("You Are a Bold One")
        log.error("Kill Him")
        log.critical("Back away! I will deal with this Jedi slime myself")
