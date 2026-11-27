import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from orq_v2 import run

class TestVisualRoute(unittest.TestCase):
 def test_visual_stage_route(self):
  a=Path('/mnt/data/VACINA01/TESTE_MOTION_V1_6/R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4')
  b=Path('/mnt/data/VACINA01/TESTE_MOTION_V1_7/R05_MAVIE_MICROTESTE_MOTION_V1_7.mp4')
  if not (a.is_file() and b.is_file()): self.skipTest('mídia real não está no CI; worker visual não simulado')
  r=run('AUDITORIA_VISUAL',Path('/mnt/data'),assets_root=Path('/mnt/data'))
  self.assertIn('VISUAL-QA',r['agentes_planejados'])
  self.assertEqual(r['estado'],'AUDITORIA_VISUAL_COM_ALERTAS')
  self.assertEqual(r['evidencias']['VISUAL-QA']['tipo'],'WORKER_QA_VISUAL')
  self.assertEqual(r['subagentes_llm_realmente_executados'],[])
  self.assertFalse(r['publicou'])
 def test_missing_media_does_not_claim_analysis(self):
  from tempfile import TemporaryDirectory
  with TemporaryDirectory() as t:
   r=run('AUDITORIA_VISUAL',Path('/mnt/data'),assets_root=Path(t))
   self.assertEqual(r['evidencias']['VISUAL-QA']['tipo'],'NÃO_EXECUTADO_SEM_ASSETS_VERIFICADOS')
   self.assertTrue(r['bloqueios'])
