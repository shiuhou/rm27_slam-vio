"""Synthetic timing fixtures, NOT real synchronized IMU or VIO PASS."""
import unittest
try:
    from compare import comparison
except ImportError:
    comparison = None


def rows(times=(100000,105100,110200), dts=(5100,5100,5100)):
    return [dict(timestamp=t+200, timestamp_sample=t, delta_angle_dt=dt,
        delta_velocity_dt=5000, gyro_device_id=6684690, accel_device_id=6946834,
        gyro_calibration_count=1, accel_calibration_count=1,
        delta_angle_clipping=0, delta_velocity_clipping=0,
        delta_angle=[0.,0.,0.], delta_velocity=[0.,0.,-.049])
        for t,dt in zip(times,dts)]


def statuses(values=(1,1), times=(99000,121000)):
    return [dict(timestamp=t, message_gaps=g, type=0, backend=2, num_messages=8)
            for t,g in zip(times,values)]


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(comparison, 'offline reader comparison missing')

    def test_no_hole_does_not_make_rate_or_vio_pass(self):
        out=comparison(rows(),rows(),statuses())
        self.assertTrue(out['observed_gyro_continuity'])
        self.assertTrue(out['observed_subscription_continuity'])
        self.assertFalse(out['original_rate_gate_pass'])
        self.assertFalse(out['openvins_admissible'])
        self.assertEqual(out['stage_c'],'CLOSED')
        self.assertEqual(out['accel_coverage'],'UNKNOWN_NO_SEPARATE_ENDPOINT')

    def test_hole_has_current_dt_semantics(self):
        candidate=rows((100000,104500,115017),(4500,4500,5963))
        out=comparison(rows(),candidate,statuses((1,2)))
        self.assertEqual(out['candidate']['uncovered_gyro_us'],4554)
        self.assertFalse(out['observed_gyro_continuity'])
        self.assertEqual(out['candidate_logger']['counter_increment_events'],1)

    def test_changed_epoch_order_or_nonfinite_refused(self):
        for key,value in (('gyro_device_id',3604506),('accel_calibration_count',2),
            ('timestamp_sample',100000),('delta_angle',[float('nan'),0.,0.])):
            candidate=rows();candidate[-1][key]=value
            with self.assertRaises(ValueError):
                comparison(rows(),candidate,statuses())

    def test_counter_reset_missing_evidence_or_wrong_backend_refused(self):
        invalid=[[],statuses()[:1],statuses((2,1))]
        wrong=statuses();wrong[-1]['backend']=3;invalid.append(wrong)
        for sample in invalid:
            with self.assertRaises(ValueError):
                comparison(rows(),rows(),sample)

    def test_hole_outside_counter_bracket_stays_unknown(self):
        candidate=rows((100000,104500,115017),(4500,4500,5963))
        out=comparison(rows(),candidate,statuses((1,2),(99000,103000)))
        self.assertEqual(out['candidate_logger']['holes'][0]['attribution'],'UNKNOWN')
        self.assertFalse(out['openvins_admissible'])

    def test_large_integral_fully_covered_is_not_loss(self):
        candidate=rows((100000,105000,110000,120000),(5000,5000,5000,10000))
        out=comparison(rows(),candidate,statuses((1,1),(99000,121000)))
        self.assertTrue(out['observed_gyro_continuity'])
        self.assertEqual(out['candidate']['large_endpoint_intervals'],1)
        self.assertFalse(out['original_rate_gate_pass'])

    def test_counter_observation_does_not_certify_source_tail(self):
        out=comparison(rows(),rows(),statuses((1,1),(99000,103000)))
        self.assertEqual(out['logger_counter_window'],[99000,103000])
        self.assertEqual(out['tail_complete'],'UNKNOWN')
        self.assertEqual(out['source_complete'],'UNKNOWN')
