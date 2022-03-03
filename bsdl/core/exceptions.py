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

"""Custom exceptions for beatsaber-playlist-manager."""


class BeatSaverApiError(Exception):
    """Error during request to BeatSaver API."""


class BeatSaberError(Exception):
    """Error during local custom level and playlist file interaction."""


class ModelError(Exception):
    """Error during construction of a data model."""
