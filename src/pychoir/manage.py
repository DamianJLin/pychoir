import polars as pl
import random
import os
import readchar
from pdfme import build_pdf
from .build_roll import generate_section_roll

alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def build_rolls(
    attfile,
    sectionsdir,
    rollsdir,
    rehid,
    rehdesc,
    messagedir,
):
    if messagedir is None:
        # TODO: Dont use attfile.parent?
        here = attfile.parent
        prefix = ''.join(random.choices(alphabet, k=6))
        name = prefix + '_message'
        tempfile = here / name
        systemreturn = os.system("$VISUAL " + str(tempfile))
        if not (systemreturn == 0 and tempfile.is_file()):
            # TODO: Work on error message.
            raise ValueError("Error with opening file. Aborting.")
        with open(tempfile, 'r') as fobj:
            message = fobj.read()
        tempfile.unlink()
    else:
        with open(messagedir, 'r') as m:
            message = m.read()

    attendance = pl.read_csv(attfile)

    # Calculate the number of rehearsals attended so far
    if attendance.drop("id", "name").shape[1] == 0:
        attendance = attendance.select("id", "name")\
            .with_columns(pl.lit(0).alias("attendance"))
    else:
        attendance = attendance.select("id", "name")\
            .with_columns(
                attendance.drop("id", "name").sum_horizontal().alias("attendance")
        )

    for secfile in sectionsdir.iterdir():
        sec = pl.read_csv(secfile)
        secattendance = attendance.filter(pl.col("id").is_in(sec)).sort("name")
        roll = generate_section_roll(
            section=secfile.stem.capitalize(),
            rehid=rehid,
            rehdesc=rehdesc,
            attendance=secattendance,
            message=message,
        )

        rollfile = rollsdir / ('rehearsal_' + rehid) / (secfile.stem + '.pdf')
        rollfile.parent.mkdir(parents=True, exist_ok=True)
        with open(rollfile, 'wb') as f:
            build_pdf(roll, f)


def mark_rolls(attfile, sectionsdir, rehname):

    attendance = pl.read_csv(attfile)
    attendance = attendance.with_columns(pl.lit(None).cast(pl.Int32).alias(rehname))

    for secfile in sectionsdir.iterdir():
        sec = pl.read_csv(secfile)

        print(
            f"\n{color.BOLD}{color.CYAN}Enter attendance for {
                str.upper(secfile.stem)} section{color.END} [Y/n]:"
        )

        # Sort how rolls are printed for easy data entry
        sectionlist = attendance.select("id", "name", rehname).filter(
            pl.col("id").is_in(sec)).sort("name")

        # Iterate over choristers in section
        for id in sectionlist["id"]:
            chorister = sectionlist.filter(pl.col("id") == id)

            if chorister.shape != (1, 3):
                raise ValueError("Index duplication inside attendance list")
            assert chorister.shape == (1, 3)
            name = chorister[0, "name"]

            # Update attendance
            print(f"{id:<6} {name:<25}? ", end='', flush=True)
            while True:
                c = readchar.readkey()
                if c in ['y', 'Y']:
                    print('Y')
                    attendance = attendance.with_columns(
                        pl.when(pl.col("id") == id)
                        .then(pl.lit(1))
                        .otherwise(pl.col(rehname))
                        .alias(rehname)
                    )
                    break
                elif c in ['n', 'N']:
                    print(color.RED + 'N' + color.END)
                    attendance = attendance.with_columns(
                        pl.when(pl.col("id") == id)
                        .then(pl.lit(0))
                        .otherwise(pl.col(rehname))
                        .alias(rehname)
                    )
                    break
                else:
                    continue
    attendance.write_csv(attfile)
