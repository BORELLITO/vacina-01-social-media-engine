# VACINA 01 — ENGINE LOCK V1

Data de sincronização: 16/11/2026
Repositório canônico: BORELLITO/vacina-01-social-media-engine
Motor principal: PROMPT_MESTRE_SOCIAL_MEDIA.md — V4
Cockpit operacional: START_COCKPIT.md
Estado do repositório: IMPLEMENTADO — sincronização inicial

## Fonte de verdade

Este repositório é a fonte técnica do motor operacional. A Library e o Google Sheets continuam como registros operacionais e evidências do projeto. Nenhuma arte deve ser criada usando cópia antiga, memória isolada ou script não reconciliado com este repositório.

## Pré-voo obrigatório

1. Ler o Prompt Mestre vigente.
2. Ler o Cockpit vigente.
3. Conferir identidade visual, assets aprovados, bloqueios e reprovações.
4. Conferir os estados independentes de arte, copy, clínica e publicação.
5. Se o repositório não puder ser lido ou houver conflito não resolvido, BLOQUEAR a produção.
6. Após produzir, executar os gates de QA e registrar a versão exata.
7. Nunca chamar candidata de aprovada sem evidência humana vinculada ao arquivo exato.

## Travas visuais vigentes

- Direção: Rosé Editorial.
- Paleta-base: branco, marfim, rosa antigo/rosé, coral suave, taupe, marrom/grafite.
- Verde e verde-oliva: PROIBIDOS na arte P04 e nas próximas peças, salvo decisão humana explícita que substitua esta regra.
- Foto da Larissa: não obrigatória. Quando usada, preservar suas características originais.
- Hook: maior destaque tipográfico da peça.
- Feed: clean, editorial, acolhedor, profissional e sem aparência genérica de IA.
- Master preferencial: 2160×2700 px, proporção 4:5.
- Não enviar binários pesados ao GitHub por padrão; usar Library/Drive para artes e GitHub para motor, manifests e controle.

## Estados independentes

Arte, copy, clínica, arquivo e publicação devem possuir estados próprios. Uma aprovação estética não aprova clínica; uma validação clínica não confirma publicação; um teste técnico não prova aprovação estética.

## Incidente que originou esta trava

Em versões anteriores do P04, a produção foi feita a partir de cockpit/Library e script local sem uma verificação obrigatória contra um repositório GitHub canônico. Isso permitiu deriva visual e a introdução de verde/oliva, posteriormente corrigida na V6. A causa foi falha de governança, não uma aprovação nova.

## Regra de rollback

Nunca sobrescrever binário aprovado ou histórico. Criar nova versão, manter a anterior intacta e registrar motivo, hash, estado anterior, estado atual e risco residual.
