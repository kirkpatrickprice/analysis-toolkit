#!/bin/python3

import re
import os
import textwrap
import sys
from colorama import Fore
import console
import string


errorCodes = {
    'invalidConfig': 1024,
    'generalError': 1023,
    'noResults': 1,
    'noFiles': 2,
}

class Search:
    def __init__(self, config):
        '''
        Inputs:
            Config      Dictionary containing the parameters of the search
                name                String              A name for the search config
                systems             List: Class System  Systems to which to apply the search
                regex               Raw string          Python-compatible regex to use https://docs.python.org/3/howto/regex.html
                maxResults          Integer             Maximum number of results to return per System (default: 0 - unlimited)
                onlyMatching        Boolean             Limit the RE match to only the text that matches the RE (default: full line)
                unique              Boolean             Only display one instance of each match 
                groupList           List                Regex groups to display -- supports both PCRE group nums and Python named groups (?P<groupName>regex)
                truncate            Boolean             Truncate the screen output to display width
                quiet               Boolean             Suppress output display to summary info only
                fullScan            Boolean             Override the search short-circuit logic to always scan the entire System.filename
                combine             Boolean             Combine results from across multiple lines to form a single record (only valid if groupList is specified)
                                                        e.g. matching Windows ProductName, ReleaseId, CurrentBuild, and UBR code
                comment             String              A helpful comment that will be added to the output file to describe how
                                                        to use this particular set of search results
        '''

        # Define the list of possible options.  Used later to determine if, e.g., the YAML file has an error in it
        configOptions = [
            'name',
            'systems',
            'regex',
            'maxResults',
            'onlyMatching',
            'unique',
            'groupList',
            'truncate',
            'quiet',
            'fullScan',
            'combine',
            'comment',
        ]
        # Set up a default configuration -- systems and regex must be provided so no defaults are set
        self.config = {
            'name': 'Manual',
            'maxResults': 0,
            'onlyMatching': False,
            'unique': False,
            'truncate': False,
            'quiet': False,
            'fullScan': False,
            'combine': False,
        }

        # Set any user-provided config options
        for key in config.keys():
            if key in configOptions:
                self.config[key] = config[key]
            else:
                error('Invalid search config key [%s]' % key)
                exit(errorCodes['invalidConfig'])
        
        # Check if 'systems' has been defined and quit with an error if not
        try:
            self.config['systems']
        except KeyError:
            error('Search config requires Systems to search')
            exit(errorCodes['invalidConfig'])
        else:
            if type(self.config['systems']) != list:                    # If a single System object was passed, then make it a list
                self.config['systems'] = [self.config['systems']]       # Later, findResults expects a list to iterate over

        # Check if 'regex' has been defined and quit with an error if not
        try:
            self.config['regex']
        except KeyError:
            error('Search config requires regular expression')
            exit(errorCodes['invalidConfig'])

        if self.config['unique'] and not self.config['onlyMatching']:           # Unique requires onlyMatching
            self.config['onlyMatching'] = True
            error('Unique was enabled.  Forcing onlyMatching...')

        # If groupList contains any entries, force onlyMatching to be True
        try:
            self.config['groupList']
        except KeyError:                            # If groupList is not defined, but onlyMatching is defined...
            if self.config['onlyMatching']:
                error('Search config includes onlyMatching, but groupList is undefined')
                exit(errorCodes['invalidConfig'])
        else:                                       # If groupList is defined, then always set onlyMatching to true
            if not self.config['onlyMatching']:
                self.config['onlyMatching'] = True
                error('groupList was providing.  Forcing onlyMatching...')

    def printConfig(self):
        '''
        Prints a prettified list of name/vaule pairs in the Search.config dictionary

        Returns None
        '''

        colWidth=getLongest(list(self.config.keys()))
        for key in sorted(self.config.keys()):
            if key == 'systems':
                sysList=[]
                for system in self.config['systems']:
                    sysList.append(system.getSystemName())
                content='['+', '.join(sysList)+']'
            else:
                content=str(self.config[key])
            print(f'%-{colWidth}s: %s' % (key, content))
        
        return None

    def getRegex(self):
        '''
        Returns the regular expression in the Search.config dictionary
        '''
        return self.config['regex']

    def getName(self):
        return self.config['name']

    def findResults(self):
        '''
            Inputs:
                Self        Class: Search       The search object to take action against

            Outputs:
                self.results                            List of results consisting of a dictionary of each result
                    system              Class: System   Reference to the System where the result was found
                    result | groupNames String          The matching results.  will be a one item dictionary with key 'Results' OR
                                                        a dictionary key for each groupname that was provided in 
                                                        Search.config['grounName']
        '''
        def combineResults(results):
            '''
                Inputs:
                    results         List of results         List of one-item dictionaries for each groupList group

                Outputs
                    combinedResults Dictionary of results   One list item where each groupList value is comined into a dictionary
            '''
            combinedResults={}
            for result in results:
                for key in result.keys():
                    combinedResults[key]=result[key]
            return [combinedResults]

        # Create a short-circuit detection so that once we move beyond the desired section in the file, we stop looking
        desiredSectionRegex=None
        desiredSectionPattern=None 
        limitToSection=False
        if self.getRegex().find('::') > 0 and not self.config['fullScan'] and self.config['maxResults'] == 0:
            desiredSectionRegex=self.getRegex().split('::')[0]

            # If the regex begins with a caret anchor, then drop it as some of our lines we want could have other text at the beginning
            if desiredSectionRegex[0] == '^':
                desiredSectionRegex=desiredSectionRegex[1:]
            
            # We can only short circuit if these regex syntax characters are balanced
            parenBalance=desiredSectionRegex.count('(') - desiredSectionRegex.count(')')
            curlyBalance=desiredSectionRegex.count('{') - desiredSectionRegex.count('}')
            squareBalance=desiredSectionRegex.count('[') - desiredSectionRegex.count(']')
            if parenBalance == 0 and curlyBalance == 0 and squareBalance == 0:
                desiredSectionPattern=re.compile(desiredSectionRegex, re.IGNORECASE)
                limitToSection=True
        
        # Matches the provided pattern
        pattern=re.compile(self.getRegex(), re.IGNORECASE)
        
        # Matches comment lines and [BEGIN], [CISReference], etc.
        commentsPattern=re.compile(r'^###|^#\[.*\]:|:: ###')
        
        # Matches lines that end in :: and zero or more white-space characters [ \t\r\n\f]
        blankLinePattern=re.compile(r'::\s*$')
        
        # Setup some more state variables
        res=[]

        for system in self.config['systems']:
            counter=0
            sectionFound=False
            inDesiredSection=None

            groupDict={}
            for line in open(system.getFilename()):
                #Capture the current line's section header
                if limitToSection:
                    inDesiredSection=desiredSectionPattern.search(line)
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
                    if self.config['onlyMatching']:
                        groupDict={}
                        groupDict['systemname'] = system.sysName

                        for group in self.config['groupList']:
                            if found.group(group):
                                foundText=found.group(group)

                                #remove any non-printable characters from the matching results
                                if not foundText.isprintable():
                                    printableText = filter(lambda x: x in string.printable, foundText)
                                    foundText = ''.join(list(printableText))

                                groupDict[group] = foundText.strip()

                        if self.config['unique']:
                            # If we're only trying to get the unique values, then try an index using a groupText.  It will throw a ValueError 
                            # if the value isn't found, in which case we'll add it to the results
                            try:
                                res.index(groupDict)
                            except ValueError:
                                res.append(groupDict)
                        else:
                            res.append(groupDict)
                    else:
                        # This paranthetical salad (inside-out) -- splices ('[1:]') the split line (on '::') to drop the first field (section header), 
                        # before rejoining on the :: field separator (at the beginning of the line)
                        foundText=line

                        #remove any non-printable characters from the matching results
                        if not foundText.isprintable():
                            printableText = filter(lambda x: x in string.printable, foundText)
                            foundText = ''.join(list(printableText))

                        res.append({
                            'SystemName': system.sysName,
                            'Results': '::'.join((foundText.split('::')[1:])).strip()
                        })

                    # If we're at the limit of our results
                    if counter == self.config['maxResults']:
                        break
                
                if (sectionFound and not inDesiredSection and not isComment and not isBlankLine):
                    break
        
        # if this search config requests to combine the results, pass the results to the combine routine
        if self.config['combine']:
            res=combineResults(res)

        self.results=res

    def to_screen(self):
        results=self.results
        screenWidth=console.getTerminalSize()[0]
        minColWidth=12
        print('<>'*screenWidth)
        print('Name: %s' % self.getName())
        if not self.config['quiet']:
            truncate=self.config['truncate']
            whiteSpace=2                                # Number of spaces between columns

            #Set up the header row and column widths
            colWidth=getLongest(results, whiteSpace)
            try:
                colWidth[self.config['groupList'][-1]]-=whiteSpace          #Remove the pad from the last item in the groupList
            except KeyError:
                colWidth['Results']-=whiteSpace                             #If groupList wasn't used...
            reduceBy=1
            firstPass=True
            needShorter = False

            # Build the format string and the header row
            while firstPass or needShorter:                #Keep making the columns shorter until they fit on the available screenWidth
                totalWidth=0
                formatStr=''
                header=[]

                for col in colWidth:
                    if needShorter and colWidth[col] > minColWidth and colWidth[col] > len(col):    # make sure that a min column width is preserved and no shorter than the column heading
                        colWidth[col]-=reduceBy
                    formatStr+=f'%-{colWidth[col]-whiteSpace}s'+' '*whiteSpace
                    header+=[str(col).upper()]
                    totalWidth+=colWidth[col]
                firstPass=False
                needShorter=(totalWidth > screenWidth) and truncate

            formatStr=formatStr[:-whiteSpace]                #Remove the final whitespace from the end of the line
                    
            print(formatStr % tuple(header))
            print('='*totalWidth)

            for item in results:
                values=[]
                for key in item.keys():
                    value=item[key]
                    if len(value) > colWidth[key]:
                        value=value[:colWidth[key]-reduceBy-3]+'...'
                    values+=[value]
                print(formatStr % tuple(values))
        print('Results found: %d\n' % len(results))
        # Return everything except for the final new-line
        return True


class System(object):
    def __init__(self, filename):
        self.sysName = os.path.split(filename)[-1].replace('.txt', '')
        self.filename = filename
        self.scriptDetails = getReportVersion(self.getFilename())
        if self.scriptDetails[0] == 'KPNIXVERSION':
            self.OSFamily = 'Linux'
            self.producer = 'kpnixaudit'
        elif self.scriptDetails[0] == 'KPWINVERSION':
            self.OSFamily = 'Windows'
            self.producer = 'kpwinaudit'
            OSDetailsSearchConfig = {
                'systems'   : self,
                'regex'     : r'System_OSInfo::(ProductName\s+:\s+(?P<ProductName>[\w ]+))|(ReleaseId\s+:\s+(?P<ReleaseId>\w+))|(CurrentBuild\s+:\s+(?P<CurrentBuild>\d+))|(UBR\s+:\s+(?P<UBR>\d+))',
                'groupList' : [
                    'ProductName',
                    'ReleaseId',
                    'CurrentBuild',
                    'UBR',
                ],
                'maxResults': 4,
                'combine' : True,
                'onlyMatching': True,
            }
            OSDetails=Search(OSDetailsSearchConfig)
            OSDetails.findResults()
            self.productName=OSDetails.results[0]['ProductName']
            self.ReleaseID=OSDetails.results[0]['ReleaseId']
            self.CurrentBuild=OSDetails.results[0]['CurrentBuild']
            self.UBR=OSDetails.results[0]['UBR']
        else: 
            self.OSFamily = 'unknown'

    def __str__(self):
        
        res=''
        for item in self.__dict__:
            value=self.__dict__[item]
            if not item.startswith('__'):
                if item == 'scriptDetails':
                    res+=value[0]+': '+'.'.join(str(i) for i in value[1])+'\n'
                else:
                    res+=item+': '+value+'\n'
        
        return res

    def getSystemName(self):
        return self.sysName
    
    def getFilename(self):
        return self.filename

    def getOSFamily(self):
        return self.OSFamily

    def getScriptProducer(self):
        return self.producer
    
    def getScriptVersion(self):
        return self.scriptDetails[1]

def error(*pargs):
    '''
    Print an error to STDERR
    '''
   

    nativeColor='\033[m'

    # Textwrap.wrap only appears to accept a single text string for wrapping (unlike print('String', variable)).  So, we'll build the full string first.
    #Set the color to RED
    text=Fore.RED
    for arg in pargs:
        text+=str(arg)

    # Set the color back.
    text+=nativeColor

    lines=textwrap.wrap(text, width=console.getTerminalSize()[0])
    for line in lines:
        print(line, file=sys.stderr)

def getReportVersion(filename):
    '''
    Read the file to determine which audit script produced it -- KPNIXAUDIT or KPWINAUDIT.
    
    Returns a tuple with (ScriptType, Version) where:
        ScriptType  - KPNIXVERSION, KPWINVERSION, ... unknown
        Version     - a list of [major, minor, release] such as [0, 4, 3] for "0.4.3"
    '''

    found=False
    # The following regex matches
    #   producer:       "KP...VERSION"
    #   Non-capturing:  ": " (so we can throw it away)
    #   version:        Version string consisting of 3 sets of one or more digits separated by periods
    pattern=re.compile(r'(?P<producer>KP\w{3}VERSION)(?:: )(?P<version>\d+.\d+.\d+)')
    for line in open(filename):
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

def getLongest(data, pad=0):
    '''
    Inputs:
        data            ==> A list of either strings or dictionaries whose key-value pairs are also strings
        pad             ==> An optional pad to add (e.g. for whitespace between columns).

    Returns the longest item.  If data type is:
        List of strings         ==> The length of the longest item in the list
        List of Dictionaries    ==> A dictionary of the longest item for each key (includes both max(len(key)) and max(len(value)))

    If type(data) is not a list or if it's neither of strings or dictionaries, it will return type None, which should cause most
    calling code to fail

    NOTE: List elements are assumed to be homogenous -- the first item in the list is used to determine the list element type
    '''
    res=None                        # default res to None type
    if type(data) == list:
        if type(data[0]) == dict:
            res={}
            for item in data:
                for key in item.keys():
                    try:
                        res[key]
                    except KeyError:
                        res[key] = len(key) + pad
                    else:
                        if len(key) > res[key] - pad:
                            res[key] = len(key) + pad
                    
                    # Check if the key's value is longer than the key
                    if len(item[key]) > res[key] - pad:
                        res[key] = len(item[key]) + pad            
        elif type(data[0]) == str:
            res=len(max(data, key=len))+pad
    return res

if __name__ == '__main__':
    test=[
        System('/home/randy/downloads/Test/test01.txt'),
        System('/home/randy/downloads/Test/test02.txt'),
    ]
    print(test)
    configs=[
        {
            'systems': test,
            'regex': r'System_Services::(?!DisplayName)(?!--)(?P<servicename>(\w+\s)+)\s+(?P<status>Running|Stopped)\s+(?P<startuptype>.*)',
            'maxResults': 5,
            'onlyMatching': True,
            'groupList': [
                'servicename',
                'status',
                'startuptype',
            ],
            'truncate': True,
            'quiet': False,
            'comment': '''A list of Windows services, their current status and the their startup config.  Useful to confirm things like anti-virus, web servers, database servers, and other system details'''
        },
        {
            'name': 'WindowsUpdateHistory',
            'systems': test,
            'regex': r'System_WindowsUpdateHistory::.*(Cumulative|Security)\sUpdate',
            'maxResults': 10,
            'onlyMatching': False,
            'truncate': True,
            'quiet': False,
            'comment': '''A list of WindowsUpdate History log results filtered for Cumulative and Securty updates.  Useful to determine patching history'''
        },
    ]
    for config in configs:
        print('\n'+'<>'*50)
        search=Search(config)
        search.printConfig()
        search.findResults()
        search.to_screen()