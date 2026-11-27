import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from orq import check
class GateTests(unittest.TestCase):
 def setUp(self):
  self.job={'estado':'DISCOVERY','frames_visuais_auditados':False,'amostra_curtissima_aprovada':False,'consentimento_uso_imagem':True,'validacao_clinica_larissa':False,'aprovacao_estetica_final':False,'licenca_trilha':False,'fontes_e_marca_verificados':False,'autorizacao_publicar':False}
 def test_discovery_allowed(self):self.assertEqual(check(self.job,'DISCOVERY'),[])
 def test_no_reel_before_frames(self):self.assertIn('falta frame visual comparado à referencia',check(self.job,'EDICAO'))
 def test_no_reel_before_short(self):self.assertIn('teste de 3-5s sem aprovacao visual',check(self.job,'EDICAO'))
 def test_no_publish_without_larissa(self):self.assertIn('falta validacao clinica Larissa',check(self.job,'PUBLICAVEL'))
 def test_no_publish_without_final_approval(self):self.assertIn('falta autorizacao de publicacao',check(self.job,'PUBLICADO'))
 def test_good_state(self):
  self.job.update({'frames_visuais_auditados':True,'amostra_curtissima_aprovada':True,'consentimento_uso_imagem':True,'validacao_clinica_larissa':True,'aprovacao_estetica_final':True,'licenca_trilha':True,'fontes_e_marca_verificados':True,'autorizacao_publicar':True})
  self.assertEqual(check(self.job,'PUBLICADO'),[])
if __name__=='__main__':unittest.main()
