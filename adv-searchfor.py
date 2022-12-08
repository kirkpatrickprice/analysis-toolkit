#!/usr/bin/python3

version="0.2.0"

# Import what we need from the kpat package
from kpat.common import errorCodes, System, Search, error, getSections
from kpat import console
import os
from time import sleep

# Set up some defaults that we need early on
defaultPath='saved/'

'''
Version History:
    0.1.0   Initial release
    0.1.1   Colorized the "no results found... deleting file" message in CSV mode
            Corrected the CSV file header line
    0.1.2   2022-11-04
            Fixed CSV export issue with non-printable characters in input files
    0.1.3   2022-11-11
            Added a short-circuit to stop processing files once we've moved beyond the interesting content.  Requires use of a "::" in the regex to identify the section we're looking for
    0.2.0   Rewrite to use OOP -- eases managing data and passing info around
            Export to Excel instad CSV files
            Unique columns whenever groupLists are provided
            Combine results from mulitple lines in the source files into a single row
'''

import argparse                                                     # To handle command line arguments and usage
import sys                                                          # Needed to test for basic pre-reqs like OS and Python version
import glob                                                         # Used to match filespec to current directory contents
import textwrap                                                     # Text handling routines
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
            * Batch/YAML mode forces CSV output (see '''+defaultPath+''' directory)
            * Using -g (Regex groups) forces -o (only matching)
        '''),
    epilog=textwrap.dedent('''
        Returns EXITCODE=0 if successful.  Examine source code for "err_*" for other exit codes that could be returned (hint: they're at the very top)
        ''')
    )

inputControl = parser.add_argument_group(title='Input Control')
inputControl.add_argument(
    '-f', '--filespec', 
    dest='fileSpec', 
    default='*.txt', 
    help='Optional file spec (single or glob matching) to process (default=*.txt).  NOTE: filespec must be enclosed in single- or double-quotes'
    )
inputControl.add_argument(
    '-c', '--conf', '--yaml',
    dest='confFile',
    help=textwrap.dedent('''
        Provide a YAML configuration file to specify the options.  If only a file name, assumes analysis-toolit/conf.d location.  Multiple 
        searches can be defined in a single file to create a scripted review.  CSV results will be written to '''+defaultPath+'''<check_name>.csv.
    ''')
    )


outputControl = parser.add_argument_group(title='Output Control')
outputControl.add_argument(
    '-e', '--regexp', 
    dest='regex', 
    help='Regular expression to search for (CaSeInSenSiTiVe).'
    )
outputControl.add_argument(
    '--name',
    dest='name',
    default='CommandLineSearch',
    type=str,
    help='Give the search a name.  This will be used as the name of the Excel table and worksheet.'
    )
outputControl.add_argument(
    '-m', '--count', 
    dest='maxResults', 
    default=0, 
    type=int, 
    help='Number of matches from each file to return (default = 0/ALL)'
    )
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
    action='store_true'
    )
outputControl.add_argument(
    '-g', '--group',
    dest='groupList',
    #default=[0],
    action='append',
    type=str,
    #nargs='+',
    help='Regex group to display, if groups are used (default=0/ALL).  Must be used with -o / --only-matching')
outputControl.add_argument(
    '--combine',
    dest='combine',
    help='Combine the results from multiple lines in the source file to one row in the search results.',
    action='store_true'
    )
outputControl.add_argument(
    '-t', '--truncate', 
    dest='truncate',
    help='Truncate lines to fit current screen width.  Does not affect CSV output.',
    action='store_true'
    )
outputControl.add_argument(
    '--out-file', '-oF',
    dest='outFile',
    type=str,
    help='Create an Excel output of the results in the "saved" folder (override with --outPath).  When using YAML config files, results will always be saved.'
    )
outputControl.add_argument(
    '--out-path', '-oP',
    dest='outPath',
    default=defaultPath,
    type=str,
    help='Specify the folder for saved files (default="saved/")'
)
outputControl.add_argument(
    '-u', '--unique',
    action='store_true',
    dest='unique',
    help='Only display each unique value once / similar to "sort -u".'
)
outputControl.add_argument(
    '--comment',
    dest='comment',
    type=str,
    help='Comment to add to the Excel output to explain how to use these search results'
    )
outputControl.add_argument(
    '-q', '--quiet',
    dest='quiet',
    action='store_true',
    help='Quiet mode -- suppress screen output except status messages / especially helpful in YAML mode or with CSV output'
)


miscOptions = parser.add_argument_group(title='Misc. Options')
miscOptions.add_argument(
    '--list', 
    dest='listSections', 
    help='List all section headings found in the current FILESPEC',
    action='store_true'
    )


##############################################################
##################### Let's get started ######################
##############################################################

# Capture the start time
startTime=time.time()

# Process command line arguments
args=parser.parse_args()

# Get the screen geometry for use throughout
screenXY=console.getTerminalSize()

# Expand the filespec into a list of files.  Print an error and exit if there aren't any matching files
files=glob.glob(args.fileSpec)

if not files:
    error('No files match the provided filespec ("', args.fileSpec, '").')
    print()
    parser.print_usage()
    exit(errorCodes['noFiles'])

# Check if results will be output and warn if the folder already exists
if args.outFile or args.confFile:
    outPath, outFile=args.outPath, args.outFile
    
    # Fix outPath if it doesn't already end in a slash
    if not outPath.endswith('/'):
        outPath+='/'
    
    # Warn if the results folder already exists
    if os.path.exists(outPath):
        sleepTime=5
        error('%s folder already exists.  File will be replaced.  Press CTRL-C within %d seconds to abort...' % (outPath, sleepTime))
        try:
            sleep(sleepTime)
        except KeyboardInterrupt:
            print ('Quitting...')
            exit(0)


# Branch based on listSections, Regex, or confFile usage modes
if args.listSections:
    sections=getSections(files)
    for section in sections:
        print(section)
    exit(0)
elif args.regex:
    systems=[System(f) for f in files]          # Build a list of systems from the matching files
    config=vars(args)                           # Mass-assign the args to the config dictionary
    
    # And then fix a few things
    config['systems']=systems
    if config['groupList']==None:
        config.pop('groupList')
    for k in ['fileSpec', 'confFile', 'listSections']:
        config.pop(k)
    config['regex'] = r'System_RunningProcesses::(ProcessName\s+:(?P<processName>.*)|Path\s+:(?P<path>.*)|(Company\s+:(?P<company>.*))|(Product\s+:(?P<product>.*)))'
    
    search=Search(config)
    search.findResults()
    if search.results:
        search.toScreen()
        if args.outFile:
            search.toExcel()
    else:
        error('No results found')
    
    exit()
elif args.confFile:
    # Stub for YAML mode
    print('YAML mode')
    exit()
else:
    error('REGEX, CONFFILE or LISTSECTIONS is required.')
    print()
    parser.print_usage()
    exit(errorCodes['generalError'])



if args.groupList != [0] and not args.onlyMatching:
    error('Groups option was specified. Enabling --only-matching')
    args.onlyMatching=True
    # print()
    # parser.print_usage()
    # exit(err_general)



# Print the list of sections from FILESPEC and exit
if args.listSections:
    sections=getSections(files)
    for section in sections:
        print(section)
    exit(0)

outFile=''

if not args.confFile:
    config={
        'files': files,
        'regex': args.regex,
        'maxResults': args.maxResults,
        'outFile': outFile,
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
    if os.path.exists(defaultPath):
        error(defaultPath,' directory already exists.  Existing files will be replaced.  Press CTRL-C within 5 seconds to abort...')
        sleep(5)

    # Check if the CSV output directory exists and create it if needed
    if not os.path.exists(defaultPath):
        os.makedirs(defaultPath)
    
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
            'outFile': defaultPath+configSection+'.csv',
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
            error('Zero matches found. Removing ',config['outFile'])
            os.remove(config['outFile'])

print('Total time: %s' % (time.strftime('%H:%M:%S', time.gmtime(time.time() - startTime))))