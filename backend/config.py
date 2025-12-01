import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Usando URL completa do Supabase
    DB_URL = os.getenv("SUPABASE_DB_URL")

    # Se quiser usar os campos separados (opcional)
    DB_HOST = os.getenv("SUPABASE_DB_HOST")
    DB_PORT = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    DB_USER = os.getenv("SUPABASE_DB_USER")
    DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    DB_NAME = os.getenv("SUPABASE_DB_NAME")
