#!/usr/bin/env python3
"""VACINA 01 / V1.3 — execução local determinística e audível.

Não invoca LLM, não navega, não gera vídeo, não publica e não gasta créditos.
Os perfis .agent.md são contratos para futuro runtime; estes workers executam tarefas
mensuráveis agora e registram seus próprios limites.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orq import check

EXPECTED = {
    '204443.jpg': ('foto_abertura', '7d488a2cbfa0539e4daf9e0b0906b416dd26140b51e98a0665d6e7c669fcce5e'),
    '204439.jpg': ('foto_momento_distinto', '87cd7b651fe04cb70840ac886ff826e345db5031cf5f729e2e0fe55c2e9bae99'),
    '204446.mp4': ('video_documental', '29f3794247fc65141d147e8f10171ed8f298d6d0ed6935b7f44c50750f422d48'),
}
DERIVATIVE = '205899_VOZ_LARISSA.mp3'


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fin:
        for chunk in iter(lambda: fin.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def media_details(path: Path) -> dict:
    """ffprobe: metadados técnicos, nunca auditoria visual nem clínica."""
    try:
        run = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries',
         'format=duration,size,format_name:stream=codec_name,codec_type,width,height,avg_frame_rate,sample_rate,channels',
         '-of', 'json', str(path)],
        capture_output=True, text=True, timeout=12, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'erro': f'ffprobe indisponível ou excedeu prazo: {type(exc).__name__}'}
    if run.returncode:
        return {'ok': False, 'erro': run.stderr.strip()[:240]}
    try:
        out = json.loads(run.stdout)
    except json.JSONDecodeError:
        return {'ok': False, 'erro': 'ffprobe não retornou JSON válido'}
    return {'ok': True, 'format': out.get('format', {}), 'streams': out.get('streams', [])}


def media_worker(media_root: Path | None) -> dict:
    if media_root is None:
        return {'agente': 'MEDIA-11', 'estado': 'SEM_ARQUIVOS_LOCAL', 'observacao': 'Inventário não executado: sem caminho local; sem suposição sobre anexos'}
    paths = {k: media_root / k for k in EXPECTED}
    paths[DERIVATIVE] = media_root / 'VACINA01' / DERIVATIVE
    rows = []
    for name, path in paths.items():
        role, expected = EXPECTED.get(name, ('voz_derivada_nao_master', None))
        if not path.is_file():
            rows.append({'arquivo': name, 'papel': role, 'estado': 'AUSENTE', 'hash_esperado': expected})
            continue
        actual = checksum(path)
        sha_ok = None if expected is None else actual == expected
        rows.append({'arquivo': name, 'papel': role, 'estado': ('IDENTICO_ORIGINAL' if sha_ok else 'DERIVADO_COM_HASH_REGISTRADO' if sha_ok is None else 'DIVERGENTE_BLOQUEIO'),
                     'sha256': actual, 'hash_esperado': expected, 'bytes': path.stat().st_size,
                     'metadados': media_details(path)})
    ok = sum(x['estado'] == 'IDENTICO_ORIGINAL' for x in rows)
    return {'agente': 'MEDIA-11', 'estado': 'AUDITORIA_TECNICA_CONCLUIDA' if ok == 3 else 'PARCIAL_BLOQUEADO',
            'originais_conferidos': ok, 'originais_esperados': 3,
            'limite': 'Conferir hash e codec não prova que a filmagem é esteticamente utilizável nem que mostra vacinação', 'itens': rows}


def memory_worker() -> dict:
    """Prioriza registro canônico V2, sem reintroduzir decisões antigas como atuais."""
    current = ROOT / 'config' / 'decisao_atual.json'
    if current.exists():
        src = json.loads(current.read_text(encoding='utf8'))
        versions = src.get('versoes', [])
        return {'agente': 'MEM-01', 'estado': 'LIDO_REGISTRO_CANONICO_V2',
                'aprovacoes': [v for v in versions if v.get('estado','').startswith('APROVADA')],
                'reprovados': [v for v in versions if v.get('estado') == 'REPROVADA'],
                'pendencias': [v for v in versions if 'CANDIDATA' in v.get('estado','')],
                'limite': 'Registro de evidência humano; Sheets e chat devem ser conciliados explicitamente'}
    src = json.loads((ROOT / 'config' / 'decisoes.json').read_text(encoding='utf8'))
    return {'agente': 'MEM-01', 'estado': 'LIDO_REGISTRO_LEGADO', 'aprovacoes': src['approved'],
            'reprovados': src['rejected'], 'pendencias': src['pending'],
            'limite': 'O registro legado pode estar desatualizado; preferir decisao_atual.json'}


def scout_worker() -> dict:
    src = json.loads((ROOT / 'research' / 'SCOUT_2026-11-25.json').read_text(encoding='utf8'))
    refs = src.get('references', [])
    watched = [x for x in refs if x.get('video_watched') is True]
    return {'agente': 'SCOUT-02', 'estado': 'FONTES_CLASSIFICADAS', 'fontes': len(refs),
            'reels_assistidos_comprova_duracao': len(watched),
            'referencias': [{'criador': x.get('creator'), 'url': x.get('profile_url'),
                             'evidencia': x.get('content_verified'), 'video_assistido': x.get('video_watched')} for x in refs],
            'limite': 'A pesquisa por texto não comprova ritmo, tipografia, edição ou eficácia; 0 benchmark visual validado'}


def finance_worker() -> dict:
    with (ROOT / 'financeiro' / 'custos_vacinas.csv').open(encoding='utf-8-sig', newline='') as f:
        entries = list(csv.DictReader(f))
    known, missing = {}, []
    for row in entries:
        label = row['vacina']
        raw = row['custo_aquisicao_por_dose_R$']
        if raw:
            known[label] = float(raw.replace(',', '.'))
        else:
            missing.append(label)
    return {'agente': 'FIN-08', 'estado': 'CUSTOS_AQUISICAO_VERIFICADOS',
            'custo_por_dose_nao_preco': known, 'vacina_sem_custo': missing,
            'margem_por_atendimento': None, 'pendencia': 'preço e custos completos de operação não conhecidos'}


def creative_worker(job: dict) -> dict:
    brand = json.loads((ROOT / 'config' / 'brand_lock.json').read_text(encoding='utf8'))
    return {'agente': 'ART-05', 'estado': ('QUADRO_CHAVE_EM_PREPARACAO' if job.get('formato')=='DOCUMENTAL_ACERVO' else 'TRAVADO_POR_BENCHMARK_E_APROVACAO'),
            'marca': brand['marca'], 'identidade': brand['direcao'],
            'fontes_aprovadas': brand['fontes_definitivas'] is not None,
            'paleta_aprovada_em_hex': brand['hex_definitivos'] is not None,
            'frame_chave_aprovado': bool(job.get('aprovacao_quadro_chave')),
            'regras_de_design': brand['visual_proibido'],
            'proximo_objeto': 'um quadro-chave que use mídia real e referência aprovada, não um Reel inteiro'}


def clinical_worker(job: dict) -> dict:
    return {'agente': 'VET-07', 'estado': 'REVISÃO_HUMANA_PENDENTE',
            'fatos_pendentes': ['primeira dose V10', 'início do protocolo', 'condição da paciente após atendimento', 'registro CRMV oficial'],
            'revisao_larissa_registrada': bool(job.get('aprovacao_clinica')), 'proibido': 'autoaprovação clínica por software'}


def qa_worker(job: dict, stage: str, items: dict) -> dict:
    failures = check(job, stage)
    if items.get('MEDIA-11', {}).get('estado') == 'PARCIAL_BLOQUEADO':
        failures.append('MEDIA: algum original ausente ou não corresponde ao hash canônico')
    return {'agente': 'QA-09', 'etapa_testada': stage, 'estado': 'BLOQUEADO' if failures else 'GATE_ESTRUTURAL_VALIDO',
            'motivos': failures,
            'limite': 'Um gate estrutural válido não é aprovação estética, clínica, comercial ou publicação'}


def execute(job: dict, stage: str, media_root: Path | None = None) -> dict:
    if stage not in {'DISCOVERY', 'BRIEFING', 'DIRECAO_VISUAL', 'TESTE_CURTO', 'EDICAO', 'QA', 'PUBLICAVEL', 'PUBLICADO'}:
        raise ValueError(f'etapa inválida: {stage}')
    if not job.get('id'):
        raise ValueError('job sem id')
    core = json.loads((ROOT / 'config' / 'agentes.json').read_text(encoding='utf8'))
    planned = core['despacho']['reel']
    # Estes agentes são workers de verificação locais; não invocação de modelos generativos.
    delivered = {
        'MEM-01': memory_worker(),
        'SCOUT-02': scout_worker(),
        'FIN-08': finance_worker(),
        'ART-05': creative_worker(job),
        'VET-07': clinical_worker(job),
        'MEDIA-11': media_worker(media_root),
    }
    delivered['QA-09'] = qa_worker(job, stage, delivered)
    return {'projeto': 'VACINA01', 'motor': '1.3', 'job': job['id'], 'etapa': stage,
            'modo': 'WORKERS_DETERMINISTICOS_LOCAIS_SEM_LLM',
            'subagentes_ativos': sorted(delivered), 'perfis_llm_registrados_nao_executados': planned,
            'resultados': delivered, 'resultado': delivered['QA-09']['estado'],
            'consumo_creditos': 0, 'publicou': False, 'renderizou': False,
            'pendencia_mais_urgente': ('aprovar quadro-chave do microdocumental com acervo real' if job.get('formato')=='DOCUMENTAL_ACERVO' else 'captação real Larissa em vídeo + referência audiovisual realmente assistida para construir quadro-chave')}


def main():
    p = argparse.ArgumentParser(description='VACINA01 - prova de execução local dos agentes não-LLM')
    p.add_argument('command', choices=['run'])
    p.add_argument('--job', default=str(ROOT / 'jobs' / 'R05_MAVIE_REBOOT.json'))
    p.add_argument('--stage', default='EDICAO')
    p.add_argument('--media-root', type=Path, default=None)
    p.add_argument('--out', type=Path, default=ROOT / 'outputs' / 'R05_VALIDACAO_V1_2.json')
    a = p.parse_args()
    job = json.loads(Path(a.job).read_text(encoding='utf8'))
    result = execute(job, a.stage, a.media_root)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({'resultado': result['resultado'], 'arquivo': str(a.out), 'agentes_executados': result['subagentes_ativos'], 'motivos': result['resultados']['QA-09']['motivos']}, ensure_ascii=False, indent=2))
    return 0 if result['resultado'] != 'BLOQUEADO' else 1

if __name__ == '__main__':
    raise SystemExit(main())
