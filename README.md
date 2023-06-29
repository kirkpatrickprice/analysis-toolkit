# analysis-toolkit

The analysis toolkit is a collection of scripts designed to assist auditors analyze the results of the KP system auditing scripts maintained at:
* [Linux](https://github.com/kirkpatrickprice/linux-audit-scripts) 
* [Windows](https://github.com/kirkpatrickprice/windows-audit-scripts)
* [MacOS](https://github.com/kirkpatrickprice/macos-auditor)

## Critical dependencies ##
* Shell: a recent version of `bash`
* Python: A recent release of version 3.  Both 3.8 (Ubuntu 20.04) and 3.10 (Ubuntu 22.04) should be fine
* Misc. commands:   `grep` `echo` `awk` `sort`

The scripts have been tested and are usually used on Ubuntu distributions. They were developed on WSL instances of Ubuntu 20.04 and 22.04.  YMMV on other distributions or versions, but I don't foresee any problems, say, on a MacOS Terminal prompt.

For KP auditors, I strongly recommend following the [Getting started with WSL](https://kirkpatrickprice.atlassian.net/l/c/jP0AuG7j) and [Bashing Our Way to Efficient Audits](https://kirkpatrickprice.atlassian.net/l/c/6oaQWQpv) pages on Confluence.

I also recommend that you use the Windows Terminal app available from the Microsoft Store.  Among other numerous benefits, this will allow to click on hyperlinks created by some of the tools.

## Installation ##
Installation is as simple as cloning this repo to your system.

Change to your favorite location where you'd like to install them.  A sub-directory will be created called `analysis-toolkit`.  If you're not sure where to put them, create a `tools` directory under home directory (the examples below assume this is your path).

```
mkdir ~/tools               # If the tools directory doesn't already exist...
cd ~/tools
git clone https://github.com/kirkpatrickprice/analysis-toolkit
```

Edit your user's .bashrc file

`nano ~/.bashrc`

And add the `analysis-toolkit` directory to your path by appending the following to the end of the file

`export PATH="${HOME}/tools:${HOME}/tools/analysis-toolkit:${PATH}"`

With the `analysis-toolkit` in your path, you will be able to use these commands anywhere in your Bash shell prompt.

Now, you'll need to install the Python dependencies.  If you'll be using your Python install for more than just the analysis toolkit, you might want to create a `venv` to run it in.  Check out https://python.land/virtual-environments/virtualenv if you need a tutorial.  Then...
```
cd ~/tools/analysis-tookit
python3 -m pip install --upgrade pip        # Upgrade PIP if it's not already up to date
python3 -m pip install -r requirements.txt  # Install the packages listed in the file
```

## Updating the toolkit ##
Change to the analysis-toolkit directory

`cd ~/tools/analysis-toolkit`

And issue the following `git` commands.  Any changes you might have made in this directory will be overwritten.
```
git fetch
git reset --hard HEAD
git merge
```

If you get any errors from Python about missing packages, re-run the PIP-related commands from the Installation section above to make sure you have all the dependencies installed.

## Using the toolkit scripts ##
Each toolkit script includes a "help" function to explain the options.

`<script> -h`