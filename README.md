# Executor verificável v1.2 — NÃO confundir com 10 LLMs em paralelo

- `python runtime/dispatch.py run --stage DISCOVERY --media-root /mnt/data`
- `python runtime/dispatch.py run --stage EDICAO --media-root /mnt/data`
- `python -m unittest discover -s tests -v`

`MEM-01`, `SCOUT-02`, `FIN-08`, `ART-05`, `VET-07`, `MEDIA-11` e `QA-09` executam **verificações determinísticas locais** e geram recibos em JSON. A condição de bloqueio é resultado correto e esperado. Os demais perfis são arquivos de especificação e **não** agentes de IA rodando de verdade. Nenhuma publicação, contato externo, gasto, geração visual ou upload foi automatizado aqui.

O `MEDIA-11` compara SHA-256 dos três originais com o Prompt V7 e registra ffprobe real. O MP3 é **derivado** e tem hash próprio, não corresponde ao original MP4. Se não houver mídia na máquina, retorna `SEM_ARQUIVOS_LOCAL`; nunca afirma que leu anexos invisíveis.

## Limites

O Scout não viu os vídeos referenciados, então não conclui tendências de edição. O Diretor de Arte não usa detecção de simetria automática como prova estética. A clínica não é validada por código. A porta de edição permanece fechada até referência realmente assistida, Larissa real captada, quadro-chave aprovado e teste curto aprovado.

## Não enviar ao GitHub

Este repositório não inclui material original de cliente, voz, nomes de tutores, autorizações ou prontuário. Não armazenar anexos privados no código. Os metadados dos arquivos saem no relatório local de ingestão; compartilhar externamente só quando necessário e autorizado.
