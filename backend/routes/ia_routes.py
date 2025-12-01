from flask import Blueprint, jsonify, request
from ia.chatbot_engine import responder
from ia.planner import gerar_plano_refeicoes

ia_bp = Blueprint("ia", __name__, url_prefix="/api/ia")


@ia_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    pergunta = data.get("pergunta", "")
    resposta, score = responder(pergunta)
    return jsonify({"resposta": resposta, "confianca": score}), 200


@ia_bp.post("/planner-refeicoes")
def planner_refeicoes():
    data = request.get_json(silent=True) or {}
    dias = int(data.get("dias", 7))
    preferencias = data.get("preferencias") or []

    plano = gerar_plano_refeicoes(preferencias, dias)
    return jsonify(plano), 200
