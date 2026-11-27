#!/usr/bin/env python3
"""VACINA01: gatekeeper deterministico local. Nao chama LLM, sites nem editor."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VALID_STATES={'DISCOVERY','BRIEFING','DIRECAO_VISUAL','TESTE_CURTO','EDICAO','QA','APROVACAO','PUBLICAVEL','PUBLICADO','REPROVADO','BLOQUEADO'}

def check(job, target):
 problems=[]
 if job.get('estado') not in VALID_STATES:problems.append('estado invalido')
 if target in {'TESTE_CURTO','EDICAO','QA','APROVACAO','PUBLICAVEL','PUBLICADO'}:
  if not job.get('frames_visuais_auditados'):problems.append('falta frame visual comparado à referencia')
 if target in {'EDICAO','QA','APROVACAO','PUBLICAVEL','PUBLICADO'}:
  if not job.get('amostra_curtissima_aprovada'):problems.append('teste de 3-5s sem aprovacao visual')
 if target in {'PUBLICAVEL','PUBLICADO'}:
  for key,label in [('consentimento_uso_imagem','consentimento de imagem'),('validacao_clinica_larissa','validacao clinica Larissa'),('aprovacao_estetica_final','aprovacao estetica final'),('licenca_trilha','licenca da trilha'),('fontes_e_marca_verificados','marca/fontes comprovados')]:
   if not job.get(key):problems.append('falta '+label)
 if target=='PUBLICADO' and not job.get('autorizacao_publicar'):problems.append('falta autorizacao de publicacao')
 if job.get('qualidade_v11') is True:
  from quality_gate import check_strict
  problems.extend(check_strict(job,target))
 return problems

def main(argv):
 if len(argv)<3 or argv[1]!='validate':
  print('Uso: python src/orq.py validate jobs/R05_MAVIE_REBOOT.json [ETAPA]');return 2
 job=json.loads(Path(argv[2]).read_text(encoding='utf8'))
 target=argv[3] if len(argv)>3 else job['estado']
 errors=check(job,target)
 print(json.dumps({'job':job['id'],'etapa':target,'status':'BLOQUEADO' if errors else 'VALIDO','motivos':errors},ensure_ascii=False,indent=2))
 return 1 if errors else 0
if __name__=='__main__':sys.exit(main(sys.argv))
