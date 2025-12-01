from typing import Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db import fetch_all, get_connection

_faq_df: Optional[pd.DataFrame] = None
_vectorizer: Optional[TfidfVectorizer] = None
_matrix = None
_ready = False


def carregar_faq():
    global _faq_df, _vectorizer, _matrix, _ready
    rows = fetch_all("""
        SELECT id, pergunta, resposta
        FROM faq
        WHERE ativo = TRUE
    """)

    if not rows:
        _faq_df = pd.DataFrame()
        _vectorizer = None
        _matrix = None
        _ready = False
        print("[IA] Nenhuma FAQ encontrada para o chatbot.")
        return

    df = pd.DataFrame(rows)
    _vectorizer = TfidfVectorizer(max_features=3000)
    _matrix = _vectorizer.fit_transform(df["pergunta"].values)
    _faq_df = df
    _ready = True
    print(f"[IA] Chatbot carregado com {len(df)} perguntas.")


def _ensure_ready():
    if not _ready:
        carregar_faq()


def responder(pergunta: str) -> Tuple[str, float]:
    """
    Retorna (resposta, score_de_confianca)
    """
    _ensure_ready()
    if not _ready or _faq_df is None or _matrix is None or not pergunta:
        return (
            "Sou a assistente IA da sfood. Em breve terei acesso à base completa de dúvidas frequentes.",
            0.0,
        )

    vec = _vectorizer.transform([pergunta])
    sims = cosine_similarity(vec, _matrix).flatten()

    idx_max = sims.argmax()
    score = float(sims[idx_max])
    resposta = _faq_df.iloc[idx_max]["resposta"]

    # limiar de confiança simples
    if score < 0.2:
        return (
            "Ainda não tenho uma resposta precisa para essa pergunta. "
            "Na apresentação, isso pode ser comentado como limite do modelo.",
            score,
        )

    return resposta, score


def registrar_log(pergunta: str, resposta: str, confianca: float, origem: str = "cliente", cliente_id=None):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chatbot_logs (cliente_id, origem, pergunta, resposta, confianca)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (cliente_id, origem, pergunta, resposta, confianca),
            )
            conn.commit()
    finally:
        conn.close()
