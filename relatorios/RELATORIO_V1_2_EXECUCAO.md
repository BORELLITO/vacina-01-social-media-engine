# VACINA01 V1.2 — execução efetiva / 25–26 de novembro de 2026

## Inspeção de arquitetura
- O projeto anterior tinha 11 perfis `.agent.md`, configuração e gates locais; **não tinha despacho real dos perfis**. O repositório VACINA 01 não está visível entre os repositórios da conta GitHub conectada; GitHub Actions continua como **configuração local, não workflow online**.
- V1.2 adiciona `runtime/dispatch.py` com verificadores determinísticos independentes e recibo JSON; sem invocação de 10 LLMs, sem trabalho de fundo.

## Execução local, sem efeitos externos
- 29 testes unitários de comportamento/segurança: **OK**; inclui regressões anteriores e novos casos de mídia adulterada, ffprobe ausente, fonte textual não assistida, preço desconhecido e veto a publicação.
- Média: `204443.jpg`, `204439.jpg`, `204446.mp4`: SHA-256 confere com V7; MP3 recebido é derivado, fingerprint registrada, sem alegar equivalência ao MP4 fonte. Metadados reais extraídos por ffprobe.
- Memória lida; SCOUT classificou 3 referências como **LEGENDA_VERIFICADA, vídeo não assistido**; FIN-08 reconheceu apenas custos de compra, sem simular margem; ART e VET reportaram pendências.
- `DISCOVERY` retornou GATE_ESTRUTURAL_VALIDO; `EDICAO` retornou **BLOQUEADO (código de saída 1)**, com motivações registradas. Nenhum vídeo gerado, publicado ou enviado, nenhum crédito gasto.

## Bloqueios sem inferir aprovação
1. Referência audiovisual realmente assistida/auditada (3 independentes no gate v1.1 atual; requisito interno, passível de discussão por custo-benefício, mas não removido).
2. Quadro-chave verdadeiro comparado à referência canônica e aprovado por Borelli.
3. 3 novas tomadas reais da Larissa; caso da Mavie histórico, sem encenar vacinação atual.
4. Amostra de 3–5 segundos aprovada antes da edição completa.
5. Texto clínico, CRMV, música licenciada e aprovação de publicação sob seus gates próprios.

## Integrações reais
- Google Sheets: registro operacional verificado na conexão da conta; integração **não** executada por `dispatch.py`; sincronização manual/externa separada.
- Google Drive: armazenamento de versões da estrutura, preservando anteriores.
- GitHub: repositório de VACINA 01 **não acessível** pela conexão atual; scripts CI locais não rodaram online.
- Canva/Descript/vidIQ: ferramentas identificadas, **não foram chamadas para render/edição** nesta operação.

## Critérios de aceite
- Testes unitários OK, digest de originais confere, bloqueio da edição efetivo, arquivo final de relatório gerado. Isso valida processos e evidência técnica; **não** comprova qualidade estética, resultado comercial ou agentes LLM autônomos.
