#!/bin/bash

#A set of functions that can be reused as needed.

function arraytoregex () {

    # Function to convert an array to a regex with "OR" (|) separators.
    #   $1      Number of items in the array that was passed
    #   $2..n   The items to concatenance into the regex string

    local STRING
    local ITEM
    local NUM_ITEMS=$1
    local i
    
    #Now that we've used $1, shift the parameters to the left so $2 is now $1
    shift 1
    
    # Run a for loop through each of the positional parameters passed to the function / we'll pop $1 off each time we use it
    for (( i=1; i<=$NUM_ITEMS; i++ )); do
        # We need to check if we've reached the last item in the array.  If so, our grep search needs to leave off the trailing OR "\|"
        if [[ $i -eq $NUM_ITEMS ]]; then
            STRING=$STRING"$1"
        else
            STRING=$STRING"$1\|"
        fi
        shift 1
    done

    #Return the completed string
    echo "$STRING"

}

longest () {
    #Function to return the longest string in a list of strings.  Strings are assumed to be seperated by a SPACE

    # Sitck all of the parameters into an array
    local array+=($@)
    local ITEM
    local l
    local m
    
    for ITEM in ${array[@]}; do
        l=${#ITEM}
        if [[ $l -gt $m ]]; then
            m=$l
        fi
    done

    echo $m
}

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

function usage () {
    # A reusable Usage function that receives parameters from the main box of the script
    # to print the help screen.
    #   SCRIPT_NAME     Just use $(basename $0), or put your own string in as the name to be displayed
    #   VERSION         The current version of the script
    #   SYNTAX          The text that will be displayed after the script name (e.g. [ OPTIONS ] REQUIRED... )
    #   OPTIONS_LIST    An indexed array (e.g. OPTIONS_LIST[0,1,etc]) with the names of the Functions that will be called
    #   OPTIONS_DATA    A hashed array (e.g. OPTIONS_DATA[Verbose]) where the array elements are named for items in OPTIONS_LIST
    #                   The array text is a DOUBLE-COLON-separated field-list "::"
    #                       FIELD1 -- Short option (e.g. -h)
    #                       FIELD2 -- Long option (e.g. --help)
    #                       FIELD3 -- Expected parameter count (usually 0)
    #                       FIELD4 -- Help text to display
    #   SYNTAX_NOTES    Any notes that will be displayed after the help
    # Options will be printed out in the order in which they appear in the OPTIONS_LIST array
    # Use XL_* to identify additional lines that will be printed without either a SHORT_OPT or LONG_OPT (used for whitespacing)

    local LONGEST TEMP_STR LONG_USED

    # First, let's get the LONGEST combination of SHORT and LONG options from the hashed array
    LONGEST=0
    for ITEM in ${OPTIONS_LIST[@]}; do
        SHORT_OPT=$(GetShort "${OPTIONS_DATA[${ITEM}]}")
        LONG_OPT=$(GetLong "${OPTIONS_DATA[${ITEM}]}")
        TEMP_STR="-${SHORT_OPT},--${LONG_OPT}"
        if [[ "${#TEMP_STR}" -gt ${LONGEST} ]]; then
            LONGEST=${#TEMP_STR}
        fi
    done
    LONGEST=$((${LONGEST}+1))

    printf "
    ${SCRIPT_NAME} Version ${VERSION}

    ${SCRIPT_PURPOSE}
    
    USAGE:
        ${SCRIPT_NAME} ${SYNTAX}
        Options:\n"
        for ITEM in ${OPTIONS_LIST[@]}; do
            TEMP_STR=""
            SHORT_OPT=$(GetShort "${OPTIONS_DATA[${ITEM}]}")
            LONG_OPT=$(GetLong "${OPTIONS_DATA[${ITEM}]}")
            HELPTEXT=$(GetHelpText "${OPTIONS_DATA[${ITEM}]}")
            # If there's a short option defined, then add it to the TEMP_STR
            if [[ -n $SHORT_OPT ]]; then
                TEMP_STR="-${SHORT_OPT}"
                # If there's also a LONG_OPT defined, then add a comma
                if [[ -n $LONG_OPT ]]; then
                    TEMP_STR="${TEMP_STR},"
                fi
            fi
            # If there's a LONG_OPT defined, then add it to the string
            if [[ -n $LONG_OPT ]]; then
                TEMP_STR="${TEMP_STR}--${LONG_OPT}"
                LONG_USED=1
            fi
            # Print the SHORT and LONG_OPT string as formatted above.  Use COLUMN-WIDTH of LONGEST.  Add the HELPTEXT
            printf "\t\t%-${LONGEST}s\t%s\n" "${TEMP_STR}" "${HELPTEXT}"
        done
    #Add the generic "-h,--help" content and any notes provided by the calling script
    if [[ ${LONG_USED} -eq 1 ]]; then 
        printf "\t\t%-${LONGEST}s\t%s\n" "-h, --help" "This help"
    else
        printf "\t\t%-${LONGEST}s\t%s\n" "-h" "This help"
    fi
    printf "\t${SYNTAX_NOTES}"
}

function GetShort {
    local STR
    STR="$1"
    echo "$(echo ${STR} | awk -F "::" '{ print $1 }')"
}

function GetLong {
    local STR
    STR="$1"
    echo "$(echo ${STR} | awk -F "::" '{ print $2 }')"
}

function GetHelpText {
    local STR
    STR="$1"
    echo "$(echo ${STR} | awk -F "::" '{ print $3 }')"
}

function VersionCheck {
    # Function to compare the KPNIXVersion that used to create the sample file to a required version needed by the analysis script
    #   $1  KPNIXVERSION used by the file
    #   $2  Required version
    # Returns the result as either 
    #   0 version requirements are NOT met
    #   1 version requirements are met
    local FILEVERSION_ARRAY=($(echo $1 | tr "." "\n"))
    local REQDVERSION_ARRAY=($(echo $2 | tr "." "\n"))
    local RESULT
    
    #Positions in the array for each part of the version string
    local MAJOR=0
    local MINOR=1
    local MAINT=2

    if [[ ${FILEVERSION_ARRAY[$MAJOR]} -gt ${REQDVERSION_ARRAY[$MAJOR]} ]]; then 
        # Major version exceeds requirements -- All is good with this file"
        RESULT=1
        else if [[ ${FILEVERSION_ARRAY[$MINOR]} -gt ${REQDVERSION_ARRAY[$MINOR]} ]]; then
            # Minor version exceeds requirements -- All is good with this file"
            RESULT=1
        else if [[ ${FILEVERSION_ARRAY[$MAINT]} -ge ${REQDVERSION_ARRAY[$MAINT]} ]]; then
            # Maint version exceeds requirements -- All is good with this file"
            RESULT=1
            else #If the MAINT version is less than the stated requirement, then it fails the test
                RESULT=0
            fi
        fi
    fi
    echo $RESULT
}

# function GetOpts {
#     #Not currently being used, but didn't want to get rid of the work on this quite yet.
#     # This is an attempt to write a modular approach to enabling options based on OPTIONS_DATA fields
#     # The current challenge is getting it to handle a variable number of PARAMs based on PARAM_COUNT.  
#     # For now, we're using statically coded CASE statements in the calling script to parse the options.
#     local i j
#     for ((i=0; i<${OPTS_COUNT}; i++)); do
#         OPTION="${CMD_OPTS[$i]}"
#         if [ "${OPTION}" == "-h" ] || [ "${OPTION}" == "--help" ]; then
#             usage
#             exit 0
#         fi
#         for ITEM in ${OPTIONS_LIST[@]}; do
#             SHORT_OPT=$(GetShort "${OPTIONS_DATA[${ITEM}]}")
#             LONG_OPT=$(GetLong "${OPTIONS_DATA[${ITEM}]}")
#             PARAM_COUNT=$(GetParamCount "${OPTIONS_DATA[${ITEM}]}")
#             printf "\n"
#             printf "OPTION=${OPTION}\n"
#             printf "SHORT=$SHORT_OPT\n"
#             printf "LONG=$LONG_OPT\n"
#             printf "PARAMCOUNT=$PARAM_COUNT\n"
#             if [[ ${OPTION} == "-${SHORT_OPT}" ]] || [[ ${OPTION} == "--${LONG_OPT}" ]]; then
#                 MODULES[${ITEM}]=1
#                 if [[ ${PARAM_COUNT} -gt 0 ]]; then
#                     for ((j=0; j<${PARAM_COUNT}; j++)); do 
#                         i=$((i+1))
#                         PARAM[${ITEM}]+="${CMD_OPTS[$i]}"
#                     done
#                 fi 
#             # else
#             #     usage
#             #     exit 1
#             fi 
#         done
#     done
# }

# declare -a MONTHS_SHORT MONTHS_LONG
# MONTHS_SHORT+=(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)
# MONTHS_LONG+=(January February March April May June July August September October November December)
# MONTHS_NUM+=( $(seq -w 1 12) )
