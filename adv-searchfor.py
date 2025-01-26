#!/usr/bin/env python
'''src/adv_searchfor/adv_searchfor.py wrapper'''

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parent / "src"))

from adv_searchfor.adv_searchfor import main

if __name__=='__main__':
    main()