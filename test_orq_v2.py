import copy, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from orq_v2 import STAGES, run, approval, verify_sha, report_md, signed_authorization
LEDGER=json.loads((ROOT/'config'/'decisao_atual.json').read_text(encoding='utf8'))
MEDIA=Path('/mnt/data')

class TestOrqV2(unittest.TestCase):
 def test_v16_approval_only_for_motion_base(self):
  p=MEDIA/'VACINA01/TESTE_MOTION_V1_6/R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4'
  r=approval(LEDGER,'R05_MOTION_V1_6','BASE_MOTION',p)
  if p.is_file():self.assertTrue(r['ok'])
  self.assertFalse(approval(LEDGER,'R05_MOTION_V1_6','PUBLICACAO_FINAL',p)['ok'])
 def test_frame_v13_asset_binds_hash(self):
  p=MEDIA/'VACINA01/DIRECAO_DOCUMENTAL_V1_3/R05_QUADRO_CHAVE_CANDIDATO_01.png'
  if p.is_file():self.assertTrue(approval(LEDGER,'R05_FRAME_V1_3','QUADRO_CHAVE',p)['ok'])
 def test_v17_not_inherited_approval(self):
  p=MEDIA/'VACINA01/TESTE_MOTION_V1_7/R05_MAVIE_MICROTESTE_MOTION_V1_7.mp4'
  self.assertFalse(approval(LEDGER,'R05_MOTION_V1_7','BASE_MOTION',p)['ok'])
 def test_wrong_hash_detected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.png';p.write_bytes(b'bad')
   self.assertEqual(verify_sha(p,LEDGER['versoes'][3]['sha256'])['estado'],'DIVERGENTE')
 def test_brand_reference_sha_verified(self):
  ref=MEDIA/LEDGER['referencia_marca']['caminho_relativo_media']
  if not ref.is_file():
   self.skipTest('referência canônica deve ser montada externamente no CI')
  r=run('DIRECAO_VISUAL',MEDIA,assets_root=MEDIA)
  self.assertNotIn('MARCA:', ' '.join(r['bloqueios']))
  self.assertEqual(r['evidencias']['ART-05']['prova_referencia_marca']['estado'],'CONFERIDO')
 def test_missing_brand_blocks_visual(self):
  with tempfile.TemporaryDirectory() as t:
   r=run('DIRECAO_VISUAL',MEDIA,assets_root=Path(t))
   self.assertTrue(any('MARCA:' in x for x in r['bloqueios']))
 def test_no_approval_if_media_missing(self):
  with tempfile.TemporaryDirectory() as t:
   s=run('TESTE_CURTO',None,assets_root=Path(t))
   self.assertEqual(s['estado'],'BLOQUEADO')
   self.assertTrue(any('quadro V1.3' in e for e in s['bloqueios']))
 def test_full_edit_blocked_even_with_approved_base(self):
  r=run('EDICAO_COMPLETA',MEDIA,assets_root=MEDIA)
  self.assertEqual(r['estado'],'BLOQUEADO')
  self.assertTrue(any('ESCOPO:' in x for x in r['bloqueios']))
 def test_publish_blocked_without_clinical_and_final(self):
  r=run('PUBLICACAO',MEDIA,assets_root=MEDIA)
  self.assertEqual(r['estado'],'BLOQUEADO')
  self.assertTrue(any('CLÍNICO:' in x for x in r['bloqueios']))
  self.assertTrue(any('PUBLICAÇÃO:' in x for x in r['bloqueios']))
 def test_diagnosis_working_and_no_llm_claim(self):
  r=run('DIAGNOSTICO',MEDIA,assets_root=MEDIA)
  self.assertEqual(r['subagentes_llm_realmente_executados'],[])
  self.assertFalse(r['publicou'])
  self.assertFalse(r['gastou'])
  self.assertIn('MEDIA-11',r['agentes_deterministicos_executados'])
  self.assertIn('não realizados',report_md(r))
 def test_finance_avoids_art_audio(self):
  r=run('DIAGNOSTICO',MEDIA,subject='financas')
  self.assertIn('FIN-08',r['agentes_planejados'])
  self.assertNotIn('ART-05',r['agentes_planejados'])
  self.assertIsNone(r['evidencias']['FIN-08']['margem_por_atendimento'])
 def test_unknown_stage_rejected(self):
  with self.assertRaises(ValueError):run('PUBLICAR_SILENCIOSAMENTE',MEDIA)
 def test_boolean_cannot_approve_master(self):
  with tempfile.TemporaryDirectory() as t:
   d=copy.deepcopy(LEDGER)
   d['restricoes']['autorizou_edicao_master_neste_pedido']=True
   p=Path(t)/'state.json';p.write_text(json.dumps(d),encoding='utf8')
   r=run('EDICAO_COMPLETA',MEDIA,assets_root=MEDIA,state_path=p)
   self.assertTrue(any('ESCOPO:' in e for e in r['bloqueios']))
 def test_boolean_cannot_approve_clinical_or_publish(self):
  with tempfile.TemporaryDirectory() as t:
   d=copy.deepcopy(LEDGER)
   for k in ['validacao_clinica_larissa','crmv_confirmado_larissa','licenca_musica_comprovada',
             'logo_e_fontes_definitivas_confirmados','aprovacao_final_publicacao','autoriza_publicar']:
    d['restricoes'][k]=True
   p=Path(t)/'state.json';p.write_text(json.dumps(d),encoding='utf8')
   r=run('PUBLICACAO',MEDIA,assets_root=MEDIA,state_path=p)
   self.assertTrue(any('CLÍNICO: campo booleano' in e for e in r['bloqueios']))
   self.assertTrue(any('PUBLICAÇÃO:' in e for e in r['bloqueios']))
 def test_proof_requires_exact_scope_and_version(self):
  approval={'aprovado':True,'acao':'EDICAO_COMPLETA','responsavel':'Borelli',
            'versao':'R05_MAVIE','evidencia':'Aprovo o job R05 master em mensagem rastreável'}
  self.assertTrue(signed_authorization(approval,action='EDICAO_COMPLETA',approver='Borelli',version='R05_MAVIE'))
  self.assertFalse(signed_authorization(approval,action='PUBLICACAO',approver='Borelli',version='R05_MAVIE'))
 def test_no_sensitive_media_embedded(self):
  r=run('DIAGNOSTICO',MEDIA,assets_root=MEDIA)
  x=json.dumps(r)
  self.assertNotIn('image/jpeg;base64',x)
  self.assertNotIn('data:audio/',x)
 def test_inputs_deterministic(self):
  r1=run('DIAGNOSTICO',MEDIA,assets_root=MEDIA)
  r2=run('DIAGNOSTICO',MEDIA,assets_root=MEDIA)
  self.assertEqual(r1['execucao_id'],r2['execucao_id'])
 def test_original_file_tampering_blocks_production(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t)
   for f in ['204443.jpg','204439.jpg','204446.mp4']:(d/f).write_bytes(b'corrupt')
   r=run('TESTE_CURTO',d,assets_root=MEDIA)
   self.assertEqual(r['estado'],'BLOQUEADO')
   self.assertTrue(any('MEDIA:' in x for x in r['bloqueios']))

if __name__=='__main__':unittest.main()
