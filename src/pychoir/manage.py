import polars as pl
import random
import os
import readchar
import itertools
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


def with_total_attendance(att_dframe):
    """Calculate the number of rehearsals attended so far and return att_dframe with this column."""

    # If the dframe has no rehearsal columns:
    if att_dframe.drop("id", "name").shape[1] == 0:
        att_dframe = att_dframe.select("id", "name")\
            .with_columns(pl.lit(0).alias("attendance"))
    else:
        att_dframe = att_dframe.select("id", "name")\
            .with_columns(
                att_dframe.drop("id", "name").sum_horizontal().alias("attendance")
        )
        return att_dframe


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

    # Calculate total attendance
    attendance = with_total_attendance(attendance)

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

        # Allow the addition of new choristers to the roll.
        print(
            "Any new choristers for the roll? [y/N]",
            end='',
            flush=True,
        )
        c = readchar.readkey()
        print()
        if c in ['y', 'Y']:

            print(
                "Enter new choristers in format: <fname> <lname>. Q to quit.",
                flush=True,
            )

            while (inp := input('New chorister: ')) not in ('q', 'Q'):
                inp = inp.strip().split()
                if len(inp) != 2:
                    print('\t' + color.RED + 'Error: needs two arguments, try again.' + color.END)
                    continue
                fname, lname = inp
                if not fname.replace('-', '').isalpha() and lname.replace('-', '').isalpha():
                    print('\t' + color.RED + 'Error: invalid name, try again.' + color.END)
                    continue

                print('\t' + color.GREEN + 'Success' + color.END)
                attendance, sec, id = insertchorister(
                    attdf=attendance,
                    sectdf=sec,
                    fname=fname,
                    lname=lname,
                )

                # Set new chorister's attendance as present for this rehearsal.
                attendance = attendance.with_columns(
                    pl.when(pl.col("id") == id)
                    .then(pl.lit(1))
                    .otherwise(pl.col(rehname))
                    .alias(rehname)
                )

        attendance.write_csv(attfile)
        sec.write_csv(secfile)


def insertchorister(attdf, sectdf, fname, lname):
    name = lname + ', ' + fname

    assigned_ids = set(attdf.get_column("id").to_list())
    for i in itertools.count(20):
        if i in assigned_ids:
            continue
        else:
            id = i
            break

    # Update chorister list.
    row = pl.DataFrame({"id": [id], "name": [name]})
    # Argument how='diagonal' means missing columns in 'row' get null values in the concatenated
    # frame (as opposed to erroring).
    attdf = pl.concat([attdf, row], how='diagonal')

    # Update section list

    row = pl.DataFrame({"id": [id]})
    sectdf = pl.concat([sectdf, row])

    return attdf, sectdf, id


def add_chorister(attfile, sectionsdir, chfname, chlname, chpart):
    attendance = pl.read_csv(attfile)

    secfile = sectionsdir / (chpart + '.csv')
    if secfile.is_file():
        section = pl.read_csv(secfile)
    else:
        secseries = pl.Series("id", [], dtype=pl.Int64)
        section = pl.DataFrame(secseries)

    attendance, section, _ = insertchorister(
        attdf=attendance,
        sectdf=section,
        fname=chfname,
        lname=chlname,
    )

    attendance.write_csv(attfile)
    section.write_csv(secfile)


def export_programme(attfile, sectionsdir, progrfile, minattendance):
    attendance = pl.read_csv(attfile)
    attendance = with_total_attendance(attendance)

    with open(progrfile, 'w') as file:

        for secfile in sectionsdir.iterdir():
            secname = secfile.stem.capitalize()

            file.write('\t' + secname + ":\n")

            # Filter by part and by attendance
            sec = pl.read_csv(secfile)
            secattendance = attendance.filter(
                pl.col("id").is_in(sec) & (pl.col("attendance") >= minattendance)
            ).sort("name")

            # Cast to list
            names = secattendance.get_column("name").to_list()

            for n in names:
                # Change lname, fname to fname lname
                lname, fname = n.split(', ')
                n = fname + ' ' + lname
                file.write(n + '\n')
