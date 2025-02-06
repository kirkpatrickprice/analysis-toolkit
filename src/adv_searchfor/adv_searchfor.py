#!/usr/bin/python3

import ast
import argparse                                                     # To handle command line arguments and usage
import copy
import glob                                                         # Used to match filespec to current directory contents
import importlib.resources as pkg_resources                         # To access the YAML configuration files
import os
import sys                                                          # Needed to test for basic pre-reqs like OS and Python version
import textwrap                                                     # Text handling routines
import time                                                         # To report run length for each check in YAML mode
import yaml                                                         # To parse the YAML configuration files

from sys import exit
from time import sleep

# Import what we need from this application's packages
from adv_searchfor import __version__
from adv_searchfor.kpat.common import (
    errorCodes,
    System,
    Search,
    error,
    getLongest,
    getSections,
    getSysFilterAttrs,
    getSysFilterComps,
    getConfigOptions,
    getSysFilterKeys,
    getErrorCodes,
)
from adv_searchfor.kpat import console

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
            Apply filters to exclude systems by specific attributes (e.g. Windows vs Linux, Debian vs RPM, script version, osVersion, etc)
    0.2.1   Fixed bug in short-circuit logic that was causing searches to bail out when a comment included the desired pattern
    0.2.2   Better error handling for UnicodeDecodeError message (e.g. when handling UTF-16 files)    
    0.2.3   Changes to support building with pyinstaller
    0.2.4   2023-06-25: Fixed unprintable characters bug
    0.3.0   2023-06-30: Added capabilities to process MacOS Auditor result files
    0.3.1   2023-07-03: Added rsDelimiter search config option to handle cases where OS tools don't always print blank values (e.g. MacOS dscl . -readall...)
            See 'audit-macos-users.yaml' for example use case
    0.3.2   2025-01-25: Make changes to support /src layout and Pypi distribution
    0.3.3   2025-02-06: Add Mint as a detected debPattern (common.py)
'''

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
            * Batch/YAML mode forces Excel output (see '''+defaultPath+''' directory)
            * Using -g (Regex groups) forces -o (only matching)
        '''),
    epilog=textwrap.dedent('''
        Returns EXITCODE=0 if successful.  Other EXITCODEs: '''+str(getErrorCodes()))
    )

# Define a custom action to store any sysFilter options as a dictionary for use in defining the Search
class StoreDictKeyPair(argparse.Action):
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values.split(","):
             k,v = kv.split("=")
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)


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
        searches can be defined in a single file to create a scripted review.  Excel results will be written to '''+defaultPath+'''<check_name>.xlsx.
    ''')
    )


outputControl = parser.add_argument_group(title='Output Control')
outputControl.add_argument(
    '-e', '--regexp', 
    dest='regex', 
    help=getConfigOptions()['regex'],
    )
outputControl.add_argument(
    '--name',
    dest='name',
    default='CommandLineSearch',
    type=str,
    help=getConfigOptions()['name'],
    )
outputControl.add_argument(
    '-m', '--count', 
    dest='maxResults', 
    default=-1, 
    type=int, 
    help=getConfigOptions()['maxResults'],
    metavar='INT',
    )
outputControl.add_argument(
    '--fullscan',
    dest='fullScan',
    help=getConfigOptions()['fullScan'],
    action='store_true',
    )
outputControl.add_argument(
    '-o', '--only-matching', 
    dest='onlyMatching',
    help=getConfigOptions()['onlyMatching'], 
    action='store_true',
    )
outputControl.add_argument(
    '-g', '--group',
    dest='groupList',
    #default=[0],
    action='append',
    type=str,
    #nargs='+',
    help=getConfigOptions()['groupList'],
    metavar='GROUPNAME [-g GROUPNAME...]',
    )
outputControl.add_argument(
    '--combine',
    dest='combine',
    help=getConfigOptions()['combine'],
    action='store_true',
    )
outputControl.add_argument(
    '-t', '--truncate', 
    dest='truncate',
    help=getConfigOptions()['truncate'],
    action='store_true',
    )
outputControl.add_argument(
    '--out-file', '-oF',
    dest='outFile',
    type=str,
    help=getConfigOptions()['outFile'],
    metavar='FILENAME',
    )
outputControl.add_argument(
    '--out-path', '-oP',
    dest='outPath',
    default=defaultPath,
    type=str,
    help=getConfigOptions()['outPath'],
    metavar='PATH',
    )
outputControl.add_argument(
    '-u', '--unique',
    action='store_true',
    dest='unique',
    help=getConfigOptions()['unique'],
    )
outputControl.add_argument(
    '--comment',
    dest='comment',
    type=str,
    help=getConfigOptions()['comment'],
    metavar="'COMMENT'",
    )
outputControl.add_argument(
    '-q', '--quiet',
    dest='quiet',
    action='store_true',
    help=getConfigOptions()['comment'],
    )

sysFilterControl = parser.add_argument_group(title='System Filters',)
sysFilterControl.add_argument(
    '--sys-filter',
    dest='sysFilter',
    type=ast.literal_eval,
    help=getConfigOptions()['sysFilter'],
    metavar="\"[{'attr'='validAttribute','comp'='eq|gt|lt|ge|le|in','value'='string'}...]\"",
    )

miscOptions = parser.add_argument_group(title='Misc. Options')
miscOptions.add_argument(
    '--list-sections', 
    dest='listSections', 
    help='List all section headings found in the current FILESPEC and then exit',
    action='store_true',
    )
miscOptions.add_argument(
    '--yaml-help',
    dest='yamlHelp',
    help='Print some helpful information for working with YAML and then exit.',
    action='store_true',
    )
miscOptions.add_argument(
    '--print-systems',
    dest='printSysDetails',
    action='store_true',
    help='Print system details.  Helpful for debugging system filters',
    )
miscOptions.add_argument(
    '--verbose',
    dest='verbose',
    action='store_true',
    help='Increase output verbosity.'
    )

class Systems(dict):
    def setVerbose(self, verbose):
        self.verbose=verbose
    
    def add(self, filename):
        self[filename]=System(filename, self.verbose)
        return self[filename]

    def search(self, filename):
        try:
            res=self[filename]
        except KeyError:
            res=False
        return res


def argsToConfig(args):
    '''
    Convert the ArgParse args object to a Search config object.  Mostly, there are a few items that need to be removed as they only have context from the command line
    '''

    config=copy.deepcopy(vars(args))                           # Mass-assign the args to the config dictionary
    
    # And then fix a few things
    if config['groupList']==None:
        config.pop('groupList')
    for k in ['confFile', 'listSections', 'yamlHelp', 'printSysDetails']:       # Remove these keys from the dictionary as they aren't needed in the Search object
        try:
            config.pop(k)
        except KeyError:
            pass

    return config

def parseFileSpec(fileSpec):
    '''
    Receives a file spec and returns a list of systems (class System) that match the spec

    NOTE: uses and makes changes to the GLOBAL AllSystems dictionary
    '''

    global AllSystems

    # Expand the filespec into a list of files.  Print an error and exit if there aren't any matching files
    files=glob.glob(fileSpec)

    if not files:
        error('No files match the provided filespec ("', fileSpec, '").')
        print()
        parser.print_usage()
        exit(errorCodes['noFiles'])

    systems=[]
    for file in files:
        found=AllSystems.search(file)
        if not found:
            systems.append(AllSystems.add(file))
        else:
            systems.append(found)

    return systems


def yamlParse(confFile, args=None):
    '''
    Receives a YAML configuration file and returns a list of configuration dictionaries.  The dictionaries will be ready to be passed to the Search object.
    '''

    global configNames
    globalConfig={}
    configs=[]
    dupesFound=False
    #If the provided confFile doesn't exist in the current directory and does not include path-y characters, then get the confFile from the package resources
    if not os.path.exists(confFile) and confFile.find('/') == -1:
        # Split and rejoin the program's root path -- minus the program name
        confPath=pkg_resources.files('adv_searchfor').joinpath('conf.d')
        confFile=os.path.join(confPath, confFile)
    
    yamlDir=os.path.abspath(os.path.dirname(confFile))
    print ('Parsing YAML file: ', confFile)
    # Import and process the YAML configuration file
    try:
        with open(confFile) as file:
            configYAML=yaml.safe_load(file)
    except FileNotFoundError:
        error("YAML file not found: "+confFile)
        exit(errorCodes['generalError'])
    except yaml.parser.ParserError as e:
        error("YAML Parsing Error")
        error(str(e))
        exit(errorCodes['invalidConfig'])

    for configSection in configYAML.keys():
        if configSection.startswith('global'):
            for key in configYAML[configSection]:
                globalConfig[key]=configYAML[configSection][key]
        elif configSection.startswith('include'):                       # If we've hit an include* section, process the additional files
            for file in configYAML[configSection]['files']:
                configs+=yamlParse(os.path.join(yamlDir, file), args)         # Append each file's configs to this one
        else:
            config=argsToConfig(args)                                   # Start with the command line options as defaults
            config['name']=configSection
            config['outFile']=configSection

            for globalKey in globalConfig.keys():                         # Assign any globally-assigned keys to the current config
                config[globalKey]=globalConfig[globalKey]

            for key in configYAML[configSection]:                       # Override the command line options if defined in the YAML section
                config[key]=configYAML[configSection][key]

            config['systems']=parseFileSpec(config['fileSpec'])
            config.pop('fileSpec')

            # Check if the config name has been added already - this can only happen when including YAML configs
            # This will cause a conflict in saved file names and maybe some other things
            if not config['name'] in configNames:
                configs.append(config)
                configNames.add(config['name'])
            else:
                error('Conflicting configuration names found: '+config['name'])
                dupesFound=True

    if dupesFound:
        error('Rename these configurations within your included YAML files')
        exit(errorCodes['invalidConfig'])

    return configs



##############################################################
##################### Let's get started ######################
##############################################################

# Create a couple of GLOBALs to store store some stuff in
# Yes, it's sloppy to make this a global, but it's the easiest way to pass the systems around
AllSystems=Systems()
configNames=set()                           # Using a global set to capture the unique names for each config

def main():
    '''
    Main function to handle command line arguments and start the search
    '''

    global AllSystems

    # Capture the start time
    startTime=time.time()

    # Process command line arguments
    args=parser.parse_args()
    AllSystems.setVerbose(args.verbose)
    if args.verbose:
        print(args)

    # Get the screen geometry for use throughout
    screenXY=console.getTerminalSize()

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
                print ('\nQuitting...')
                exit(0)


    # Branch based on listSections, Regex, or confFile usage modes
    if args.yamlHelp:
        optionsText={}
        for option in [getConfigOptions, getSysFilterKeys, getSysFilterAttrs, getSysFilterComps]:
            optionsText[option.__name__]=''
            D=option()
            longest=getLongest(list(D.keys()))
            lineCount=0
            for key in sorted(list(D.keys())):
                lineCount+=1
                if lineCount>1:                                         # Preserve indentation when printing
                    optionsText[option.__name__]+=f'    '
                if key == 'systems':
                    optionsText[option.__name__]+=f'%-{longest+2}s%s\n' % ('fileSpec', 'A glob-able file specification such as "myfiles*.txt"')
                else:
                    optionsText[option.__name__]+=f'%-{longest+2}s%s\n' % (key, option()[key])
        
        text=textwrap.dedent('''\
        YAML mode allows you to store your searches for reuse later, for instance when working the same client next year or for a set of general purpose content to use in all audits.

        A YAML file is just a text file with a ".yaml" extension.  Two all-purpose YAML files are provided as part of the Analysis Toolkit:
            .../conf.d
                audit-windows.yaml      Set of searches appropriate for use with Windows systems
                audit-linux.yaml        Set of searches appropriate for use with Linux systems

        Reference these files for the basic structure of what a configuration section should look like.  There are also examples of most (all?) options that you can model your own after.
        
        You can also create your own, but it is strongly recommended to store them somewhere else besides in the Analysis Toolkit folder as this location will likely be overwritten upon the next update.

        You can also include the contents in other YAML files by using the "include_<unique_but_arbitrary_name>:" section within your own files.
            myfile.yaml
                include_audit_windows:
                    files:
                    - audit-windows.yaml

                my_custom_check:
                regex: 'an awesome search pattern'
                ...more options
        
        This will bring in all of the checks in 'audit-windows.yaml' and the tool knows to look in it's conf.d folder if not path info is provided.  For anything not including the conf.d folder, you'll need to provide path info.  In fact, audit-windows.yaml and audit-linux.yaml both use this method to keep the configs easier to read and so that you can run just a subset of the checks if you'd like.
        
        There are help sections at the top of each of the provided YAML files, but the most authoritative list of available options is provided here.

        #####################################
        #### VALID CONFIG SECTION OPTIONS ###
        #####################################
        '''+optionsText['getConfigOptions']+'''
        
        #####################################
        ####### VALID SYSFILTER KEYS ########
        #####################################
        '''+optionsText['getSysFilterKeys']+'''

        #####################################
        #### VALID SYSFILTER ATTRIBUTES #####
        #####################################
        '''+optionsText['getSysFilterAttrs']+'''

        #####################################
        ## VALID SYSFILTER COMPARISON OPS ###
        #####################################
        '''+optionsText['getSysFilterComps']+'''
        ''').splitlines()
        for line in text:
            if line=='':
                print()
            else:
                wrapped=textwrap.wrap(line, width=screenXY[0], replace_whitespace=False)
                for wrappedLine in wrapped:
                    print(wrappedLine)    
        exit(0)
    elif args.listSections:
        sections=getSections(glob.glob(args.fileSpec))
        for section in sections:
            print(section)
        exit(0)
    elif args.printSysDetails:
        systems=parseFileSpec(args.fileSpec)          # Build a list of systems from the matching files, and iterate through them
        for system in systems:
            print(system)
        print('\nTotal systems: %d' % len(systems))
        exit(0)
    elif args.regex:

        config=argsToConfig(args)
        config['systems']=parseFileSpec(config['fileSpec'])                                     # Convert fileSpec into systems
        config.pop('fileSpec')                                                                  # Remove fileSpec from the dictionary as we don't need it now


        # The following is for testing a regexc that couldn't be passed through the debugger and needs to be removed before going into production
        # error('SPECIAL REGEX IN PLACE')
        # config['regex'] = r'System_RunningProcesses::(ProcessName\s+:(?P<processName>.*)|Path\s+:(?P<path>.*)|(Company\s+:(?P<company>.*))|(Product\s+:(?P<product>.*)))'
        
        search=Search(config)
        search.findResults()
        if search.results:
            search.toScreen()
            if args.outFile:
                search.toExcel()
        else:
            error('No results found')
            exit(errorCodes['noFiles'])
        
        exit(0)
    elif args.confFile:
        configs=yamlParse(args.confFile, args)

        for config in configs:
            search=Search(config)
            search.findResults()
            search.toScreen()
            if search.results:
                try:
                    if len(config['outFile']) > 0:
                        search.toExcel()
                except AttributeError:
                    if config['verbose']:
                        error('Skipping Excel output')
            

        # # Clean up the directory if it already exists
        # if os.path.exists(defaultPath):
        #     error(defaultPath,' directory already exists.  Existing files will be replaced.  Press CTRL-C within 5 seconds to abort...')
        #     sleep(5)

        # # Check if the Excel output directory exists and create it if needed
        # if not os.path.exists(defaultPath):
        #     os.makedirs(defaultPath)

        exit()
    else:
        error('REGEX, CONFFILE or LISTSECTIONS is required.')
        print()
        parser.print_usage()
        exit(errorCodes['generalError'])




    if args.confFile:
        import yaml

        confFile=args.confFile



    print('Total time: %s' % (time.strftime('%H:%M:%S', time.gmtime(time.time() - startTime))))

if __name__ == '__main__':
    main()