#!/usr/bin/python3

"""
Process a Nipper CSV export to create one row for each device where each finding was observed.
This allows easier analysis using Excel, such as with PivotTables.
"""

import csv
import argparse
import sys

version="0.1.1"

parser = argparse.ArgumentParser(prog=sys.argv[0], description='Expand Nipper CSV file into one line per finding instance')
parser.add_argument('infile', help="Nipper CSV filename")
parser.add_argument('--version', '-v', action='version', version='%(prog)s v'+version)

args=parser.parse_args()

outfile=args.infile.split('.')[0] + '-expanded.csv'
print('Infile : %s\nOutfile: %s' % (args.infile, outfile))

confirm=input("\nPress ENTER to continue or CTRL-C to quit")

with open(args.infile, newline='') as csvinfile:
    csvreader=csv.DictReader(csvinfile)
    csvoutfile=open(outfile, 'w')
    fieldnames=csvreader.fieldnames
    csvwriter=csv.DictWriter(csvoutfile, fieldnames=fieldnames)
    csvwriter.writeheader()
    #Initialize some counters so we can list a summary of the work done at the end.
    finding_counter=0
    row_counter=0

    #For each row in the original file
    for record in csvreader:
        #The Nipper CSV file lists mulitple devices on a single row.  They are listed in the 'Devices' column and separate with a Carriage Return
        #We split them out there into a Python list.  We'll iterate through them in the for loop a few lines down.
        devices=record['Devices'].split('\r')
        
        #We need to create a fresh 'Row' dictionary each time through to avoid contamination on subsequent passes
        row={}
        finding_counter += 1
        for device in devices:
            row_counter += 1
            #Create our new 'expanded' row
            row['Issue Title']=record['Issue Title']
            row['Devices'] = device.strip()
            row['Rating'] = record['Rating']
            row['Finding'] = record['Finding']
            row['Impact'] = record['Impact']
            row['Ease'] = record['Ease']
            row['Recommendation'] = record['Recommendation']
            
            #Print a summary of the row to the screen
            print('Row#:%d\t%s\t%s' % (row_counter, row['Issue Title'], row['Devices']))
            
            #Write the row to the new 'expanded' file
            csvwriter.writerow(row)
    csvoutfile.close()

#Print the final summary
print('\n\n%d findings expanded into %d rows.\n\nYou can now open the %s file in Excel' % (finding_counter, row_counter, outfile))