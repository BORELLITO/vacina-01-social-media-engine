import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from orq import check
DOC=json.loads((ROOT/'jobs'/'R05_MAVIE_DOCUMENTAL_ACERVO.json').read_text())
CREATOR=json.loads((ROOT/'jobs'/'R05_MAVIE_REBOOT.json').read_text())
class DocumentaryMode(unittest.TestCase):
 def test_visual_prototype_allowed_with_real_archive(self):
  self.assertEqual(check(copy.deepcopy(DOC),'DIRECAO_VISUAL'),[])
 def test_prototype_video_requires_frame_approval(self):
  self.assertTrue(any('quadro-chave' in x for x in check(copy.deepcopy(DOC),'TESTE_CURTO')))
 def test_full_edit_requires_short_test(self):
  self.assertTrue(any('teste' in x.lower() for x in check(copy.deepcopy(DOC),'EDICAO')))
 def test_no_fake_larissa(self):
  j=copy.deepcopy(DOC);j['declara_larissa_em_video']=True
  self.assertTrue(any('incompatível' in x for x in check(j,'EDICAO')))
 def test_unverified_assets_block_visual(self):
  j=copy.deepcopy(DOC);j['originais_sha256']['204443.jpg']='0'*64
  self.assertTrue(any('originais' in x for x in check(j,'DIRECAO_VISUAL')))
 def test_canonical_design_lock_required(self):
  j=copy.deepcopy(DOC);j['referencia_canonica_sha256']='f'*64
  self.assertTrue(any('referência' in x for x in check(j,'DIRECAO_VISUAL')))
 def test_creator_remains_blocked(self):
  self.assertTrue(any('SCOUT' in x for x in check(copy.deepcopy(CREATOR),'TESTE_CURTO')))
 def test_no_automatic_publish(self):
  self.assertTrue(any('VET:' in x for x in check(copy.deepcopy(DOC),'PUBLICAVEL')))
 def test_unknown_format_is_blocked(self):
  j=copy.deepcopy(DOC);j['formato']='DOC_FAKE'
  self.assertTrue(any('desconhecido' in x for x in check(j,'DIRECAO_VISUAL')))
if __name__=='__main__':unittest.main()
