"""Valida que los model IDs de Gemini existan y sean accesibles con la API key configurada.

Uso:
    python scripts/validate_models.py [model_id ...]

Si no se pasan argumentos, valida los modelos por defecto (condenser/documenter actuales).
No genera contenido: solo consulta metadata del modelo (client.models.get), para no
consumir cuota de generación innecesariamente.
"""
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

DEFAULT_MODELS = ["gemini-3.7-flash", "gemini-3.6-flash"]


def validate_model(client, model_id):
    try:
        info = client.models.get(model=model_id)
        methods = getattr(info, "supported_actions", None)
        print(f"OK   {model_id}  (display_name={getattr(info, 'display_name', '?')}, supported_actions={methods})")
        return True
    except genai_errors.ClientError as e:
        print(f"FAIL {model_id}  -> {e}")
        return False
    except Exception as e:
        print(f"FAIL {model_id}  -> {type(e).__name__}: {e}")
        return False


def main():
    load_dotenv("./config/.env")
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("No se encontro API_KEY en config/.env")
        sys.exit(1)

    models = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_MODELS

    client = genai.Client(api_key=api_key)

    results = [validate_model(client, m) for m in models]

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
