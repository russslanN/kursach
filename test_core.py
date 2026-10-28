import unittest
from core import Room,MAX_CODE
class RoomTests(unittest.TestCase):
    def setUp(self): self.r=Room()
    def test_01_initial_revision(self): self.assertEqual(self.r.revision,0)
    def test_02_initial_code_string(self): self.assertIsInstance(self.r.code,str)
    def test_03_join_returns_snapshot(self): self.assertEqual(self.r.join('a','Ann')['type'],'snapshot')
    def test_04_join_registers_user(self): self.r.join('a','Ann');self.assertEqual(self.r.users['a'],'Ann')
    def test_05_trim_username(self): self.r.join('a',' Ann ');self.assertEqual(self.r.users['a'],'Ann')
    def test_06_reject_blank_name(self):
        with self.assertRaises(ValueError): self.r.join('a','  ')
    def test_07_reject_empty_id(self):
        with self.assertRaises(ValueError): self.r.join('','Ann')
    def test_08_max_name(self): self.r.join('a','z'*100);self.assertEqual(len(self.r.users['a']),32)
    def test_09_leave(self): self.r.join('a','Ann');self.r.leave('a');self.assertFalse(self.r.users)
    def test_10_leave_unknown(self): self.r.leave('unknown');self.assertEqual(self.r.revision,0)
    def test_11_snapshot_users(self): self.r.join('a','Ann');self.assertIn('Ann',self.r.snapshot()['users'])
    def test_12_valid_update(self): self.assertEqual(self.r.update('x',0)['type'],'update')
    def test_13_update_code(self): self.r.update('x',0);self.assertEqual(self.r.code,'x')
    def test_14_increment_revision(self): self.r.update('x',0);self.assertEqual(self.r.revision,1)
    def test_15_outdated_revision(self): self.r.update('x',0);self.assertEqual(self.r.update('y',0)['type'],'conflict')
    def test_16_conflict_does_not_overwrite(self): self.r.update('x',0);self.r.update('y',0);self.assertEqual(self.r.code,'x')
    def test_17_reject_nontext(self): self.assertEqual(self.r.update(123,0)['type'],'error')
    def test_18_reject_large(self): self.assertEqual(self.r.update('a'*(MAX_CODE+1),0)['type'],'error')
    def test_19_reject_float_revision(self): self.assertEqual(self.r.update('x',0.0)['type'],'error')
    def test_20_empty_document(self): self.r.update('',0);self.assertEqual(self.r.code,'')
if __name__=='__main__': unittest.main()
