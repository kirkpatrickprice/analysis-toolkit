#!/bin/bash

# Change log
#   0.1     Initially, this works on Ubuntu server results (maybe even all Debian-based distros).  RPM-based distros will be added later.
#   0.1.1   Added Verbose output to the -f option to display individual server package update counts per month
#   0.1.2   Added EMAIL and DNS servers 
#   0.1.3   Rename "usage" to "usage_local" to support changes made in functions.inc.sh for "long options"
#   0.1.4   Make the script compatible with the shared usage function in functions.inc.sh
#           Add an option to print the interesting packages
#           Make the script compatible with the arraytoregex function added to functions.inc.sh

VERSION=0.1.4

# Bring in our shared functions
source functions.inc.sh

# Initialize some variables
# We'll use an array to build the list of interesting packages so we can work with them a little easier.  We'll walk through this array later to build a grep-able expression.
declare -a PACKAGES

#Add MISC packages to the packages array
PACKAGES+=( ansible chef chrony ftpd gdm jenkins jq libc linux-headers linux-image linux-modules ntpd openssh puppet samba snapd timesyncd xserver )
#Add CONTAINER packages to the packages array
PACKAGES+=( containerd docker etcd kubectl kubernetes )
#Add some WEB, PROXY and APPLICATION SERVERS to the array
PACKAGES+=( apache2 java jetty lighttpd nginx nodejs openjdk squid tomcat )
#Add some popular DNS servers to the array
PACKAGES+=( bind dnsmasq maradns nsd yadifa )
# Add some EMAIL servers to the array
PACKAGES+=( dovecot exim4 postfix qmail sendmail )
#Add some DATABASE SERVERS to the array
PACKAGES+=( cassandra elastic mysql postgres )
#Add some AUTHENTICATION SERVERS to the array
PACKAGES+=( 389-ds apacheds openldap sssd )
#Add some SECURITY packages to the array
PACKAGES+=( aide apparmor clamav openvpn selinux snort tripwire )

#Re-sort the array alphabetically
PACKAGES=($(for each in ${PACKAGES[@]}; do echo $each; done | sort))

declare -A MODULES OPTIONS_DATA MODULES
declare -a OPTIONS_LIST
OPTIONS_LIST=( OS_Packages Container_Packages Frequency XL_Freq2 XL_Freq3 Print Verbose )

#OPTIONS_DATA format:
#   ShortOption::LongOption::HelpText

SCRIPT_NAME=$(basename $0)
SCRIPT_PURPOSE="Analyze Linux servers for missing, important package updates."
SYNTAX="[ -cdhopv ] [ -f MONTH_COUNT [-v] ]"
OPTIONS_DATA[OS_Packages]="o::::DEFAULT ACTION Print the missing OS package updates (using the \"interesting\" packages list)"
OPTIONS_DATA[Container_Packages]="c::::Print the missing container package updates (using the \"interesting\" packages list)"
OPTIONS_DATA[Frequency]="f::::Audit package manager logs/package install dates for patching frequency by month"
OPTIONS_DATA[XL_Freq2]="::::Only works on OS packages (not on container packages)"
OPTIONS_DATA[XL_Freq3]="::::MONTH_COUNT is how many months to count backwards -- always counted from the current month"
OPTIONS_DATA[Print]="p::::Print the \"Interesting Packages\" list"
OPTIONS_DATA[Verbose]="v::::Enable verbose mode"
SYNTAX_NOTES="
    NOTE:   This script must be run in a directory containing Linux-Audit-Script results 
            (https://github.com/kirkpatrickprice/linux-audit-scripts)"


# function usage_local () {
#     echo "
#     audit-linux-packages.sh Version $VERSION

#     Analyze Linux servers for missing, important package updates.

#     USAGE:
#         $(basename $0) [ -cdhov ] [ -f MONTH_COUNT [-v] ]
#         Options:
#             -o      DEFAULT ACTION 
#                     Print the missing OS package updates (using the \"interesting\" packages list)
#             -c      Print the missing container package updates (using the \"interesting\" packages list)
#             -f      Audit package manager logs/package install dates for patching frequency by month
#                     Only works on OS packages (not on container packages)
#                     MONTH_COUNT is how many months to count backwards -- always counted from the current month
#             -v      Print details for each missing package update.  Must be used with either -o, -c or -f
#                     For OS packages, it lists each server where the result was found
#                     For container packages, it lists each server and container where the result was found
#                     For frequency counts, it also lists the individual hits for each system in the sample
#             -h      this help

#         NOTE:   This script must be run in a directory containing Linux-Audit-Script results 
#                 (https://github.com/kirkpatrickprice/linux-audit-script)
#     "
# }

function OS_Packages {
    # SECTION_HEADER is just an input to Grep.  Any grep-able regular expression is acceptable.
    SECTION_HEADER="System_PackageManagerUpdates"

    readarray RESULTS < <(searchfor.sh "${SECTION_HEADER}.*=>" | 
        awk '{
            $1=""; 
            gsub(/^[ \t]+/,"",$0); 
            printf "%s\n",$0
            }' | 
        sort -u | 
        grep "$INTERESTING" )

    # Get the longest result so we can set up some columns to print the results
    SAVEIFS=$IFS
    IFS='::'                            #Set IFS to something that won't be seen so it doesn't mangle the line on every [SPACE]
    MAX_LENGTH=0
    RESULTS_COUNT=${#RESULTS[@]}

    for (( i=0; i<$RESULTS_COUNT; i++)); do 
        LEN=${#RESULTS[$i]}
        if [[ $LEN -gt $MAX_LENGTH ]]; then
            MAX_LENGTH=${LEN}
        fi
    done

    MAX_LENGTH=$((MAX_LENGTH+3))

    #Format and print the results with hyperlinks
    printf "\nOperating System Packages\n"
    for (( i=0; i<$RESULTS_COUNT; i++)); do 
        # Eliminate the trailing newline captured in the results
        RESULT="$(echo -e ${RESULTS[$i]} | awk '{ gsub(/\n$/,"",$0); print $0 }')"
        rawurlencode "${RESULT}"
        printf "%-${MAX_LENGTH}shttps://duckduckgo.com?q=%s\n" ${RESULT} ${URLENCODED}
        if [[ ${OPTIONS[Verbose]} -eq 1 ]]; then
            readarray AFFECTED < <(grep -il "${RESULT}" *)
            for ITEM in ${AFFECTED[@]}; do
                printf "\t%s" ${ITEM}
            done
        fi
    done
    IFS=$SAVEIFS
}

function Frequency {
    SECTION_HEADER="System_PackageInstalledSoftware::/var/log/dpkg.log"

    for n in $(seq 0 ${MONTH_COUNT}); do 
        DATESTR=$(date -d "$(date +%Y-%m-1) -$n month" +%Y-%m)
        COUNT=$(searchfor.sh "${SECTION_HEADER}.*${DATESTR}" | wc -l)
        printf "%s: %d\n" ${DATESTR} ${COUNT}

        #If the Verbose option is set and there were results for the current month, provide per-item counts for each month.
        if [[ ${OPTIONS[Verbose]} -eq 1 ]] && [[ ${COUNT} -gt 0 ]]; then
            for ITEM in $(ls); do
                ITEM_COUNT=$(grep "${SECTION_HEADER}.*${DATESTR}" ${ITEM} | wc -l)
                MAX_WIDTH=$(file-width.sh)
                printf "\t%-${MAX_WIDTH}s:\t%d\n" ${ITEM} ${ITEM_COUNT}
            done
        fi
    done
}

function Container_Packages {
    SECTION_HEADER="Docker_ContainerDetails-.*Updates::"

    readarray RESULTS < <(grep "${SECTION_HEADER}.*=>" * | 
        awk '{
            $1=""; 
            gsub(/^[ \t]+/,"",$0); 
            printf "%s\n",$0
            }' | 
        sort -u | 
        grep "$INTERESTING" )

    # Get the longest result so we can set up some columns to print the results
    SAVEIFS=$IFS
    IFS='::'                            #Set IFS to something that won't be seen so it doesn't mangle the line on every [SPACE]
    MAX_LENGTH=0
    RESULTS_COUNT=${#RESULTS[@]}

    for (( i=0; i<$RESULTS_COUNT; i++)); do 
        LEN=${#RESULTS[$i]}
        if [[ $LEN -gt $MAX_LENGTH ]]; then
            MAX_LENGTH=${LEN}
        fi
    done

    MAX_LENGTH=$((MAX_LENGTH+3))

    #Format and print the results with hyperlinks
    printf "\nContainer Packages\n"
    for (( i=0; i<$RESULTS_COUNT; i++)); do 
        # Eliminate the trailing newline captured in the results
        RESULT="$(echo -e ${RESULTS[$i]} | awk '{ gsub(/\n$/,"",$0); print $0 }')"
        rawurlencode "${RESULT}"
        printf "%-${MAX_LENGTH}shttps://duckduckgo.com?q=%s\n" ${RESULT} ${URLENCODED}
        if [[ ${OPTIONS[Verbose]} -eq 1 ]]; then
            grep "${SECTION_HEADER}.*${RESULT}" * | 
                awk '
                    BEGIN {
                        OFS="::";
                        FS="::";
                    }
                    {
                        sub(/.txt:/,".txt::")
                        sub(/^Docker_ContainerDetails-/,"");
                        sub(/-Updates::/,"::");
                        printf "\t%s::%s\n",$1,$2
                    }'
        fi
    done
    IFS=$SAVEIFS
}

declare -A OPTIONS
NUM_ARGS=$#

#Set OS_Packages=1 as the default action if no other arguments provided
if [[ $NUM_ARGS -eq 0 ]]; then
    OPTIONS[OS_Packages]=1
else
    while getopts "cf:hopv" OPT; do
        case $OPT in
            v )
                OPTIONS[Verbose]=1
                ;;
            o )
                OPTIONS[OS_Packages]=1
                ;;
            c ) 
                OPTIONS[Container_Packages]=1
                ;;
            f )
                OPTIONS[Frequency]=1
                MONTH_COUNT=$((OPTARG-1))
                ;;
            p )               
                echo "Interesting packages list:"
                COUNT=1
                for p in ${PACKAGES[@]}; do
                    printf "\t%3s) %s\n" $COUNT $p
                    COUNT=$((${COUNT}+1))
                done
                exit 0
                ;;
            * )
                usage
                exit 1
                ;;
        esac
    done
fi

#Check if Verbose was used without either OS_Packages or Container_Packages options
if [[ ${OPTIONS[Verbose]} -eq 1 ]]; then
    if [[ ${OPTIONS[OS_Packages]} -eq 0 ]] && [[ ${OPTIONS[Container_Packages]} -eq 0 ]] && [[ ${OPTIONS[Frequency]} -eq 0 ]]; then
        printf "Verbose was used, but requires -o, -c or -f options.\n"
        usage
        EXITCODE=1
        exit $EXITCODE
    fi
fi

#Build a regaular expression to be used with Grep to find the interesting packages
INTERESTING=$(arraytoregex ${#PACKAGES[@]} ${PACKAGES[@]})


#Iterate through the OPTIONS array and run the appropriate functions as selected by command line options
for ITEM in ${OPTIONS_LIST[@]}; do
    # Using a CASE statement for better readability even though an IF-THEN-ELSE would probably be better since there's only two options
    case ${ITEM} in
        Verbose|XL_*)
            # Do nothing if the ITEM is either "VERBOSE" or any of the "XL_" lines
            ;;
        *)
            if [[ ${OPTIONS[${ITEM}]} -eq 1 ]]; then
                ${ITEM}
            fi
            ;;
    esac
    # if [[ "${ITEM}" != "Verbose" ]]; then
    #     if [[ ${OPTIONS[${ITEM}]} -eq 1 ]]; then
    #         ${ITEM}
    #     fi
    # fi
done