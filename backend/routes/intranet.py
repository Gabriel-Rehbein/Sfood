from flask import Blueprint, jsonify
from db import fetch_all

intranet_bp = Blueprint("intranet", __name__, url_prefix="/api/intranet")


@intranet_bp.get("/pedidos")
def listar_pedidos():
    pedidos = fetch_all("""
        SELECT id, cliente_nome, total, status, criado_em
        FROM pedidos
        ORDER BY criado_em DESC;
    """)
    return jsonify(pedidos), 200
