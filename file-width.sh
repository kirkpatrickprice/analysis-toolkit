#!/bin/bash

# Script returns the max width of all files in the current directory.  Useful for AWK column width, for example.

MAXWIDTH=0

# Loop through all of the files in the current directory.  If the length of the filename is greater than MAXWIDTH (initialized to zero, above), then update MAXWIDTH.
# When done, MAXWIDTH will be the length of the longest file in the current directory.
for n in $(ls -1); do 
    LEN=${#n}
    if [ "$LEN" -gt "$MAXWIDTH" ]; then
        MAXWIDTH=$LEN
    fi
done

echo "$MAXWIDTH"