import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'financeiro'))
from calcular import margem
class TestFinance(unittest.TestCase):
 def test_incomplete_never_zero(self):self.assertIsNone(margem(None,55,None,None,None,None,None)['lucro'])
 def test_margin(self):self.assertEqual(margem(200,55,10,20,5,10,20)['lucro'],80)
 def test_reject_negative(self):
  with self.assertRaises(ValueError):margem(200,55,-1,20,5,10,20)
