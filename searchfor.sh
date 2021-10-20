#!/bin/bash

function usage () {
    echo "
        A script to take a search parameter and return the results for all files in the current directory.  
            $1 - Parameter to search for
        
        Output: Formatted results, excluding lines containing \"Processing\" or \"###\".  
                Results will also exclude the \"Section_Header::\" text.
            
                <File_Name>     <Everything_Else>
            
                File_Name -- Name of the file where the string was found
                Everything_Else -- After removing the \"Section_Header::\", all the rest of the content on the line
    
        Examples:
            searchfor.sh \"System_PackageManagerUpdates\" will return all of the pending updates results. 
            searchfor.sh \"/etc/passwd\" will return the contents of all /etc/passwd files collected in the sample.
            
            You can then additionally grep|awk|sort the results to see just what you need

        NOTE: searchfor.sh also relies on \"file-width.sh\" included as part of the toolkit.
    "
}

if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]]; then
    usage
    EXITCODE=1
    exit $EXITCODE
fi


#First determine the max width of all of the files so we can make pretty columns in AWK

MAXWIDTH=$((`file-width.sh` + 1))

#Search for the string, pass it to AWK, replace the everything betwen ".txt" and "::" with just "::" and print the columns
#A note on the "substr(...index())" function:
#   index       find the character position for PARAM2 within PARAM1
#               So... find the starting position for FIELD3 within the full string
#   substr      Print a substring of PARAM1 starting at PARAM2.  If PARAM3 is omitted, print to the end of the line

#So... the full effect is to print from the starting position of FIELD3 to the end of the line, which is everything after the second ::

grep -i "$1" * | grep -v "\(Processing.*\)\|\[.*\]\|###" | awk -v width="$MAXWIDTH" '
    BEGIN {
        OFS="::";
        FS="::";
    }
    {
        sub(/.txt:/, "::"); 
        systemname=$1
        printf "%-*s",width,systemname; 
        print substr($0, index($0, $3))
    }'
