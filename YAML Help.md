# YAML Search Configurations

## Overview
You can author your own search configurations as YAML files.  For instance, if you have some custom searches for a specific customer, you can save them for reuse when working them next year.

A YAML file is just a text file with a ".yaml" extension.  Some pre-defined YAML files are provided as part of the Analysis Toolkit:
    .../conf.d
        audit-windows.yaml      Set of searches appropriate for use with Windows systems
        audit-linux.yaml        Set of searches appropriate for use with Linux systems

Reference these files for the basic structure of what a configuration section should look like.  There are also examples of most (all?) options that you can model your own after.

You can also include the contents in other YAML files by using the "include_<unique_but_arbitrary_name>:" section within your own files.
```yaml
myfile.yaml
  include_audit_windows:
    files:
      - audit-windows.yaml

    my_custom_check:
      regex: 'an awesome search pattern'
      comment: 'This check looks for something awesome.  When you review this later in Excel, this comment will remind you of its awesomeness.'
      ...more options
```

This will bring in all of the checks in `audit-windows.yaml` and the tool knows to look in it's `conf.d` folder if no path info is provided.  For anything not including the `conf.d` folder, you'll need to provide path info.  In fact, `audit-windows.yaml` and `audit-linux.yaml` both use this method to keep the configs easier to read and so that you can run just a subset of the checks if you'd like.

There are help sections at the top of each of the provided YAML files, but the most authoritative list of available options is provided here.

### Configuration sections
| Option        | Description |
-------------------------------
| `regex`         | Python-compatible, CaSeInSenSiTiVe regex to use https://docs.python.org/3/howto/regex.html. |
| `comment`       | A helpful comment that will be added to the output file to describe how to use this particular set of search results. |
| `max_results`   | Maximum number of results to return per System (default: -1 - unlimited). |
| `only_matching` | Only provide the matching string instead of the full line (default: full line). |
| `unique`        | Only display one instance of each match. |
| `field_list`    | Maps regex "groups" `(<P<group_name>pattern)` to Excel fields.  Must be used with -o / --only-matching.  If regex groups aren't used, then one field name will be added as `raw_data` |
| `full_scan`     | Override the search short-circuit logic to always scan the entire file. |
| `rs_delimiter`  | A regex pattern to identify a new recordset.  Only valid in use with `combine`. |
| `combine`       | Combine results from across multiple lines to form a single record (only valid if groupList is specified). |
| `sys_filter`    | A list of conditions represented in a dictionary with keys `attr`, `comp`, and `value`. |

## System Filters
`sys_filter` can be used to limit the search's applicability to just some of system types.  For instance, if you want to limit the search to just Debian-derived Linux distros or to Windows 11 machines.

Defning a `sys_filter` involves three parts:

```yaml
sys_filter:
  attr: <attribute_name>
  comp: <comparison_operator>
  value: <value_to_match>
```

### Global Section
You can also create a `global` section at the top of your file to define some parameters that will apply to the rest of the search configurations.  This is especially useful when applying `sys_filter`s for types of operating systems, like we see in each of `audit-linux*.yaml`, `audit-macos*.yaml` and `audit-windows*.yaml`.

Here's the example from `audit-windows-system.yaml`:

```yaml
global:
  sys_filter:
    - attr: os_family
      comp: eq
      value: Windows
```

NOTE: The `global` section to all searches *in the current file*.  `global` sections do not inherit across files, event if `include`d as described above.  This helps avoid code complexity in the program related to some weird headaches where conflicting settings are defined.

### sys_filter Attributes
| Attribute         | Description | Aplicable OS | Data Type |
|-------------------|-------------|--------------|-----------|
| `os_family`       | OS Family such as `Windows`, `Linux` or `Darwin` (MacOS). | All | OSFamilyType |
| `producer`        | Script that produced the file such as `kpnixaudit.sh` or `kpwinaudit.ps1`. | All | ProducerType |
| `producer_version`| Version of the audit script that produced the results | All | string | 
| `product_name`    | Windows Product Name such as `Windows 10 Professional` | Windows | string |
| `release_id`      | Windows Release ID as captured from the registry -- e.g. `2009` or `2H21` | Windows | string |
| `current_build`   | Windows current_build as captured from the registry | Windows | string |
| `ubr`             | Windows UBR Code (mapped to a specific hotfix version) | Windows | string
| `distro_family`   | Linux distribution family such as `rpm`, `deb` or `unknown` | Linux | DistroFamilyType |
| `os_pretty_name`  | Directly from /etc/os-release - e.g. `Ubuntu 22.04.1 LTS` | Linux | string |
| `os_version`      | Exactly as it appears in PrettyName -- e.g. 22.04.1 or 8.7 | Linux | string |


### sys_filter Comparison Operators
| `eq`    | Equals -- an exact comparion |
| `gt`    | Greater than -- compares numbers, strings, list members, etc |
| `lt`    | Less than -- compares numbers, strings, list members, etc | 
| `ge`    | Greater than or equals |
| `le`    | Less than or equals |
| `in`    | Tests set membership |

## Data Types 

### [OSFamilyType](src/kp_analysis_toolkit/process_scripts/models/enums.py)
- `Windows` - Windows operating system
- `Linux` - Linux operating system
- `Darwin` - macOS operating system
- `Undefined` - Unknown operating system

### [DistroFamilyType](src/kp_analysis_toolkit/process_scripts/models/enums.py)
- `rpm` - RPM-based Linux distributions (RHEL, CentOS, Fedora, etc.)
- `deb` - Debian-based Linux distributions (Debian, Ubuntu, etc.)
- `unknown` - Other Linux distributions

### [ProducerType](src/kp_analysis_toolkit/process_scripts/models/enums.py)
- `KPNIXAUDIT` - Linux audit script
- `KPWINAUDIT` - Windows audit script
- `KPMACAUDIT` - macOS audit script
- `OTHER` - Other producer

## Filter examples
### Filter by OS Family
```yaml
sys_filter:
  - attr: os_family
    comp: eq
    value: Windows
```

### Filter by Producer and Version
```yaml
sys_filter:
  - attr: producer
    comp: eq
    value: KPNIXAUDIT
  - attr: producer_version
    comp: ge
    value: "0.6.19"
```

### OS-Specific Filters
```yaml
sys_filter:
  - attr: os_family
    comp: eq
    value: Windows
  - attr: product_name
    comp: contains
    value: "Windows 10"
```