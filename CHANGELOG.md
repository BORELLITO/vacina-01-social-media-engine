# HISTÓRICO — REDIRECT TO CHANGELOG_V4_1.md

Este arquivo é mantido apenas para rastreabilidade. O changelog append-only vigente é `CHANGELOG_V4_1.md`.

# CHANGELOG — VACINA 01

## 2026-11-16 — V1 — Sincronização inicial do motor

### Implementado

- Criado o repositório privado BORELLITO/vacina-01-social-media-engine.
- Sincronizado o Prompt Mestre V4 a partir da Library.
- Sincronizado o Cockpit atual a partir da Library.
- Criados os arquivos ENGINE_LOCK, QA_GATE e MANIFEST.
- Registrada a regra de bloqueio para verde/verde-oliva.
- Registrada a separação entre arte, copy, clínica e publicação.
- Mantidos os binários das artes fora do GitHub por padrão.

### Correção de governança

A produção anterior do P04 ocorreu com cockpit/Library e script local, sem preflight obrigatório contra um repositório canônico. Isso permitiu deriva visual. A causa foi falha de governança, não uma aprovação nova.

### Estado

- Motor: IMPLEMENTADO.
- Repositório: IMPLEMENTADO.
- QA gate: IMPLEMENTADO como documento operacional.
- Arte P04 V6: CANDIDATA; não aprovada automaticamente.
- Clínica: revisão preliminar; sem validação clínica automática.
- Publicação: não confirmada.

## 2026-11-16 — V4.1 — Lapidação do motor

### Implementado

- Criado CURRENT_ENGINE.md como índice de carregamento único.
- Criado MOTOR_V4_1_ADDENDUM.md sem apagar o Prompt Mestre V4.
- Separado snapshot vigente do histórico no cockpit.
- Transformados os cinco critérios de Borelli em gate perceptivo obrigatório.
- Definida a escolha de ferramenta: composição determinística para texto/layout; edição controlada para fotos; geração de imagem somente quando adequada.
- Reforçado o hard stop para motor, assets, conflitos, claims clínicos e aprovações ausentes.
- Atualizados ENGINE_LOCK, QA_GATE e MANIFEST para V4.1.

### Estado

- Motor V4.1: IMPLEMENTADO.
- Preflight: IMPLEMENTADO como protocolo documental.
- P04 V7: CANDIDATA; revisão humana pendente.
- Publicação: não realizada.
