#!/bin/bash

# Fortigate IPSEC VPN Config Parser

FILE=$1

# Define what to look for in each VPN block
declare -A CONFIG
CONFIG[SECTION]="config vpn ipsec phase1"
CONFIG[PAD]=2
CONFIG[HOSTNAME]="hostname"
CONFIG[INTERFACE]="interface"
CONFIG[IKE]="ike-version"
CONFIG[MODE]="mode"
CONFIG[KEX]="dhgrp"
CONFIG[AUTH]="authmethod"
CONFIG[CIPHER]="proposal"
CONFIG[MAC]="proposal"

# Build an array of the "config vpn ipsec" section headings
#readarray VPN_PROFILES <<<$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | grep '\bedit' | awk 'BEGIN {FS="\"";}{printf "%s ",$2;}')

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

COL_HEADINGS=("SYS_NAME" "PROFILE_NAME" "INTERFACE" "IKE_VERSION" "IKE_MODE" "KEX" "AUTH_METHOD" "CIPHER" "MAC")
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
            COL_WIDTH[SYS_NAME]=$((LONGEST_HOST+2))
            ;;
        "PROFILE_NAME")
            COL_WIDTH[PROFILE_NAME]=$LONGEST_VPN
            ;;
        "INTERFACE")
            LONGEST_IFACE=${#ITEM}
            for IFACE in $(sed -n "/\bconfig system interface/,/^end/p" $FILE | grep '\bedit' | awk '{gsub(/"/,""); print $2}'); do
                if [[ "${#IFACE}" -gt "${LONGEST_IFACE}" ]]; then
                    LONGEST_IFACE=${#IFACE}
                fi
            done
            COL_WIDTH[INTERFACE]=$((LONGEST_IFACE+${CONFIG[PAD]}))
            ;;
        "CIPHER")
            LONGEST_CIPHER=${#ITEM}
            for CIPHER in $(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | grep " ${CONFIG[CIPHER]} " | awk '{print $3}' | awk -F "-" '{print $1}'); do
                if [[ "${#CIPHER}" -gt "$LONGEST_CIPHER" ]]; then
                    LONGEST_CIPHER=${#CIPHER}
                fi
            done
            COL_WIDTH[CIPHER]=$((LONGEST_CIPHER+${CONFIG[PAD]}))
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

for PROFILE in ${VPN_PROFILES[*]}; do
    RESULTS[PROFILE_NAME]=$PROFILE
    RESULTS[INTERFACE]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[INTERFACE]} " | awk '{gsub(/"/,""); print $3}')
    RESULTS[IKE_VERSION]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[IKE]} " | awk '{print $3}')
    RESULTS[IKE_MODE]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[MODE]} " | awk '{print $3}')
    RESULTS[KEX]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep " ${CONFIG[KEX]} " | awk '{print $3}')
    RESULTS[AUTH_METHOD]=$(sed -n "/\b${CONFIG[SECTION]}/,/\bend/p" $FILE | sed -n "/edit .$PROFILE.$/,/\bnext/p" | grep "${CONFIG[AUTH]}" | awk '{print $3}')
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