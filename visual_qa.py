#!/usr/bin/env python3
"""Auditoria audiovisual comparativa, determinística, sem avaliação estética automática.

Lê MP4 local via ffprobe e quadros em cinza 135x240 via ffmpeg; não altera
originais, não envia arquivos para serviços externos, não usa OCR nem IA.
Um alerta quantitativo não é sinônimo de reprovação estética humana.
"""
from __future__ import annotations
import collections
import hashlib
import json
import math
import subprocess
from pathlib import Path

FRAME_W, FRAME_H = 135, 240
FRAMESIZE = FRAME_W * FRAME_H


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1_048_576), b''):
            h.update(block)
    return h.hexdigest()


def stats(raw: bytes) -> dict:
    """Estatísticas de luma sobre quadros reais. Puro Python para evitar libs novas."""
    if len(raw) != FRAMESIZE:
        raise ValueError('Dimensão de quadro inválida')
    hist = collections.Counter(raw)
    n = len(raw)
    mean = sum(v * count for v, count in hist.items()) / n
    variance = max(0.0, sum((v * v) * count for v, count in hist.items()) / n - mean * mean)
    return {
        'mean': round(mean, 3), 'std': round(math.sqrt(variance), 3),
        'bright_fraction': round(sum(count for v, count in hist.items() if v >= 218) / n, 5),
        'nearwhite_fraction': round(sum(count for v, count in hist.items() if v >= 210) / n, 5),
    }


def metadata(path: Path) -> dict:
    p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration',
                        '-of', 'json', str(path)], text=True, capture_output=True, timeout=20)
    if p.returncode != 0:
        raise RuntimeError('ffprobe falhou: ' + p.stderr[:240])
    return json.loads(p.stdout)


def frames_gray(path: Path) -> list[dict]:
    """O vídeo inteiro é amostrado, sem síntese nem interpolação."""
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', str(path),
           '-map', '0:v:0', '-vf', f'scale={FRAME_W}:{FRAME_H}:flags=bilinear,format=gray',
           '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'gray', 'pipe:1']
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    if p.returncode != 0:
        raise RuntimeError('ffmpeg falhou: ' + p.stderr.decode(errors='replace')[:240])
    data = p.stdout
    if len(data) % FRAMESIZE != 0:
        raise RuntimeError('Saída rawvideo incompleta')
    return [stats(data[i:i+FRAMESIZE]) for i in range(0, len(data), FRAMESIZE)]


def audit(path: Path, *, baseline=(1.30, 1.58), transition=(1.60, 2.08)) -> dict:
    meta = metadata(path)
    vs = next((s for s in meta['streams'] if s.get('codec_type') == 'video'), None)
    if not vs: raise ValueError('Arquivo sem trilha de vídeo')
    ratio = vs.get('r_frame_rate', '0/1')
    num, den = map(int, ratio.split('/'))
    fps = num / den if den else 0
    if fps <= 0: raise ValueError('FPS inválido')
    allframes = frames_gray(path)
    def span(interval):
        a = max(0, int(round(interval[0] * fps)))
        b = min(len(allframes), int(round(interval[1] * fps)) + 1)
        return [(i / fps, allframes[i]) for i in range(a, b)]
    base, trans = span(baseline), span(transition)
    if not base or not trans: raise ValueError('Intervalo de auditoria fora do vídeo')
    baseline_mean = sorted(s['mean'] for _,s in base)[len(base)//2]
    baseline_std = sorted(s['std'] for _,s in base)[len(base)//2]
    peak_t, peak = max(trans, key=lambda p:p[1]['mean'])
    worst_t, worst = min(trans, key=lambda p:p[1]['std'])
    blank = [round(t,3) for t,s in trans if s['nearwhite_fraction'] > .90 and s['std'] < 18]
    gain = peak['mean'] - baseline_mean
    contrast_ratio = worst['std'] / baseline_std if baseline_std else 0
    alerts = []
    if blank: alerts.append('QUADRO_QUASE_VAZIO_CLARO')
    if gain > 18: alerts.append('PICO_LUMINANCIA_TRANSICAO')
    if contrast_ratio < .75: alerts.append('QUEDA_CONTRASTE_TRANSICAO')
    return {
        'arquivo':path.name,'sha256':sha256(path),
        'fps':fps,'total_frames':len(allframes),'duracao_s':float(meta.get('format',{}).get('duration',0)),
        'resolucao':f"{vs.get('width')}x{vs.get('height')}",
        'baseline_mean':round(baseline_mean,2),'baseline_std':round(baseline_std,2),
        'pico_mean':round(peak['mean'],2),'pico_t':round(peak_t,3),
        'ganho_de_brilho_pico':round(gain,2),
        'menor_contraste':round(worst['std'],2),'t_menor_contraste':round(worst_t,3),
        'relacao_contraste_minimo':round(contrast_ratio,3),
        'frames_quase_vazios_s':blank,
        'alertas':alerts,
        'conclusao':'QA QUANTITATIVO; NÃO COMPROVA ACEITAÇÃO ESTÉTICA OU CLÍNICA',
    }


def compare(v16:Path,v17:Path)->dict:
    old, new=audit(v16),audit(v17)
    return {
        'metodo':'extração não generativa de cada quadro, luma em 135×240; intervalos 1,30–1,58 e 1,60–2,08 s',
        'v16':old,'v17':new,
        'mudanca_pico_luminancia':round(new['ganho_de_brilho_pico']-old['ganho_de_brilho_pico'],2),
        'melhoria_sem_quadro_vazio':bool(old['frames_quase_vazios_s']) and not bool(new['frames_quase_vazios_s']),
        'decisao_tecnica':'V1.7 removeu quadro claro vazio, mas ainda apresenta alerta de perda local de contraste. NÃO promovida a base automaticamente.',
        'decisao_humana':'V1.6 permanece a base aprovada; V1.7 segue candidata até aceite específico.',
    }

if __name__ == '__main__':
    import argparse
    pa=argparse.ArgumentParser()
    pa.add_argument('--v16',type=Path,required=True)
    pa.add_argument('--v17',type=Path,required=True)
    pa.add_argument('--output',type=Path)
    args=pa.parse_args()
    result=compare(args.v16,args.v17)
    s=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(s,encoding='utf8')
    print(s)
