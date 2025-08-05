# KPAT Changes

## 2025-08-04
Version 2.0.6

* Bumped `process_scripts` to v.0.5.0
* implemented sleep prevention through `wakepy`

## **2025-06-27**  
Version 2.0.0 is a complete rewrite of the toolkit.  It merges what used to be different utilities into one common CLI.

* Overall changes
    * Unified Click-based CLI as a starting point for future tool development
    * Uses `pydantic` for data modeling and validation to increase overall program reliability
    * Uses `pandas` for all CSV and Excel file handling -- greatly simplified interface
    * Uses `charset-normalizer` to modernize file encoding detection
    * Extensive unit tests built in `pytest`
* Formerly `adv-searchfor` --> `kpat_cli scripts`
    * Searches for all files starting at the current working directory or at a path provided by the user (`-d`)
    * Processes all Windows, MacOS, and Linux systems concurrently -- no longer need to run them each separately
    * Saves all results into separate OS-specific Excel workbook (one each for supported OSes)
    * Provides a search summary and a system summary worksheets
* Formerly `nipper_expander` --> `kpat_cli nipper`
    * Expands a Nipper CSV file with "one-row-per-finding" with multiple devices listed in the same row into "one-row-per-device-per-finding"
    * Helps with sorting and filtering Nipper findings in Excel
* New tool -- RTF to Text Converter
    * Converts RTF files to plaintext, ASCII-encoded files
    * Useful for router configs (and other files) where the information was provided in RTF, but needs to be used (e.g. by Nipper) as plaintext files.

**06/28/2025**

    * Add `conf.d` folder to build
    * Bump toolkit to v2.0.1
    * Bump `process_scripts` to v0.4.1
    * Add progress bar to non-verbose output
    * Bump toolkit to v2.0.2

**06/29/2025** v2.0.3
    * Implement Rich formatting for all CLI user interaction

**06/29/2025** v2.0.4
    * Implement new behavior for upgrade notifications as in-process upgrades resulted in locked, open files