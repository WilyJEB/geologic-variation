"""Offline archive replay and rejection checks; no Minecraft/TD execution."""
import io,json,runpy,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=runpy.run_path(str(ROOT/'scripts/export-retained-navigation.py'))
class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=(ROOT/'docs/evidence/td-navigation.zip').read_bytes()
        cls.summary=json.loads((ROOT/'docs/evidence/td-navigation.json').read_text())
        assert E['sha'](data)==cls.summary['archive_sha256']
        with zipfile.ZipFile(io.BytesIO(data)) as z:cls.members={n:z.read(n) for n in z.namelist()}
    def test_replay_failed_outcome(self):
        self.assertEqual({n:E['sha'](b) for n,b in self.members.items()},self.summary['members'])
        for n,v in E['audit'](self.members).items():self.assertEqual(v,self.summary[n])
    def test_forbidden_class(self):
        m=dict(self.members);m['raw/attempt-02/class-load.log']+=b'ai.onnxruntime.OrtEnvironment'
        with self.assertRaises(AssertionError):E['audit'](m)
    def test_other_save(self):
        m=dict(self.members);n='raw/attempt-02/inventory.json';v=json.loads(m[n]);v['saves/continuing/level.dat']={};m[n]=json.dumps(v).encode()
        with self.assertRaises(AssertionError):E['audit'](m)
    def test_modified_records(self):
        m=dict(self.members);m['raw/attempt-02/executed/retained-map.tsv']+=b'changed'
        with self.assertRaises(AssertionError):E['audit'](m)
    def test_missing_guard(self):
        m=dict(self.members);n='raw/attempt-02/logs/debug.log';m[n]=m[n].replace(b'Mixing SaveBarrier',b'Missing SaveBarrier')
        with self.assertRaises(AssertionError):E['audit'](m)
if __name__=='__main__':unittest.main()
