"""
Data structure for performing sampling of a boostrap random variable
with exponentially weighted samples in time.


TODO: Implement purge of low-weight samples (automatic or manual) to reduce memory usage


by Michael J.T. O'Kelly, 2014-04-09
"""
from __future__ import print_function
from __future__ import absolute_import

import random
import bisect

import numpy
import numpy.random

from . import frecency


class Bootstrap(object):
    """Bootstrap random variable with exponentially weighted
    samples in time.
    This code is optimized for samples which are continuous variables.  For large
    numbers of low-cardinality samples, it could be greatly sped up.
    """
    def __init__(self, timescale=frecency.DEFAULT_TIMESCALE):
        """* *timescale* is the halflife of events, in seconds.  With the default (24 hours)
        an event now counts twice as much as an event 24 hours ago.
        """
        self.timescale = timescale
        self.sample_list = []
        self.weight_cummulant_list = []
        self.weight_list = []
        self.event_time_list = []
        self.total_weight = frecency.Frecency(timescale)

    def add_sample(self, sample, weight=1.0, event_time=None):
        """Add an observed sample (which may be any object) to the bootstrap.
        * *weight* is the relative weight assigned to this sample.
        * *event_time* is the epoch time of this sample (if different from 'now')
        """
        self.sample_list.append(sample)
        self.total_weight.increment(weight, event_time=event_time)
        # Get the internal current value representing the total weight
        weight_cummulant = self.total_weight.log2_value
        self.weight_cummulant_list.append(weight_cummulant)
        # Record weight and event_time so we can resample if desired
        self.weight_list.append(weight)
        self.event_time_list.append(event_time)

    def get_sample(self):
        """This is faster than get_samples() for n==1"""
        # A random number in [0,1] represents what fraction of the cummulant we're seeking for our sample
        seek_fraction = random.random()
        # Since the cummulants are all in log2-space, we need to convert.
        # seek_position will be a float in (-Infinity, total_weight)
        seek_position = self.total_weight.log2_value + frecency.log2(seek_fraction)
        seek_index = bisect.bisect(self.weight_cummulant_list, seek_position)
        sample = self.sample_list[seek_index]
        return sample

    def get_samples(self, num_samples):
        """Efficient sampling for num_samples >> 1"""
        # We perform num_samples samples simultaneously
        # A random number in [0,1] represents what fraction of the cummulant we're seeking for our sample
        seek_fraction_array = numpy.random.rand(num_samples)
        # Since the cummulants are all in log2-space, we need to convert.
        # seek_position will be a float in (-Infinity, total_weight)
        seek_position_array = self.total_weight.log2_value + numpy.log2(seek_fraction_array)
        seek_indexes = numpy.searchsorted(self.weight_cummulant_list, seek_position_array)
        samples = [ self.sample_list[seek_index] for seek_index in seek_indexes ]
        return samples

    def resample(self, filter_func=None, timescale=None):
        """Build a new Bootstrap object containing only samples for which
        filter_func(sample) is True (if given) and with new timescale (if given)."""
        if timescale is None:
            timescale = self.timescale
        new_bootstrap = Bootstrap(timescale)
        for i in range(len(self.sample_list)):
            sample = self.sample_list[i]
            # Include this sample if there's no filter_func, or if it's True on this sample
            if not filter_func or filter_func(sample):
                weight = self.weight_list[i]
                event_time = self.event_time_list[i]
                new_bootstrap.add_sample(sample, weight=weight, event_time=event_time)
        return new_bootstrap


if __name__=='__main__':
    import time
    from collections import Counter
    b = Bootstrap(timescale=1.)
    start_time = time.time()
    b.add_sample(1., event_time=start_time)
    b.add_sample(2., event_time=start_time + 1, weight=2.)
    b.add_sample(3., event_time=start_time + 2)
    b.add_sample(4., event_time=start_time + 3)
    samples = b.get_samples(2 ** 20)
    sample_counts = Counter(samples)
    print("time passed:", time.time() - start_time)
    print(sample_counts)

    b2 = b.resample(lambda s: s>2)
    samples2 = b2.get_samples(2 ** 20)
    sample_counts2 = Counter(samples2)
    print(sample_counts2)
