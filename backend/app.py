import os
from flask import Flask, jsonify
from flask_cors import CORS

from routes import cliente_bp, intranet_bp, ceo_bp, ia_bp
from ia.recommender import treinar_recomendador
from ia.chatbot_engine import carregar_faq


def create_app():
    # base_dir = G:\sfood
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # static_folder aponta para a RAIZ, onde está o index.html
    app = Flask(
        __name__,
        static_folder=base_dir,   # G:\sfood
        static_url_path=""        # arquivos acessíveis em "/"
    )
    CORS(app)

    # ============================
    # BLUEPRINTS DA API
    # ============================
    app.register_blueprint(cliente_bp)
    app.register_blueprint(intranet_bp)
    app.register_blueprint(ceo_bp)
    app.register_blueprint(ia_bp)

    # ============================
    # HEALTHCHECK
    # ============================
    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "message": "sfood API rodando."})

    # ============================
    # PÁGINA INICIAL (FRONT)
    # ============================
    @app.route("/")
    def index():
        # Vai buscar G:\sfood\index.html
        return app.send_static_file("index.html")

    # ============================
    # INICIALIZA IA
    # ============================
    with app.app_context():
        treinar_recomendador()
        carregar_faq()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
