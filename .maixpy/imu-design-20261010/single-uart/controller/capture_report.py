"""Offline audit of a UART session directory; never manufactures admission/PASS."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from session import Controller, Reassembler, ReassemblyError
from startup_sync import StartupSync
from ulog_mavlink import decoder_module, inspect_imu


def distribution(values):
    values = sorted(values)
    if any(not math.isfinite(v) for v in values):
        raise ValueError('nonfinite metric')
    def percentile(q):
        if not values: return None
        position = (len(values)-1)*q
        lo = int(position); hi = min(lo+1,len(values)-1)
        return values[lo]+(values[hi]-values[lo])*(position-lo)
    return dict(count=len(values),median=statistics.median(values) if values else None,
                p95=percentile(.95),p99=percentile(.99),max=max(values) if values else None)


def _imu_summary(raw, *, instance, gyro_device, accel_device, epoch):
    imu = inspect_imu(raw,instance=instance,gyro_device=gyro_device,accel_device=accel_device,epoch=epoch)
    means = imu.pop('diagnostic_means')
    imu['publication_minus_sample_us'] = distribution([
        x['original']['timestamp']-x['original']['timestamp_sample'] for x in means])
    imu['gyro_dt_us'] = distribution([x['original']['delta_angle_dt'] for x in means])
    imu['accel_dt_us'] = distribution([x['original']['delta_velocity_dt'] for x in means])
    imu['gyro_coverage_residual_us_summary'] = distribution(imu.pop('gyro_coverage_residual_us'))
    return imu


def audit_capture(directory, *, epoch, instance=0,gyro_device=6684690,accel_device=6946834):
    directory = Path(directory)
    rows = [json.loads(line) for line in (directory/'wire.jsonl').read_text(encoding='utf-8').splitlines()]
    summary = json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    replay = []
    chunks = [r for r in rows if r.get('event') == 'rx_chunk']
    kinds = ('frame','bad_data')
    negotiation_events = ('mavlink2_negotiation_policy','mavlink2_negotiation_started',
                          'mavlink2_negotiation_confirmed')
    negotiation_policy = summary.get('mavlink2_negotiation_policy')
    negotiation_fields = ('negotiate_mavlink2','negotiation_started_mono_ns',
                          'negotiation_confirmed_mono_ns')
    if negotiation_policy is None:
        if (any(k in summary for k in negotiation_fields)
                or any(r.get('event') in negotiation_events for r in rows)):
            raise ValueError('missing negotiation policy on versioned capture')
        negotiate = False  # Historical captures retain their strict-v2 behavior.
    else:
        if negotiation_policy not in (Controller.STRICT_POLICY,Controller.NEGOTIATION_POLICY):
            raise ValueError('unsupported negotiation policy')
        negotiate = negotiation_policy == Controller.NEGOTIATION_POLICY
        if type(summary.get('negotiate_mavlink2')) is not bool or summary['negotiate_mavlink2'] != negotiate:
            raise ValueError('negotiation policy / opt-in mismatch')
        kinds += negotiation_events
    policy = summary.get('startup_policy')
    if policy is None and (any(k.startswith('startup_') for k in summary)
            or any(r.get('event') in ('startup_unframed','startup_boundary') for r in rows)):
        raise ValueError('missing startup policy on versioned capture')
    if policy is not None:
        if policy != StartupSync.POLICY:
            raise ValueError('unsupported startup policy')
        kinds += ('startup_unframed','startup_boundary')
        # Pure wire/state replay: emits intents only, never opens or writes IO.
        controller = Controller(summary['controller_started_mono_ns'],
                                seconds=summary['configured_duration_s'],emit=replay.append,
                                negotiate_mavlink2=negotiate)
        for row in chunks:
            controller.feed_wire(bytes.fromhex(row['wire_hex']),row['receipt_mono_ns'])
        replay_summary = controller.summary()
        for field in ('startup_boundary_found','startup_received_bytes',
                      'startup_excluded_bytes','startup_buffered_bytes','startup_completeness'):
            if (type(summary.get(field)) is not type(replay_summary[field])
                    or summary[field] != replay_summary[field]):
                raise ValueError('startup summary / raw wire parity failed: '+field)
        if negotiation_policy is not None:
            for field in negotiation_fields:
                if (field not in summary or type(summary.get(field)) is not type(replay_summary[field])
                        or summary[field] != replay_summary[field]):
                    raise ValueError('negotiation summary / raw wire parity failed: '+field)
        replay = [r for r in replay if r.get('event') in kinds]
    else:
        if negotiation_policy is not None:
            raise ValueError('negotiation policy requires versioned controller replay')
        decoder = decoder_module.Decoder()
        for row in chunks:
            replay.extend(decoder.feed(bytes.fromhex(row['wire_hex']),row['receipt_mono_ns']))
    stored = [r for r in rows if r.get('event') in kinds]
    if replay != stored:
        raise ValueError('raw wire / decoded row parity failed')
    if negotiate:
        # Actual write receipts, not timer-dependent intents, gate logging TX.
        # A valid intent/full wire does NOT prove a partial write was delivered.
        confirmed = summary['negotiation_confirmed_mono_ns']
        started = summary['negotiation_started_mono_ns']
        for row in rows:
            if row.get('event') != 'tx_write':
                continue
            wire = bytes.fromhex(row['wire_hex'])
            decoded = decoder_module.Decoder().feed(wire,row['receipt_mono_ns'])
            if (len(decoded) != 1 or decoded[0].get('event') != 'frame'
                    or decoded[0].get('crc_status') != 'VERIFIED'
                    or decoded[0].get('mavlink_version') != 2 or wire[2] != 0
                    or (decoded[0].get('sysid'),decoded[0].get('compid')) != (1,191)):
                raise ValueError('unverified negotiation TX frame')
            ns = row['receipt_mono_ns']
            if type(ns) is not int:
                raise ValueError('integer negotiation TX receipt required')
            if confirmed is None or ns < confirmed:
                if decoded[0]['type'] != 'HEARTBEAT' or started is None or ns < started:
                    raise ValueError('logging/control TX before MAVLink2 negotiation confirmation')
    raw = (directory/'received-prefix.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest() != summary['received_prefix_sha256']:
        raise ValueError('received prefix SHA mismatch')
    packet_rows = [r for r in rows if r.get('event') == 'logging_packet' and not r['retransmission']]
    receipt_ns = [r['receipt_mono_ns'] for r in packet_rows]
    receipt_delta = [(b-a)/1e6 for a,b in zip(receipt_ns,receipt_ns[1:])]
    wire_bytes = sum(len(r['wire_hex'])//2 for r in chunks)
    span = (chunks[-1]['receipt_mono_ns']-chunks[0]['receipt_mono_ns'])/1e9 if len(chunks)>1 else 0
    report = dict(raw_decode_parity=True,session=summary,
        wire_received_bytes=wire_bytes,wire_chunk_span_s=span,
        received_wire_B_s=wire_bytes/span if span>0 else None,
        logging_packet_receipt_interval_ms=distribution(receipt_delta),
        receipt_timing_caveat='Read/packet receipt burst statistics, not per-IMU latency; first/last-byte boundary not known',
        tx_write_calls=len([r for r in rows if r.get('event') == 'tx_write']),
        bad_data_events=len([r for r in rows if r.get('event') == 'bad_data']),
        startup_policy=policy,
        startup_excluded_bytes=sum(len(r['wire_hex'])//2 for r in stored
                                   if r['event'] == 'startup_unframed'),
        startup_completeness='NOT_MEASURED_PRE_START',
        upstream_source_complete='UNKNOWN',tail_complete='UNKNOWN',
        end_to_end_latency_ms=None,clock_synchronization='UNKNOWN',
        openvins_admissible=False,transport_qualified=False,
        imu_status='NOT_PARSED_FAILED_SESSION')
    if summary['error'] is None and summary['finite_framing_verified']:
        r = Reassembler()
        for row in stored:
            if row.get('event') in ('frame','bad_data'):
                r.feed(row)
        if r.finish() != raw or (directory/'framing-valid.ulg').read_bytes() != raw:
            raise ValueError('reassembly / prefix / framed-file bytes differ')
        try:
            imu = _imu_summary(raw,instance=instance,gyro_device=gyro_device,accel_device=accel_device,epoch=epoch)
            report.update(imu_status='DIAGNOSTICS_VERIFIED_NOT_OPENVINS',imu=imu)
        except (ReassemblyError,ValueError) as exc:
            report.update(imu_status='FAILED',imu_error=str(exc))
    elif str(summary['error']).startswith('truncated ULog record'):
        # Statistics on complete retained records ONLY. Do not write a shortened
        # ULog, modify received bytes, mark framing verified or admit this prefix.
        cursor = 16
        while cursor+3 <= len(raw):
            end = cursor+3+int.from_bytes(raw[cursor:cursor+2],'little')
            if end>len(raw): break
            cursor = end
        try:
            imu = _imu_summary(raw[:cursor],instance=instance,gyro_device=gyro_device,accel_device=accel_device,epoch=epoch)
            report.update(imu_status='PARTIAL_PREFIX_DIAGNOSTICS_ONLY',imu=imu,
                          analysis_prefix_excluded_bytes=len(raw)-cursor,
                          partial_analysis='IN_MEMORY_COMPLETE_RECORD_VIEW_ONLY; original bytes unchanged, session failed, no repaired ULog')
        except (ReassemblyError,ValueError) as exc:
            report.update(imu_status='FAILED_PARTIAL_PREFIX',imu_error=str(exc))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory'); p.add_argument('--epoch',required=True)
    p.add_argument('--output',required=True)
    args = p.parse_args()
    result = audit_capture(args.directory,epoch=args.epoch)
    with Path(args.output).open('x',encoding='utf-8') as output:
        json.dump(result,output,indent=2,allow_nan=False)
    print(json.dumps(dict(imu_status=result['imu_status'],transport_qualified=False,
                         openvins_admissible=False,tail_complete='UNKNOWN')))


if __name__ == '__main__': main()
