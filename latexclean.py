#!/usr/bin/env python3

"""
Clean LaTeX build files with the option of doing so recursively.
Asks before removing files.
https://gist.github.com/klieret/b3e032095d78269c811f4f8c85f6227b
Kilian Lieret 2020
MIT license
No warranty
"""

import argparse
from pathlib import Path, PurePath
import re
from typing import Iterable, List, Union
import os


latex_aux_extensions = [
    "aux",
    "bbl",
    "blg",
    "brf",
    "idx",
    "ilg",
    "ind",
    "lof",
    "log",
    "lol",
    "lot",
    "out",
    "toc",
    "synctex.gz",
    "nav",
    "snm",
    "vrb",
    "pyg",
    "bfc",
    "fls",
    "glo",
    "ist",
    "run.xml",
    "bcf",
    "fdb_latexmk",
    "glg",
    "gls",
    "tdo"
]


def yn_prompt(question: str, yes=None, no=None) -> bool:
    """Ask yes-no question.
    Args:
        question: Description of the prompt
        yes: List of strings interpreted as yes
        no: List of strings interpreted as no
    Returns:
        True if yes, False if no.
    """
    if yes is None:
        yes = ["yes", "ye", "y"]
    if no is None:
        no = ["no", "n"]

    prompt = question
    if not prompt.endswith(" "):
        prompt += " "
    prompt += "[{} or {}] ".format("/".join(yes), "/".join(no))

    print(prompt, end="")

    while True:
        choice = input().lower().strip()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print(
                "Please respond with '{}' or '{}': ".format(
                    "/".join(yes), "/".join(no)
                ),
                end="",
            )


def build_file_ext_regex(extensions: Iterable[str]):
    """ Regular expression that matches file names of any extension.
    Args:
        extensions: List of extensions without leading '.'
    Returns:
        Compiled regular expression
    """
    return re.compile(".*\\.(" + "|".join(extensions) + ")")


def get_files_with_extension(
        working_dir: Union[str, PurePath], extensions: Iterable[str], recursive=False
) -> List[Path]:
    """ Get all files with extension in directory.
    '.git' directories are ignored.
    Args:
        working_dir: directory
        extensions:
    Returns:
        list of Path objects with the matches
    """
    regex = build_file_ext_regex(extensions)
    if not recursive:
        return [
            path for path in Path(working_dir).iterdir()
            if regex.match(path.name)
        ]
    else:
        matches = []
        for root, dirs, files in os.walk(str(working_dir)):
            # Remove .git directories, because they contain .idx files
            dirs[:] = [d for d in dirs if d not in [".git"]]
            matches += [Path(root) / file for file in files if regex.match(file)]
        return matches


def ask_remove(files: List[Union[str, PurePath]], stream=print) -> None:
    """ Ask whether to remove files and then do it
    Args:
        files: List of files as paths or string
        stream: alternative print function (e.g. for logging)
    Returns:
        None
    """
    if not files:
        stream("No files to remove.")
        return
    stream("The following files will be removed:")
    for file in files:
        stream("* " + str(file))
    if yn_prompt("Remove?"):
        for file in files:
            os.remove(str(file))
    else:
        stream("Abort.")


def cli() -> None:
    """ Command line interface
    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        "latexclean",
        description=__file__.__doc__
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="Remove files recursively",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Do not prompt before removing files.",
        action="store_true",
        default=False
    )
    args = parser.parse_args()
    files = get_files_with_extension(Path("."), latex_aux_extensions, recursive=args.recursive)
    if not args.force:
        ask_remove(files)
    else:
        for file in files:
            os.remove(str(file))


if __name__ == "__main__":
    cli()