#!/usr/bin/env python
'''src/adv_searchfor/adv_searchfor.py wrapper'''

import sys
import traceback
from pathlib import Path

from nipper.nipper_expander import main

exitCode = 0

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        exit_code = 1
        errorFile='nipper_expander_error.log'
        print(f'An unknown error was encountered.  Detailed error information has been written to {errorFile}.')
        traceback.print_exception(file=errorFile)
    sys.exit(exitCode)
    