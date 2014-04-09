"""
Data structure for performing sampling of a boostrap random variable
with exponentially weighted samples in time.


by Michael J.T. O'Kelly, 2014-04-09
"""

import random
from collections import deque
import bisect

import frecency
