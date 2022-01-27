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

"""Setup script."""

import subprocess  # nosec

from pathlib import Path
from typing import List

from setuptools import find_packages, setup

PROG = "beatsaver-manager"
DESC = ""
VERSION = "0.0.1"
GITHUB = "https://github.com/vlntnwbr/beatsaver-manager"

HEREDIR = Path(__file__).resolve().parent
REQUIREMENTS_TXT = HEREDIR.joinpath("requirements.txt")
PIPFILE_LOCK = HEREDIR.joinpath("Pipfile.lock")
README_MD = HEREDIR.joinpath("README.md")


def execute_command(args: List[str]) -> List[str]:
    """Execute external command and return stdout as list of strings."""
    try:
        process = subprocess.run(  # nosec
            args,
            capture_output=True,
            check=True,
            text=True
        )
        return [line.strip() for line in process.stdout.splitlines()]
    except subprocess.CalledProcessError:
        return []


def create_requirements_txt() -> None:
    """Create file 'requirements.txt' from 'Pipfile.lock'."""
    if not PIPFILE_LOCK.is_file():
        return
    pipenv_lines = execute_command(["pipenv", "lock", "-r"])
    if not pipenv_lines:
        return
    lines = [line for line in pipenv_lines[1:] if line]
    with REQUIREMENTS_TXT.open("w", encoding="utf-8") as req_file:
        req_file.write("### DO NOT EDIT! This file was generated.\n")
        req_file.write("\n".join(lines))
        req_file.write("\n")


def read_requirements() -> List[str]:
    """Read lines of requirements.txt and return them as list."""
    with REQUIREMENTS_TXT.open("r", encoding="utf-8") as file:
        return [
            line.strip() for line in file.readlines()
            if line and not line.startswith("#") and not line.startswith("-i")
        ]


if __name__ == '__main__':
    create_requirements_txt()
    REQUIREMENTS = read_requirements()
    README = README_MD.read_text(encoding="utf-8")
    setup(
        name=PROG,
        description=DESC,
        long_description=README_MD,
        long_description_content_type="text/markdown",
        version=VERSION,
        packages=find_packages(),
        include_package_data=True,
        install_requires=REQUIREMENTS,
        license="EUPL",
        url=GITHUB,
        author="Valentin Weber",
        author_email="dev@vweber.eu"
    )
