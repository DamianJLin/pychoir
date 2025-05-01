from __future__ import annotations
from . import parse_args
import pathlib
import sys
from .manage import build_rolls, mark_rolls, add_chorister, export_programme


def main():

    here = pathlib.Path.cwd()

    attfile = here / 'attendance.csv'
    sectionsdir = here / 'sections'
    rollsdir = here / 'rolls'
    progrfile = here / 'programme.txt'

    config = parse_args.parse_args(sys.argv)
    match config:

        case parse_args.RollConfig():
            build_rolls(
                attfile,
                sectionsdir,
                rollsdir,
                config.rehid,
                config.rehdesc,
                config.messagedir,
            )

        case parse_args.MarkConfig():
            mark_rolls(
                attfile,
                sectionsdir,
                config.rehname,
            )

        case parse_args.AddConfig():
            add_chorister(
                attfile,
                sectionsdir,
                config.chfname,
                config.chlname,
                config.chpart,
            )

        case parse_args.ExportProgrammeConfig():
            export_programme(
                attfile,
                sectionsdir,
                progrfile,
                config.minattendance
            )


if __name__ == '__main__':
    main()
