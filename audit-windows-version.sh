#!/bin/bash


MAX_WIDTH=$(file-width.sh)
FORMAT_STRING="%-${MAX_WIDTH}s%-40s%-15s%-10s\n"

#Print the header row
printf "$FORMAT_STRING" "System Name" "Product Name" "Current Build" "UBR Code"

for FILE in $(ls -1 *.txt); do
    SYSTEM_NAME=${FILE/'.txt'/''}
    OLD_IFS=$IFS
    IFS='%%%'

    # Get the necessary info from each file
    PRODUCT_NAME=$(grep -m 1 '^System_OSInfo::ProductName' $FILE | awk -F ':' '{sub(/^ /,"",$4); print $4}')
    CURRENT_BUILD=$(grep -m 1 '^System_OSInfo::CurrentBuild' $FILE | awk '{print $NF}')
    UBR_CODE=$(grep -m 1 '^System_OSInfo::UBR' $FILE | awk '{print $NF}')

    #Print the results
    printf "$FORMAT_STRING" $SYSTEM_NAME $PRODUCT_NAME $CURRENT_BUILD $UBR_CODE
    IFS=$OLD_IFS
done

#Print a blank line to keep the terminal from getting all scrunched up
echo