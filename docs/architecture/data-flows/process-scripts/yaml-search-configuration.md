# YAML Search Configuration Patterns

## YAML File Overview

All search configurations are retained in the `src/kp_analysis_toolkit/process_scripts/conf.d` directory.

File can include one or more of the following:

* **`include_*` directive:** Any YAML key that begins with this pattern will list one or more files that will also be parsed in the order that they're listed
* **`global` directive:** Placed at the top of the file, the settings captured here are applied to all search configurations in the current file.  The typical use case is to apply a `sys_filter` to limit all searches in the file to a specific OS family such as Windows, Linux, or MacOS.  **NOTE:** The scope is *ONLY FOR THIS FILE* and does not apply to any `include`d file.
* **Search definitions:** Any content that doesn't begin with either of the previous keywords will be treated as a search configuration and will follow the patterns laid out in [YAML Help](../../user-guides/YAML%20Help.md)

## YAML File Processing

Search configuration loading occurs as follows:

1. Start with the user-provided search configuration `--audit-config-file` option in the CLI.  **DEFAULT: `audit-all.yaml`
2. Parse the file for `global` and `include_*` directives
3. Add any search definitions if found, applying any `global`ly defined settings
4. Recursively process each `include_*` file in sequence, starting again at Step 2 above

**NOTE:** Only the files either explicitly referenced in #1 or included through inheritence will be included.  For instance, if the user specifies `audit-linux.yaml` as their starting point instead of the default, then only `Linux` searches will be included and Windows and MacOS searches will be ignored even through they are listed in the `conf.d` folder.  THE FOLDER IS NOT RECURSIVELY SEARCHED FOR YAML FILES, only the `include_`d files are recursively added to the list of eligible searches.

## YAML Processing Service

A DI-based service is implemented to parse the YAML search configurations.  It is available at `process_scripts.services.search_config`.  It will return a list of fully configured searches after implementing the processing steps described above.

The list of searches are filtered against the list of discovered systems types to remove unneeded searches.  For instance, if only Linux systems were found by the `system_detection` service, then the final list of searches will exclude both Windows and MacOS systems.

## Search Execution

The list of relevant search configurations and the list of discovered systems are provided to the `process_scripts.services.search_engine` service to perform the searches and return the results.  The search engine service is beyond the scope of the document and is covered elsewhere.