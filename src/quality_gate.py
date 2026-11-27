"""Strict v1.1 proof-aware preflight. It does NOT replace human visual/vet review.

The purpose is to reject status-by-boolean, not to certify artistic quality.
"""
from urllib.parse import urlsplit

PRODUCTION = {'EDICAO', 'QA', 'APROVACAO', 'PUBLICAVEL', 'PUBLICADO'}
DESIGN = {'TESTE_CURTO', *PRODUCTION}


def _source_url(url):
    if not isinstance(url, str):
        return False
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and bool(p.hostname) and p.hostname.lower() in {
            'www.instagram.com', 'instagram.com', 'www.youtube.com', 'youtube.com',
            'youtu.be', 'www.tiktok.com', 'tiktok.com'
        }
    except ValueError:
        return False


def _evidence_approval(approval, stage):
    """Human approval attestation must name version, approver, evidence and time."""
    if not isinstance(approval, dict):
        return False
    expected = 'Larissa' if stage == 'CLINICA' else 'Borelli'
    fingerprint = approval.get('arquivo_sha256')
    verified_format = isinstance(fingerprint, str) and len(fingerprint)==64 and all(c in '0123456789abcdefABCDEF' for c in fingerprint)
    return bool(approval.get('aprovado') is True
                and approval.get('responsavel') == expected
                and verified_format
                and isinstance(approval.get('referencia_aprovacao'),str) and len(approval['referencia_aprovacao'].strip())>=10
                and isinstance(approval.get('versao'), str) and approval['versao'].strip()
                and isinstance(approval.get('evidencia'), str) and len(approval['evidencia'].strip()) > 12
                and isinstance(approval.get('data'), str) and len(approval['data']) >= 10
                and approval.get('fase') == stage)


def check_strict(job, stage):
    """Provenance gates only. Never validates aesthetic/medical quality."""
    problems = []
    formato = job.get('formato', 'CREATOR_LARISSA')
    if formato not in {'CREATOR_LARISSA', 'DOCUMENTAL_ACERVO'}:
        problems.append('ORQ: formato desconhecido, proibido assumir modalidade com menos requisitos')
        return problems
    if formato == 'DOCUMENTAL_ACERVO':
        # A separately-scoped documentary mode avoids requiring fabricated on-camera
        # footage. It is not a loophole for calling the result an influencer film.
        sha = job.get('referencia_canonica_sha256')
        expected = 'a5bfe4181e31e9bee3871ca3c11c8515e2dbbceeb4e3c422e25345fe529b4aaa'
        hashes = job.get('originais_sha256', {})
        refs_ok = all(hashes.get(k) == v for k,v in {
           '204443.jpg':'7d488a2cbfa0539e4daf9e0b0906b416dd26140b51e98a0665d6e7c669fcce5e',
           '204439.jpg':'87cd7b651fe04cb70840ac886ff826e345db5031cf5f729e2e0fe55c2e9bae99',
           '204446.mp4':'29f3794247fc65141d147e8f10171ed8f298d6d0ed6935b7f44c50750f422d48'
        }.items())
        if stage in {'DIRECAO_VISUAL', *DESIGN} and (sha != expected or not refs_ok or not job.get('limite_material_real_reconhecido')):
            problems.append('DOCUMENTAL: referência/manifesto de originais ou limitação do material sem prova')
        if stage in {'TESTE_CURTO', *PRODUCTION} and not _evidence_approval(job.get('aprovacao_quadro_chave'), 'QUADRO_CHAVE'):
            problems.append('ART/QA: falta aprovação humana rastreável do quadro-chave documental')
        if stage in PRODUCTION and not _evidence_approval(job.get('aprovacao_amostra'), 'TESTE_CURTO'):
            problems.append('EDIT/QA: falta aprovação humana rastreável do teste curto documental')
        # Documentary scope must remain explicitly non-creator and non-procedural.
        if stage in PRODUCTION and (job.get('simula_procedimento') or job.get('declara_larissa_em_video') or job.get('promete_sem_estresse')):
            problems.append('DOCUMENTAL: narrativa incompatível com os arquivos existentes')
    else:
        refs = job.get('benchmarks_audiovisuais', [])
        if stage in DESIGN:
            watched = [r for r in refs if isinstance(r,dict) and r.get('tipo_evidencia')=='VIDEO_ASSISTIDO'
                       and _source_url(r.get('url'))
                       and len(r.get('observacoes_por_timestamp', []))>=2
                       and isinstance(r.get('responsavel_revisao'),str) and r['responsavel_revisao'].strip()]
            unique = {r.get('criador','').strip().lower() for r in watched if isinstance(r.get('criador'),str) and r['criador'].strip()}
            if len(unique)<3:
                problems.append('SCOUT: faltam 3 Reels realmente assistidos, independentes e com notas por tempo')
            if not _evidence_approval(job.get('aprovacao_quadro_chave'), 'QUADRO_CHAVE'):
                problems.append('ART/QA: falta aprovação humana rastreável do quadro-chave')
        if stage in PRODUCTION:
            media=job.get('media_captada', [])
            video_larissa=[x for x in media if isinstance(x,dict)
                           and x.get('profissional_real_em_cena') is True
                           and x.get('tipo')=='video_real'
                           and isinstance(x.get('sha256'), str) and len(x['sha256'])==64
                           and isinstance(x.get('descricao'),str) and len(x['descricao'].strip())>=20]
            if len(video_larissa)<1:
                problems.append('EDIT: falta mídia real verificável da Larissa em câmera para linguagem creator')
            if not _evidence_approval(job.get('aprovacao_amostra'), 'TESTE_CURTO'):
                problems.append('EDIT/QA: falta aprovação humana rastreável do teste curto')
    if stage in {'PUBLICAVEL','PUBLICADO'}:
        if not _evidence_approval(job.get('aprovacao_clinica'), 'CLINICA'):
            problems.append('VET: falta validação clínica rastreável pela Larissa')
        if not _evidence_approval(job.get('aprovacao_final'), 'PUBLICACAO_FINAL'):
            problems.append('ORQ: falta aprovação humana final rastreável')
        if not job.get('licenca_trilha_prova'):
            problems.append('AUDIO: falta comprovante da licença da trilha')
    return problems
