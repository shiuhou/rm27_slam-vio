"""Synthetic /proc deltas only, not claimed physical CPU measurements."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).with_name('trial_analysis.py')
if path.exists():
    spec=importlib.util.spec_from_file_location('trial_analysis',path)
    analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
else: analysis=None

def samples():
    return [dict(event='receiver_cpu',pid=42,starttime_ticks=5,clk_tck=100,
        receipt_mono_ns=t,utime_ticks=u,stime_ticks=s,rss_bytes=4096)
        for t,u,s in ((1000000000,1,1),(2000000000,2,1),(3000000000,3,2))]

class CPUDeltas(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(analysis,'Measured CPU summarizer missing')
    def test_actual_span_one_core_and_pre_gate_coverage(self):
        rows=samples()+[dict(event='receiver_gate_released',receipt_mono_ns=1100000000)]
        r=analysis.cpu_summary(rows)
        self.assertEqual(r['sample_span_s'],2.)
        self.assertAlmostEqual(r['cpu_seconds'],.03)
        self.assertAlmostEqual(r['mean_percent_of_one_core'],1.5)
        self.assertIs(r['first_sample_before_gate'],True)
    def test_incomplete_is_unknown_not_zero(self):
        self.assertEqual(analysis.cpu_summary(samples()[:1])['status'],'UNKNOWN_INSUFFICIENT_SAMPLES')
    def test_pid_counter_clock_and_order_changes_refused(self):
        for fields in (dict(pid=43),dict(starttime_ticks=6),dict(utime_ticks=0),
                       dict(clk_tck=250),dict(receipt_mono_ns=1000000000)):
            rows=samples();rows[1].update(fields)
            with self.assertRaises(ValueError): analysis.cpu_summary(rows)

class DiagnosticSerialization(unittest.TestCase):
    def test_nan_health_field_is_explicit_not_zero_or_silently_dropped(self):
        self.assertTrue(analysis is not None and hasattr(analysis,'diagnostic_json'),
            'Explicit nonfinite diagnostic encoding missing')
        source=dict(temperature_gyro=float('nan'),finite=[1.,0.,None,float('inf'),-float('inf')])
        encoded=analysis.diagnostic_json(source)
        self.assertEqual(encoded['temperature_gyro'],dict(status='NONFINITE_DIAGNOSTIC',value='nan'))
        self.assertEqual(encoded['finite'][:3],[1.,0.,None])
        self.assertEqual(encoded['finite'][3:],[
            dict(status='NONFINITE_DIAGNOSTIC',value='inf'),dict(status='NONFINITE_DIAGNOSTIC',value='-inf')])
        import math,json
        self.assertTrue(math.isnan(source['temperature_gyro']))
        json.dumps(encoded,allow_nan=False)

if __name__=='__main__':unittest.main()
