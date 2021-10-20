#!/bin/bash

#A set of functions that can be reused as needed.

rawurlencode() {
    #URL-encodes a string provided as PARAM #1
    # Copied from https://stackoverflow.com/questions/296536/how-to-urlencode-data-for-curl-command 
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] )
                o="${c}" 
                ;;
            * )
                printf -v o '%%%02x' "'$c"
                ;;
        esac
        encoded+="${o}"
    done
    
    #  echo "${encoded}"    # You can either set a return variable (FASTER) 
    URLENCODED="${encoded}"   #or echo the result (EASIER)... or both... :p
}

# declare -a MONTHS_SHORT MONTHS_LONG
# MONTHS_SHORT+=(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)
# MONTHS_LONG+=(January February March April May June July August September October November December)
# MONTHS_NUM+=( $(seq -w 1 12) )
