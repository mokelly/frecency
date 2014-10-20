
import random
import time
from collections import Counter


import numpy

from frecency import *
from frecency.weighted_average import WeightedAverage
from frecency.bootstrap import Bootstrap


def approx_equal(float1, float2, tol=0.001):
    result = (1. - tol) * float2 <= float1 <= (1. + tol) * float2
    return result


def test_frecency_weighting():
    now = time.time()
    timescale = 10.  # 10 seconds
    soon = now + timescale
    later = soon + timescale
    f1 = Frecency(timescale=timescale)
    f2 = Frecency(timescale=timescale)
    f1.increment(event_time=now)
    f2.increment(event_time=soon)
    value1 = f1.get_present_weight(event_time=now)
    value2 = f2.get_present_weight(event_time=soon)
    assert approx_equal(value1, 1.)
    assert approx_equal(value2, 1.)
    # Values at each event time should be equal
    assert approx_equal(value1, value2)
    # At time "soon", value2 should have twice the weight
    value3 = f1.get_present_weight(event_time=soon)
    assert approx_equal(value3 * 2., value2)
    # At any later time, the ratio should remain constant
    value4 = f1.get_present_weight(event_time=later)
    value5 = f2.get_present_weight(event_time=later)
    assert approx_equal(value4 * 2., value5)
    # Weights should decay exponentially
    assert approx_equal(value4, 0.25)
    assert approx_equal(value5, 0.5)
    # Present values should accumulate linearly
    f1.increment(9)
    value6 = f1.get_present_weight(event_time=now)
    assert approx_equal(value6, 10.)


def test_timescales():
    now = time.time()
    timescale = 10.  # 10 seconds
    soon = now + timescale
    later = soon + timescale
    f1 = Frecency(timescale=timescale)
    f2 = Frecency(timescale=timescale / 2.)  # Decays twice as fast
    f1.increment(event_time=now)
    f2.increment(event_time=now)
    value1 = f1.get_present_weight(event_time=soon)
    value2 = f2.get_present_weight(event_time=soon)
    assert approx_equal(value1, value2 * 2.)


def test_weighted_average():
    now = time.time()
    timescale = 10.  # 10 seconds
    soon = now + timescale
    w = WeightedAverage(timescale=timescale)
    num_samples = 100000
    samples = []
    for i in xrange(num_samples):
        sample = random.random()  # Mean 0.5, std 12**-0.5
        w.add_sample(sample, event_time=now)
        samples.append(sample)
    mean, std, uncertainty = w.get_mean_std_uncertainty(event_time=now)
    assert approx_equal(mean, numpy.mean(samples))
    assert approx_equal(std, numpy.std(samples))
    assert approx_equal(uncertainty, std / num_samples ** 0.5)
    # After some time, uncertainty has increased, but mean and std are stable
    mean2, std2, uncertainty2 = w.get_mean_std_uncertainty(event_time=soon)
    assert approx_equal(mean, mean2)
    assert approx_equal(std, std2)
    assert approx_equal(uncertainty * 2 ** .5, uncertainty2)


def test_bootstrap():
    timescale = 1.  # 1 second
    num_samples = 2 ** 20
    tol = 0.05
    b = Bootstrap(timescale=timescale)
    start_time = time.time()
    b.add_sample(1., event_time=start_time)
    b.add_sample(2., event_time=start_time + timescale, weight=2.)
    b.add_sample(3., event_time=start_time + 2 * timescale)
    b.add_sample(4., event_time=start_time + 3 * timescale)
    samples = b.get_samples(num_samples)
    sample_counts = Counter(samples)
    assert len(samples) == num_samples
    # Check that the ratios of the sample counts are as expected
    assert sample_counts[4] > 0
    assert approx_equal(sample_counts[4], sample_counts[3] * 2, tol=tol)
    assert approx_equal(sample_counts[4], sample_counts[2] * 2, tol=tol)
    assert approx_equal(sample_counts[4], sample_counts[1] * 8, tol=tol)

    # Test resampling with a predicate
    b2 = b.resample(lambda s: s>2)
    samples2 = b2.get_samples(num_samples)
    sample_counts2 = Counter(samples2)
    assert sample_counts2[4] > 0
    assert approx_equal(sample_counts2[4], sample_counts2[3] * 2, tol=tol)
    assert sample_counts2[2] == 0
    assert sample_counts2[1] == 0
    

