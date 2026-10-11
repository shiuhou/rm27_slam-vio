"""Synthetic offline gap attribution tests, no new capture or manufactured PASS."""
import importlib.util
from pathlib import Path
import unittest
path=Path(__file__).resolve().parent/'analyze_failure.py'
if path.exists():
    spec=importlib.util.spec_from_file_location('failure_analysis',path)
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
else:a=None

def frame(seq,typ='HEARTBEAT',logging=None):
    return dict(event='frame',sysid=1,compid=1,seq=seq,type=typ,receipt_mono_ns=seq*1_000_000,
                fields={'sequence':logging} if logging is not None else {})

class AnalysisTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(a,'Saved failure wire analysis missing')
    def test_logging_gap_with_contiguous_transport_not_called_electrical_loss(self):
        result=a.wire_gaps([frame(10,'LOGGING_DATA',434),frame(11),frame(12,'LOGGING_DATA',436)])
        self.assertEqual(len(result['logging_discontinuities']),1)
        self.assertEqual(result['mavlink_sequence_discontinuities'],[])
        self.assertFalse(result['transport_qualified'])
    def test_wire_gap_and_modulo_wrap_are_distinct(self):
        result=a.wire_gaps([frame(254),frame(255),frame(0),frame(2)])
        self.assertEqual(len(result['mavlink_sequence_discontinuities']),1)
        self.assertEqual(result['mavlink_sequence_discontinuities'][0]['missing_modulo256'],1)
    def test_foreign_source_does_not_pollute_px4_sequence(self):
        foreign=frame(100);foreign['sysid']=2
        self.assertEqual(a.wire_gaps([frame(1),foreign,frame(2)])['mavlink_sequence_discontinuities'],[])
    def test_complete_prefix_view_never_appends_or_qualifies(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'imu-design-20261010/single-uart/controller'))
        from test_session import fixture
        raw=fixture()[:-1]
        view,excluded=a.complete_record_view(raw)
        self.assertEqual(raw[:len(view)],view)
        self.assertGreater(excluded,0)
        self.assertEqual(len(view)+excluded,len(raw))

if __name__=='__main__':unittest.main()
