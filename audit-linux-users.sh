#!/bin/bash

# Change Log
# 0.1.0
#   - First version of the script
# 0.1.1
#   - Added a version check for BlankPasswords
#   - Cleaned up and added additional details to the User Status report

VERSION="0.1.1"

source functions.inc.sh

declare -A MODULES OPTIONS_DATA MODULES
declare -a OPTIONS_LIST
OPTIONS_LIST+=( BlankPasswords XL_BP1 UserStatus XL_Usr1 Sudoers All )

#OPTIONS_DATA format:
#   ShortOption::LongOption::HelpText

SCRIPT_NAME=$(basename $0)
SCRIPT_PURPOSE="This script analyzes user information collected by the Linux Audit Script."
SYNTAX="[ OPTION ]..."
OPTIONS_DATA[BlankPasswords]="b::blank::Test for users with blank password"
OPTIONS_DATA[XL_BP1]="::::Requires results produced by KPNIXAUDIT.SH version >=0.6.11"
OPTIONS_DATA[UserStatus]="u::user-status::Report on user status"
OPTIONS_DATA[XL_Usr1]="::::Requires results produced by KPNIXAUDIT.SH version >=0.6.12"
#OPTIONS_DATA[PasswordPolicy]="p::passpol::Audit the password policy on each server"
OPTIONS_DATA[Sudoers]="s::sudoers::Test for users with Sudo access"
OPTIONS_DATA[All]="a::all::Run all tests"
#OPTIONS_DATA[Verbose]="v::verbose::Enable verbose mode"
SYNTAX_NOTES="
    NOTE:   This script must be run in a directory containing Linux-Audit-Script results 
            (https://github.com/kirkpatrickprice/linux-audit-script)"

function BlankPasswords {
    local RESULT ITEM FILEOK KPNIXVERSION REQDVERSION SECTION_HEADER f SAVEIFS

    echo "Test for users with blank password"

    SECTION_HEADER="Users_BlankPasswd"
    REQDVERSION="0.6.11"

    for f in $(ls -1); do
        # Get the version KPNIXVERSION from the file | if Grep fails because it can't find the line (e.g. a REALLY old version was used), set the version to 0.0.0 so it fails the check.
        KPNIXVERSION=$(grep "KPNIXVERSION" $f | awk -F ": " '{print $2}')
        
        if [[ -z $KPNIXVERSION ]]; then
            KPNIXVERSION="0.0.0"
        fi

        # Check the version of the results file against the required version for this check.
        FILEOK=$(VersionCheck "$KPNIXVERSION" "$REQDVERSION")

        if [[ $FILEOK -eq 1 ]]; then

            readarray RESULT <<< $(grep "${SECTION_HEADER}" $f | awk -F :: '/has a blank password/{printf "\t%s\n",$2}')
            printf "\tResults for %s\n" $f

            # Check if the first item in the array is longer than 1 characters (means we have a result)
            if [[ ${#RESULT[0]} -gt 1 ]]; then
                #Change the IFS to something meaningless so it doesn't mangle the output
                SAVEIFS=$IFS
                IFS=':::'

                # Iterate through the results array and print each line
                for ITEM in ${RESULT[@]}; do
                    # Eliminate extra tabs and new lines
                    ITEM=$(echo $ITEM | tr -d '\n|\t')
                    printf "\t\t%s\n" $ITEM
                done

                # Restore IFS
                IFS=$SAVEIFS
            else # If there weren't any results
                printf "\t\tNo blank passwords found\n"
            fi
        else    # FILEOK=0
            if [[ "$KPNIXVERSION" = "0.0.0" ]]; then
                printf "\t%s does not appear to be a kpnixaudit.sh result file or it was created by a truly ancient version.  Skipping file.\n" $f
            else
                printf "\t%s was created by kpnixaudit.sh version %s.  Skipping file.\n" $f $KPNIXVERSION
            fi    
        fi
    done

    printf "\n"
}

function UserStatus {
    local NOT_LOGIN_SHELLS EXCLUDE_SHELLS REQDVERSION KPNIXVERSION SECTION_HEADER LONGEST_USER SHELL LONGEST_SHELL ITEM f FILEOK 
    local SECTION_HEADER SSH_KEY SAVEIFS SSH_WIDTH PASSWD_STATUS PASSWD_WIDTH PASSWD_CHANGED PASSWD_MAX_AGE
    
    # Define a lit of shells that don't result in an interactive login / these can be excluded from the check for inactive users)
    NOT_LOGIN_SHELLS+=(nologin sync reboot sync false)
    EXCLUDE_SHELLS=$(arraytoregex ${#NOT_LOGIN_SHELLS[@]} ${NOT_LOGIN_SHELLS[@]})
    
    # This check will only work on a results file based on a minimum version
    REQDVERSION="0.6.12"

    # Hard-code the longest shell to 15 characters (for now)
    LONGEST_SHELL=15
    SSH_WIDTH=15
    PASSWD_WIDTH=16
    
    printf "Report on User Status\n"
    
    #Analyze and report the results one file at a time
    for f in $(ls -1); do
        # Get the version KPNIXVERSION from the file | if Grep fails because it can't find the line (e.g. a REALLY old version was used), set the version to 0.0.0 so it fails the check.
        KPNIXVERSION=$(grep "KPNIXVERSION" $f | awk -F ": " '{print $2}')
        
        if [[ -z $KPNIXVERSION ]]; then
            KPNIXVERSION="0.0.0"
        fi

        # Check the version of the results file against the required version for this check.
        FILEOK=$(VersionCheck "$KPNIXVERSION" "$REQDVERSION")

        if [[ $FILEOK -eq 1 ]]; then
            SECTION_HEADER="Users_etcpasswd"
            printf "\tResults for $f\n"
            
            # Grep for strings that include $SECTION_HEADER, deselect any lines that include any of the non-interactive shells and use AWK to get the username in field 5
            readarray SHELL_USERS <<< $(grep "$SECTION_HEADER" $f |
                grep -v "$EXCLUDE_SHELLS" | awk -F ":" '{print $5}' | sort )

            # Find the longest shell user so we can set up some columns for pretty printing
            LONGEST_USER=$(longest ${SHELL_USERS[@]})
            LONGEST_USER=$(( $LONGEST_USER +2 ))

            printf "\t\tAll users with an interactive shell\n"

            printf "\t\t\t%-${LONGEST_USER}s%-${LONGEST_SHELL}s%-${SSH_WIDTH}s%-${PASSWD_WIDTH}s%-${PASSWD_WIDTH}s%-${PASSWD_WIDTH}s\n" "USERNAME" "SHELL" "SSH Key AUTH" "PASSWD STATUS" "PASSWD CHANGED" "MAX PASSWD AGE"
            for ITEM in ${SHELL_USERS[@]}; do
                SHELL=$(grep "$SECTION_HEADER.*$ITEM" $f | awk -F ":" '{print $11}')
                SSH_KEY=$(grep "Users_AuthorizedKeys::.*$ITEM" $f)
                if [[ -n $SSH_KEY ]]; then
                    SSH_KEY="Enabled"
                else
                    SSH_KEY="Disabled"
                fi

                PASSWD_STATUS=$(grep "Users_UserStatus::$ITEM" $f | awk '{print $2}')
                case "${PASSWD_STATUS}" in
                    L)
                        PASSWD_STATUS="Locked"
                        ;;
                    P)
                        PASSWD_STATUS="Enabled"
                        ;;
                    NP)
                        PASSWD_STATUS="No Password"
                        ;;
                    *)
                        PASSWD_STATUS="Unknown"
                        ;;
                esac

                PASSWD_CHANGED=$(grep "Users_UserStatus::$ITEM" $f | awk '{print $3}')
                PASSWD_MAX_AGE=$(grep "Users_UserStatus::$ITEM" $f | awk '{print $5}')

                SAVEIFS=$IFS
                IFS=':::'
                printf "\t\t\t%-${LONGEST_USER}s%-${LONGEST_SHELL}s%-${SSH_WIDTH}s%-${PASSWD_WIDTH}s%-${PASSWD_WIDTH}s%-${PASSWD_WIDTH}s\n" $ITEM $SHELL $SSH_KEY $PASSWD_STATUS $PASSWD_CHANGED $PASSWD_MAX_AGE
                IFS=$SAVEIFS
            done

            # For each user account with an interactive shell, check the Users_LastLog90 report to see if they're there
            # NOTE: LastLog90 only shows those users who haven't logged in within the last 90 days (lastlog -b 90)
            printf "\t\tShell-enabled users without a login in the last 90 days (based on when kpnixaudit.sh was run)\n"

            SECTION_HEADER="Users_LastLog90"
            for ITEM in ${SHELL_USERS[@]}; do
                grep "$SECTION_HEADER::$ITEM" $f | awk -F "::" '{printf "\t\t\t%s\n",$2}'
            done
            printf "\n"
        else    # FILEOK=0
            if [[ "$KPNIXVERSION" = "0.0.0" ]]; then
                printf "\t%s does not appear to be a kpnixaudit.sh result file or it was created by a truly ancient version.  Skipping file.\n" $f
            else
                printf "\t%s was created by kpnixaudit.sh version %s.  Skipping file.\n" $f $KPNIXVERSION
            fi
        fi

    done
}

function PasswordPolicy {
    echo "STUB: Testing for Password Policy"
}

function Sudoers {
    echo "Testing Sudoers Config"

    # Local variables for holding the list of groups and users with sudoers ALL permissions
    local SUDOERS_GROUPS_ALL SUDOERS_USERS_ALL GROUP_NAME f RESULT GREP MATCHED LONGEST_FILENAME SECTION_HEADER ITEM f

    SECTION_HEADER="Users_SudoersConfig::/etc/sudoers"
    LONGEST_FILENAME=$((`file-width.sh` + 1))
    MATCHED=0

    # Get this list of all users and groups in the /etc/sudoers and /etc/sudoers.d/* files
    readarray SUDOERS_USERS_ALL <<< $(grep "$SECTION_HEADER.*ALL=" * | grep "sudoers.*::[A-Za-z]" | awk -F "::" '{print $3}' | awk '{print $1}' | sort -u)
    readarray SUDOERS_GROUPS_ALL <<< $(grep "$SECTION_HEADER.*ALL=" * | grep "sudoers.*::%[A-Za-z]" | awk -F "::" '{print $3}' | awk '{print $1}' | sort -u)
    
    # Print the list of users (don't start with a %)
    printf "\tUsers with sudoers ALL permissions:\n" 
        for ITEM in ${SUDOERS_USERS_ALL[@]}; do
            printf "\t\t%s\n" $ITEM
            grep -l "$SECTION_HEADER.*$ITEM" * | awk '{printf "\t\t\t%s\n",$0}'
        done
    
    # Print the list of groups as well as the group membership list for each sampled system
    printf "\tGroups with sudoers ALL permissions:\n" 
        for ITEM in ${SUDOERS_GROUPS_ALL[@]}; do
            GROUP_NAME=$(echo $ITEM | tr -d "%")
            printf "\t\t%s\n" $GROUP_NAME

            SECTION_HEADER="Users_SudoersConfig::/etc/sudoers"

            for f in $(grep -l "$SECTION_HEADER.*$ITEM" *); do
                SECTION_HEADER="Users_etcgroupContents::/etc/group::"
                RESULT=$(grep "$SECTION_HEADER.*$GROUP_NAME" $f | awk -F "::" '{printf "\t\t\t%s\n",$3}' | awk -F ":" '{print $4}')
                if [[ ${#RESULT} -gt 3 ]]; then
                    printf "\t\t\t%-${LONGEST_FILENAME}s%s\n" $f $RESULT
                    MATCHED=1
                fi
            done

            if [[ $MATCHED -eq 0 ]]; then
                printf "\t\t\tNo matches for group \"%s\" on any sampled systems\n" $GROUP_NAME
            fi
        done
    
    printf "\n"
    
}

CMD_OPTS=( "$@" )
OPTS_COUNT=$#

if [[ ${OPTS_COUNT} -eq 0 ]]; then
    usage
    exit 1
fi

#if no argument is passed this for loop will be skipped

for ((i=0; i<${OPTS_COUNT}; i++)); do
    OPTION="${CMD_OPTS[$i]}"
    case "${OPTION}" in
        -a|--all)
            for ITEM in ${OPTIONS_LIST[@]}; do
                MODULES[${ITEM}]=1
            done
            ;;
        -b|--blank)
            MODULES[BlankPasswords]=1
            ;;
        -u|--user-status)
            MODULES[UserStatus]=1
            ;;
        -s|--sudoers)
            MODULES[Sudoers]=1
            ;;
        -p|--passpol)
            MODULES[PasswordPolicy]=1
            ;;
        -v|--verbose)
            MODULES[Verbose]=1
            ;;
        -h|--help)
            usage
            exit 1
            ;;
        # --notused)
        #     #Option requires another parameter
        #     # "${opts[$((i+1))]}" is the immediately follwing option
        #     if [[ "${CMD_OPTS[$((i+1))]}" != "" ]]; then
        #         value="${CMD_OPTS[$((i+1))]}"
        #         echo "$value"
        #         #skips the nex adjacent argument as it is already taken
        #         ((i++))
        #     else
        #         usage
        #         EXITCODE=0
        #         exit ${EXITCODE}
        #     fi
        #     ;;

    *)
        #other unknown options
        echo Invalid option selected
        usage
        exit 1

        ;;
    esac
done

#Run everything that's been enabled on the command line
for ITEM in ${OPTIONS_LIST[@]}; do
    # Using a CASE statement for better readability even though an IF-THEN-ELSE would probably be better since there's only two options
    case ${ITEM} in
        Verbose|XL_*|All)
            # Do nothing if the ITEM is either "VERBOSE" or any of the "XL_" lines
            ;;
        *)
            if [[ ${MODULES[${ITEM}]} -eq 1 ]]; then
                ${ITEM}
            fi
            ;;
    esac
done