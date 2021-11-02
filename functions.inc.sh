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

    #local SHORT LONG HELPTEXT

    printf "
    ${SCRIPT_NAME} Version ${VERSION}

    ${SCRIPT_PURPOSE}
    
    USAGE:
        ${SCRIPT_NAME} ${SYNTAX}
        Options:\n"
        for ITEM in ${OPTIONS_LIST[@]}; do
            SHORT_OPT=$(GetShort "${OPTIONS_DATA[${ITEM}]}")
            LONG_OPT=$(GetLong "${OPTIONS_DATA[${ITEM}]}")
            HELPTEXT=$(GetHelpText "${OPTIONS_DATA[${ITEM}]}")
            printf "\t\t-${SHORT_OPT}, --${LONG_OPT}\t\t${HELPTEXT}\n"
        done
        
    printf "\t\t-h, --help\t\tThis help\n"
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

# function GetOpts {
#     #Not currently being used, but didn't want to get rid of the work on this quite yet.
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
