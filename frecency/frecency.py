"""
Frecency library.
==================================

Implementation of exponentially weighted frecency (similar to http://mathb.in/708 )




* TODO: Django model?  (a la http://djangosnippets.org/snippets/1694/)
* TODO: Fast containers (Numpy array?  heapq?) with sortability, random sampling, histogram, percentiles, top-k
* TODO: https://read-the-docs.readthedocs.org/en/latest/getting_started.html
* TODO: Automatic half-life determination based on overall usage.
* TODO: Add exponentially weighted averaging.
* TODO: Standard arithmetic operations, where 2nd argument can be Frecency or number
* TODO: Overflow and underflow detection


by Michael J.T. O'Kelly, 2013-05-05
"""

import time
import warnings

from numpy import logaddexp2, log2
import numpy


DEFAULT_TIME0 = time.mktime((2014, 1, 1, 0, 0, 0, 0, 0, 0))  # Arbitrarily chosen base time for exponential weight normalization
DEFAULT_TIMESCALE = 24. * 60. * 60.


class Frecency():
    """Exponentially weighted frecency measure"""
    def __init__(self,
                 timescale=DEFAULT_TIMESCALE,
                 start_value=0.,
                 time0=DEFAULT_TIME0,
                 suppress_warnings=False,
                 fast_comparisons=True):
        """
        * *timescale* is the halflife of events, in seconds.  With the default (24 hours)
          an event now counts twice as much as an event 24 hours ago.
        * *start_value* sets the starting weighted frecency at the present time.  (Defaults to 0.)
        * *time0* is the base time (since the epoch) for exponential weight normalization.  *Not generally worthwhile to change from default*
        * *suppress_warnings* turns off any possible warnings from misuse of this object. (Defaults to False)
        * *fast_comparisons*  If True, performs fastest possible comparison in calls to __cmp__ without sanity checking.  Overrides *suppress_warnings*
        """
        self.timescale = timescale
        self.time0 = time0
        self.fast_comparisons = fast_comparisons
        if fast_comparisons:
            self.suppress_warnings = True
        else:
            self.suppress_warnings = suppress_warnings
        self.log2_value = -numpy.Infinity  # Frecency value is stored in log2 scale
        if start_value:
            self.increment(start_value)

    def increment(self, value_added=1., event_time=None):
        """
        Increment frecency, with value_added weighted according to time of observation.
        
        * *value_added* is the number or weight of current events to add to the Frecency counter.  (e.g., 1 for one view)
        * *event_time* can be used to set the time at which the new value was added; otherwise, the present time is used.
        """
        if not event_time:
            event_time = time.time()
        log2_weight_added = (event_time - self.time0) / self.timescale + log2(value_added)
        self.log2_value = logaddexp2(self.log2_value, log2_weight_added)  # All calculations in log2 space to avoid overflow

    def get_present_weight(self, event_time=None):
        """Return the equivalent number of instantaneous events to get the current frecency, at event_time (if given) or present time."""
        if not event_time:
            event_time = time.time()
        present_weight = 2. ** (self.log2_value - (event_time - self.time0) / self.timescale)
        return present_weight

    def __cmp__(self, frec2):
        """
        Compare the present weighted values of two Frecency objects.
        **Note:** Comparison is of doubtful value between Frecencies with different timescales.  A
        Warning will trigger if this is done, unless suppress_warnings is True.
        If fast_comparisons == True, 
        (Different values for time0 are correctly handled.)
        """
        if self.fast_comparisons:
            return cmp(self.log2_value, frec2.log2_value)
        else:
            if self.timescale != frec2.timescale:
                if not self.suppress_warnings:
                    warnings.warn("Different frecency timescales, {} vs. {}.  Comparison may be meaningless.".format(self.timescale, frec2.timescale))
            present_weight1 = self.get_present_weight()
            present_weight2 = frec2.get_present_weight()
            return cmp(present_weight1, present_weight2)


 


if __name__ == '__main__':
    f1 = Frecency()
    print f1.get_present_weight(), f1.log2_value
    f1.increment()
    print f1.get_present_weight(), f1.log2_value
    f1.increment(3)
    print f1.get_present_weight(), f1.log2_value

    yesterday = time.time() - 24 * 60 * 60
    f1 = Frecency()
    print f1.get_present_weight(), f1.log2_value
    f1.increment(event_time=yesterday)
    print f1.get_present_weight(), f1.log2_value
    f1.increment()
    print f1.get_present_weight(), f1.log2_value
    for i in range(10):
        f1.increment()
        print f1.log2_value,
    print

    the_future = time.time() + 10 * 365 * 24 * 60 * 60
    f1 = Frecency(timescale=1.)
    print f1.get_present_weight(), f1.log2_value
    f1.increment(event_time=the_future)
    print f1.get_present_weight(event_time=the_future), f1.log2_value

    f1 = Frecency(suppress_warnings=False)
    f2 = Frecency()
    f2 = Frecency(timescale=1.,
                  fast_comparisons=False,
                  suppress_warnings=False)
    f1.increment(10, yesterday)
    while f1 > f2:
        f2.increment(1.)
        print f1.get_present_weight(), f2.get_present_weight()






