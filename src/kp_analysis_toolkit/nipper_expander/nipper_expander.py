import argparse
import csv
import os
import sys

from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version

desc = """Process a Nipper CSV export to create one row for each device where each finding was observed.
This allows easier analysis using Excel, such as with PivotTables.
The input file will be autoselected if only one CSV file is in the current directory.
If more than one CSV is present, a choice will be offered.
"""


def main() -> None:
    # print (sys.maxsize)
    csv.field_size_limit(sys.maxsize)

    parser = argparse.ArgumentParser(prog=sys.argv[0].split("/")[-1], description=desc)
    parser.add_argument("-i", "--infile", dest="infile", help="Nipper CSV filename")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s v" + nipper_expander_version,
    )

    args = parser.parse_args()

    # If an infile was specified, use it
    if args.infile:
        infile = args.infile
    else:
        # Get a directory listing of all CSV files in the current director
        dirlist = [x for x in os.listdir(".") if x.endswith(".csv")]
        if len(dirlist) == 0:
            print(
                "No CSV files found.  Change to a directory with a Nipper CSV file or use the --infile to specify the input file",
            )
            sys.exit(1)
        elif len(dirlist) == 1:
            infile: str = dirlist[0]
        else:
            # if more than one CSV file is found, print the results and provide the user a choice
            print(
                'Multiple CSV files found.  Use "nipper-expander.py --infile <filename>" to specify the input file or choose from below.',
            )
            for n, f in enumerate(dirlist):
                print(f"({n + 1:03d}) {f}")
            print()
            try:
                choice = int(input("Choose a file or press CTRL-C to quit: "))
            except KeyboardInterrupt:
                print("\nExiting...\n")
                sys.exit()
            except ValueError:
                print("\nSpecify the line number (digits only)\n")
                sys.exit()
            else:
                try:
                    infile = dirlist[choice - 1]
                except IndexError:
                    print("\nInvalid line number selected\n")
                    sys.exit()

    outfile = infile.split(".")[0] + "-expanded.csv"
    print(f"Infile : {infile}\nOutfile: {outfile}")

    try:
        _: str = input("\nPress ENTER to continue or CTRL-C to quit")
    except KeyboardInterrupt:
        print("\nExiting...\n")

    with open(infile, newline="") as csvinfile:
        csvreader = csv.DictReader(csvinfile)
        csvoutfile = open(outfile, "w")
        fieldnames = csvreader.fieldnames
        csvwriter = csv.DictWriter(csvoutfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        # Initialize some counters so we can list a summary of the work done at the end.
        finding_counter = 0
        row_counter = 0

        # For each row in the original file
        for record in csvreader:
            # The Nipper CSV file lists mulitple devices on a single row.  They are listed in the 'Devices' column and separate with a Carriage Return
            # We split them out there into a Python list.  We'll iterate through them in the for loop a few lines down.
            devices = record["Devices"].split("\r")

            # We need to create a fresh 'Row' dictionary each time through to avoid contamination on subsequent passes
            row = {}
            finding_counter += 1
            for device in devices:
                row_counter += 1
                # Create our new 'expanded' row
                row["Issue Title"] = record["Issue Title"]
                row["Devices"] = device.strip()
                row["Rating"] = record["Rating"]
                row["Finding"] = record["Finding"]
                row["Impact"] = record["Impact"]
                row["Ease"] = record["Ease"]
                row["Recommendation"] = record["Recommendation"]

                # Print a summary of the row to the screen
                print(f"Row#:{row_counter}\t{row['Issue Title']}\t{row['Devices']}")

                # Write the row to the new 'expanded' file
                csvwriter.writerow(row)
        csvoutfile.close()

    # Print the final summary
    print(
        f"\n\n{finding_counter} findings expanded into {row_counter} rows.\n\nYou can now open the {outfile} file in Excel",
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
