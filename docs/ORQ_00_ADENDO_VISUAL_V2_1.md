# ORQ-00 V2.1 — QA audiovisual comparativo

## Avanço realizado
Foi adicionado `runtime/visual_qa.py`, um inspetor que decodifica **os quadros reais** de uma mídia local com ffmpeg e mede luminância e contraste no trecho da transição. Sem IA generativa, OCR, rede ou escrita nas mídias originais. Testes de regressão estão em `tests/test_visual_qa.py`.

Este módulo deve ser usado pelo QA-09 / EDIT-06 **antes** de sugerir promoção de uma candidata. Ele gera alertas matemáticos, não aprova estética ou clínica. Os alertas identificam quadros quase vazios, picos de luminância e quedas de contraste.

## Execução
```bash
python -m unittest discover -s tests -v
python runtime/visual_qa.py --v16 /mnt/data/VACINA01/TESTE_MOTION_V1_6/R05_MAVIE_MICROTESTE_MOTION_V1_6.mp4 --v17 /mnt/data/VACINA01/TESTE_MOTION_V1_7/R05_MAVIE_MICROTESTE_MOTION_V1_7.mp4 --output reports/QA_VISUAL_V16_V17.json
```

## Não mudou
Aprovação do quadro V1.3 e da base V1.6, veto às versões V1–V3, status pendente da V1.7, gates clínico, publicação e gastos. O módulo não realiza renderização nem publicação. Execução automática em nuvem não foi implantada.
