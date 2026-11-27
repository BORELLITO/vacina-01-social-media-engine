#!/usr/bin/env python3
"""Calcula lucro por atendimento apenas com todos os custos conhecidos."""
def margem(preco,custo_vacina,materiais,deslocamento,cadeia_frio,tributos,tempo):
    vals=[preco,custo_vacina,materiais,deslocamento,cadeia_frio,tributos,tempo]
    if any(v is None for v in vals):return {'estado':'PENDENTE','lucro':None,'margem':None}
    if preco<=0 or any(v<0 for v in vals[1:]):raise ValueError('valores invalidos')
    lucro=preco-sum(vals[1:])
    return {'estado':'SIMULACAO','lucro':round(lucro,2),'margem':round(lucro/preco,4)}
