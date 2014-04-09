"""
Data structures for taking exponentially weighted averages of sampled variables
over time.

TODO: Graphical demo showing noisy data with abrupt shift in mean.
    Demonstrate that a longer timescale takes longer to adjust, but is
    smoother when there are no discontinuities.


by Michael J.T. O'Kelly, 2014-04-09
"""

import frecency


class WeightedAverage():
    """Exponentially weighted average of a variable sampled over time.
    NOTE: The underlying data structure requires that all samples be greater
    than zero."""
    # TODO: Arbitrary values could potentially be accepted by keeping
    # an offset value
    def __init__(self, timescale=24. * 60. * 60.):
        """* *timescale* is the halflife of events, in seconds.  With the default (24 hours)
        an event now counts twice as much as an event 24 hours ago."""
        self.n_sum = frecency.Frecency(timescale)  # Weight accumulator
        self.x_sum = frecency.Frecency(timescale)  # Variable accumulator
        self.x2_sum = frecency.Frecency(timescale)  # Variable squared accumulator
        self.timescale = timescale

    def add_sample(self, sample, weight=1.0, event_time=None):
        """Incorporate a new sample into the weighted average.

        * *sample* is one sampled value of the variable.  (It must be
            greater than zero.)
        * *weight* is the relative weight assigned to this sample.
        * *event_time* is the epoch time of this sample (if different from 'now')
        """
        if sample <= 0.:
            raise ValueError("Samples must be greater than zero", sample)
        self.n_sum.increment(weight, event_time=event_time)
        self.x_sum.increment(sample, event_time=event_time)
        self.x2_sum.increment(sample ** 2, event_time=event_time)

    def get_mean_std_uncertainty(self):
        """Returns (mean, std, uncertainty) tuple of present best estimates.

        *uncertainty* is the estimated error of the *mean*.

        The accuracy of these estimates becomes dubious when
        the sample rate is smaller than the timescale."""
        present_n = self.n_sum.get_present_weight()
        present_x = self.x_sum.get_present_weight()
        present_x2 = self.x2_sum.get_present_weight()

        mean = present_x / present_n
        # Calculate the variance from the X^2 cumulant
        # (http://en.wikipedia.org/wiki/Variance#Definition)
        variance = present_x2 / present_n - mean ** 2
        # http://en.wikipedia.org/wiki/Variance#Sample_variance
        # TODO: Sample bias correction.  This was attempted:
        # variance = present_n / (present_n - 1.)
        # but that didn't work in the exponential weighting framework
        std = variance ** 0.5
        uncertainty = std / present_n ** 0.5
        return (mean, std, uncertainty)


if __name__=='__main__':
    import random
    import time
    w = WeightedAverage(timescale=0.01)
    start_time = time.time()
    for i in range(100000):
        sample = random.gauss(10., 1.)
        w.add_sample(sample)
    print "time passed:", time.time() - start_time
    print w.get_mean_and_std()
