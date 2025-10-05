"""
conexion con el modelo
interfaz para enviar prompts y recibir respuestas

build prompt
read output documentation language selection
count request tokens
count response tokens
"""

import os
from google import genai
from google.genai import types
from typing import Dict, Any, List

# --- La función que queremos que el LLM pueda llamar ---


def read_file(file_path: str) -> str:
    """
    Lee y retorna el contenido completo de un archivo de código del repositorio.
    Útil cuando se necesita entender el detalle de una implementación.

    Args:
        file_path: La ruta relativa del archivo de código a leer (ej. "src/auth/service.py").

    Returns:
        El contenido del archivo como una cadena de texto, o un mensaje de error si no existe.
    """
    # Nota: Aquí se simula la lectura. En tu proyecto, esta función
    # usaría Pathlib/os para leer el archivo del disco.

    # SIMULACIÓN: Aquí deberías tener una lista de archivos y su contenido.
    simulated_repo_files = {
        "src/config.py": "# Código de configuración de la API...",
        "src/models/user.py": "class User: # Definición del modelo de usuario...",
        "lambda/go/GetTransactionTypeService/cmd/main.go": "// Código Go que el LLM podría solicitar.",
        "common/pkg/utils/utils.go": "package utils\n// Contenido de las utilidades que el LLM podría querer ver.",
    }

    if file_path in simulated_repo_files:
        return f"Contenido de {file_path}:\n---\n{simulated_repo_files[file_path]}\n---"
    else:
        # Importante: Si la ruta es inválida, devuelve un error claro.
        return f"ERROR: Archivo no encontrado en el repositorio: {file_path}. Por favor, elige una ruta de la estructura de archivos provista."


# --- Mapeo de funciones disponibles para el LLM ---
AVAILABLE_TOOLS = {
    "read_file": read_file,
}

# --- Estructura Singleton (simplificada) ---


class LLMManager:
    """
    Clase para manejar la conexión y la lógica de Function Calling.
    (Asume que el patrón Singleton Meta ya fue implementado).
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def process_documentation_request(
        self, prompt: str, repo_structure: str, tools: Dict[str, callable]
    ) -> str:

        # 2. Iniciar la conversación (loop de llamadas a herramientas)
        messages = [
            types.Content(role="user", parts=[types.Part.from_text(full_prompt)])
        ]

        # Limita el número de llamadas a herramientas para evitar loops infinitos
        max_tool_calls = 5

        for i in range(max_tool_calls):
            # Llamada inicial o de loop con todas las herramientas disponibles
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=types.GenerateContentConfig(tools=list(tools.values())),
            )

            # 3. Analizar la respuesta del LLM
            if response.function_calls:
                # El LLM decidió llamar a una o más herramientas (Tools)
                messages.append(
                    response.candidates[0].content
                )  # Añade la petición de la función

                tool_results = []
                for fc in response.function_calls:
                    function_name = fc.name
                    args = dict(fc.args)

                    # Ejecuta la función real de Python
                    function_to_call = tools.get(function_name)
                    if function_to_call:
                        print(
                            f"\n🤖 LLM solicitó la función: {function_name} con argumentos: {args}"
                        )

                        # Ejecución real de la función (el RAG dinámico)
                        result = function_to_call(**args)

                        # Añade el resultado de la función al historial de mensajes
                        tool_results.append(
                            types.Part.from_function_response(
                                name=function_name, response={"content": result}
                            )
                        )
                    else:
                        tool_results.append(
                            types.Part.from_text(
                                f"Error: Función {function_name} no disponible."
                            )
                        )

                # Añade el resultado de la herramienta al historial (para la siguiente iteración)
                messages.append(types.Content(role="tool", parts=tool_results))

            else:
                # El LLM respondió con la respuesta final (no llamó a más herramientas)
                return response.text

        return (
            "⚠️ Límite de llamadas a herramientas excedido. Respuesta parcial o error."
        )


if __name__ == "__main__":
    # Simulación de tu contexto de proyecto (la estructura de archivos que GitPython provee)
    REPO_STRUCTURE_EXAMPLE = """
    .
    ├── src/
    │   ├── config.py
    │   └── models/
    │       └── user.py
    └── lambda/
        └── go/
            └── GetTransactionTypeService/
                └── cmd/
                    └── main.go
    """

    # 1. Inicializar (con la API Key real)
    # Reemplaza con tu clave
    API_KEY = os.getenv("GEMINI_API_KEY", "TU_CLAVE_AQUI")
    if API_KEY == "TU_CLAVE_AQUI":
        print(
            "❌ Por favor, establece la variable de entorno GEMINI_API_KEY o reemplaza 'TU_CLAVE_AQUI'."
        )
    else:
        llm_manager = LLMManager(api_key=API_KEY)

        # Tarea que requiere que el LLM lea código
        user_task = "Explica cómo se maneja la inicialización de la base de datos o servicios de persistencia en el proyecto, buscando en los archivos de configuración y servicio."

        print("\n--- INICIO DE PROCESAMIENTO DINÁMICO ---")

        final_documentation = llm_manager.process_documentation_request(
            prompt=user_task,
            repo_structure=REPO_STRUCTURE_EXAMPLE,
            tools=AVAILABLE_TOOLS,
        )

        print("\n--- DOCUMENTACIÓN FINAL GENERADA ---")
        print(final_documentation)
