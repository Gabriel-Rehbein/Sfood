# backend/routes/ceo_routes.py

from flask import Blueprint, jsonify
from pathlib import Path
import csv

ceo_bp = Blueprint("ceo", __name__, url_prefix="/api/ceo")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@ceo_bp.get("/analytics")
def analytics_resumo():
    from db import fetch_one

    # Exemplo simples de contagem (ajusta se quiser algo mais avançado)
    row = fetch_one(
        """
        SELECT
          (SELECT COUNT(*) FROM produtos WHERE ativo = TRUE) AS total_produtos,
          (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
          (SELECT COUNT(*) FROM clientes) AS total_clientes
        """
    ) or {}
    return jsonify(row), 200


@ceo_bp.get("/vendas-categorias")
def vendas_categorias():
    """
    Lê o arquivo sfood_produtos.csv em backend/data e monta
    séries de vendas por categoria ao longo do tempo.
    Espera cabeçalhos como:
    data, mes, ano, vendas_hortifruti, vendas_carnes, vendas_laticinios,
    vendas_bebidas, vendas_higiene, vendas_limpeza, vendas_comida_pronta, ...
    """
    csv_path = DATA_DIR / "sfood_produtos.csv"
    if not csv_path.exists():
        return jsonify({"error": "Arquivo sfood_produtos.csv não encontrado"}), 404

    labels = []
    series_data = {
        "Hortifruti": [],
        "Carnes": [],
        "Laticínios": [],
        "Bebidas": [],
        "Higiene": [],
        "Limpeza": [],
        "Comida pronta": [],
    }

    try:
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                # label: exemplo "01/2025" ou a própria coluna data
                data_bruta = row.get("data") or ""
                mes = row.get("mes")
                ano = row.get("ano")

                if mes and ano:
                    label = f"{mes}/{ano}"
                elif data_bruta:
                    label = data_bruta
                else:
                    continue

                labels.append(label)

                def parse_num(key):
                    val = row.get(key, "").strip()
                    if not val:
                        return 0
                    return float(val.replace(",", "."))
                
                series_data["Hortifruti"].append(parse_num("vendas_hortifruti"))
                series_data["Carnes"].append(parse_num("vendas_carnes"))
                series_data["Laticínios"].append(parse_num("vendas_laticinios"))
                series_data["Bebidas"].append(parse_num("vendas_bebidas"))
                series_data["Higiene"].append(parse_num("vendas_higiene"))
                series_data["Limpeza"].append(parse_num("vendas_limpeza"))
                series_data["Comida pronta"].append(parse_num("vendas_comida_pronta"))

    except Exception as e:
        return jsonify({"error": f"Erro ao ler CSV: {e}"}), 500

    # monta resposta
    series = []
    for label_serie, data in series_data.items():
        series.append({
            "label": label_serie,
            "data": data,
        })

    return jsonify({
        "labels": labels,
        "series": series,
    }), 200
