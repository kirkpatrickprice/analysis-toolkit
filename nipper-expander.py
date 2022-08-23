#!/usr/bin/python3

import csv
import argparse

version="0.1"

parser = argparse.ArgumentParser(prog='nipper-expander.py', description='Expand Nipper CSV file into one line per finding instance')
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
    finding_counter=0
    row_counter=0
#    finaldata=[]
    for record in csvreader:
        devices=record['Devices'].split('\r')
        row={}
        #row['Devices']=[]
        finding_counter += 1
        for device in devices:
            row_counter += 1
            row['Issue Title']=record['Issue Title']
            row['Devices'] = device.strip()
            row['Rating'] = record['Rating']
            row['Finding'] = record['Finding']
            row['Impact'] = record['Impact']
            row['Ease'] = record['Ease']
            row['Recommendation'] = record['Recommendation']
            print('Row#:%d\t%s\t%s' % (row_counter, row['Issue Title'], row['Devices']))
            csvwriter.writerow(row)
    csvoutfile.close()

print('\n\n%d findings expanded into %d rows.\n\nYou can now open the %s file in Excel' % (finding_counter, row_counter, outfile))