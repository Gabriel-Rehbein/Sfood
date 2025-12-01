import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import csv
from pathlib import Path
from db import execute_many
from ia.recommender import treinar_recomendador
from ia.chatbot_engine import carregar_faq  # se não tiver FAQ, tudo bem


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _abrir_csv_inteligente(path: Path):
    """
    Tenta detectar se o CSV está com ; ou ,
    e devolve (reader, delimiter_real)
    """
    with path.open(encoding="utf-8") as f:
        amostra = f.read(2048)
        # heurística bem simples
        if amostra.count(";") > amostra.count(","):
            delim = ";"
        else:
            delim = ","
    f = path.open(encoding="utf-8")
    reader = csv.DictReader(f, delimiter=delim)
    return reader, delim


def importar_produtos_csv():
    path = DATA_DIR / "sfood_produtos.csv"
    if not path.exists():
        print("[CSV] sfood_produtos.csv não encontrado em backend/data")
        return

    print(f"[CSV] Importando produtos de {path}...")

    reader, delim = _abrir_csv_inteligente(path)
    headers_orig = reader.fieldnames or []
    headers = [h.strip().lower() for h in headers_orig]

    print(f"[CSV] Delimitador detectado: '{delim}'")
    print(f"[CSV] Cabeçalhos encontrados: {headers_orig}")

    def achar_coluna(possiveis):
        for c in possiveis:
            if c in headers:
                return c
        return None

    # tenta mapear campos principais
    col_nome = achar_coluna(["nome", "produto", "nome_produto", "produto_nome"])
    col_desc = achar_coluna(["descricao", "descrição", "descricao_produto", "descricao_prod"])
    col_cat = achar_coluna(["categoria_slug", "categoria", "categoria_nome", "cat_slug"])
    col_preco = achar_coluna(["preco", "preço", "preco_venda"])
    col_un = achar_coluna(["unidade", "unidade_medida", "un"])
    col_saude = achar_coluna(["eh_saudavel", "saudavel", "saudável", "is_healthy"])
    col_tags = achar_coluna(["tags_texto", "tags", "palavras_chave"])

    obrigatorios = {
        "nome": col_nome,
        "categoria": col_cat,
        "preco": col_preco,
    }
    faltando = [k for k, v in obrigatorios.items() if v is None]
    if faltando:
        print(f"[CSV] Não consegui mapear colunas obrigatórias: {faltando}")
        print("[CSV] Ajuste os nomes das colunas OU adicione mais aliases no script.")
        return

    rows_to_insert = []

    for row in reader:
        try:
            get = lambda col, default="": row[col] if col and col in row and row[col] is not None else default

            nome = get(col_nome).strip()
            if not nome:
                continue

            desc = get(col_desc, "").strip()
            slug = get(col_cat).strip().lower()
            if not slug:
                continue

            preco_str = get(col_preco, "0").strip().replace(",", ".")
            preco = float(preco_str or "0")
            unidade = get(col_un, "un").strip() or "un"

            eh_saudavel_raw = get(col_saude, "0").strip().lower()
            eh_saudavel = eh_saudavel_raw in ("1", "true", "sim", "s", "yes")

            tags = get(col_tags, "").strip()

            rows_to_insert.append(
                (nome, desc, preco, unidade, eh_saudavel, tags, slug)
            )

        except Exception as e:
            print(f"[CSV] Erro em linha de sfood_produtos.csv: {e}")

    if not rows_to_insert:
        print("[CSV] Nenhum produto válido encontrado.")
        return

    sql = """
    INSERT INTO produtos
        (nome, descricao, categoria_id, preco, unidade, eh_saudavel, tags_texto, ativo)
    SELECT %s, %s, c.id, %s, %s, %s, %s, TRUE
    FROM categorias_produto c
    WHERE c.slug = %s
    """

    if execute_many(sql, rows_to_insert):
        print(f"[CSV] {len(rows_to_insert)} produtos importados.")
    else:
        print("[CSV] Erro ao executar INSERTs em lote.")


def rodar_treino_completo():
    importar_produtos_csv()

    treinar_recomendador()
    try:
        carregar_faq()
    except Exception:
        pass

    print("[IA] Treino a partir de sfood_produtos.csv finalizado.")


if __name__ == "__main__":
    rodar_treino_completo()
