import json
import re  # Importamos el módulo de expresiones regulares
from typing import List, Dict
from langchain_google_vertexai import VertexAI

# Asegúrate de que este import sea correcto para tu estructura
from .prompts import EVALUATION_PROMPT_TEMPLATE


class ChunkingEvaluator:
    """
    Este servicio utiliza un LLM para evaluar la calidad de una lista de chunks.
    """

    def __init__(self):
        # Usamos un modelo estable y universalmente disponible
        self.llm = VertexAI(model_name="gemini-2.5-flash", temperature=0.1)

    def evaluate_chunks(self, chunks: List[str]) -> Dict:
        """
        Envía los chunks a un LLM para su evaluación, limpia la respuesta y
        devuelve el resultado JSON.
        """
        chunks_as_json_string = json.dumps(chunks, indent=2, ensure_ascii=False)
        prompt = EVALUATION_PROMPT_TEMPLATE.format(chunks_json=chunks_as_json_string)

        raw_response = ""
        try:
            raw_response = self.llm.invoke(prompt)

            # --- NUEVA LÓGICA DE LIMPIEZA ---
            # Buscamos un bloque JSON dentro de la respuesta usando una expresión regular.
            # Esto es robusto contra los bloques de código Markdown ```json ... ```
            match = re.search(r"\{[\s\S]*\}", raw_response)

            if match:
                json_string = match.group(0)
                evaluation = json.loads(json_string)
                return evaluation
            else:
                # Si no se encuentra ningún JSON, fallamos con un mensaje claro.
                raise ValueError(
                    "No se encontró un objeto JSON válido en la respuesta del LLM."
                )

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Error al parsear la respuesta del LLM: {e}")
            print(f"Respuesta recibida:\n---\n{raw_response}\n---")
            return {
                "score": 0,
                "reasoning": "La respuesta del LLM no fue un JSON válido o estaba mal formada.",
                "suggestion": "",
            }
