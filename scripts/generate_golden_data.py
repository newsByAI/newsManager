import json
import os
from datetime import date
from chunking.chunker import DocumentChunker
from chunking.strategies.semantic import SemanticChunkingStrategy
from ingestion.models import Article

# --- Textos que usaremos para generar los chunks ---

SHORT_TEXT = (
    "La Tierra es el tercer planeta del sistema solar, un mundo oceánico con una "
    "atmósfera rica en nitrógeno y oxígeno. Su satélite natural, la Luna, "
    "estabiliza su eje de rotación y genera las mareas. A diferencia de la Tierra, "
    "Marte es un planeta desértico y frío, conocido como el Planeta Rojo. "
    "A pesar de sus diferencias, ambos planetas rocosos se encuentran en la "
    "zona habitable de nuestra estrella, el Sol."
)

LONG_TEXT = (
    "La inteligencia artificial (IA) es una de las disciplinas más fascinantes de "
    "la ciencia computacional moderna, buscando crear sistemas capaces de realizar "
    "tareas que normalmente requieren inteligencia humana. Su historia se remonta a "
    "mediados del siglo XX, con pioneros como Alan Turing sentando las bases teóricas.\n\n"
    "Dentro de la IA, el Machine Learning (ML) o aprendizaje automático es el "
    "subcampo más prominente. En lugar de ser programados explícitamente, los "
    "algoritmos de ML aprenden patrones a partir de grandes volúmenes de datos. "
    "Un ejemplo clásico es el filtro de spam en el correo electrónico, que aprende "
    "a distinguir entre mensajes legítimos y no deseados analizando millones de "
    "ejemplos previos.\n\n"
    "Una de las técnicas más poderosas del Machine Learning son las redes "
    "neuronales profundas, inspiradas en la estructura del cerebro humano. "
    "Estas redes consisten en capas de nodos o 'neuronas' interconectadas, donde "
    "cada capa aprende a detectar características cada vez más complejas. La "
    "primera capa podría reconocer bordes en una imagen, la siguiente formas "
    "simples, y las capas más profundas podrían identificar objetos completos como "
    "un rostro o un automóvil.\n\n"
    "Otro campo vital de la IA es el Procesamiento del Lenguaje Natural (PLN), "
    "que se enfoca en la interacción entre las computadoras y el lenguaje humano. "
    "Los modelos de PLN permiten a las máquinas leer texto, comprender su "
    "significado, traducir idiomas y hasta generar texto coherente por sí mismos. "
    "Los asistentes de voz como Siri o Alexa son aplicaciones comerciales exitosas "
    "del PLN, capaces de interpretar comandos hablados y responder de manera relevante."
)


def generate_golden_files():
    """
    Ejecuta el chunker semántico en los textos de prueba y guarda los resultados
    en archivos JSON para usarlos en snapshot testing.
    """
    print("🤖 Iniciando la generación de archivos 'golden' para testing...")

    today_date_str = date.today().isoformat()

    # 1. Preparar los datos de entrada
    short_article = Article(
        title="Short Article",
        content=SHORT_TEXT,
        url="http://example.com/short",
        published_at=today_date_str,
        content_preview="",
    )
    long_article = Article(
        title="Long Article",
        content=LONG_TEXT,
        url="http://example.com/long",
        published_at=today_date_str,
        content_preview="",
    )

    # 2. Instanciar el chunker (esto usará la API real de GCP)
    print("🧠 Instanciando el DocumentChunker con la estrategia semántica...")
    chunker = DocumentChunker(strategy=SemanticChunkingStrategy())

    # 3. Definir el directorio de salida y crearlo si no existe
    output_dir = os.path.join(
        os.path.dirname(__file__), "..", "tests", "data", "goldenData"
    )
    os.makedirs(output_dir, exist_ok=True)
    print(f"📂 Directorio de salida verificado: {output_dir}")

    # 4. Procesar el artículo corto
    print("Processing short article...")
    short_chunks = chunker.chunk(short_article)
    short_output_path = os.path.join(output_dir, "1-short_article_golden_data.json")
    with open(short_output_path, "w", encoding="utf-8") as f:
        json.dump(short_chunks, f, ensure_ascii=False, indent=4)
    print(f"✅ Archivo de chunks cortos guardado en: {short_output_path}")

    # 5. Procesar el artículo largo
    print("\nProcessing long article...")
    long_chunks = chunker.chunk(long_article)
    long_output_path = os.path.join(output_dir, "1-long_article_golden_data.json")
    with open(long_output_path, "w", encoding="utf-8") as f:
        json.dump(long_chunks, f, ensure_ascii=False, indent=4)
    print(f"✅ Archivo de chunks largos guardado en: {long_output_path}")

    print("\n🎉 Proceso completado.")


if __name__ == "__main__":
    # Asegúrate de que tus credenciales de GCP estén configuradas antes de ejecutar
    # gcloud auth application-default login
    generate_golden_files()
