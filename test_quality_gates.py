import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quality_gate import check_strict


def example():
 return {'qualidade_v11':True,'benchmarks_audiovisuais':[], 'media_captada':[],'aprovacao_quadro_chave':None,'aprovacao_amostra':None}

class StrictGates(unittest.TestCase):
 def test_block_captions_as_watched(self):
  j=example();j['benchmarks_audiovisuais']=[{'tipo_evidencia':'LEGENDA_VERIFICADA','url':'https://instagram.com/reel/abc','criador':'a','observacoes_por_timestamp':['x','y'],'responsavel_revisao':'SCOUT'}]*3
  self.assertTrue(any('SCOUT' in x for x in check_strict(j,'TESTE_CURTO')))
 def test_block_boolean_without_proof(self):
  j=example();j['amostra_curtissima_aprovada']=True;j['frames_visuais_auditados']=True
  self.assertTrue(any('EDIT/QA' in x for x in check_strict(j,'EDICAO')))
 def test_block_actorless_creator_reel(self):
  j=example();j['media_captada']=[{'tipo':'video_real','profissional_real_em_cena':False,'sha256':'a'*64,'descricao':'Filmagem autenticada do pet em casa'}]
  self.assertTrue(any('Larissa' in x for x in check_strict(j,'EDICAO')))
 def test_block_fake_url(self):
  j=example();j['benchmarks_audiovisuais']=[{'tipo_evidencia':'VIDEO_ASSISTIDO','url':'https://fake.example/reel/abc','criador':str(i),'observacoes_por_timestamp':['0.5s','3.0s'],'responsavel_revisao':'SCOUT'} for i in range(3)]
  self.assertTrue(any('SCOUT' in x for x in check_strict(j,'TESTE_CURTO')))
 def test_block_unproven_clinical(self):
  j=example();self.assertTrue(any('VET:' in x for x in check_strict(j,'PUBLICAVEL')))
 def test_clinical_must_be_larissa(self):
  j=example();j['aprovacao_clinica']={'aprovado':True,'responsavel':'Borelli','versao':'c1','evidencia':'trecho validado documentalmente','data':'2026-11-25','fase':'CLINICA','arquivo_sha256':'f'*64,'referencia_aprovacao':'Mensagem usuário 25/11/2026'}
  self.assertTrue(any('VET:' in x for x in check_strict(j,'PUBLICAVEL')))
 def test_bad_fingerprint_blocked(self):
  j=example();j['aprovacao_quadro_chave']={'aprovado':True,'responsavel':'Borelli','versao':'v1','evidencia':'mensagem de aprovação','data':'2026-11-25','fase':'QUADRO_CHAVE','arquivo_sha256':'notvalid','referencia_aprovacao':'Mensagem 2026-11-25'}
  self.assertTrue(any('ART/QA' in x for x in check_strict(j,'TESTE_CURTO')))
 def test_zero_cost_discovery(self):
  self.assertEqual(check_strict(example(),'DISCOVERY'),[])
 def test_approval_format(self):
  j=example();j['aprovacao_quadro_chave']={'aprovado':True,'responsavel':'Borelli','versao':'frame-v1','evidencia':'arquivo real avaliado','data':'2026-11-25','fase':'QUADRO_CHAVE','arquivo_sha256':'f'*64,'referencia_aprovacao':'Mensagem Borelli 25/11/2026'}
  errs=check_strict(j,'TESTE_CURTO');self.assertFalse(any('ART/QA' in e for e in errs))

if __name__=='__main__':unittest.main()
