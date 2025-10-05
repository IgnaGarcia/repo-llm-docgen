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

import repo_reader


def read_file(file_path: str) -> str:
    try:
        content = repo_reader.get_file_content(file_path)
        return f"Contenido de {file_path}:\nSTART\n{content}\nEND"
    except Exception as e:
        return f"ERROR({e}). Por favor, elige una ruta de la estructura de archivos provista."


AVAILABLE_TOOLS = {
    "read_file": read_file,
}


class LLMManager:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def process_documentation_request(self, prompt: str) -> str:

        messages = [types.Content(role="user", parts=[types.Part.from_text(prompt)])]
        args_calls = []
        keep_calling = True

        while keep_calling:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=list(AVAILABLE_TOOLS.values())
                ),
            )

            if response.function_calls:
                messages.append(response.candidates[0].content)

                tool_results = []
                for fc in response.function_calls:
                    function_name = fc.name
                    args = dict(fc.args)
                    if args[0] in args_calls:
                        print(
                            f"\nLLM solicitó la función: {function_name} con argumentos {args} nuevamente"
                        )
                        keep_calling = False
                        break
                    args_calls.append(args[0])

                    function_to_call = AVAILABLE_TOOLS.get(function_name)
                    if function_to_call:
                        print(
                            f"\nLLM solicitó la función: {function_name} con argumentos: {args}"
                        )

                        result = function_to_call(**args)
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
                messages.append(types.Content(role="tool", parts=tool_results))
            else:
                return response.text
        return "Límite de llamadas a herramientas excedido. Respuesta parcial o error."
