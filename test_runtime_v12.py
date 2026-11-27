import copy
import json
import tempfile
import unittest
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from dispatch import EXPECTED, checksum, media_details, media_worker, finance_worker, scout_worker, execute
JOB = json.loads((ROOT / 'jobs' / 'R05_MAVIE_REBOOT.json').read_text(encoding='utf8'))

class RuntimeTests(unittest.TestCase):
    def test_original_hashes_declared(self):
        self.assertEqual(len(EXPECTED), 3)
        self.assertEqual(len({x[1] for x in EXPECTED.values()}), 3)
    def test_missing_media_is_not_assumed(self):
        x = media_worker(None)
        self.assertEqual(x['estado'], 'SEM_ARQUIVOS_LOCAL')
    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '204443.jpg'
            p.write_bytes(b'alterado')
            x = media_worker(Path(d))
            self.assertEqual(x['estado'], 'PARCIAL_BLOQUEADO')
            self.assertEqual(x['itens'][0]['estado'], 'DIVERGENTE_BLOQUEIO')
    def test_probe_absence_is_nonfatal(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'a.mp4'; p.write_bytes(b'video')
            with patch('subprocess.run', side_effect=FileNotFoundError('ffprobe')):
                r = media_details(p)
            self.assertFalse(r['ok'])
            self.assertIn('indisponível', r['erro'])
    def test_zero_claims_watched(self):
        x = scout_worker()
        self.assertEqual(x['reels_assistidos_comprova_duracao'], 0)
    def test_finance_not_price(self):
        x = finance_worker()
        self.assertEqual(x['custo_por_dose_nao_preco']['V10'], 55)
        self.assertIsNone(x['margem_por_atendimento'])
    def test_dispatch_uses_real_workers(self):
        x = execute(copy.deepcopy(JOB), 'DISCOVERY')
        self.assertIn('MEM-01', x['subagentes_ativos'])
        self.assertIn('MEDIA-11', x['subagentes_ativos'])
        self.assertEqual(x['modo'], 'WORKERS_DETERMINISTICOS_LOCAIS_SEM_LLM')
    def test_edit_remains_blocked(self):
        x = execute(copy.deepcopy(JOB), 'EDICAO')
        self.assertEqual(x['resultado'], 'BLOQUEADO')
    def test_publication_remains_blocked(self):
        x = execute(copy.deepcopy(JOB), 'PUBLICADO')
        self.assertEqual(x['resultado'], 'BLOQUEADO')
        self.assertFalse(x['publicou'])
    def test_fake_stage_rejected(self):
        with self.assertRaises(ValueError):
            execute(copy.deepcopy(JOB), 'PUBLISH_SILENTLY')
    def test_no_secret_or_media_content_in_serialized_result(self):
        x = execute(copy.deepcopy(JOB), 'DISCOVERY')
        self.assertNotIn('private_key', json.dumps(x))
        self.assertNotIn('base64', json.dumps(x))

if __name__ == '__main__':
    unittest.main()
