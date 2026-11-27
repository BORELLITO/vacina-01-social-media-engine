import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from visual_qa import stats, FRAMESIZE, audit

class TestVisualQA(unittest.TestCase):
 def test_uniform_bright_detectable(self):
  d=stats(bytes([220])*FRAMESIZE)
  self.assertEqual(d['mean'],220)
  self.assertEqual(d['nearwhite_fraction'],1)
  self.assertEqual(d['std'],0)
 def test_low_brightness_not_blank(self):
  d=stats(bytes([110])*FRAMESIZE)
  self.assertEqual(d['nearwhite_fraction'],0)
 def test_checkerboard_has_contrast(self):
  d=stats(bytes([0,255])*(FRAMESIZE//2))
  self.assertGreater(d['std'],100)
  self.assertAlmostEqual(d['mean'],127.5)
 def test_frame_size_rejected(self):
  with self.assertRaises(ValueError):stats(b'')
 def test_real_v16_v17_if_present(self):
  root=Path('/mnt/data/VACINA01')
  a=root/'TESTE_MOTION_V1_6/R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4'
  b=root/'TESTE_MOTION_V1_7/R05_MAVIE_MICROTESTE_MOTION_V1_7.mp4'
  if not (a.exists() and b.exists()):
   self.skipTest('mídia original não está no workspace; nenhum QA real presumido')
  aa=audit(a);bb=audit(b)
  self.assertEqual(aa['total_frames'],324)
  self.assertEqual(bb['total_frames'],324)
  self.assertIn('QUADRO_QUASE_VAZIO_CLARO',aa['alertas'])
  self.assertNotIn('QUADRO_QUASE_VAZIO_CLARO',bb['alertas'])
  self.assertIn('QUEDA_CONTRASTE_TRANSICAO',bb['alertas'])
if __name__=='__main__': unittest.main()
