# backend/db.py
from urllib.parse import urlparse
import ssl
import pg8000
from config import Config


def _parse_db_url():
    """
    Lê a URL do Supabase no .env (SUPABASE_DB_URL) e converte
    em parâmetros para o pg8000.
    Exemplo:
    postgresql://postgres:SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
    """
    url = Config.DB_URL
    if not url:
        raise RuntimeError("SUPABASE_DB_URL não definida no .env")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise RuntimeError(f"Erro ao fazer urlparse da SUPABASE_DB_URL: {url} -> {e}")

    ctx = ssl.create_default_context()
    # Em ambiente local, desligamos a validação do certificado
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return {
        "host": parsed.hostname,
        "port": parsed.port or 6543,
        "database": parsed.path.lstrip("/") or "postgres",
        "user": parsed.username,
        "password": parsed.password,
        "ssl_context": ctx,
    }


def get_connection():
    params = _parse_db_url()
    conn = pg8000.connect(**params)
    return conn


def fetch_all(query: str, params=None):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        print(f"[DB] Erro em fetch_all: {e}")
        return []
    finally:
        if conn:
            conn.close()


def fetch_one(query: str, params=None):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        row = cur.fetchone()
        if not row:
            return None
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))
    except Exception as e:
        print(f"[DB] Erro em fetch_one: {e}")
        return None
    finally:
        if conn:
            conn.close()


def execute(query: str, params=None):
    """Executa um único INSERT/UPDATE/DELETE."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] Erro em execute: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def execute_many(query: str, seq_params):
    """
    Executa vários INSERTs/UPDATEs de uma vez (usado para CSV).
    seq_params é uma lista de tuplas com os parâmetros.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.executemany(query, seq_params)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] Erro em execute_many: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
