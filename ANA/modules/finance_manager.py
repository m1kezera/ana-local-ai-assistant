# modules/finance_manager.py

import logging
from datetime import datetime, timedelta

def calcular_multa(valor_original, dias_atraso, taxa_multa=2.0):
    """Calcula multa fixa sobre um valor com base nos dias de atraso."""
    multa = (taxa_multa / 100) * valor_original if dias_atraso > 0 else 0
    return round(multa, 2)

def calcular_juros_simples(valor_original, dias_atraso, taxa_juros_diaria=0.033):
    """Calcula juros simples diários sobre um valor com base no atraso."""
    juros = (taxa_juros_diaria / 100) * valor_original * dias_atraso if dias_atraso > 0 else 0
    return round(juros, 2)

def analisar_pagamento(data_vencimento_str, valor):
    """Avalia um pagamento vencido e calcula multa e juros."""
    data_venc = datetime.strptime(data_vencimento_str, "%Y-%m-%d")
    hoje = datetime.now()
    dias_atraso = (hoje - data_venc).days

    multa = calcular_multa(valor, dias_atraso)
    juros = calcular_juros_simples(valor, dias_atraso)

    total = round(valor + multa + juros, 2)
    logging.info(f"Análise: {dias_atraso} dias de atraso, multa R${multa}, juros R${juros}, total R${total}")
    
    return {
        "dias_atraso": dias_atraso,
        "multa": multa,
        "juros": juros,
        "total": total
    }
