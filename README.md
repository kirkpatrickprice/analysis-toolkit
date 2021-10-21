# analysis-toolkit

The analysis toolkit is a collection of scripts designed to assist auditors analyze the results of the KP system auditing scripts maintained at:
* [Linux](https://github.com/kirkpatrickprice/linux-audit-scripts) 
* [Windows](https://github.com/kirkpatrickprice/windows-audit-scripts)

## Critical dependencies ##
* Shell: a recent version of `bash`
* Misc. commands:   `grep` `echo` `awk` `sort`

The scripts have been tested and are usually used on Ubuntu distributions. They were developed on Ubuntu 20.04.  YMMV on other distributions or versions, but I don't foresee any problems, say, on a MacOS Terminal prompt.

For KP auditors, I strongly recommend following the [Getting started with WSL](https://kirkpatrickprice.atlassian.net/l/c/jP0AuG7j) and [Bashing Our Way to Efficient Audits](https://kirkpatrickprice.atlassian.net/l/c/6oaQWQpv) pages on Confluence.


I also recommend that you use the Windows Terminal app available from the Microsoft Store.  Among other numerous benefits, this will allow to click on hyperlinks created by some of the tools.

## Installation ##
Installation is as simple as cloning this repo to your system.

Change to your favorite location where you'd like to install them.  A sub-directory will be created called `analysis-toolkit`.  If you're not sure where to put them, use your Windows Downloads directory if you're using WSL (the examples below assume this is your path).

```
cd /mnt/c/Users/RandyBartels/Downloads/
git clone https://github.com/kirkpatrickprice/analysis-toolkit
```

Edit your user's .bashrc file

`nano ~/.bashrc`

And add the `analysis-toolkit` directory to your path by appending the following to the end of the file

`export PATH="${HOME}/tools:/mnt/c/Users/RandyBartels/Downloads/analysis-toolkit:${PATH}"`

With the `analysis-toolkit` in your path, you will be able to use these commands anywhere in your Bash shell prompt.

## Updating the toolkit ##
Change to the analysis-toolkit directory

`cd /mnt/c/Users/RandyBartels/Downloads/analysis-toolkit`

And issue the following `git` commands.  All local changes will be overwritten.
```
git fetch
git reset --hard HEAD
git merge
```

## Using the toolkit scripts ##
Each toolkit script includes a "help" function to explain the options.

`<script> -h`