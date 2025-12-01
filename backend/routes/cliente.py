# backend/routes/cliente.py

from flask import Blueprint, jsonify, request
from db import fetch_all
from ia.recommender import recomendar_por_carrinho  # <- ESTA função existe no recommender.py

cliente_bp = Blueprint("cliente", __name__, url_prefix="/api/cliente")


@cliente_bp.get("/produtos")
def listar_produtos():
    rows = fetch_all("""
        SELECT p.id,
               p.nome,
               p.descricao,
               p.tags_texto,
               p.eh_saudavel,
               c.nome AS categoria
        FROM produtos p
        LEFT JOIN categorias_produto c ON c.id = p.categoria_id
        WHERE p.ativo = TRUE
        ORDER BY p.id;
    """)
    return jsonify(rows or []), 200


@cliente_bp.post("/recomendacoes")
def recomendar():
    """
    Espera um JSON assim:
    {
      "ids": [1, 2, 3]
    }
    """
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []

    try:
        ids = [int(x) for x in ids]
    except Exception:
        ids = []

    recomendados = recomendar_por_carrinho(ids)
    return jsonify(recomendados or []), 200
