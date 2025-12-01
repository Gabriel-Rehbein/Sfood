import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "faq_sfood.csv")

def main():
    df = pd.read_csv(CSV_PATH, sep=";")

    df["pergunta"] = df["pergunta"].fillna("").str.lower()
    df["resposta"] = df["resposta"].fillna("")

    perguntas = df["pergunta"].tolist()
    respostas = df["resposta"].tolist()

    # Vetorizador TF-IDF
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),      # 1 ou 2 palavras
        max_features=5000
    )
    X_faq = vectorizer.fit_transform(perguntas)

    # Salva tudo em .pkl
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "vectorizer_faq.pkl"))
    joblib.dump(perguntas, os.path.join(BASE_DIR, "faq_perguntas.pkl"))
    joblib.dump(respostas, os.path.join(BASE_DIR, "faq_respostas.pkl"))
    joblib.dump(X_faq, os.path.join(BASE_DIR, "faq_matrix.pkl"))

    print("✅ Treino FAQ concluído e arquivos salvos em ia/")

if __name__ == "__main__":
    main()
