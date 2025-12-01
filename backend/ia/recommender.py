# backend/ia/recommender.py
"""
Módulo de recomendação simples para a SFOOD.

- treinar_recomendador(): carrega os produtos do banco
  e pré-processa as tags.
- recomendar_por_carrinho(lista_ids): recebe uma lista
  de IDs de produtos do carrinho e devolve recomendações
  ordenadas por similaridade (Jaccard).
"""

from db import fetch_all

_produtos = []
_produtos_por_id = {}
_tags_por_id = {}


def _tokenizar_tags(texto: str):
  """
  Transforma o campo tags_texto em set de palavras.
  """
  if not texto:
    return set()
  # tudo minúsculo + separa por espaço
  tokens = (
    texto.lower()
    .replace(",", " ")
    .replace(";", " ")
    .replace(".", " ")
    .split()
  )
  return set(t.strip() for t in tokens if t.strip())


def treinar_recomendador():
  """
  Carrega os produtos do banco e monta estrutura em memória.
  Deve ser chamada na inicialização da app.
  """
  global _produtos, _produtos_por_id, _tags_por_id

  rows = fetch_all(
    """
    SELECT
      p.id,
      p.nome,
      p.descricao,
      p.tags_texto,
      p.eh_saudavel,
      p.preco,
      c.nome AS categoria
    FROM produtos p
    LEFT JOIN categorias_produto c ON c.id = p.categoria_id
    WHERE p.ativo = TRUE
    ORDER BY p.id;
    """
  )

  _produtos = rows or []
  _produtos_por_id = {p["id"]: p for p in _produtos}
  _tags_por_id = {p["id"]: _tokenizar_tags(p.get("tags_texto", "")) for p in _produtos}

  print(f"[IA] Recomendador treinado com {len(_produtos)} produtos.")


def _jaccard(a: set, b: set) -> float:
  if not a or not b:
    return 0.0
  inter = len(a & b)
  if inter == 0:
    return 0.0
  uni = len(a | b)
  return inter / uni


def recomendar_por_carrinho(ids_carrinho, top_n: int = 5):
  """
  Recebe lista de IDs de produtos que estão no carrinho
  e retorna uma lista de recomendações:

  [
    {"id": 10, "nome": "...", "categoria": "...", "score": 0.87},
    ...
  ]
  """
  if not isinstance(ids_carrinho, (list, tuple)):
    ids_carrinho = []

  # garante que o modelo está carregado
  if not _produtos:
    treinar_recomendador()

  # monta conjunto de tags do carrinho
  tags_carrinho = set()
  for pid in ids_carrinho:
    pid_int = int(pid) if str(pid).isdigit() else pid
    tags_carrinho |= _tags_por_id.get(pid_int, set())

  # se não tiver tag nenhuma, retorna vazio
  if not tags_carrinho:
    return []

  candidatos = []
  ids_carrinho_set = {int(x) for x in ids_carrinho if str(x).isdigit()}

  for p in _produtos:
    pid = p["id"]
    if pid in ids_carrinho_set:
      continue

    tags_prod = _tags_por_id.get(pid, set())
    score = _jaccard(tags_carrinho, tags_prod)
    if score <= 0:
      continue

    candidatos.append(
      {
        "id": pid,
        "nome": p["nome"],
        "categoria": p.get("categoria"),
        "score": float(score),
      }
    )

  # ordena do mais similar pro menos
  candidatos.sort(key=lambda x: x["score"], reverse=True)
  return candidatos[:top_n]
