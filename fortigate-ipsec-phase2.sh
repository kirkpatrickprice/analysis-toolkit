#!/bin/bash

# Fortigate IPSEC VPN Config Parser

FILE=$1

# Define what to look for in each VPN block
declare -A CONFIG
CONFIG[SECTION]="config vpn ipsec phase2"
CONFIG[PAD]=2
CONFIG[HOSTNAME]="hostname"
CONFIG[PHASE1]="phase1name"
CONFIG[PFS]="pfs"
CONFIG[KEX]="dhgrp"
CONFIG[ENCAP]="encapsulation"
CONFIG[CIPHER]="proposal"
CONFIG[MAC]="proposal"

# Build an array of the "config vpn ipsec" section headings

LONGEST_VPN=0
COUNT=0

declare -A VPN_PROFILES
# Find the longest VPN Profile so we can build some columns
for ITEM in $(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | grep '\bedit' | awk 'BEGIN {FS="\"";}{printf "%s ",$2;}'); do
    COUNT=$((COUNT+1))
    VPN_PROFILES[$COUNT]=$ITEM
    if [[ "${#ITEM}" -gt "$LONGEST_VPN" ]]; then
        LONGEST_VPN=${#ITEM}
    fi
done

#Pad the longest VPN Profile Name by a couple of spaces
LONGEST_VPN=$((LONGEST_VPN+${CONFIG[PAD]}))

echo "${#VPN_PROFILES[*]} VPN Profiles Discovered"

COL_HEADINGS=("SYS_NAME" "PROFILE_NAME" "PHASE1" "PFS" "ENCAP" "KEX" "CIPHER" "MAC")
declare -A COL_WIDTH

# Loop through each column heading to determine the width of the columns.  Some have special methods to determine width.
for ITEM in ${COL_HEADINGS[*]}; do
    case $ITEM in
        "SYS_NAME")
            LONGEST_HOST=${#ITEM}
            HOSTNAME=$(sed -n "/\bconfig system global/,/^end/p" $FILE | grep " ${CONFIG[HOSTNAME]} " | awk '{gsub(/"/,""); print $3}')
            if [[ "${#HOSTNAME}" -gt "${LONGEST_HOST}" ]]; then
                LONGEST_HOST=${#HOSTNAME}
            fi
            COL_WIDTH[${ITEM}]=$((LONGEST_HOST+${CONFIG[PAD]}))
            ;;
        "PROFILE_NAME")
            COL_WIDTH[${ITEM}]=$LONGEST_VPN
            ;;
        "PHASE1")
            LONGEST_PHASE1=${#ITEM}
            for PHASE1 in $(sed -n "/\b${CONFIG[SECTION]}/,/^end/p" $FILE | grep "${CONFIG[PHASE1]}" | awk '{gsub(/"/,""); print $3}'); do
                if [[ "${#PHASE1}" -gt "${LONGEST_PHASE1}" ]]; then
                    LONGEST_PHASE1=${#PHASE1}
                fi
            done
            COL_WIDTH[${ITEM}]=$((LONGEST_PHASE1+${CONFIG[PAD]}))
            ;;
        "ENCAP")
            # Hard-set to 16 as Options are "tunnel-mode" (11) or "transport-mode" (14)
            COL_WIDTH[${ITEM}]=$((${CONFIG[PAD]}+16))
            ;;
        "PFS")
            # Hard-set as options are "enable" or "disable"
            COL_WIDTH[${ITEM}]=$((${CONFIG[PAD]}+7))
            ;;
        "CIPHER")
            LONGEST_CIPHER=${#ITEM}
            for CIPHER in $(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | grep " ${CONFIG[CIPHER]} " | awk '{print $3}' | awk -F "-" '{print $1}'); do
                if [[ "${#CIPHER}" -gt "$LONGEST_CIPHER" ]]; then
                    LONGEST_CIPHER=${#CIPHER}
                fi
            done
            COL_WIDTH[${ITEM}]=$((LONGEST_CIPHER+${CONFIG[PAD]}))
            ;;
        *)
            TEMP=${#ITEM}
            COL_WIDTH[$ITEM]=$((TEMP+3))
            ;;
    esac
done

# Print the header row
for ITEM in ${COL_HEADINGS[*]}; do
    if [[ "$ITEM" -eq "PROFILE_NAME" ]]; then
        printf "%-*s%*s" ${COL_WIDTH[$ITEM]} ${ITEM}
    else
        printf "%*s" ${COL_WIDTH[$ITEM]} ${ITEM}
    fi
done
printf "\n"

# Declare an array to hold our results in as we iterate through the VPN Profiles
declare -A RESULTS

RESULTS[SYS_NAME]=$HOSTNAME

#Column headings repeated here for reference:
# "SYS_NAME" "PROFILE_NAME" "PHASE1" "PFS" "ENCAP" "KEX" "CIPHER" "MAC"
for PROFILE in ${VPN_PROFILES[*]}; do
    RESULTS[PROFILE_NAME]=$PROFILE
    RESULTS[PHASE1]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[PHASE1]} " | awk '{gsub(/"/,""); print $3}')
    RESULTS[PFS]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[PFS]} " | awk '{print $3}')
    RESULTS[ENCAP]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[ENCAP]} " | awk '{print $3}')
    RESULTS[KEX]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[KEX]} " | awk '{print $3}')
    RESULTS[CIPHER]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[CIPHER]} " | awk '{print $3}' | awk -F "-" '{print $1}')
    RESULTS[MAC]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[MAC]} " | awk '{print $3}' | awk -F "-" '{print $2}')
    for COL in ${COL_HEADINGS[*]}; do        
        if [[ "$COL" -eq "PROFILE_NAME" ]]; then
            printf "%-*s" ${COL_WIDTH[$COL]} ${RESULTS[$COL]}
        else
            printf "%*s" ${COL_WIDTH[$COL]} ${RESULTS[$COL]}
        fi
    done
    printf "\n"        
done