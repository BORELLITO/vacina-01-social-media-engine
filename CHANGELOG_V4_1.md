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

## 2026-11-16 — V4.1.1 — Correção de governança e rastreabilidade

### Corrigido

- Normalizadas as referências para `START_COCKPIT_CURRENT_V4_1.md`, `ENGINE_LOCK_V1_1.md` e `QA_GATE_V1_1.md`.
- Arquivos sem sufixo vigente foram explicitamente classificados como históricos/compatibilidade.
- Manifesto atualizado de V1 para V4.1.
- Criado o registro de estado dos tokens visuais, sem inventar hex, fontes ou medidas ainda não validados.
- Gate perceptivo passou a exigir cinco respostas registradas no manifesto da versão exata.
- Estados de QA foram desambiguados para não confundir teste técnico com aprovação humana.
- Registrado o problema de leitura via API/conector GitHub, mantendo a verificação web separada.

### Estado

- Motor: V4.1.1 documental implementado.
- P04 V7: continua candidata; não aprovada automaticamente.
- Novas artes: condicionadas à reconciliação da leitura do GitHub e à validação dos tokens necessários.

## 2026-11-16 — V4.1.2 — Redirecionamento de aliases históricos

- `ENGINE_LOCK.md`, `QA_GATE.md`, `MANIFEST.md` e `CHANGELOG.md` passaram a conter redirecionamento explícito para suas fontes V4.1.
- `START_COCKPIT_CURRENT.md` passou a ser marcado como superseded e redirecionado para `START_COCKPIT_CURRENT_V4_1.md`.
- Os aliases históricos foram mantidos para rastreabilidade, sem poder substituir o motor vigente.
- GitHub: commits de governança `e248f02` e `f528e6e` verificados na branch `main`.
