# analysis-toolkit

The analysis toolkit is a collection of scripts designed to assist auditors analyze the results of the KP system auditing scripts maintained at:
* [Linux](https://github.com/kirkpatrickprice/linux-audit-scripts) 
* [Windows](https://github.com/kirkpatrickprice/windows-audit-scripts)

## Critical dependencies ##
* Shell: a recent version of `bash`
* Misc. commands:   `grep` `echo` `awk` `sort`

The scripts have been tested and are usually used on Ubuntu distributions. They were developed on Ubuntu 20.04.  YMMV on other distributions or versions.

## Installation ##
Installation is as simple as cloning this repo to your system.

Change to your favorite location where you'd like to install them.  A sub-directory will be created called `analysis-toolkit`

`git clone https://github.com/kirkpatrickprice/analysis-toolkit`

## Updating the toolkit ##
Change to the analysis-toolkit directory
    `cd /path/to/your/analysis-toolkit`

And issue the following `git` commands.  All local changes will be overwritten.
```
git fetch
git reset --hard HEAD
git merge
```

## Using the toolkit scripts ##
Each toolkit script includes a "help" function to explain the options.

`<script> -h`