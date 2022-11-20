#!/bin/bash

#   0.1.0 - Iniital release
#   0.1.1 - Added ReleaseID and <blank> checking to keep the tables pretty(er, I hope)

VERSION="0.1.1"

MAX_WIDTH=$(file-width.sh)
FORMAT_STRING="%-${MAX_WIDTH}s%-40s%-11s%-15s%-10s\n"

#Print the header row
printf "$FORMAT_STRING" "System Name" "Product Name" "ReleaseID" "Current Build" "UBR Code"

for FILE in $(ls -1 *.txt); do
    SYSTEM_NAME=${FILE/'.txt'/''}
    OLD_IFS=$IFS
    IFS='%%%'

    # Get the necessary info from each file
    PRODUCT_NAME=$(grep -i -m 1 '^System_OSInfo::ProductName' $FILE | awk -F ':' '{sub(/^ /,"",$4); print $4}')
    RELEASE_ID=$(grep -i -m 1 '^System_OSInfo::ReleaseID' $FILE | awk '{print $NF}')
    if [[ "${RELEASE_ID}" == ":" ]] || [[ "${RELEASE_ID}" == "" ]]; then
        RELEASE_ID="<Blank>"
    fi
    
    CURRENT_BUILD=$(grep -i -m 1 '^System_OSInfo::CurrentBuild' $FILE | awk '{print $NF}')
    if [[ "${CURRENT_BUILD}" == ":" ]] || [[ "${CURRENT_BUILD}" == "" ]]; then
        CURRENT_BUILD="<Blank>"
    fi

    UBR_CODE=$(grep -i -m 1 '^System_OSInfo::UBR' $FILE | awk '{print $NF}')
    if [[ "${UBR_CODE}" == ":" ]] || [[ "${UBR_CODE}" == "" ]]; then
        UBR_CODE="<Blank>"
    fi


    #Print the results
    printf "$FORMAT_STRING" $SYSTEM_NAME $PRODUCT_NAME $RELEASE_ID $CURRENT_BUILD $UBR_CODE
    IFS=$OLD_IFS
done

#Print a blank line to keep the terminal from getting all scrunched up
echo