#!/usr/bin/env python3
"""ORQ-00 v2: orquestração local verificável; NÃO é executor de subagentes LLM.

Sem chamadas de rede, sem edição de vídeo, sem gastos e sem publicação.
Fluxo: confirmar evidência -> despachar workers determinísticos -> gate por escopo -> relatório.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from dispatch import EXPECTED, checksum, media_worker, scout_worker, finance_worker
from visual_qa import compare

STAGES = {"DIAGNOSTICO", "DIRECAO_VISUAL", "TESTE_CURTO", "EDICAO_COMPLETA", "PRE_PUBLICACAO", "PUBLICACAO", "AUDITORIA_VISUAL"}
# Cada etapa usa apenas os workers necessários. Nunca alegar que um perfil LLM foi executado.
AGENTS = {
    "DIAGNOSTICO": ["MEM-01", "SCOUT-02", "MEDIA-11", "QA-09"],
    "AUDITORIA_VISUAL": ["MEM-01", "ART-05", "EDIT-06", "VISUAL-QA", "QA-09"],
    "DIRECAO_VISUAL": ["MEM-01", "SCOUT-02", "ART-05", "MEDIA-11", "QA-09"],
    "TESTE_CURTO": ["MEM-01", "ART-05", "EDIT-06", "MEDIA-11", "QA-09"],
    "EDICAO_COMPLETA": ["MEM-01", "SCRIPT-04", "ART-05", "EDIT-06", "MEDIA-11", "QA-09"],
    "PRE_PUBLICACAO": ["MEM-01", "VET-07", "ART-05", "FIN-08", "QA-09"],
    "PUBLICACAO": ["MEM-01", "VET-07", "QA-09"],
}
# Stage -> trabalho externo pretendido. O CLI audita; não despacha editores ou serviços.
SENSITIVE = {"TESTE_CURTO", "EDICAO_COMPLETA", "PRE_PUBLICACAO", "PUBLICACAO"}


def signed_authorization(record: Any, *, action: str, approver: str, version: str, artifact_sha: str | None = None) -> bool:
    """Prova de autorização por versão/ação. NÃO verifica identidade criptográfica; apenas exige proveniência explícita."""
    if not isinstance(record, dict) or record.get("aprovado") is not True:
        return False
    if (record.get("acao") != action or record.get("responsavel") != approver
            or record.get("versao") != version):
        return False
    evidence = record.get("evidencia")
    if not isinstance(evidence, str) or len(evidence.strip()) < 20:
        return False
    if artifact_sha is not None and record.get("arquivo_sha256") != artifact_sha:
        return False
    if artifact_sha is not None and (len(artifact_sha) != 64 or
                                    any(c not in "0123456789abcdef" for c in artifact_sha.lower())):
        return False
    return True


def verify_sha(path: Path, expected: str) -> dict[str, Any]:
    if not path.is_file():
        return {"estado": "AUSENTE", "local": str(path)}
    actual = checksum(path)
    return {"estado": "CONFERIDO" if actual == expected else "DIVERGENTE", "sha256": actual,
            "tamanho_bytes": path.stat().st_size, "local": str(path)}


def approval(ledger: dict, version: str, scope: str, asset: Path) -> dict:
    found = next((x for x in ledger.get("versoes", []) if x.get("versao") == version), None)
    if not found:
        return {"ok": False, "motivo": "versão não consta no registro"}
    if found.get("escopo") != scope:
        return {"ok": False, "motivo": "aprovação de escopo diferente", "estado": found.get("estado")}
    if not isinstance(found.get("evidencia"), str) or not found.get("aprovador"):
        return {"ok": False, "motivo": "sem evidência nominal da aprovação"}
    proof = verify_sha(asset, found.get("sha256", ""))
    return {"ok": proof["estado"] == "CONFERIDO", "versao": version, "escopo": scope,
            "prova": proof, "fonte_aceite": found["evidencia"]}


def run(stage: str, media_root: Path | None = None, *, state_path: Path | None = None,
        assets_root: Path | None = None, subject: str = "reel") -> dict:
    if stage not in STAGES:
        raise ValueError(f"Etapa desconhecida: {stage}")
    if subject not in {"reel", "financas"}:
        raise ValueError("Assunto desconhecido")
    if stage != "DIAGNOSTICO" and subject == "financas":
        raise ValueError("Financeiro usa DIAGNOSTICO; produção audiovisual não se aplica")
    ledger = json.loads((state_path or ROOT / "config" / "decisao_atual.json").read_text(encoding="utf8"))
    assets_root = assets_root or media_root or Path("/nonexistent")
    rr = ledger["restricoes"]
    brand = ledger["referencia_marca"]
    brand_proof = verify_sha(assets_root / brand["caminho_relativo_media"], brand["sha256"])
    authorizations = ledger.get("autorizacoes_especificas", {})
    acts: dict[str, Any] = {}
    issues: list[str] = []
    notes: list[str] = []
    selected = ["MEM-01", "FIN-08", "QA-09"] if subject == "financas" else AGENTS[stage]

    acts["MEM-01"] = {"tipo": "LEITURA_VERIFICAVEL", "versoes": {v["versao"]: v["estado"] for v in ledger["versoes"]},
                      "limite": "o registro continua dependente das mensagens humanas e da reconciliação com Sheets"}
    if "SCOUT-02" in selected:
        acts["SCOUT-02"] = scout_worker()
    if "FIN-08" in selected:
        acts["FIN-08"] = finance_worker()
    if "MEDIA-11" in selected:
        acts["MEDIA-11"] = media_worker(media_root)
        if stage in SENSITIVE and (not media_root or acts["MEDIA-11"]["estado"] != "AUDITORIA_TECNICA_CONCLUIDA"):
            issues.append("MEDIA: arquivos originais ausentes, divergentes ou não verificados neste ambiente")

    frame = approval(ledger, "R05_FRAME_V1_3", "QUADRO_CHAVE",
                     assets_root / "VACINA01" / "DIRECAO_DOCUMENTAL_V1_3" / "R05_QUADRO_CHAVE_CANDIDATO_01.png")
    motion = approval(ledger, "R05_MOTION_V1_6", "BASE_MOTION",
                      assets_root / "VACINA01" / "TESTE_MOTION_V1_6" / "R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4")
    candidate = next((v for v in ledger["versoes"] if v["versao"] == "R05_MOTION_V1_7"), {})
    if subject == "reel":
        if "ART-05" in selected:
            acts["ART-05"] = {"tipo": "EVIDENCIA_LOCAL", "quadro": frame,
                               "identidade": ledger["referencia_marca"]["estado"],
                               "prova_referencia_marca": brand_proof,
                               "limite": "não substitui auditoria visual humana de tipografia/composição"}
        if "EDIT-06" in selected:
            acts["EDIT-06"] = {"tipo": "EVIDENCIA_LOCAL", "base_movimento": motion,
                                "v1_7": candidate.get("estado"), "limite": "não realizou edição, cor nem áudio"}
        if "VET-07" in selected:
            acts["VET-07"] = {"tipo": "GATE_HUMANO", "validacao_larissa": rr["validacao_clinica_larissa"],
                               "limite": "a execução de um auditor não é parecer veterinário"}
    if subject == "reel" and stage != "DIAGNOSTICO" and brand_proof["estado"] != "CONFERIDO":
        issues.append("MARCA: referência Rosé Editorial canônica não conferida contra hash")
    if subject == "reel" and stage in {"TESTE_CURTO", "EDICAO_COMPLETA", "PRE_PUBLICACAO", "PUBLICACAO"} and not frame["ok"]:
        issues.append("ARTE: quadro V1.3 aprovado não corresponde ao arquivo ou não está disponível")
    if subject == "reel" and stage in {"EDICAO_COMPLETA", "PRE_PUBLICACAO", "PUBLICACAO"}:
        if not motion["ok"]:
            issues.append("EDIÇÃO: base V1.6 aprovada não corresponde ao vídeo ou não está disponível")
        if not signed_authorization(authorizations.get("edicao_master"), action="EDICAO_COMPLETA",
                                    approver="Borelli", version="R05_MAVIE"):
            issues.append("ESCOPO: base V1.6 não autoriza master; falta autorização rastreável por job e finalidade")
    if subject == "reel" and stage in {"PRE_PUBLICACAO", "PUBLICACAO"}:
        requirements = [
            ("validacao_clinica_larissa", "CLÍNICO: Larissa ainda não validou afirmações"),
            ("crmv_confirmado_larissa", "REGULATÓRIO: CRMV ainda não confirmado"),
            ("licenca_musica_comprovada", "ÁUDIO: licença comercial ainda não comprovada"),
            ("logo_e_fontes_definitivas_confirmados", "MARCA: logo/tipografia ainda não confirmados"),
            ("aprovacao_final_publicacao", "HUMANO: versão final não aprovada")]
        issues.extend(message for field, message in requirements if not rr.get(field))
        if not signed_authorization(authorizations.get("validacao_clinica"), action="VALIDACAO_CLINICA",
                                    approver="Larissa", version="R05_MAVIE"):
            issues.append("CLÍNICO: campo booleano não substitui validação específica da Larissa")
        if not signed_authorization(authorizations.get("aprovacao_final"), action="APROVACAO_FINAL",
                                    approver="Borelli", version="R05_MAVIE",
                                    artifact_sha=ledger.get("master_sha256", "")):
            issues.append("HUMANO: master final exato sem autorização vinculada ao SHA-256")
    if stage == "PUBLICACAO" and not signed_authorization(authorizations.get("publicacao"),
                       action="PUBLICACAO", approver="Borelli", version="R05_MAVIE",
                       artifact_sha=ledger.get("master_sha256", "")):
        issues.append("PUBLICAÇÃO: não existe autorização específica vinculada ao arquivo final")
    if subject == "reel" and stage == "AUDITORIA_VISUAL":
        v16 = assets_root / "VACINA01/TESTE_MOTION_V1_6/R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4"
        v17 = assets_root / "VACINA01/TESTE_MOTION_V1_7/R05_MAVIE_MICROTESTE_MOTION_V1_7.mp4"
        expected16 = next((v.get("sha256") for v in ledger["versoes"] if v["versao"] == "R05_MOTION_V1_6"), None)
        expected17 = next((v.get("sha256") for v in ledger["versoes"] if v["versao"] == "R05_MOTION_V1_7"), None)
        ok16 = expected16 and verify_sha(v16,expected16)["estado"] == "CONFERIDO"
        ok17 = expected17 and verify_sha(v17,expected17)["estado"] == "CONFERIDO"
        if not (ok16 and ok17):
            issues.append("VISUAL: V1.6 e V1.7 precisam ter hashes verificados antes da comparação")
            acts["VISUAL-QA"] = {"tipo":"NÃO_EXECUTADO_SEM_ASSETS_VERIFICADOS"}
        else:
            try:
                comp = compare(v16,v17)
            except (OSError,ValueError,RuntimeError,TimeoutError) as exc:
                issues.append("VISUAL: análise não concluída: " + type(exc).__name__)
                acts["VISUAL-QA"] = {"tipo":"FALHOU"}
            else:
                acts["VISUAL-QA"] = {"tipo":"WORKER_QA_VISUAL", "comparativo":comp,
                    "limite":"não produz revisão estética humana; não aprova candidata ou master"}
                if comp["v17"]["alertas"]:
                    issues.append("VISUAL: alertas de luminância/contraste na V1.7; NÃO promover automaticamente")
                notes.append("A comparação de quadros foi executada; V1.6 segue como base aprovada por humano")
    if rr.get("autoriza_gasto") is not True:
        notes.append("Orçamento aprovado para gastos: R$0 / 0 crédito; nenhum consumo permitido")
    if stage == "DIAGNOSTICO" and subject == "reel":
        notes.append("V1.7 é CANDIDATA_NAO_APROVADA. A V1.6 é base de movimento, não master publicado.")
    for agent in selected:
        if agent not in acts and agent != "QA-09":
            acts[agent] = {"tipo": "PERFIL_DEFINIDO_NAO_EXECUTADO", "observacao": "necessita IA externa, editor ou humano; não foi acionado"}
    acts["QA-09"] = {"tipo": "VALIDADOR_DE_GATES", "bloqueios": list(issues),
                     "limite": "validação documental e técnica não prova qualidade criativa nem segurança clínica"}
    # Ações sensíveis ficam bloqueadas por padrão, mesmo quando a inspeção não aponta falha técnica.
    status = ("AUDITORIA_VISUAL_COM_ALERTAS" if stage == "AUDITORIA_VISUAL" and issues
              else "BLOQUEADO" if issues else "AUDITORIA_CONCLUIDA_SEM_EXECUCAO_DE_PRODUCAO")
    fingerprint = hashlib.sha256(json.dumps({"stage":stage,"subject":subject,"ledger":ledger,
                                            "assets": {"frame":frame["ok"],"motion":motion["ok"],
                                                       "referencia_marca":brand_proof["estado"],
                                                       "visual": {"v17_sha":acts.get("VISUAL-QA",{}).get("comparativo",{}).get("v17",{}).get("sha256"),
                                                                   "alertas":acts.get("VISUAL-QA",{}).get("comparativo",{}).get("v17",{}).get("alertas")}}},
                                           sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    return {"motor": "2.1.0", "job": ledger["trabalho"], "assunto": subject,
            "etapa_solicitada": stage, "execucao_id": fingerprint,
            "estado": status, "agentes_planejados": selected,
            "agentes_deterministicos_executados": [k for k in selected if acts[k].get("tipo") not in {"PERFIL_DEFINIDO_NAO_EXECUTADO", "GATE_HUMANO"}],
            "subagentes_llm_realmente_executados": [], "atos_externos_executados": [],
            "gastou": False, "publicou": False, "renderizou": False,
            "evidencias": acts, "bloqueios": issues, "notas": notes,
            "proximo_passo_prioritario": (
                "Revisar alerta de transição V1.7; preservar V1.6 como base até aceite visual específico"
                if subject=="reel" else "Apurar custos completos e preços de venda antes de calcular margens")}


def report_md(result: dict) -> str:
    rows=[f"# ORQ-00 · VACINA 01 / {result['etapa_solicitada']}",
          f"- Estado: **{result['estado']}**", f"- Execução: `{result['execucao_id']}`",
          f"- Perfil LLM efetivamente iniciado: **{len(result['subagentes_llm_realmente_executados'])}**",
          f"- Produção/publicação/gastos: **não realizados**", "", "## Especialistas envolvidos"]
    rows += [f"- {agent}: {result['evidencias'][agent].get('tipo','WORKER_LOCAL')}" for agent in result['agentes_planejados']]
    rows += ["", "## Bloqueios"] + ([f"- {e}" for e in result['bloqueios']] if result['bloqueios'] else ["- Nenhum bloqueio estrutural nesta etapa; não significa aprovação humana."])
    rows += ["", "## Próximo passo", result['proximo_passo_prioritario'], "",
             "Este relatório não substitui aprovação visual ou clínica. Nenhum arquivo público foi produzido."]
    return "\n".join(rows)+"\n"


def main():
    p=argparse.ArgumentParser(description="ORQ-00 2.1 · audit-only sem créditos")
    p.add_argument("command", choices=["run"])
    p.add_argument("--stage", choices=sorted(STAGES), default="DIAGNOSTICO")
    p.add_argument("--subject", choices=["reel", "financas"], default="reel")
    p.add_argument("--media-root", type=Path)
    p.add_argument("--assets-root", type=Path)
    p.add_argument("--state-path", type=Path)
    p.add_argument("--out", type=Path, default=ROOT / "reports" / "ORQ00_ULTIMA_EXECUCAO.json")
    args=p.parse_args()
    result=run(args.stage,args.media_root,state_path=args.state_path,assets_root=args.assets_root,subject=args.subject)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    args.out.with_suffix(".md").write_text(report_md(result),encoding="utf8")
    print(json.dumps({"estado":result["estado"], "agentes":result["agentes_planejados"],
                      "executados":result["agentes_deterministicos_executados"],
                      "bloqueios":result["bloqueios"], "relatorio":str(args.out)},ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
