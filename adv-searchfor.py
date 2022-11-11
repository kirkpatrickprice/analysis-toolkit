#!/usr/bin/python3

version="0.1.2"

# Set up the exit codes for different error conditions and other global variables
err_noresults=1
err_nofiles=2
err_general=999

defaultShortenFactor=.25                                                   # defaultShortenFactor is used when truncating the output.  It's the max column width for the file name.
csvPath='saved-csv/'                                                # Hard-coded path for exporting CSV files.  Future development to make this configurable from the command line.

'''
Version History:
    0.1.0   Initial release
    0.1.1   Colorized the "no results found... deleting file" message in CSV mode
            Corrected the CSV file header line
    0.1.2   2022-11-04
            Fixed CSV export issue with non-printable characters in input files
    0.1.3   2022-11-11
            Added a short-circuit to stop processing files once we've moved beyond the interesting content.  Requires use of a "::" in the regex to identify the section we're looking for
'''

import argparse                                                     # To handle command line arguments and usage
import sys                                                          # Needed to test for basic pre-reqs like OS and Python version
import glob                                                         # Used to match filespec to current directory contents
import re                                                           # Regular expression parser
import textwrap                                                     # Text handling routines
import csv                                                          # Import the CSV module so we can write the output to CSV as well...
import os                                                           # Import the OS module so can work with files and directories in the local file system
from time import sleep                                              # Grab the sleep function from time to support delays for user confirmation
import string                                                       # Needed to process matches for potentially unprintable characters
import time                                                         # To report run length for each check in YAML mode

# Set up the arguments that can be set on the command line
parser = argparse.ArgumentParser(
    prog=sys.argv[0].split('/')[-1], 
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
        Search the files in the current directory for a specified string.  Return a formatted list of the results.  
        The first column is file name (system name) where it was found.  The remainder of the line is the contents of the matching line.

        Where a similar option below is also implemented in GNU grep, the options have the same meaning.

        NOTES:
            * Either -e (command line mode) OR -c (YAML mode) is required.
            * Batch/YAML mode forces CSV output (see '''+csvPath+''' directory)
            * Using -g (Regex groups) forces -o (only matching)
        '''),
    epilog=textwrap.dedent('''
        Returns EXITCODE=0 if successful.  Examine source code for "err_*" for other exit codes that could be returned (hint: they're at the very top)
        '''))

inputControl = parser.add_argument_group(title='Input Control')
inputControl.add_argument(
    '-f', '--filespec', 
    dest='fileSpec', 
    default='*.txt', 
    help='Optional file spec (single or glob matching) to process (default=*.txt).  NOTE: filespec must be enclosed in single- or double-quotes')
inputControl.add_argument(
    '-c', '--conf', '--yaml',
    dest='confFile',
    help=textwrap.dedent('''
        Provide a YAML configuration file to specify the options.  If only a file name, assumes analysis-toolit/conf.d location.  Multiple 
        searches can be defined in a single file to create a scripted review.  CSV results will be written to '''+csvPath+'''<check_name>.csv.
    '''))


outputControl = parser.add_argument_group(title='Output Control')
outputControl.add_argument(
    '-e', '--regexp', 
    dest='regex', 
    help='Regular expression to search for (CaSeInSenSiTiVe).')
outputControl.add_argument(
    '-m', '--count', 
    dest='maxResults', 
    default=0, 
    type=int, 
    help='Number of matches from each file to return (default = 0/ALL)')
outputControl.add_argument(
    '--fullscan',
    dest='fullScan',
    help=textwrap.dedent('''
        Command line only: Override the short-circuit behavior to scan the entire file.  Recommended if you're testing a complex Regex expression until you 
        know you have the resulst you expect.  This is always OFF for YAML mode, but you can use the 'fullScan: True' setting to enabled it for specific checks.'''),
    action='store_true'
)
outputControl.add_argument(
    '-o', '--only-matching', 
    dest='onlyMatching',
    help=textwrap.dedent('''
        Only provide the matching string instead of the full line.  NOTE: Especially useful with -g / --group as this overrides any clean-up to remove the section
        header from the output.  Results will be an exact match of REGEXP.  Adds ''G#: '' to separate group numbers.'''), 
    action='store_true')
outputControl.add_argument(
    '-g', '--group',
    dest='groupList',
    default=[0],
    type=str,
    nargs='+',
    help='Regex group to display, if groups are used (default=0/ALL).  Must be used with -o / --only-matching')
outputControl.add_argument(
    '-t', '--truncate', 
    dest='truncate',
    help=textwrap.dedent('''
        Truncate lines to fit current screen width.  System name will be truncated to '''+str(int(defaultShortenFactor*100))+'''%% of screen width and the 
        results will fill the rest of the line.  Does not affect CSV output.'''), 
    action='store_true')
outputControl.add_argument(
    '--csv',
    dest='csvFile',
    type=str,
    help='Create a CSV output of the results.  Especially useful in batch (config-file) mode.  Results will be saved in "'+csvPath+'<csvFile>.csv".'
)
outputControl.add_argument(
    '-u', '--unique',
    action='store_true',
    dest='unique',
    help='Only display each unique value once / similar to "sort -u".'
)
outputControl.add_argument(
    '-q', '--quiet',
    dest='quiet',
    action='store_true',
    help='Quiet mode -- suppress screen output except status messages / especially helpful in YAML mode or with CSV output'
)


miscOptions = parser.add_argument_group(title='Misc. Options')
miscOptions.add_argument(
    '-d', '--debug', 
    dest='debug',
    help='Print extra debug messages.  Really only helpful for developing', 
    action='store_true')
miscOptions.add_argument(
    '--list', 
    dest='listSections', 
    help='List all section headings found in the current FILESPEC',
    action='store_true')


#############################################################
################# Define the necessary functions ############
#############################################################


def debug(*pargs, **kargs):
    '''
    Accept an arbitrary number of parameters for use in a print statement.  Any parameters that are valid in print() are acceptable.  
    Only prints if args.debug (Global var) is True.
    '''
    if args.debug:
        print(*pargs, **kargs)


def error(*pargs):
    '''
    Print an error to STDERR
    '''
    from colorama import Fore
    nativeColor='\033[m'

    # Textwrap.wrap only appears to accept a single text string for wrapping (unlike print('String', variable)).  So, we'll build the full string first.
    #Set the color to RED
    text=Fore.RED
    for arg in pargs:
        text+=arg

    # Set the color back.
    text+=nativeColor

    lines=textwrap.wrap(text, width=70)
    for line in lines:
        print(line, file=sys.stderr)

def getMaxWidth(l):
    '''
    Function to return the longest item in a list.
    '''
    longest=-1
    for item in (l):
        if len(item) > longest:
            longest=len(item)
    return longest

def getReportVersion(file):
    '''
    Read the first line of the file to determine which audit script produced it.
    
    Returns a tuple with (ScriptType, Version) where:
        ScriptType  - KPNIXVERSION, KPWINVERSION, etc.
        Version     - a list of [major, minor, release] such as [0, 4, 3] for "0.4.3"
    '''

    found=False
    # The following regex matches
    #   producer:       "KP...VERSION"
    #   Non-capturing:  ": " (so we can throw it away)
    #   version:        Version string consisting of 3 sets of one or more digits separated by periods
    pattern=re.compile(r'(?P<producer>KP.{3}VERSION)(?:: )(?P<version>\d+.\d+.\d+)')
    for line in open(file):
        match=pattern.search(line)
        if match:
            found=True
            reportType=match.group('producer')
            #Turn the version string into a list of integers instead of a list of strings consisting of numbers.
            reportVersion=[int(i) for i in match.group('version').split('.')]
            break

    if not found:
        reportType='unknown'
        reportVersion=None
    
    return (reportType, reportVersion)

def getSections(files):
    '''
    Get the list of identified sections (lines containining "[BEGIN]") for all of the files in the list.
    Uses a set to ensure that each item is listed only once.

    Returns an alphabetized list containing all items
    '''
    sections=set()
    pattern=re.compile(r'\[BEGIN\]')
    for file in files:
        counter=0
        reportType=getReportVersion(file)
        if reportType[0] == 'unknown':
            error('Skipping... unable to determine which script produced file "', file, '".')
            break

        for line in open(file):
            if pattern.search(line):
                if reportType[0] == 'KPNIXVERSION':
                    header=line.split(':')[-1].strip()
                elif reportType[0] == 'KPWINVERSION':
                    header=line.split(':')[0].strip()
                sections.add(header)
            counter+=1
    
    #Return an alphabetized list of sections
    return list(sorted(sections))

def findResults(regex, file, maxResults, onlyMatching, groupList, unique, fullScan):
    # Create a short-circuit detection so that once we move beyond the desired section in the file, we stop looking
    desiredSectionRegex=None
    desiredSectionPattern=None 
    limitToSection=False
    if regex.find('::') > 0 and not fullScan and maxResults == 0:
        desiredSectionRegex=regex.split('::')[0]

        # If the regex begins with a caret anchor, then drop it as some of our lines we want could have other text at the beginning
        if desiredSectionRegex[0] == '^':
            desiredSectionRegex=desiredSectionRegex[1:]
        
        # We can only short circuit if these regex syntax characters are balanced
        parenBalance=desiredSectionRegex.count('(') - desiredSectionRegex.count(')')
        curlyBalance=desiredSectionRegex.count('{') - desiredSectionRegex.count('}')
        squareBalance=desiredSectionRegex.count('[') - desiredSectionRegex.count(']')
        if parenBalance + curlyBalance + squareBalance == 0:
            desiredSectionPattern=re.compile(desiredSectionRegex, re.IGNORECASE)
            limitToSection=True
            debug('Desired section:', desiredSectionRegex)
    
    # Matches the provided pattern
    pattern=re.compile(regex, re.IGNORECASE)
    
    # Matches comment lines and [BEGIN], [CISReference], etc.
    commentsPattern=re.compile(r'^###|^#\[.*\]:|:: ###')
    
    # Matches lines that end in :: and zero or more white-space characters [ \t\r\n\f]
    blankLinePattern=re.compile(r'::\s*$')
    
    # Setup some more state variables
    counter=0
    res=[]
    sectionFound=False
    inDesiredSection=None

    for line in open(file):
        #Capture the current line's section header
        if limitToSection:
            inDesiredSection=desiredSectionPattern.search(line)
            debug('\nCurrent line:', line.strip())
            debug('Desired section:', desiredSectionRegex)
            if inDesiredSection:
                sectionFound=True
        found = pattern.search(line)
        isComment = commentsPattern.search(line)
        isBlankLine = blankLinePattern.search(line)
        if found and not isComment and not isBlankLine:
            counter+=1
            # # Capture the current section as the one we want and flag that we found what we're looking for
            # desiredSection=currentSection
            # sectionFound=True
            # If we're only supposed to grab the matching text...
            if onlyMatching:
                groupText=''
                for group in groupList:
                    # See if the group can be converted to an integer.  If so, numbered groups are in use.  Otherwise, they must be named groups.
                    try:
                        int(group)
                        groupText+='G'+str(group)+'='+found.group(group)+' '
                    except ValueError:
                        # If the try fails, it must be a string.
                        groupText+=str(group)+'='+found.group(group)+' '

                if unique:
                    # If we're only trying to get the unique values, then try an index using a groupText.  It will throw a ValueError if the value isn't found, in which case we'll add it to the results
                    try:
                        res.index(groupText)
                    except ValueError:
                        res.append(groupText)
                else:
                    res.append(groupText)
            else:
                # This paranthetical salad (inside-out) -- splices ('[1:]') the split line (on '::') to drop the first field (section header), 
                # before rejoining on the :: field separator (at the beginning of the line)
                res.append('::'.join((line.split('::')[1:])).strip())

            # If we're at the limit of our results
            if counter == maxResults:
                break
        
        if (sectionFound and not inDesiredSection and not isComment and not isBlankLine):
            break
    return res

def printMatches(regex, files, screenXY, csvFile, truncate, maxResults, onlyMatching, groupList, quiet=False, shortenFactor=defaultShortenFactor, unique=False, fullScan=False):
    '''
    Receives regex, list of files, truncate flag, shortenFactor, maxResults, onlyMatching flag, group numbers and screen geometry
    Prints one line for each result that includes the file name (system name) and the matching text from Regex and other output control options

    Returns a total count of hits found across the set of files
    '''

    #Get the max length of all of the files.
    fileColumnWidth=getMaxWidth(files)
    if csvFile:
        csvOutFile=open(csvFile, 'w')
        fieldnames=['System Name', 'Results']
        csvWriter=csv.DictWriter(csvOutFile, fieldnames=fieldnames)
        csvWriter.writeheader()
    if args.truncate:
        fileColumnWidth=min(fileColumnWidth, int(screenXY[0]*shortenFactor))

    debug('Max width of all files:', fileColumnWidth, "Truncate:", args.truncate)

    matchCount=0
    for file in files:
        matches=None
        if not getReportVersion(file)[0] == 'unknown':
            matches = findResults(regex=regex, file=file, maxResults=maxResults, onlyMatching=onlyMatching, groupList=groupList, unique=unique, fullScan=fullScan)
            for match in matches:
                # Clean up any non-printable characters that might be in the results
                if not match.isprintable():
                    printableMatch = filter(lambda x: x in string.printable, match)
                    match = ''.join(list(printableMatch))
                    error('WARNING: Potential corruption detected.')
                    error('File: ',file)
                    error('Match:',match)
                matchCount+=1
                if csvFile:
                    row={}
                    row['System Name']=file.replace('.txt', '')
                    row['Results']=match
                    csvWriter.writerow(row)
                if truncate:
                    resultsWidth=screenXY[0]-fileColumnWidth
                    if len(file) > fileColumnWidth:
                        file=file.replace('.txt', '')[:fileColumnWidth-5] + '...'
                    if len(match) > resultsWidth:
                        match=match[:resultsWidth-3] + '...'
                if not quiet:
                    line=f'%-{fileColumnWidth}s%s' % (file.replace('.txt', ''), match)
                    print(line)
    return(matchCount)
    csvWriter.close()

##############################################################
##################### Let's get started ######################
##############################################################

# Capture the start time
startTime=time.time()

# Process command line arguments
args=parser.parse_args()

# Print the args object if the debug switch was set
debug(args)


# Get the screen geometry for use throughout
import console
screenXY=console.getTerminalSize()
debug('Screensize:', screenXY)

# Check to make sure that either, listSections regex or confFile was used
if not (args.regex or args.confFile or args.listSections):
    error('Either REGEX or CONFFILE is required.')
    print()
    parser.print_usage()
    exit(err_general)



if args.groupList != [0] and not args.onlyMatching:
    error('Groups option was specified. Enabling --only-matching')
    args.onlyMatching=True
    # print()
    # parser.print_usage()
    # exit(err_general)


# Expand the filespec into a list of files.  Print an error and exit if there aren't any matching files
files=glob.glob(args.fileSpec)

if not files:
    error('No files match the provided filespec ("', args.fileSpec, '").')
    print()
    parser.print_usage()
    exit(err_nofiles)

# Print the list of sections from FILESPEC and exit
if args.listSections:
    sections=getSections(files)
    for section in sections:
        print(section)
    exit(0)

csvFile=''

if args.csvFile:
    # For now, the CSV file option only supports a file name -- no path names.  All results will be saved in the PWD/saved-csv/ directory
    csvFile=args.csvFile
    if csvFile.endswith('/'):
        error('Paths not currently supported in CSV export.  Only specify a file name.  Results will be saved in the '+csvPath+' directory.')
        print()
        parser.print_usage()
        exit(err_general)
    
    # Check if the file name ends with '.csv' and append if it does not
    if not csvFile.endswith('.csv'):
        csvFile+='.csv'
    
    # Finally, create the directory and assemble the full csvFile with path info
    if not os.path.exists(csvPath):
        os.makedirs(csvPath)

    csvFile=csvPath+csvFile
    if os.path.exists(csvPath):
        error(csvFile,'file already exists.  File will be replaced.  Press CTRL-C within 5 seconds to abort...')
        sleep(5)

if not args.confFile:
    config={
        'files': files,
        'regex': args.regex,
        'maxResults': args.maxResults,
        'csvFile': csvFile,
        'onlyMatching': args.onlyMatching,
        'unique': args.unique,
        'groupList': args.groupList,
        'truncate': args.truncate,
        'screenXY': screenXY,
        'quiet': args.quiet,
        'fullScan': args.fullScan}
    debug(config)
    matchCount=printMatches(**config)
            
    if matchCount == 0:
        error('No matching results found using pattern "', args.regex, '"')
        exit(err_noresults)
    else:
        print('Matches found:',matchCount)

if args.confFile:
    import yaml

    confFile=args.confFile

    #If the provided confFile does not include path-y characters, then prepend the conf.d directory to the overall path
    if confFile.find('/') == -1 and confFile.find('\\') == -1:
        # Split and rejoin the program's root path -- minus the program name
        confPath='/'.join((sys.argv[0]).split('/')[:-1])
        confFile=confPath+'/conf.d/'+confFile

    # Clean up the directory if it already exists
    if os.path.exists(csvPath):
        error(csvPath,' directory already exists.  Existing files will be replaced.  Press CTRL-C within 5 seconds to abort...')
        sleep(5)

    # Check if the CSV output directory exists and create it if needed
    if not os.path.exists(csvPath):
        os.makedirs(csvPath)
    
    # Import and process the YAML configuration file
    with open(confFile) as file:
        configYAML=yaml.safe_load(file)

    for configSection in configYAML.keys():
        sectionStartTime=time.time()
        fileSpec = args.fileSpec
        print('\n', '=' * 50, sep='')

        config={
            'regex': args.regex,
            'maxResults': args.maxResults,
            'csvFile': csvPath+configSection+'.csv',
            'onlyMatching': args.onlyMatching,
            'unique': args.unique,
            'groupList': args.groupList,
            'truncate': args.truncate,
            'screenXY': screenXY,
            'quiet': args.quiet,
            'fullScan': args.fullScan}
        for key in configYAML[configSection]:
            if key == 'fileSpec': 
                fileSpec=configYAML[configSection][key]
            else: 
                config[key]=configYAML[configSection][key]

        debug(config)

        # Automatically enable onlyMatching if a groupList is used
        if config['groupList'] != [0]:
            config['onlyMatching'] = True

        config['files']=glob.glob(fileSpec)
        if not config['files']:
            error('No files match the provided filespec ("', args.fileSpec, '").')
            print()
            parser.print_usage()
            exit(err_nofiles)
        print('Checking:', configSection)
        matchCount=printMatches(**config)
        # Remove the CSV file there weren't any matches written
        print('Matches found:',matchCount)
        print('Section time: %s' % (time.strftime('%H:%M:%S', time.gmtime(time.time() - sectionStartTime))))
        print('Elapsed time: %s' % (time.strftime('%H:%M:%S', time.gmtime(time.time() - startTime))))
        if matchCount == 0:
            error('Zero matches found. Removing ',config['csvFile'])
            os.remove(config['csvFile'])

print('Total time: %s' % (time.strftime('%H:%M:%S', time.gmtime(time.time() - startTime))))