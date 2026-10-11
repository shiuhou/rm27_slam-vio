import unittest
import numpy as np
import analyze_ulog as a

class AnalysisTests(unittest.TestCase):
    def test_gap_timing_and_integer_order(self):
        s=a.timing(np.array([1000000000000,1000000000633,1000000001266,1000000002532],dtype=np.uint64))
        self.assertEqual(s['median_dt_us'],633)
        self.assertEqual(s['gaps_over_1_5_median'],1)
        self.assertEqual(s['estimated_missing_from_time_gaps'],1)
        self.assertEqual(s['nonincreasing'],0)
    def test_duplicate_and_backward_are_not_unsigned_wrapped(self):
        s=a.timing(np.array([1000,1000,999,1632],dtype=np.uint64))
        self.assertEqual(s['nonincreasing'],2)
        self.assertEqual(s['duplicates'],1)
    def test_scale_and_last_anchor(self):
        t,x=a.expand_fifo(dict(timestamp_sample=np.array([2000]),samples=np.array([2]),dt=np.array([625.]),scale=np.array([.01]),
           **{f'{axis}[{i}]':np.array([j]) for axis in 'xyz' for i,j in enumerate([10,20])}))
        np.testing.assert_array_equal(t,[1375,2000])
        np.testing.assert_allclose(x,[[.1,.1,.1],[.2,.2,.2]])

if __name__=='__main__': unittest.main()
