---
name: orquestrador-vacina01
description: Aciona ORQ-00 em trabalhos de vacinação veterinária domiciliar, Reel e identidade Rosé Editorial, pesquisa e preço, preservando aprovações de versões por hash.
---

# Orquestrador VACINA 01 — roteiro de execução

Ative o ORQ-00 na solicitação de próxima etapa, conteúdo, Reel, análise financeira, auditoria e continuidade. Antes de gerar qualquer arte:
1. Leia o estado atual (`config/decisao_atual.json`), a referência canônica e o contrato (`docs/ORQ_00_CONTRATO_OPERACIONAL.md`).
2. Execute `python runtime/orq_v2.py run --stage DIAGNOSTICO` com `--media-root` e `--assets-root` somente quando os originais estiverem acessíveis.
3. Diferencie especialistas realmente acionados de perfis apenas definidos.
4. Despache pesquisa, finanças, arte, vídeo e QA somente conforme a natureza do pedido; nenhum fluxo exige todos os agentes.
5. Para R05: V1.3 quadro aprovado; V1.6 BASE audiovisual aprovada; V1.7 candidata sem aprovação. Preserve todas.
6. Não trate booleanos sem prova como autorização, nem publique/consuma créditos sem ato específico.
7. A saída deve apresentar entregas verificadas, bloqueios e **um** próximo passo prioritário.

É necessário um runtime compatível para executar subagentes LLM; esta skill não o instala, liga ou substitui.
