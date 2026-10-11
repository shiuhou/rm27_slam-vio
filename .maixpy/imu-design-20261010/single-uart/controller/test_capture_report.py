"""Offline result audit tests using synthetic wire peer, never transport PASS."""
import json
from pathlib import Path
import tempfile
import unittest
from test_uart_session import Clock, Peer
from uart_session import run_session
from test_session import fixture, packets

try:
    from capture_report import audit_capture, distribution
except ImportError:
    audit_capture = distribution = None


class ReportTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(audit_capture,'capture audit implementation missing')

    def test_receipt_clock_is_never_called_source_latency(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'peer'
            run_session(Peer(clock),output,seconds=1,clock=clock)
            result = audit_capture(output,epoch='SYNTHETIC_ONLY')
        self.assertTrue(result['raw_decode_parity'])
        self.assertEqual(result['imu']['count'],2)
        self.assertAlmostEqual(result['imu']['source_intervals']['effective_hz'],200)
        self.assertEqual(result['imu']['clock_status'],'UNKNOWN')
        self.assertIsNone(result['end_to_end_latency_ms'])
        self.assertFalse(result['openvins_admissible'])
        self.assertEqual(result['upstream_source_complete'],'UNKNOWN')
        self.assertEqual(result['tail_complete'],'UNKNOWN')
        self.assertEqual(result['imu']['gyro_device_id'],6684690)
        self.assertEqual(result['imu']['accel_device_id'],6946834)

    def test_raw_wire_tampering_cannot_pass_parity(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'peer'
            run_session(Peer(clock),output,seconds=1,clock=clock)
            rows = [json.loads(x) for x in (output/'wire.jsonl').read_text().splitlines()]
            next(r for r in rows if r['event']=='rx_chunk')['wire_hex']='00'
            # Test-only adversarial file mutation inside isolated fixture directory.
            (output/'wire.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError,'parity'): audit_capture(output,epoch='SYNTHETIC_ONLY')

    def test_wrong_imu_ids_never_qualified(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'peer'
            run_session(Peer(clock),output,seconds=1,clock=clock)
            result = audit_capture(output,epoch='SYNTHETIC_ONLY',gyro_device=3604506)
        self.assertEqual(result['imu_status'],'FAILED')
        self.assertIn('identity',result['imu_error'])
        self.assertFalse(result['openvins_admissible'])

    def test_partial_capture_reports_failure_without_parsing_as_success(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'peer'
            run_session(Peer(clock,'partial'),output,seconds=1,clock=clock)
            result = audit_capture(output,epoch='SYNTHETIC_ONLY')
        self.assertEqual(result['imu_status'],'NOT_PARSED_FAILED_SESSION')
        self.assertFalse(result['transport_qualified'])

    def test_statistics_percentile_empty_and_ordering(self):
        self.assertEqual(distribution([])['p99'],None)
        result = distribution([1,2,3,100])
        self.assertEqual(result['max'],100)
        self.assertGreater(result['p99'],result['p95'])

    def test_truncated_tail_reports_retained_integrals_without_repair(self):
        clock = Clock(); peer = Peer(clock)
        original_write = peer.write
        def truncate_source(wire):
            result = original_write(wire)
            if len(peer.queue)>2:
                peer.queue = peer.queue[:1]+packets(fixture()[:-1])
            return result
        peer.write = truncate_source
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'truncated'
            summary = run_session(peer,output,seconds=1,clock=clock)
            original = (output/'received-prefix.bin').read_bytes()
            report = audit_capture(output,epoch='SYNTHETIC_TRUNCATION_ONLY')
            self.assertEqual((output/'received-prefix.bin').read_bytes(),original)
            self.assertFalse((output/'framing-valid.ulg').exists())
        self.assertIn('truncated',summary['error'])
        self.assertEqual(report['imu_status'],'PARTIAL_PREFIX_DIAGNOSTICS_ONLY')
        self.assertEqual(report['imu']['count'],1)
        self.assertGreater(report['analysis_prefix_excluded_bytes'],0)
        self.assertFalse(report['transport_qualified'])


if __name__ == '__main__': unittest.main()
