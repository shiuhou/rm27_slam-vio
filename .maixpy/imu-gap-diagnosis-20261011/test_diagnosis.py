"""Synthetic offline diagnostics; not a physical PASS or altered acceptance."""
import importlib.util
from pathlib import Path
import struct
import unittest
from pymavlink.dialects.v20.common import x25crc

path = Path(__file__).resolve().parent/'diagnose.py'
if path.exists():
    spec = importlib.util.spec_from_file_location('diagnosis', path)
    d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
else:
    d = None

def link_frame(seq=1, stamp=1_000_000, sent=10, overflow=0, source=(1, 1), v2=True, truncate=True):
    # Independent fixed-layout fixture, checked against the pinned XML schema.
    payload = struct.pack('<QIIIIIHHHBB', stamp, 20_000, 100, sent, 10, 0, 0, overflow, 0, 0, 0)
    if v2:
        if truncate: payload = payload.rstrip(b'\0') or b'\0'
        wire = bytes([253, len(payload), 0, 0, seq, *source, 8, 0, 0])+payload
    else:
        wire = bytes([254, len(payload), seq, *source, 8])+payload
    wire += struct.pack('<H', x25crc(wire[1:]+bytes([117])).crc)
    return dict(event='frame', seq=seq, sysid=source[0], compid=source[1], msgid=8,
                type='UNKNOWN_8', wire_hex=wire.hex(), receipt_mono_ns=stamp*1000,
                mavlink_version=2 if v2 else 1, crc_status='UNKNOWN_DIALECT_UNVERIFIED')

def other(seq, receipt=1_500_000_000):
    return dict(event='frame', seq=seq, sysid=1, compid=1, msgid=0, type='HEARTBEAT',
                receipt_mono_ns=receipt)

def logging(sequence, payload, offset=0):
    return dict(event='frame', seq=20, sysid=1, compid=1, type='LOGGING_DATA_ACKED',
                crc_status='VERIFIED', mavlink_version=2, receipt_mono_ns=2_000_000_000,
                fields=dict(sequence=sequence, length=len(payload), first_message_offset=offset,
                            target_system=1, target_component=191,
                            data=list(payload.ljust(249, b'\0'))))

def info(value='mavlink: ulog_stream messages missed: 0 events'):
    key = ('char[%d] perf_counter_postflight' % len(value)).encode()
    body = bytes([0, len(key)])+key+value.encode()
    return struct.pack('<HB', len(body), ord('M'))+body

class DecodeTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(d, 'Pinned offline LINK_NODE_STATUS diagnostic missing')
    def test_exact_xml_layout_crc_and_trimmed_v2(self):
        schema = d.link_schema()
        self.assertEqual((schema['id'], schema['crc_extra'], schema['length']), (8, 117, 36))
        row = d.decode_link(link_frame(overflow=5))
        self.assertEqual(row['tx_overflows'], 5)
        self.assertEqual(row['timestamp'], 1_000_000)
        self.assertEqual(row['timestamp_unit'], 'PX4_HRT_US_SOURCE_AUDITED_NOT_XML_MS')
        self.assertEqual(row['tx_overflows_unit'], 'PX4_SEND_REJECTION_EVENTS_LOW16_NOT_XML_BYTES')
        self.assertEqual(row['free_buffer_status'], 'UNKNOWN_TX_RX_BUF_ARE_TODO_ZERO')
    def test_v1_full_payload_still_crc_checked(self):
        self.assertEqual(d.decode_link(link_frame(v2=False))['messages_sent'], 10)
    def test_bad_crc_wrong_source_length_or_flags_refused(self):
        good = link_frame()
        for wire in (bytes.fromhex(good['wire_hex'])[:-1],
                     bytes.fromhex(good['wire_hex'])[:-1]+b'\x00',
                     bytes.fromhex(good['wire_hex'])[:2]+b'\x01'+bytes.fromhex(good['wire_hex'])[3:]):
            row = dict(good, wire_hex=wire.hex())
            with self.subTest(wire=wire.hex()), self.assertRaises(ValueError): d.decode_link(row)
        with self.assertRaises(ValueError): d.decode_link(link_frame(source=(2, 1)))
    def test_sender_counter_and_global_gap_agree(self):
        frames = [link_frame(seq=10, sent=100), other(11), link_frame(seq=13, stamp=2_000_000, sent=102, overflow=1)]
        interval = d.correlate(frames)['intervals'][0]
        self.assertEqual(interval['tx_rejected_delta'], 1)
        self.assertEqual(interval['tx_success_delta'], interval['received_frame_count'])
        self.assertEqual(interval['verdict'], 'ATTRIBUTED_PX4_TX_BUFFER_REJECTION_INTERVAL')
    def test_receiver_missing_frame_is_not_sole_sender_rejection(self):
        frames = [link_frame(seq=10, sent=100), link_frame(seq=13, stamp=2_000_000, sent=102, overflow=1)]
        interval = d.correlate(frames)['intervals'][0]
        self.assertEqual(interval['unaccounted_successful_sends'], 1)
        self.assertEqual(interval['verdict'], 'MIXED_OR_UNOBSERVED_DELIVERY_NOT_ISOLATED')
    def test_counter_wrap_or_reset_never_automatically_confirmed(self):
        frames = [link_frame(sent=2**32-1, overflow=65535), link_frame(seq=2, stamp=2_000_000, sent=0, overflow=0)]
        self.assertEqual(d.correlate(frames)['intervals'][0]['verdict'], 'UNKNOWN_COUNTER_WRAP_OR_RESET')
    def test_timestamp_reset_breaks_epoch(self):
        frames = [link_frame(), link_frame(seq=2, stamp=500_000, sent=11)]
        self.assertEqual(d.correlate(frames)['intervals'][0]['verdict'], 'UNKNOWN_COUNTER_EPOCH')
    def test_no_counter_samples_stay_unknown(self):
        self.assertEqual(d.correlate([other(1)])['status'], 'UNKNOWN_NO_COUNTER_INTERVAL')

class MetadataTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(d, 'Boundary-scoped post-failure metadata diagnostics missing')
    def test_complete_post_failure_metadata_dedup_without_reassembly(self):
        raw = b'partial'+info()+info('second')[:-1]
        rows = [logging(437, raw, offset=7)]*3
        result = d.packet_metadata(rows)
        self.assertEqual(len(result['records']), 1)
        self.assertEqual(result['records'][0]['value'], 'mavlink: ulog_stream messages missed: 0 events')
        self.assertEqual(result['duplicates_ignored'], 2)
        self.assertFalse(result['transport_qualified'])
        self.assertEqual(result['truncated_records_not_decoded'], 1)
    def test_no_boundary_does_not_guess_or_join(self):
        self.assertEqual(d.packet_metadata([logging(437, info(), 255)])['records'], [])
    def test_bad_route_not_admitted_for_metadata(self):
        row = logging(437, info()); row['fields']['target_component'] = 190
        with self.assertRaises(ValueError): d.packet_metadata([row])

class UnknownWireTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(hasattr(d, 'verify_unknown_frame'), 'Pinned CRC verification for other retained unknown frames missing')

    def row(self):
        payload = struct.pack('<HB', 1234, 1)
        wire = bytes([253, len(payload), 0, 0, 25, 1, 1, 155, 1, 0])+payload
        wire += struct.pack('<H', x25crc(wire[1:]+bytes([106])).crc)
        return dict(event='frame', msgid=411, seq=25, sysid=1, compid=1,
                    type='UNKNOWN_411', wire_hex=wire.hex())

    def test_other_unknown_crc_is_verified_from_exact_definition(self):
        result = d.verify_unknown_frame(self.row())
        self.assertEqual(result['name'], 'CURRENT_EVENT_SEQUENCE')
        self.assertEqual(result['crc_extra'], 106)
        self.assertTrue(result['crc_verified'])

    def test_unknown_corruption_or_stored_header_mismatch_rejected(self):
        row = self.row()
        corrupt = bytearray.fromhex(row['wire_hex']); corrupt[10] ^= 1
        for bad in (dict(row, wire_hex=corrupt.hex()), dict(row, seq=26)):
            with self.assertRaises(ValueError): d.verify_unknown_frame(bad)

    def test_unreviewed_schema_is_not_guessed(self):
        with self.assertRaises(ValueError): d.verify_unknown_frame(dict(self.row(), msgid=999))

class BurstTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(d, 'Explicitly labeled burst sensitivity calculation missing')
    def test_mean_headroom_does_not_imply_instant_burst_fits(self):
        result = d.burst_bound([267]*3, baud=921600, free_bytes=799)
        self.assertEqual(result['required_bytes'], 801)
        self.assertFalse(result['fits_without_drain'])
        self.assertGreater(result['minimum_drain_s'], 0)
        self.assertEqual(result['evidence_kind'], 'SYNTHETIC_NO_DRAIN_SENSITIVITY_NOT_MEASURED_QUEUE')

if __name__ == '__main__': unittest.main()
