"""OFFLINE saved-wire attribution only; no UART, transmit, repair or admission.

Reuse pymavlink CRC/checksum and existing capture/ULog audits. Decode one WIP
diagnostic using the EXACT firmware submodule XML, not the installed latest map.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

from pymavlink.dialects.v20.common import x25crc
from pymavlink.generator import mavparse

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent/'imu-uart-negotiated-trial-20261011'
XML_SHA = 'bbc1c382a217209f2cb3922416539da3226878dd19c7549f928913a6f72b1498'

@lru_cache(maxsize=1)
def link_schema():
    path = HERE/'source/common.xml'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != XML_SHA:
        raise ValueError('Pinned MAVLink XML hash differs')
    node = ET.fromstring(raw).find("./messages/message[@id='8']")
    if node is None or node.get('name') != 'LINK_NODE_STATUS' or node.find('extensions') is not None:
        raise ValueError('Audited fixed LINK_NODE_STATUS schema absent')
    message = mavparse.MAVType(node.get('name'), 8, 0)
    message.fields = [mavparse.MAVField(f.get('name'), f.get('type'), None, None) for f in node.findall('field')]
    if any(f.array_length for f in message.fields):
        raise ValueError('Audited scalar diagnostic layout changed')
    message.ordered_fields = sorted(message.fields, key=lambda f: -f.type_length)
    codes = {'uint64_t':'Q', 'uint32_t':'I', 'uint16_t':'H', 'uint8_t':'B'}
    fmt = '<'+''.join(codes[f.type] for f in message.ordered_fields)
    return dict(id=8, name=message.name, length=struct.calcsize(fmt), fmt=fmt,
                fields=[f.name for f in message.ordered_fields], crc_extra=mavparse.message_checksum(message))

def decode_link(row):
    schema = link_schema()
    wire = bytes.fromhex(row['wire_hex'])
    if len(wire) < 8 or wire[0] not in (253, 254):
        raise ValueError('Incomplete MAVLink diagnostic')
    v2 = wire[0] == 253
    header = 10 if v2 else 6
    length = wire[1]
    if (len(wire) != header+length+2 or not 1 <= length <= schema['length']
            or (not v2 and length != schema['length']) or (v2 and wire[2] != 0)):
        raise ValueError('Unexpected diagnostic length/signing/incompatibility flags')
    source = (wire[5], wire[6]) if v2 else (wire[3], wire[4])
    msgid = int.from_bytes(wire[7:10], 'little') if v2 else wire[5]
    seq = wire[4] if v2 else wire[2]
    if source != (1, 1) or msgid != 8:
        raise ValueError('Unexpected diagnostic source/message')
    if (row.get('sysid'), row.get('compid'), row.get('seq'), row.get('msgid')) != (*source, seq, msgid):
        raise ValueError('Stored header differs from raw diagnostic')
    crc = x25crc(wire[1:header+length]+bytes([schema['crc_extra']])).crc
    if crc != int.from_bytes(wire[-2:], 'little'):
        raise ValueError('Pinned diagnostic CRC verification failed')
    payload = wire[header:header+length].ljust(schema['length'], b'\0')
    fields = dict(zip(schema['fields'], struct.unpack(schema['fmt'], payload)))
    fields.update(seq=seq, receipt_mono_ns=row['receipt_mono_ns'], crc_verified=True,
        timestamp_unit='PX4_HRT_US_SOURCE_AUDITED_NOT_XML_MS',
        tx_overflows_unit='PX4_SEND_REJECTION_EVENTS_LOW16_NOT_XML_BYTES',
        free_buffer_status='UNKNOWN_TX_RX_BUF_ARE_TODO_ZERO')
    return fields

def verify_unknown_frame(row):
    """CRC-only audit of five retained unknown types; no new receive dialect."""
    names = {8: 'LINK_NODE_STATUS', 380: 'TIME_ESTIMATE_TO_TARGET',
             410: 'EVENT', 411: 'CURRENT_EVENT_SEQUENCE', 436: 'CURRENT_MODE'}
    msgid = row.get('msgid')
    if msgid not in names:
        raise ValueError('Unreviewed unknown frame type')
    link_schema()  # Pin common.xml before deriving another checksum.
    node = ET.parse(HERE/'source/common.xml').find(f"./messages/message[@id='{msgid}']")
    if node is None or node.get('name') != names[msgid] or node.find('extensions') is not None:
        raise ValueError('Audited fixed unknown schema differs')
    message = mavparse.MAVType(names[msgid], msgid, 0)
    message.fields = [mavparse.MAVField(f.get('name'), f.get('type'), None, None) for f in node.findall('field')]
    message.ordered_fields = sorted(message.fields, key=lambda f: -f.type_length)
    length = sum(f.type_length*(f.array_length or 1) for f in message.fields)
    extra = mavparse.message_checksum(message)
    wire = bytes.fromhex(row['wire_hex'])
    if len(wire) < 8 or wire[0] not in (253, 254):
        raise ValueError('Incomplete unknown frame')
    v2 = wire[0] == 253
    header = 10 if v2 else 6
    if (len(wire) != header+wire[1]+2 or not 1 <= wire[1] <= length
            or (v2 and wire[2] != 0) or (not v2 and wire[1] != length)):
        raise ValueError('Unexpected unknown frame length or flags')
    source = (wire[5], wire[6]) if v2 else (wire[3], wire[4])
    wire_id = int.from_bytes(wire[7:10], 'little') if v2 else wire[5]
    seq = wire[4] if v2 else wire[2]
    if (source != (1, 1) or wire_id != msgid
            or (row.get('sysid'), row.get('compid'), row.get('seq')) != (*source, seq)):
        raise ValueError('Unknown raw header/source differs')
    if x25crc(wire[1:header+wire[1]]+bytes([extra])).crc != int.from_bytes(wire[-2:], 'little'):
        raise ValueError('Pinned unknown CRC failed')
    return dict(msgid=msgid, name=names[msgid], crc_extra=extra, crc_verified=True)

def correlate(frames):
    frames = [r for r in frames if r.get('event') == 'frame' and (r.get('sysid'), r.get('compid')) == (1, 1)]
    snapshots = [dict(frame_index=i, **decode_link(r)) for i, r in enumerate(frames) if r.get('msgid') == 8]
    intervals = []
    for a, b in zip(snapshots, snapshots[1:]):
        segment = frames[a['frame_index']:b['frame_index']+1]
        gaps = []
        sequence_ambiguous = False
        for before, after in zip(segment, segment[1:]):
            step = (after['seq']-before['seq']) & 255
            if step != 1:
                sequence_ambiguous |= step == 0 or step >= 128
                gaps.append(dict(before_seq=before['seq'], after_seq=after['seq'],
                                 missing_modulo256=(step-1)&255))
        sent = b['messages_sent']-a['messages_sent']
        rejected = b['tx_overflows']-a['tx_overflows']
        observed = b['frame_index']-a['frame_index']
        missing = sum(x['missing_modulo256'] for x in gaps)
        if b['timestamp'] <= a['timestamp']:
            verdict = 'UNKNOWN_COUNTER_EPOCH'
        elif sent < 0 or rejected < 0:
            verdict = 'UNKNOWN_COUNTER_WRAP_OR_RESET'
        elif sequence_ambiguous:
            verdict = 'UNKNOWN_SEQUENCE_REORDER_RESET_OR_WRAP'
        elif sent != observed or missing != rejected:
            verdict = 'MIXED_OR_UNOBSERVED_DELIVERY_NOT_ISOLATED'
        elif rejected:
            verdict = 'ATTRIBUTED_PX4_TX_BUFFER_REJECTION_INTERVAL'
        else:
            verdict = 'CONSISTENT_NO_OBSERVED_REJECTION_IN_INTERVAL'
        intervals.append(dict(before_frame_index=a['frame_index'], after_frame_index=b['frame_index'],
            before_px4_hrt_us=a['timestamp'], after_px4_hrt_us=b['timestamp'],
            before_receipt_ns=a['receipt_mono_ns'], after_receipt_ns=b['receipt_mono_ns'],
            tx_success_delta=sent, tx_rejected_delta=rejected, received_frame_count=observed,
            unaccounted_successful_sends=sent-observed, sequence_gaps=gaps,
            missing_modulo_positions=missing, verdict=verdict))
    return dict(snapshots=snapshots, intervals=intervals,
        status='COUNTER_INTERVALS_EVALUATED' if intervals else 'UNKNOWN_NO_COUNTER_INTERVAL',
        caveat='Unsigned counters/source audited; not authentication or exact sensor loss; before-first/after-last unobserved',
        transport_qualified=False, openvins_admissible=False)

def packet_metadata(rows):
    """Complete packet-local M records only; never join across missing packets."""
    records = []; seen = set(); duplicates = truncated = 0
    for row in rows:
        if row.get('type') != 'LOGGING_DATA_ACKED':
            continue
        f = row['fields']
        if (row.get('event') != 'frame' or row.get('crc_status') != 'VERIFIED'
                or row.get('mavlink_version') != 2 or (row.get('sysid'), row.get('compid')) != (1, 1)
                or (f.get('target_system'), f.get('target_component')) != (1, 191)):
            raise ValueError('Unverified or unexpected metadata route')
        length, offset = f['length'], f['first_message_offset']
        if type(length) is not int or not 1 <= length <= 249 or len(f['data']) != 249:
            raise ValueError('Invalid logging metadata length')
        payload = bytes(f['data'][:length])
        fingerprint = (f['sequence'], length, offset, payload)
        if fingerprint in seen:
            duplicates += 1; continue
        seen.add(fingerprint)
        if offset == 255:
            continue
        if type(offset) is not int or not 0 <= offset < length:
            raise ValueError('Invalid metadata boundary')
        cursor = offset
        while cursor+3 <= length:
            size, kind = struct.unpack_from('<HB', payload, cursor)
            end = cursor+3+size
            if end > length:
                truncated += 1; break
            body = payload[cursor+3:end]
            if kind == ord('M'):
                if len(body) < 2 or body[0] not in (0, 1) or 2+body[1] > len(body):
                    raise ValueError('Invalid complete ULog metadata record')
                key = body[2:2+body[1]].decode('utf-8')
                value = body[2+body[1]:]
                match = re.fullmatch(r'char\[(\d+)\] ([A-Za-z0-9_]+)', key)
                if match:
                    if int(match[1]) != len(value):
                        raise ValueError('Metadata value differs from declared type')
                    records.append(dict(logging_sequence=f['sequence'], packet_offset=cursor,
                        receipt_mono_ns=row['receipt_mono_ns'], key=match[2], typed_key=key,
                        continued=bool(body[0]), value=value.decode('utf-8'),
                        evidence_kind='PACKET_LOCAL_COMPLETE_METADATA_NOT_RECOVERED_DATASET'))
            cursor = end
    return dict(records=records, duplicates_ignored=duplicates,
        truncated_records_not_decoded=truncated, transport_qualified=False, openvins_admissible=False)

def burst_bound(lengths, *, baud, free_bytes):
    if not lengths or any(type(x) is not int or x <= 0 for x in lengths):
        raise ValueError('Positive integer frame sizes required')
    if type(baud) is not int or baud <= 0 or type(free_bytes) is not int or free_bytes < 0:
        raise ValueError('Explicit baud/free byte bound required')
    need = sum(lengths)
    return dict(required_bytes=need, modeled_free_bytes=free_bytes, fits_without_drain=need <= free_bytes,
        minimum_drain_s=max(0, need-free_bytes)/(baud/10),
        evidence_kind='SYNTHETIC_NO_DRAIN_SENSITIVITY_NOT_MEASURED_QUEUE')

def main():
    sys.path.insert(0, str(TRIAL))
    from analyze_failure import complete_record_view
    sys.path.insert(0, str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture
    from ulog_mavlink import validate_ulog
    capture = TRIAL/'download/physical-trial-01'
    audit = audit_capture(capture, epoch='CURRENT_D6F12AD1_FAILED_UART_PREFIX')
    assert audit == json.loads((TRIAL/'capture-audit.json').read_text())
    assert audit['session']['error'] == 'logging sequence discontinuity: expected 435, received 436'
    rows = [json.loads(x) for x in (capture/'wire.jsonl').read_text().splitlines()]
    frames = [r for r in rows if r.get('event') == 'frame' and (r.get('sysid'), r.get('compid')) == (1, 1)]
    counters = correlate(frames)
    log436 = next(i for i, r in enumerate(frames) if r['type'] == 'LOGGING_DATA' and r['fields']['sequence'] == 436)
    critical = next(i for i in counters['intervals'] if i['before_frame_index'] < log436 < i['after_frame_index'])
    assert len(counters['snapshots']) == 10
    assert all(i['unaccounted_successful_sends'] == 0 for i in counters['intervals'])
    assert sum(i['tx_rejected_delta'] for i in counters['intervals']) == 6
    assert critical['tx_rejected_delta'] == critical['missing_modulo_positions'] == 1
    assert critical['sequence_gaps'] == [dict(before_seq=34, after_seq=36, missing_modulo256=1)]
    assert critical['verdict'] == 'ATTRIBUTED_PX4_TX_BUFFER_REJECTION_INTERVAL'
    metadata = packet_metadata([r for r in frames if r['type'] == 'LOGGING_DATA_ACKED' and r['fields']['sequence'] >= 437])
    postflight = [r for r in metadata['records'] if r['key'] == 'perf_counter_postflight' and not r['continued']]
    assert any(r['value'] == 'mavlink: ulog_stream messages missed: 0 events' for r in postflight)
    raw = (capture/'received-prefix.bin').read_bytes()
    original_sha = hashlib.sha256(raw).hexdigest()
    view, excluded = complete_record_view(raw)
    _, ulog = validate_ulog(view)
    statuses = []
    for data in ulog.data_list:
        if data.name == 'logger_status':
            statuses = [{key: values[index].item() for key, values in data.data.items()}
                        for index in range(len(data.data['timestamp']))]
    result = dict(scope='OFFLINE_SAVED_REAL_FAILED_TRIAL_NO_NEW_CAPTURE',
        exact_px4_hash='d6f12ad1c4f70ad3230afd7d86e971421e02fef4',
        mavlink_submodule_hash='33af200d25ec6f0925b49b1ba82bbf1294ea5f72',
        raw_replay_verified=True, raw_prefix_sha256=original_sha,
        original_failure=audit['session']['error'], diagnosis='PX4_TX_SEND_BUFFER_REJECTION_ACCOUNTING_MATCHES_TERMINAL_GAP',
        counters=counters, logging435_counter_interval=critical, packet_local_post_failure_metadata=metadata,
        diagnostic_in_memory_excluded_partial_bytes=excluded, retained_logger_status=statuses,
        source_coverage='SEPARATE_RETAINED_INTEGRAL_GAPS_UNRESOLVED_NOT_FIXED_BY_TRANSPORT',
        cause_scope='Confirmed sender FIONSPACE rejection layer; exact scheduling/burst/driver drain trigger not measured',
        synthetic_burst_sensitivity=burst_bound([267]*3, baud=921600, free_bytes=799),
        receiver_loss_evidence='NO_UNACCOUNTED_SUCCESSFUL_SENDS_IN_NINE_COUNTER_INTERVALS_NOT_UNIVERSAL_NO_LOSS_PROOF',
        firmware_patch='NOT_IMPLEMENTED', physical_fix='NOT_VALIDATED',
        source_complete='UNKNOWN', tail_complete='UNKNOWN', clock_synchronization='UNKNOWN',
        transport_qualified=False, openvins_admissible=False, vio_s0='PARTIAL', stage_c='CLOSED')
    assert hashlib.sha256((capture/'received-prefix.bin').read_bytes()).hexdigest() == original_sha
    with (HERE/'diagnosis.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2, allow_nan=False))

if __name__ == '__main__': main()
