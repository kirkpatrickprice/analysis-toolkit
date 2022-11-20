#!/bin/bash

function usage () {
    echo "

    Covert files from RTF to plain text format

    USAGE:
        $(basename $0) [ -chov ] [ -f MONTH_COUNT ]
        Options:
            -h      this help

        NOTE:   This script requires the use of unrtf.  Install with \"apt update && apt install unrtf\" 
                if you receive errors that it is not installed.
    "
}

if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]]; then
    usage
    EXITCODE=1
    exit $EXITCODE
fi

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for n in *; do
  unrtf --text "$n" > `echo $n | awk -F " " '{ print $1 ".txt" }'`
done
IFS=$SAVEIFS
