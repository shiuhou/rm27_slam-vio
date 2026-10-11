"""Synthetic timing fixtures, NOT real synchronized IMU or qualified VIO."""
from pathlib import Path
import unittest

import diagnosis as d


def fixture(times=(100000, 104500, 110500), dts=(4500, 4500, 6000)):
    return [dict(timestamp=t+200, timestamp_sample=t, delta_angle_dt=dt,
        delta_velocity_dt=5000, gyro_device_id=6684690, accel_device_id=6946834,
        gyro_calibration_count=1, accel_calibration_count=1,
        delta_angle_clipping=0, delta_velocity_clipping=0,
        delta_angle=[0., 0., 0.], delta_velocity=[0., 0., -.049])
        for t, dt in zip(times, dts)]


class CadenceTests(unittest.TestCase):
    def test_variable_integrals_are_not_loss(self):
        out=d.cadence(fixture())
        self.assertEqual(out['gyro_holes'], [])
        self.assertEqual(out['large_endpoint_intervals'], 0)
        self.assertEqual(out['covered_gyro_us'], 10500)
        self.assertFalse(out['openvins_admissible'])

    def test_large_fully_covered_interval_is_not_hole(self):
        out=d.cadence(fixture((100000,104500,109000,118000),(4500,4500,4500,9000)))
        self.assertEqual(out['large_endpoint_intervals'],1)
        self.assertEqual(out['gyro_holes'],[])

    def test_hole_is_current_dt_residual_not_endpoint_size(self):
        out=d.cadence(fixture((100000,104500,115017),(4500,4500,5963)))
        self.assertEqual(out['gyro_holes'][0]['residual_us'],4554)
        self.assertEqual(out['gyro_holes'][0]['after_index'],2)
        self.assertEqual(out['uncovered_gyro_us'],4554)
        self.assertEqual(out['accel_coverage'],'UNKNOWN_NO_SEPARATE_ENDPOINT')

    def test_overlap_is_not_loss(self):
        out=d.cadence(fixture(dts=(4500,4500,6500)))
        self.assertEqual(out['gyro_holes'],[])
        self.assertEqual(out['gyro_overlap_events'],1)

    def test_uint32_dt_and_uint64_endpoints_keep_integer_precision(self):
        rows=fixture((2**54,2**54+4500,2**54+10500))
        self.assertEqual(d.cadence(rows)['span_us'],10500)

    def test_ordering_rejected(self):
        with self.assertRaises(ValueError):d.cadence(fixture((100000,100000,110500)))

    def test_identity_or_calibration_change_requires_segmentation(self):
        for key in ('gyro_device_id','accel_calibration_count'):
            rows=fixture();rows[-1][key]+=1
            with self.assertRaises(ValueError):d.cadence(rows)

    def test_nonfinite_source_integral_rejected(self):
        rows=fixture();rows[-1]['delta_angle'][0]=float('nan')
        with self.assertRaises(ValueError):d.cadence(rows)

    def test_below_original_gate_not_rounded_to_pass(self):
        out=d.cadence(fixture((100000,105100,110200),(5100,5100,5100)))
        self.assertFalse(out['original_rate_gate_pass'])
        self.assertEqual(out['original_minimum_hz'],200)
        self.assertAlmostEqual(out['retained_hz'],1e6/5100)


class SourceModelTests(unittest.TestCase):
    def test_exact_200hz_configuration_is_quantized_not_timer_guarantee(self):
        out=d.configuration(200,1502.314,1247.794)
        self.assertEqual(out['gyro_samples'],3)
        self.assertEqual(out['accel_samples'],4)
        self.assertEqual(out['gyro_callback_updates'],3)
        self.assertEqual(out['gyro_reset_interval_us'],3756)
        self.assertEqual(out['accel_reset_interval_us'],4367)
        self.assertEqual(out['backup_schedule_us'],4991)
        self.assertEqual(out['semantic'],'TIMING_CONFIGURATION_MODEL_NOT_PUBLICATION_TRACE')

    def test_c_round_half_away_not_python_bankers(self):
        self.assertEqual(d.configuration(200,2000,1000)['gyro_samples'],3)

    def test_quantized_multiples_are_labeled_not_raw_counts(self):
        out=d.multiples([4991,4992,8735],1247.794,4)
        self.assertEqual(out['counts'],{'4':2,'7':1})
        self.assertEqual(out['extra_periods_over_baseline'],3)
        self.assertEqual(out['semantic'],'INFERRED_SI_PUBLICATION_PERIOD_MULTIPLES_NOT_HARDWARE_COUNTS')

    def test_bad_rate_inputs_rejected(self):
        for x in (0,-1,float('nan')):
            with self.assertRaises(ValueError):d.configuration(200,x,1247.)

    def test_small_config_rate_raise_does_not_guarantee_more_publications(self):
        # Timing-model sensitivity only; NO parameter writes or PASS simulation.
        a=d.configuration(200,1502.314,1247.794)
        b=d.configuration(210,1502.314,1247.794)
        for key in ('gyro_samples','accel_samples','gyro_callback_updates',
                    'gyro_reset_interval_us','accel_reset_interval_us','backup_schedule_us'):
            self.assertEqual(a[key],b[key])


class CounterTests(unittest.TestCase):
    def test_bracket_matches_not_point_timestamp_causality(self):
        hole=d.cadence(fixture((100000,104500,115017),(4500,4500,5963)))['gyro_holes']
        out=d.correlate(hole,[dict(timestamp=103000,message_gaps=1),
            dict(timestamp=120000,message_gaps=2)],['vehicle_imu'])
        self.assertEqual(out['counter_increment_events'],1)
        self.assertEqual(out['holes'][0]['attribution'],'LOGGER_VEHICLE_IMU_SUBSCRIPTION_SKIP')
        self.assertEqual(out['holes'][0]['exact_missing_generations'],'UNKNOWN')

    def test_multiple_fullrate_topics_ambiguous(self):
        hole=d.cadence(fixture((100000,104500,115017),(4500,4500,5963)))['gyro_holes']
        out=d.correlate(hole,[dict(timestamp=103000,message_gaps=1),
            dict(timestamp=120000,message_gaps=2)],['vehicle_imu','sensor_gyro'])
        self.assertEqual(out['holes'][0]['attribution'],'AMBIGUOUS')

    def test_reset_not_silently_summed(self):
        with self.assertRaises(ValueError):d.correlate([], [dict(timestamp=1,message_gaps=2),
            dict(timestamp=2,message_gaps=0)],['vehicle_imu'])

    def test_unbracketed_hole_stays_unknown(self):
        hole=d.cadence(fixture((100000,104500,115017),(4500,4500,5963)))['gyro_holes']
        out=d.correlate(hole,[dict(timestamp=200000,message_gaps=1),
            dict(timestamp=210000,message_gaps=2)],['vehicle_imu'])
        self.assertEqual(out['holes'][0]['attribution'],'UNKNOWN')


class SavedEvidenceTests(unittest.TestCase):
    def test_saved_real_log_not_synthetic_or_admitted(self):
        path=Path(__file__).resolve().parents[1]/'imu-uart-reduced-trial-20261011/download/physical-trial-01/framing-valid.ulg'
        out=d.analyze(path)
        self.assertEqual(out['provenance'],'REAL_SAVED_REDUCED_TELEMETRY_LOG_OFFLINE_REANALYSIS')
        self.assertEqual(out['cadence']['count'],11843)
        self.assertEqual(out['cadence']['uncovered_gyro_us'],4554)
        self.assertEqual(out['logger']['counter_increment_events'],1)
        self.assertFalse(out['cadence']['original_rate_gate_pass'])
        self.assertEqual(out['parameters']['IMU_INTEG_RATE'],200)
        self.assertEqual(out['accel_period_model']['counts'],{'4':11545,'5':37,'6':71,'7':190})
        self.assertFalse(out['openvins_admissible'])


if __name__=='__main__':unittest.main()
