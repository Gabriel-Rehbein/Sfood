# backend/ia/planner.py

from db import fetch_all


def gerar_plano_refeicoes(preferencias=None, dias=7):
    """
    Gera um plano simples de refeições usando os produtos cadastrados.
    Retorna um dicionário com 'mensagem' e 'dias', onde cada dia
    tem 3 refeições (café, almoço, janta).
    """
    preferencias = preferencias or []

    produtos = fetch_all("""
        SELECT id, nome, descricao, eh_saudavel, tags_texto
        FROM produtos
        WHERE ativo = TRUE
        ORDER BY id;
    """)

    if not produtos:
        return {
            "mensagem": "Nenhum produto cadastrado para montar o plano.",
            "dias": []
        }

    dias_plano = []
    idx = 0

    for d in range(dias):
        refeicoes_dia = []
        for _ in range(3):  # café, almoço, janta
            prod = produtos[idx % len(produtos)]
            refeicoes_dia.append({
                "produto_id": prod["id"],
                "nome": prod["nome"],
                "descricao": prod["descricao"],
                "tags": prod.get("tags_texto", ""),
                "saudavel": bool(prod.get("eh_saudavel")),
            })
            idx += 1

        dias_plano.append({
            "dia": d + 1,
            "refeicoes": refeicoes_dia
        })

    return {
        "mensagem": "Plano de refeições gerado com sucesso.",
        "dias": dias_plano
    }
