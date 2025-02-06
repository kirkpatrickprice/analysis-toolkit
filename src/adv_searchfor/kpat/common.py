#!/bin/python3

import re
import os
import string
import sys
import textwrap

from sys import exit

import xlsxwriter
from colorama import Fore

import adv_searchfor.kpat.console as console

def getErrorCodes():
    return {
        'invalidConfig': 126,
        'generalError': 127,
        'noResults': 1,
        'noFiles': 2,
    }

errorCodes = getErrorCodes()

class Search:
    def __init__(self, config):
        '''
        Inputs:
            Config      Dictionary containing the parameters of the search
                See definition in getConfigOptions, getSysFilterAttrs, getSysFilterKeys, and getSysFilterComps
        '''

        def compareAttr(f, system):
            '''
            Compares attributes provided in a sysFilter dictionary against a system object.  Returns True or False
            '''
            def compareList(value1, comp, value2):
                '''
                Compares list elements 
                '''
                
                if len(value1) == len(value2):
                    tests=[]                              # Create a list to hold the results.  We'll convert it to a single Boolean at the end
                    for i in range(len(value1)):
                        if comp == 'eq':
                            tests.append(value1 == value2)
                        elif comp == 'gt':
                            tests.append(value1 > value2)
                        elif comp == 'lt':
                            tests.append(value1 < value2)
                        elif comp == 'ge':
                            tests.append(value1 >= value2)
                        elif comp == 'le':
                            tests.append(value1 <= value2)
                        elif comp == 'in':
                            tests.append(value1 in value2)

                    res=all(tests)                   # Perform a boolean AND on all items in res and return the final result
                else:
                    res=False

                return res

            comp=f['comp']
            value2=f['value']
            try:
                value1=system.__getattribute__(f['attr'])
            except AttributeError:                                  # If the provided System attribute doesn't exist, return False
                return False
                        
            if type(value1) == list:                             # If it's a List, we need to compare each list element in 
                res=compareList(value1, comp, value2)
            else:
                if comp == 'eq':
                    res=value1 == value2
                elif comp == 'gt':
                    res=value1 > value2
                elif comp == 'lt':
                    res=value1 < value2
                elif comp == 'ge':
                    res=value2 >= value1
                elif comp == 'le':
                    res=value1 <= value2
                elif comp == 'in':
                    res=value2 in value1

            return res

        # Define the list of possible options.  Used later to determine if, e.g., the YAML file has an error in it
        configOptions = list(getConfigOptions().keys())

        # Define the list of sysFilter keys
        sysFilterOptions= list(getSysFilterKeys().keys())

        #Define the list of comparators that can be used
        compOptions= list(getSysFilterComps().keys())

        # Define the list of attr options
        attrOptions= list(getSysFilterAttrs().keys())

        # Set up a default configuration -- systems and regex must be provided so no defaults are set
        self.config = {
            'name': '',
            'rsDelimiter': None,
            'maxResults': -1,
            'onlyMatching': False,
            'unique': False,
            'truncate': False,
            'quiet': False,
            'fullScan': False,
            'combine': False,
            'outPath': 'saved',
            'verbose': False,
        }

        try:
            if config['sysFilter'] is None:                     # sysFilter can come through as a None (null) object in a few scenarios.  Remove it.
                config.pop('sysFilter')
        except KeyError:
            pass

        # Set any user-provided config options
        for key in config.keys():
            if key in configOptions:
                if key == 'sysFilter':
                    counter=0
                    for filterItem in config[key]:
                        for filterKey in filterItem.keys():
                            if filterKey not in sysFilterOptions:
                                error('sysFilter key invalid: %s' % filterKey)
                                error('Should be one of: %s' % sysFilterOptions)
                                exit(errorCodes['invalidConfig'])
                            elif filterKey == 'attr' and filterItem[filterKey] not in attrOptions:
                                error('sysFilter attr invalid: %s' % filterItem[filterKey])
                                error('Should be one of: %s' % attrOptions)
                                exit(errorCodes['invalidConfig'])
                            elif filterKey == 'comp' and filterItem[filterKey] not in compOptions:
                                error('sysFilter comparison invalid: %s' % filterItem[filterKey])
                                error('Should be one of: %s' % compOptions)
                                exit(errorCodes['invalidConfig'])
                            attr=filterItem['attr']
                            val=filterItem['value']

                            # Search.findResults expects version-type data to be represented in a list
                            if (attr == 'osVersion' or attr == 'kpnixversion' or attr == 'kpwinversion') and not type(val) == list:
                                try:
                                    config['sysFilter'][counter]['value'] = [int(x) for x in val.split('.')]
                                except:
                                    error('Error pasring version string info: %s %s.' % (attr, val))
                                    exit(errorCodes['invalidConfig'])
                        counter+=1

                self.config[key] = config[key]
            else:
                error('Invalid search config key [%s].  Valid options: %s' % (key, configOptions))
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
            if self.config['regex'] is None:
                error('Search config requires regular expression')
                error('Search name: '+self.getName())
                exit(errorCodes['invalidConfig'])    
        except KeyError:
            error('Search config requires regular expression')
            exit(errorCodes['invalidConfig'])

        # Check the list of systems against any sysFilters that have been defined
        if 'sysFilter' in self.config.keys():
            sysList=self.config['systems'][:]
            poppedList=[]
            popCount=0
            for i in range(len(self.config['systems'])):
                for f in self.config['sysFilter']:
                    if not compareAttr(f, self.config['systems'][i]):
                        popped=sysList.pop(i-popCount).getSystemName()
                        popCount+=1
                        poppedList.append(popped)
                        if self.config['verbose']:
                            error('Removing %s. sysFilter does not match: ' % popped)
                        if f['comp'] == 'in' and self.config['verbose']:
                            error('\tFilter: %s %s %s' % ( f['value'],f['comp'],f['attr'],))
                        elif self.config['verbose']:
                            error('\tFilter: %s %s %s' % ( f['attr'],f['comp'],f['value'],))
                        try:
                            obsValue=self.config['systems'][i].__getattribute__(f['attr'])
                        except AttributeError:
                            obsValue='NOT FOUND'
                        if self.config['verbose']:
                            error('\tObserved value: %s' % obsValue)
                        break
            if self.config['verbose']:
                if len(poppedList) > 0:
                    print('Removed systems:', poppedList)
                print('\nFinal list of systems:', [x.getSystemName() for x in sysList])
            self.config['systems']=sysList[:]

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
                if self.config['verbose']:
                    error('groupList was provided.  Forcing onlyMatching...')
    
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

    def get_rsDelimiter(self):
        '''
        Returns the recordset delimiter regular expression in the Search.config dictionary.
        '''
        return self.config['rsDelimiter']
    
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
                    combinedResults Dictionary of results   A dictionary of groupList items value
            '''
            combinedResults={}
            for result in results:
                for key in result.keys():
                    combinedResults[key]=result[key]
            return combinedResults

        # Create a short-circuit detection so that once we move beyond the desired section in the file, we stop looking
        desiredSectionRegex=None
        desiredSectionPattern=None 
        limitToSection=False
        if self.getRegex().find('::') > 0 and not self.config['fullScan']: # and self.config['maxResults'] == 0:
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
        
        try:
            pattern=re.compile(self.getRegex(), re.IGNORECASE)                          # Matches the provided pattern
        except re.error as reError:
            error('Regex error   : '+str(reError))
            error('Search name:  '+self.getName())
            error('Provided regex: '+self.getRegex())
            exit(errorCodes['invalidConfig'])

        try:
            if self.get_rsDelimiter():
                rsDelimiter=re.compile(self.get_rsDelimiter(), re.IGNORECASE)                          # Matches the provided pattern
        except re.error as reError:
            error('Regex error   : '+str(reError))
            error('Search name:  '+self.getName())
            error('Provided delimiter: '+self.getDelim())
            exit(errorCodes['invalidConfig'])

        commentsPattern=re.compile(r'^###|^#\[.*\]:|:: ###')                            # Matches comment lines and [BEGIN], [CISReference], etc.
        blankLinePattern=re.compile(r'::\s*$')                                          # Matches lines that end in :: and zero or more white-space characters [ \t\r\n\f]
        finalResults=[]                                                                 # Set up a blank list to hold our results
        

        for system in self.config['systems']:
            sectionFound=False
            inDesiredSection=None
            groupDict={}                                                                # Create a blank dictionary to hold each regex group results
            groupResults=[]                                                                 # Create a blank list to hold our group results dictionaries as we complete each one
            systemResults=[]                                                                # Create a blank list to hold our system results that we'll append to the final results
            combined=False                                                                  # Have we successfully combined the results
            
            # We already checked earlier (in getReportVersion) if the file is of the wrong encoding, so we can now ignore individual byte errors.  These could occur
            # for instance when specific Linux (and maybe Windows) utilities produce non-printable characters
            for line in open(system.getFilename(),encoding='ascii',errors='ignore'):
                line=makePrintable(line)
                isDelimiter=None
                if limitToSection:                                                      # Are we supposed to take the short cut?
                    inDesiredSection=desiredSectionPattern.search(line)
                    if inDesiredSection and not isComment:
                        sectionFound=True
                found = pattern.search(line)                                            # Perform the search for our regex pattern
                isComment = commentsPattern.search(line)                                # Check if we're on a comment or blank line that also matched our search pattern
                isBlankLine = blankLinePattern.search(line)
                if self.get_rsDelimiter():
                    isDelimiter = rsDelimiter.search(line)
                if isDelimiter and len(groupResults)>0:                                 # If we've stumbled on a delimiter line, combine and commit the results
                    systemResults.append(combineResults(groupResults))
                    combined=True
                    groupResults=[]
                    #break
                
                if found and not isComment and not isBlankLine:
                    if self.config['onlyMatching']:                                     # OnlyMatching is true when we're processing groups
                        groupDict={}
                        groupDict['systemName'] = system.getSystemName()
                        for group in self.config['groupList']:
                            try:
                                if found.group(group):
                                    groupDict[group]=makePrintable(found.group(group)).strip()
                            except IndexError as e:
                                error('Group not found in search results')
                                error('Search name: '+self.getName())
                                error('Group name : '+group)
                                exit(errorCodes['invalidConfig'])

                        if self.config['unique']:
                            # If we're only trying to get the unique values, then try an index using a groupText.  It will throw a ValueError 
                            # if the value isn't found, in which case we'll add it to the results
                            try:
                                systemResults.index(groupDict)
                            except ValueError:
                                groupResults.append(groupDict)
                        else:
                            groupResults.append(groupDict)

                        # if this search config requests to combine the results, append the combined results to the system results
                        if self.config['combine']:
                            foundGroups=[]
                            foundBool=[]
                            combined=False
                            for result in groupResults:
                                foundGroups+=list(result.keys())

                            for reqdGroup in self.config['groupList']:
                                foundBool+=[reqdGroup in foundGroups]

                            #if (len(groupResults) == len(self.config['groupList'])):
                            if all(foundBool):
                                systemResults.append(combineResults(groupResults))
                                combined=True
                                groupResults=[]
                        else:
                            for result in groupResults:
                                systemResults.append(result)
                            groupResults=[]                             # Reset groupresults to null list after appending
                    else:
                        foundText=makePrintable(line)

                        # The "results" paranthetical salad (inside-out) -- splices ('[1:]') the split line (on '::') to drop the first field (section header), 
                        # before rejoining on the :: field separator (at the beginning of the line)                        
                        systemResults.append({
                            'systemName': system.getSystemName(),
                            'Results': '::'.join((foundText.split('::')[1:])).strip()
                        })

                    # If we're at the limit of our results
                    if len(systemResults) == self.config['maxResults']:
                        break
                elif (limitToSection and sectionFound and not inDesiredSection and not isComment and not isBlankLine):
                    break
            
            # If we finished the file, but we didn't find all of the groups we though we needed, go ahead and combine what we have
            if self.config['combine'] and not combined and len(groupResults) > 0:
                for group in self.config['groupList']:                      # Add a blank result for any group name that wasn't found
                    if not group in foundGroups:
                        groupResults.append(
                            {
                            'systemName': system.getSystemName(),
                            group: '',
                            }
                        )

                systemResults.append(combineResults(groupResults))

            #Append all of our system system results to the final results
            for result in systemResults:
                finalResults.append(result)       

        self.results=finalResults

    def toScreen(self):
        results=self.results
        screenWidth=console.getTerminalSize()[0]
        minColWidth=12
        print('<>'*screenWidth)
        print('Name: %s' % self.getName())
        if not self.config['quiet']:
            truncate=self.config['truncate']
            whiteSpace=2                                # Number of spaces between columns

            #Set up the header row and column widths
            if len(results) > 0:
                colWidth=getLongest(results, whiteSpace)
                try:
                    colWidth[self.config['groupList'][-1]]-=whiteSpace          #Remove the pad from the last item in the groupList
                except KeyError:
                    colWidth['Results']-=whiteSpace                             #If groupList wasn't used...
                reduceBy=1
                firstPass=True
                needShorter = False
                colHeaderLength=0
                for colHeader in results[0].keys():
                    colHeaderLength+=len(colHeader)+whiteSpace

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
                    if colHeaderLength > totalWidth and truncate:
                        error('Cannot truncate')
                        needShorter=False
                    else:
                        needShorter=(totalWidth > screenWidth) and truncate

                formatStr=formatStr[:-whiteSpace]                #Remove the final whitespace from the end of the line
                        
                print(formatStr % tuple(header))
                print('='*totalWidth)

                for result in results:
                    values=[result['systemName']]
                    try:
                        keys=self.config['groupList']           # Check if groupList was set in the config
                    except KeyError:
                        keys=list(result.keys())[1:]                     # If not, use the columns from the results dictionary, dropping systemname since we already have it
                    for key in keys:
                        try:
                            value=result[key]
                        except KeyError:                      # If the result set didn't find the matching group name, fill it with <None>
                            value='<None>'
                        if len(value) > colWidth[key]:
                            value=value[:colWidth[key]-reduceBy-3]+'...'
                        values+=[value]
                    try:
                        print(formatStr % tuple(values))
                    except TypeError as e:
                        error("Error printing results: "+str(e))
                        error("\tColumn headers  : "+str(header))
                        error("\tFormat string   : "+formatStr)
                        error('\tValues to print : '+str(tuple(values)))
                        exit(errorCodes['generalError'])
                    
        print('Results found: %d\n' % len(results))
        if len(results) == 0:
            error('No results found')
        # Return everything except for the final new-line
        return True

    def toExcel(self):
        '''
        Saves the results to an Excel file in self.config['outPath']/self.config['outFile]
        '''
        class Columns():
            def __init__(self, value=['systemName']):
                self.names=[]
                if value:
                    if hasattr(value, '__iter__'):
                        for v in value:
                            self.names.append(v)
                else:
                    self.names=[value]

            def append(self, value):
                if hasattr(value, '__iter__'):
                    for v in value:
                        if not v in self.names:
                            self.names.append(v)


        #Set up some variables we'll need...
        maxWorkSheetNameLength=31
        results=self.results
        columns=Columns()
        path=self.config['outPath']
        if not path.endswith('/'):
            path+='/'
        filename=self.config['outFile']
        if len(self.config['name']) > maxWorkSheetNameLength:
            worksheetName=self.getName()[0:maxWorkSheetNameLength]
        else:
            worksheetName=self.getName()
        defaultCommentWidth=6                   # Number of columns to merge into the comment cell.  We'll adjust based on the actual number of columns so that the marged cell doesn't get out of control
        heightPerLine=15                        # Excel row height for a single row (defaults to 15 on my Excel).  We'll use it to approximate a row height for the merged comment cell
        try:
            commentLen=len(self.config['comment'])
        except TypeError:
            commentLen=0
        commentHeight=int(commentLen / 50) * heightPerLine
        cursor={
            'row': 0,
            'col': 0,
        }

        # Create the folder if it doesn't already exist
        if not os.path.exists(path):
            os.makedirs(path)

        # If the filename doesn't already end with an '.xlsx', then add it
        if not filename.endswith('.xlsx'):
            filename+='.xlsx'

        # Create a new Excel workbook to store the results
        # Use 'constant_memory' mode to write the results to the file as they are saved / saves memory
        if os.path.exists(path+filename):
            fileIsOpen=True
            while fileIsOpen:
                try:
                    os.remove(path+filename)
                    fileIsOpen=False
                except PermissionError:
                    try:
                        error('File %s appears to be open.  Close the file and press ENTER or CTRL-C to quit' % filename)
                        input()
                    except KeyboardInterrupt:
                        print("\nQuitting...")
                        exit(errorCodes['generalError'])
        

        wb=xlsxwriter.Workbook(path+filename)
        ws=wb.add_worksheet(worksheetName)

        # Create Excel format objects we'll need to make things pretty
        merge_format = wb.add_format({
            'border': 2,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True,
        })
        cell_format = wb.add_format({
            'border': 0,
            'align': 'left',
            'valign':'top',
            'text_wrap': True,
        })                                               

        # We're gonna cheat a little bit by using getLongest.  We don't really need column widths, just the column names
        columns.append(getLongest(self.results).keys())
            
        # Write the comment (if provided) into the first cell
        if commentLen > 0:
            if len(columns.names) > 2:
                commentWidth=defaultCommentWidth
            else:
                commentWidth = 1
            ws.merge_range(cursor['row'], cursor['col'], cursor['row'], cursor['col']+commentWidth, self.config['comment'], merge_format)
            ws.set_row(cursor['row'], commentHeight)
            cursor['row']+=2                                            #Skip a line before writing the header

        # Populate the Excel table's header row
        tableColumns=[]
        for col in columns.names:
            tableColumns.append({'header': col})

        # Move the cursor to the beginning of the next row
        cursor['row']+=1
        cursor['col']=0

        # Get the dimensions for the table we'll add to contain the results
        tableStart={}
        tableStart['row']=cursor['row']
        tableStart['col']=0
        tableEnd={}
        tableEnd['row']=tableStart['row']+len(results)
        tableEnd['col']=tableStart['col']+len(columns.names)-1

        # Initialize a list for use in creating the Excel table
        tableData=[]

        for result in results:
            rowData=[]
            for key in columns.names:
                try:
                    rowData.append(result[key])
                except KeyError:
                    rowData.append('')
            tableData.append(rowData.copy())
            
        tableName=self.getName().replace(' ', '_')
        if tableName[0].isdigit():
            tableName='_'+tableName

        # Create a table out of the results so their easier to work with.
        ws.add_table(
            tableStart['row'], 
            tableStart['col'], 
            tableEnd['row'], 
            tableEnd['col'], 
            {
                'data': tableData,
                'columns': tableColumns,
                'name': tableName
            }
        )

        # Move the cursor to the beginning of the next row after the end of the table
        cursor['row']=tableEnd['row']+1
        cursor['col']=0

        # Save the workbook
        wb.close()                
            

class System(object):
    def __init__(self, filename, verbose):
        self.sysName = os.path.split(filename)[-1].replace('.txt', '')
        self.filename = filename
        self.scriptDetails = getReportVersion(self.getFilename())
        if self.scriptDetails[0] == 'KPNIXVERSION':
            self.osFamily = 'Linux'
            self.producer = 'kpnixaudit'
            self.kpnixversion = self.scriptDetails[1]
            osDetailsSearchConfig = {
                'systems'   : self,
                'regex'     : r'(System_VersionInformation::/etc/os-release::PRETTY_NAME="(?P<prettyName>.*)"$)|(System_VersionInformation::/etc/redhat-release::(?P<rpmPrettyName>.*))',
                'groupList' : [
                    'prettyName',
                    'rpmPrettyName',
                ],
                'maxResults': 1,
                'combine' : True,
                'onlyMatching': True,
            }
            osDetails=Search(osDetailsSearchConfig)
            osDetails.findResults()
            if len(osDetails.results) > 0:
                self.osPrettyName=osDetails.results[0]['prettyName']
                rpmPattern=r'Alma|Amazon|ClearOS|CentOS|Oracle|(Red Hat)|SUSE'
                debPattern=r'Debian|Gentoo|Knoppix|Mint|Ubuntu'
                distroSearch=re.compile(r'(?P<debDistro>'+debPattern+')|(?P<rpmDistro>'+rpmPattern+')', re.IGNORECASE)
                versionSearch=re.compile(r'(?P<osVersion>((\d+\.?)+))')
                searchText=osDetails.results[0]['prettyName']
                if len(osDetails.results[0]['rpmPrettyName']) > 0:
                    searchText=osDetails.results[0]['rpmPrettyName']
                    self.rpmPrettyName=searchText
                distro=distroSearch.search(searchText)
                version=versionSearch.search(searchText)
                if distro.group('debDistro') is not None:
                    self.distroFamily='deb'
                elif distro.group('rpmDistro') is not None:
                    self.distroFamily='rpm'
                else:
                    self.distroFamily='unknown'
                if version.group('osVersion'):
                    self.osVersion = [int(x) for x in version.group('osVersion').split('.')]
                else:
                    self.osVersion = 0
            elif verbose:
                error("File: %s\nCouldn't determine OS Pretty Name" % filename)
        elif self.scriptDetails[0] == 'KPWINVERSION':
            self.osFamily = 'Windows'
            self.producer = 'kpwinaudit'
            self.kpwinversion = self.scriptDetails[1]
            osDetailsSearchConfig = {
                'systems'   : self,
                'regex'     : r'System_OSInfo::(ProductName\s+:\s+(?P<ProductName>[\w ]+))|(ReleaseId\s+:\s+(?P<ReleaseId>\w+))|(CurrentBuild\s+:\s+(?P<CurrentBuild>\d+))|(UBR\s+:\s+(?P<UBR>\d+))',
                'groupList' : [
                    'ProductName',
                    'ReleaseId',
                    'CurrentBuild',
                    'UBR',
                ],
                'maxResults': 1,
                'combine' : True,
                'onlyMatching': True,
            }
            osDetails=Search(osDetailsSearchConfig)
            osDetails.findResults()
            for key in osDetails.results[0]:
                setattr(self, key, osDetails.results[0][key])
        elif self.scriptDetails[0] == 'KPMACVERSION':
            self.osFamily='Darwin'
            self.producer='kpmacaudit'
            osDetailsSearchConfig = {
                'systems'   : self,
                'regex'     : r'System_VersionInformation::((ProductName:\s+(?P<ProductName>\w+))|(ProductVersion+:\s+(?P<ProductVersion>[\w.]+))|(BuildVersion:\s+(?P<BuildVersion>\w+)))',
                'groupList' : [
                    'ProductName',
                    'ProductVersion',
                    'BuildVersion',
                ],
                'maxResults': 1,
                'combine' : True,
                'onlyMatching': True,
            }
            osDetails=Search(osDetailsSearchConfig)
            osDetails.findResults()
            for key in osDetails.results[0]:
                setattr(self, key, osDetails.results[0][key])
        else: 
            self.osFamily = 'unknown'
            if verbose:
                error('Report version details could not be determined.\nFile will not be processed.')
                error('Filename: %s' % self.getFilename())

    def __str__(self):
        
        res=''
        for item in self.__dict__:
            value=self.__dict__[item]
            if not item.startswith('__'):
                if item == 'scriptDetails':
                    pass
                elif type(value) == list:
                    res+=item+': '+'.'.join(str(i) for i in value)+'\n'
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
    try:
        for line in open(filename,encoding='ascii'):
            match=pattern.search(line)
            if match:
                found=True
                reportType=match.group('producer')
                #Turn the version string into a list of integers instead of a list of strings consisting of numbers.
                reportVersion=[int(i) for i in match.group('version').split('.')]
                break
    except UnicodeDecodeError:
        error('Filename: %s' % (filename))
        error('File appears to be encoded with an unsupported Unicode format (likely UTF-16) and was probably created using')
        error('an old version kpwinaudit.ps1.  Try opening the file in Notepad or VSCode and compare the KPWinVersion with the')
        error('change history at https://github.com/kirkpatrickprice/windows-audit-scripts/blob/main/kpwinaudit/kpwinaudit.ps1')
        error('to see what you might be missing.')
        print()
        error('If you really want to proceed, use "dos2unix %s" Linux command to convert the file to a Unicode encoding that will work')
        response=input('\n[C]ontinue to the next file, or [Q]uit? ')
        if response.lower()=='q':
            exit(errorCodes['generalError'])

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

def getConfigOptions():
        return {
            'rsDelimiter': 'A regex pattern to identify a new recordset.  Only valid in use with \'combine\'',
            'name': 'A name for the search config.  Will be used to name the Excel table and worksheet.',
            'systems': 'Systems (Class: System) to apply the search to',
            'regex': 'Python-compatible, CaSeInSenSiTiVe regex to use https://docs.python.org/3/howto/regex.html',
            'maxResults': 'Maximum number of results to return per System (default: -1 - unlimited)',
            'onlyMatching': 'Only provide the matching string instead of the full line (default: full line)',
            'unique': 'Only display one instance of each match',
            'groupList': 'Regex group to display, if groups are used (default=0/ALL).  Must be used with -o / --only-matching',
            'truncate': 'Truncate lines to fit current screen width.  Does not affect CSV output.',
            'quiet': 'Quiet mode -- suppress screen output except status messages / especially helpful in YAML mode or with Excel output',
            'fullScan': 'Override the search short-circuit logic to always scan the entire file',
            'combine': 'Combine results from across multiple lines to form a single record (only valid if groupList is specified)',
            'comment': 'A helpful comment that will be added to the output file to describe how to use this particular set of search results',
            'outFile': 'File name to save the results to',
            'outPath': 'Path to save the results to (Default: ./saved)',
            'sysFilter': 'A list of conditions represented in a dictionary with keys ''attr'', ''comp'', and ''value''.  See --yaml-help for details',
            'verbose': 'Increase output verbosity',
        }

def getSysFilterAttrs():
    return {
            'osFamily': 'OS Family such as Windows or Linux',
            'producer': 'Script that produced the file such as kpnixaudit.sh or kpwinaudit.ps1',
            'kpwinversion': 'kpwinaudit.ps1 script version that produced the results',
            'productName': 'Windows Product Name such as "Windows 10 Professional"',
            'releaseID': 'Windows Release ID as captured from the registry -- e.g. "2009" or "2H21',
            'currentBuild': "Windows CurrentBuild as captured from the registry",
            'ubr': "Windows UBR Code",
            'kpnixversion': 'kpnixaudit.sh script that produced the results',
            'distroFamily': 'Linux distribution family such as "rpm", "deb" or "unknown"',
            'osPrettyName': 'Directly from /etc/os-release - e.g. "Ununtu 22.04.1 LTS"',
            'rpmPrettyName': 'For RPM-based distros, osPrettyName will be non-descript, but rpmPrettyName will be more specific',
            'osVersion': 'Exactly as it appears in PrettyName or rpmPrettyName -- e.g. 22.04.1 or 8.7',
    }

def getSysFilterComps():
    return {
            'eq': 'Equals -- an exact comparion',
            "gt": 'Greater than -- compares numbers, strings, list members, etc',
            "lt": 'Less than -- compares numbers, strings, list members, etc',
            "ge": 'Greater than or equals',
            "le": 'Less than or equals',
            'in': 'Tests set membership',
    }

def getSysFilterKeys():
    return {
            'attr': 'The attribute to compare.  See list of possible attributes.',
            'comp': 'The comparison operator.  See list of possible comparison operators.',
            'value': 'The value to test against',
    }

def makePrintable(text):
    '''
    Receives text and will return only the printable characters
    '''
    if not text.isprintable():
        printableText = filter(lambda x: x in string.printable, text)
        return ''.join(list(printableText))
    else:
        return text

############################################
####### Module Self-test Code ##############
############################################

if __name__ == '__main__':
    import glob
    files=glob.glob('/home/randy/Downloads/Customers/test-script-results/kpat-test-data/*.txt')
    test=[System(f, verbose=True) for f in files]
    #     System('/home/randy/Downloads/Customers/Test Script Results/Windows Script Results/THE-BEAST.txt'),
    #     System('/home/randy/Downloads/Customers/Test Script Results/Windows Script Results/ACC-3791-PC.txt'), 
    #     System('/home/randy/Downloads/Customers/Test Script Results/Windows Script Results/cpaas_dev-jenkins-win.txt'),
    #     System('/home/randy/Downloads/Customers/Test Script Results/Linux/11792-tdc3-dns.modernniagara.miaas.txt'),
    #     System('/home/randy/Downloads/Customers/Test Script Results/Linux/chalet_chalet-realm-chalet-ng-erl.txt'),
    #     System('/home/randy/Downloads/Customers/Test Script Results/Linux/olorin-0.6.11.txt'),
    #     System('/home/randy/Downloads/Customers/Test Script Results/Linux/ccaas-fr1-eu51-ldap64-1.fr1.whitepj.net.txt'),

    # ]
    configs=[
        {
            'name': 'Windows System Services',
            'systems': test,
            'regex': r'System_Services::(?!DisplayName)(?!--)(?P<ServiceName>(\w+\s)+)\s+(?P<Status>Running|Stopped)\s+(?P<StartType>.*)',
            'maxResults': 5,
            'onlyMatching': True,
            'groupList': [
                'ServiceName',
                'Status',
                'StartType',
            ],
            'truncate': True,
            'quiet': True,
            'comment': '''A list of Windows services, their current status and the their startup config.  Useful to confirm things like anti-virus, web servers, database servers, and other system details''',
            'outFile': 'windows_system_services',
            'sysFilter': [
                {
                    'attr': 'osFamily',
                    'comp': 'eq',
                    'value': 'Windows'
                },
            ],
            'verbose': True,
        },        
        {
            'name': 'Linux Pending Yum Updates',
            'systems': test,
            'regex': r'System_PackageManagerUpdates::(?!Loaded plugins)(?!Loading mirror)(?!Updated Packages)(?P<pkg_name>[\w\-.]+)\s+(?P<pend_version>[\d\-.\w]+\s)',
            'maxResults': 5,
            'onlyMatching': True,
            'groupList': [
                'pkg_name',
                'pend_version',
            ],
            'truncate': True,
            'quiet': True,
            'comment': '''A list of packages with a pending update.  The version string indicates the version that is pending installation.  You can use this to search the internet for CVEs that were fixed.''',
            'outFile': 'linux_yum_updates',
            'sysFilter': [
                {
                    'attr': 'osPrettyName',
                    'comp': 'in',
                    'value': 'Red Hat'
                },
            ]
        },
        {
            'name': 'WindowsUpdateHistory',
            'systems': test,
            'regex': r'System_WindowsUpdateHistory::.*(Cumulative|Security)\sUpdate',
            'maxResults': 10,
            'onlyMatching': False,
            'truncate': True,
            'quiet': True,
            'comment': '''A list of WindowsUpdate History log results filtered for Cumulative and Securty updates.  Useful to determine patching history''',
            'outFile': 'windows_update_history',
            'sysFilter': [
                {
                    'attr': 'osFamily',
                    'comp': 'eq',
                    'value': 'Windows'
                },
            ]
        },
    ]
    for config in configs:
        search=Search(config)
        if search.config['verbose']:
            search.printConfig()
        if len(search.config['systems']) > 0:
            search.findResults()
            if search.results:
                search.toScreen()
                try:
                    search.config['outfile']                
                    search.toExcel()
                except KeyError:
                    pass
            else:
                error('No results found')
        else:
            error('No systems matched provided criteria.  Skipping search: %s' % search.getName())