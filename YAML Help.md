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
| `systems`       | Systems to apply the search to. |
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


### sys_filter Attributes
| Attribute         | Description |
-------------------------------
| `osFamily`        | OS Family such as `Windows`, `Linux` or `Darwin` (MacOS). |
| `producer`        | Script that produced the file such as `kpnixaudit.sh` or `kpwinaudit.ps1`. |
| `kp_mac_version`  | `kpmacaudit.ps1` script version that produced the results |
| `kp_nix_version`  | `kpnixaudit.ps1` script version that produced the results |
| `kp_win_version`  | `kpwinaudit.ps1` script version that produced the results |
| `product_name`    | Windows Product Name such as `Windows 10 Professional` |
| `release_id`      | Windows Release ID as captured from the registry -- e.g. `2009` or `2H21` |
| `current_build`   | Windows current_build as captured from the registry |
| `ubr`             | Windows UBR Code (mapped to a specific hotfix version) |
| `kp_nix_version`  | kpnixaudit.sh script that produced the results |
| `distro_family`   | Linux distribution family such as `rpm`, `deb` or `unknown` |
| `os_pretty_name`  | Directly from /etc/os-release - e.g. `Ununtu 22.04.1 LTS` |
| `rpm_pretty_name` | For RPM-based distros, os_pretty_name will be non-descript, but rpm_pretty_name will be more specific |
| `os_version`      | Exactly as it appears in PrettyName or rpm_pretty_name -- e.g. 22.04.1 or 8.7 |


### sys_filter Comparison Operators
| `eq`    | Equals -- an exact comparion |
| `gt`    | Greater than -- compares numbers, strings, list members, etc |
| `lt`    | Less than -- compares numbers, strings, list members, etc | 
| `ge`    | Greater than or equals |
| `le`    | Less than or equals |
| `in`    | Tests set membership |