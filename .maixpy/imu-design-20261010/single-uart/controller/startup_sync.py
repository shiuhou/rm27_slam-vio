"""Bounded pre-START frame acquisition; no device IO or post-boundary recovery.

Reuse pymavlink CRC decoding. Unframed startup bytes are evidence, not IMU loss.
"""
from ulog_mavlink import decoder_module
from pymavlink.dialects.v10 import common as mavlink1


class StartupSync:
    POLICY = 'BOUNDED_CRC_SYNC_V1'
    MAX_BYTES = 65536
    MAX_FRAME = 280  # MAVLink2 header +255 payload +CRC +13 signature.

    def __init__(self, decoder):
        self.decoder = decoder  # Existing strict decoder after the boundary.
        self.buffer = bytearray()
        self.offset = self.received_bytes = self.excluded_bytes = 0
        self.complete = False

    def _unframed(self, count, receipt_ns):
        row = dict(event='startup_unframed',receipt_mono_ns=receipt_ns,
                   stream_offset=self.offset,wire_hex=bytes(self.buffer[:count]).hex(),
                   classification='UNFRAMED_OR_REJECTED_CANDIDATES_NOT_LOGGING_LOSS')
        self.excluded_bytes += count
        self._consume(count)
        return row

    def _consume(self, count):
        del self.buffer[:count]
        self.offset += count

    def feed(self, data, receipt_ns):
        if self.complete:
            return self.decoder.feed(data, receipt_ns)
        # Conservative cap includes the entire read containing the boundary.
        if self.received_bytes+len(data) > self.MAX_BYTES:
            raise ValueError('startup byte limit exceeded')
        self.received_bytes += len(data)
        self.buffer.extend(data)
        rows = []
        while self.buffer:
            pos = next((i for i,b in enumerate(self.buffer) if b in (0xfe,0xfd)),
                       len(self.buffer))
            if pos:
                rows.append(self._unframed(pos, receipt_ns))
            if not self.buffer:
                break
            magic = self.buffer[0]
            # Partial headers and plausible declared bodies are barriers. Never
            # search their payload for an embedded HEARTBEAT (even if split).
            if len(self.buffer) < 3:
                break
            if magic == 0xfd and self.buffer[2] & ~1:
                rows.append(self._unframed(1, receipt_ns))
                continue  # Unsupported incompatibility flags disprove header.
            header_size = 6 if magic == 0xfe else 10
            if len(self.buffer) < header_size:
                break
            payload_size = self.buffer[1]
            msgid = self.buffer[5] if magic == 0xfe else int.from_bytes(self.buffer[7:10],'little')
            dialect = mavlink1 if magic == 0xfe else decoder_module.m
            definition = dialect.mavlink_map.get(msgid)
            if definition is not None and (payload_size > definition.unpacker.size
                    or magic == 0xfe and payload_size != definition.unpacker.size):
                rows.append(self._unframed(1, receipt_ns))
                continue  # Known impossible length, not a merely incomplete body.
            length = payload_size+header_size+2
            if magic == 0xfd and self.buffer[2] & 1:
                length += 13
            if len(self.buffer) < length:
                break
            try:
                decoded = decoder_module.Decoder().feed(bytes(self.buffer[:length]),receipt_ns)
            except Exception:
                decoded = []
            if not (len(decoded) == 1 and decoded[0].get('event') == 'frame'
                    and decoded[0].get('crc_status') == 'VERIFIED'):
                # Unknown IDs / rejected CRCs are opaque excluded candidates,
                # not permission to scan payload. Plausible noise may therefore
                # consume a heartbeat or time out; fail closed within the caps.
                rows.append(self._unframed(length, receipt_ns))
                continue
            row = decoded[0]
            rows.append(row)
            self._consume(length)
            if row.get('type') == 'HEARTBEAT' and (row['sysid'],row['compid']) == (1,1):
                # Candidate framing boundary only. Controller still rejects
                # armed/signed/v1/wrong autopilot/version before any START/TX.
                self.complete = True
                rows.append(dict(event='startup_boundary',receipt_mono_ns=receipt_ns,
                                 stream_offset=self.offset,excluded_bytes=self.excluded_bytes,
                                 policy=self.POLICY,
                                 qualification='CRC_FRAME_BOUNDARY_NOT_AUTHENTICATION'))
                trailing = bytes(self.buffer)
                self._consume(len(self.buffer))
                rows.extend(self.decoder.feed(trailing, receipt_ns))
                break
        assert len(self.buffer) < self.MAX_FRAME
        return rows
