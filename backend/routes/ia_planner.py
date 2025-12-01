from flask import request, jsonify
from . import ia_bp

@ia_bp.post("/chatbot")
def chatbot_responder():
    """
    Depois vamos plugar IA de verdade.
    Agora, responde com uma mensagem fixa só pra testar.
    """
    payload = request.get_json() or {}
    pergunta = payload.get("pergunta", "")
    resposta_mock = (
        "Sou o protótipo de chatbot da sfood. "
        "Em breve responderei com base na base de conhecimento real."
    )
    return jsonify({"ok": True, "pergunta": pergunta, "resposta": resposta_mock})

@ia_bp.post("/planner-refeicoes")
def planner_refeicoes():
    """
    Endpoint para o planner de refeições.
    Por enquanto devolve um plano fixo.
    """
    plano_mock = {
        "segunda": ["Overnight oats com frutas", "Bowl de frango grelhado", "Sopa de legumes"],
        "terca": ["Pão integral com ovos mexidos", "Salada completa com grãos", "Massa integral com molho leve"],
    }
    return jsonify({"ok": True, "plano": plano_mock})
