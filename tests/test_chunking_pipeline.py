import pytest
import json
import os
from unittest.mock import patch, MagicMock
from chunking.chunker import DocumentChunker
from chunking.strategies.semantic import SemanticChunkingStrategy
from ingestion.models import Article
from datetime import date
from services.evaluation_client import ChunkingEvaluator


MINIMUM_ACCEPTABLE_SCORE = 2


# Esta función busca automáticamente todos los pares de archivos (artículo y golden data).
def find_snapshot_test_cases():
    """
    Escanea los directorios 'articles' y 'goldenData' para encontrar
    casos de prueba y los prepara para la parametrización de pytest.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    articles_dir = os.path.join(test_data_dir, "articles")
    golden_dir = os.path.join(test_data_dir, "goldenData")

    test_cases = []
    if not os.path.exists(articles_dir):
        return []

    for article_filename in os.listdir(articles_dir):
        if article_filename.endswith(".txt"):
            base_name = os.path.splitext(article_filename)[0]
            golden_filename = f"{base_name}_golden_data.json"

            article_path = os.path.join(articles_dir, article_filename)
            golden_path = os.path.join(golden_dir, golden_filename)

            # Solo añade el caso de prueba si ambos archivos existen
            if os.path.exists(golden_path):
                # Usamos pytest.param para darle un ID legible a cada prueba
                test_cases.append(pytest.param(article_path, golden_path, id=base_name))

    return test_cases


def find_all_articles():
    """Encuentra todos los archivos de artículos para pruebas que no necesitan golden data."""
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    articles_dir = os.path.join(test_data_dir, "articles")

    article_paths = []
    if not os.path.exists(articles_dir):
        return []

    for article_filename in os.listdir(articles_dir):
        if article_filename.endswith(".txt"):
            base_name = os.path.splitext(article_filename)[0]
            article_path = os.path.join(articles_dir, article_filename)
            article_paths.append(pytest.param(article_path, id=base_name))

    return article_paths


# --- PARTE 2: Las Pruebas Parametrizadas ---


@pytest.mark.integration
@pytest.mark.parametrize("article_path, golden_path", find_snapshot_test_cases())
def test_chunking_quality_against_golden_snapshot(article_path, golden_path):
    """
    Prueba CADA artículo encontrado contra su correspondiente archivo golden data.
    """
    with open(article_path, "r", encoding="utf-8") as f:
        article_content = f.read()

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_chunks = json.load(f)

    article = Article(
        content=article_content,
        title="Test Title",
        url="http://example.com",
        published_at=date.today().isoformat(),
        content_preview="",
    )

    chunker = DocumentChunker(strategy=SemanticChunkingStrategy())
    result_chunks = chunker.chunk(article)

    assert result_chunks == golden_chunks


@pytest.mark.integration
@pytest.mark.parametrize("article_path", find_all_articles())
def test_chunking_heuristics_for_quality(article_path):
    """
    Verifica las heurísticas de calidad para CADA artículo encontrado.
    """
    with open(article_path, "r", encoding="utf-8") as f:
        article_content = f.read()

    article = Article(
        content=article_content,
        title="Test Title",
        url="http://example.com",
        published_at=date.today().isoformat(),
        content_preview="",
    )

    chunker = DocumentChunker(strategy=SemanticChunkingStrategy())
    chunks = chunker.chunk(article)

    assert len(chunks) > 0, "El chunker no debería devolver una lista vacía."
    for i, chunk in enumerate(chunks):
        assert chunk.strip() != "", f"El chunk {i} está vacío."
        assert len(chunk) > 10, f"El chunk {i} es demasiado corto."


class MockLangchainDocument:
    def __init__(self, content):
        self.page_content = content


@pytest.fixture
def sample_article():
    """Fixture para crear un objeto Article de prueba."""
    today_date_str = date.today().isoformat()

    return Article(
        title="Test Title",
        content="El sol es una estrella. La luna refleja su luz. Los planetas giran alrededor del sol.",
        url="http://example.com",
        published_at=today_date_str,
        content_preview="El sol es una estrella.",
    )


@pytest.mark.unit
def test_pipeline_functional_with_mocks(sample_article):
    """
    Verifica que el pipeline completo funciona, desde DocumentChunker
    hasta la llamada al text_splitter mockeado.
    """
    # 1. Definimos la salida que esperamos de nuestro text_splitter falso
    mocked_output_docs = [
        MockLangchainDocument("El sol es una estrella."),
        MockLangchainDocument("La luna refleja su luz."),
        MockLangchainDocument("Los planetas giran alrededor del sol."),
    ]
    expected_chunks = [doc.page_content for doc in mocked_output_docs]

    # 2. Usamos 'patch' para interceptar la creación de AIClientsSingleton
    # Esto evita que se conecte a servicios reales de IA.
    with patch(
        "chunking.strategies.semantic.AIClientsSingleton"
    ) as MockAIClientsSingleton:
        # 3. Configuramos el comportamiento de nuestros mocks
        mock_ai_instance = MockAIClientsSingleton.return_value
        mock_text_splitter = MagicMock()
        mock_text_splitter.create_documents.return_value = mocked_output_docs
        mock_ai_instance.semantic_chunker = mock_text_splitter

        # 4. Ejecutamos nuestro pipeline
        strategy = SemanticChunkingStrategy()
        chunker = DocumentChunker(strategy=strategy)
        result_chunks = chunker.chunk(sample_article)

        # 5. Hacemos las aserciones (Asserts)
        # ¿Se llamó al método 'create_documents' con el contenido del artículo?
        mock_text_splitter.create_documents.assert_called_once_with(
            [sample_article.content]
        )

        # ¿El resultado final es el que esperábamos del mock?
        assert result_chunks == expected_chunks
        print("✅ Prueba unitaria del pipeline superada.")


@pytest.mark.integration
@pytest.mark.llm_eval  # Una nueva marca para poder ejecutar solo estas pruebas
@pytest.mark.parametrize("article_path", find_all_articles())
def test_llm_evaluation_of_chunking(article_path):
    """
    Prueba la calidad del chunking utilizando un LLM como juez.
    """
    print(f"\n🔬 Iniciando evaluación con LLM para: {os.path.basename(article_path)}")

    with open(article_path, "r", encoding="utf-8") as f:
        article_content = f.read()

    article = Article(
        content=article_content,
        title="Test Title",
        url="http://example.com",
        published_at=date.today().isoformat(),
        content_preview="",
    )

    # 1. Genera los chunks como lo harías normalmente
    chunker = DocumentChunker(strategy=SemanticChunkingStrategy())
    chunks_to_evaluate = chunker.chunk(article)

    # 2. Llama al servicio de evaluación
    evaluator = ChunkingEvaluator()
    evaluation_result = evaluator.evaluate_chunks(chunks_to_evaluate)

    # Imprime el resultado para una fácil depuración
    print(
        f"📝 Resultado de la Evaluación: Puntuación={evaluation_result.get('score')}, Razón='{evaluation_result.get('reasoning')}'"
    )

    # 3. Compara la puntuación con el umbral
    score = evaluation_result.get("score", 0)
    reasoning = evaluation_result.get("reasoning", "No se proporcionó una razón.")

    assert score >= MINIMUM_ACCEPTABLE_SCORE, (
        f"La evaluación del LLM no superó el umbral de {MINIMUM_ACCEPTABLE_SCORE}. "
        f"Puntuación recibida: {score}. Razón: '{reasoning}'"
    )
