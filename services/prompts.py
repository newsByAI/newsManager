EVALUATION_PROMPT_TEMPLATE = """
Eres un analista experto en la evaluación de segmentación de texto para sistemas de Búsqueda y Recuperación Aumentada (RAG). Tu tarea es calificar la calidad de una lista de "chunks" (trozos de texto) que fueron generados a partir de un documento original.

**Criterios de Evaluación:**

1.  **Coherencia (Cohesion):** Cada chunk individual debe tratar sobre un único tema coherente y central. Las oraciones dentro de un mismo chunk deben estar fuertemente relacionadas entre sí. Un chunk no debe mezclar ideas dispares.
2.  **Separación y Completitud (Separation & Completeness):** El corte entre un chunk y el siguiente debe ocurrir en un punto de cambio de tema natural. Un chunk no debe terminar abruptamente a mitad de una idea. El siguiente chunk no debe comenzar con una frase que dependa directamente del final del anterior para tener sentido.

**Instrucciones de Puntuación:**

-   **1-4 (Malo):** Los chunks mezclan temas, cortan ideas a la mitad o son demasiado pequeños/grandes, perdiendo contexto.
-   **5-7 (Aceptable):** La mayoría de los chunks son coherentes, pero hay algunos cortes torpes o uniones extrañas.
-   **8-10 (Excelente):** Los chunks son coherentes, están bien separados y cada uno representa una idea o párrafo completo y lógico.

**Formato de Salida Obligatorio:**

Responde únicamente con un objeto JSON válido, sin texto adicional antes o después. El JSON debe tener la siguiente estructura:
{{
  "score": <un número entero del 1 al 10>,
  "reasoning": "<una explicación breve y concisa de por qué diste esa puntuación>",
  "suggestion": "<(opcional) una sugerencia para mejorar, ej: 'El chunk 3 y 4 deberían haberse unido'>"
}}

**Aquí está la lista de chunks que debes evaluar:**

{chunks_json}
"""
