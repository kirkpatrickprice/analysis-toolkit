# Process Scripts Search Engine

## Search Engine Overview

The `search_engine` is the heart and soul of the `process_scripts` toolkit command.  Earlier steps in the workflow were responsible for identifying system attributes in source files and parsing the search configurations from YAML files.  The `search_engine` is responsible for bringing these two pieces of information together and conducting the searches to extract meaningful information from the files.

## Search Processing

Each YAML configuration includes at least the four following pieces of information:

- `regex` pattern to search for using Python extensions specifically for named groups
- `excel_sheet_name` pretty name to use to for the Excel worksheet when exporting results
- `comment` includes useful information to present on the worksheet which guides users on how to use the results
- `keywords` to create a topical index to help users get to the information that they're lookgin for.

There are ample optional fields to implement various features.  These are documented in [YAML Help](../../../user-guides/YAML%20Help.md)

## Search Results Processing

Search results are returned in a data model described in `process_scripts.models.results.search` and are collected per operating system type `['linux', 'darwin', 'windows']`.  The results are then processed into OS-specific Excel workbooks.

Excel export services are handled using `core.services.excel_export` as well as enhanced, `process_scripts`-specific handling through `process.scripts.services.enhanced_excel_export`.  The specifics of Excel export processing are covered in more detail in another document.