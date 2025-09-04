# conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: Unit tests that do not require external services"
    )
    config.addinivalue_line(
        "markers",
        "integration: Testing for integration with external services",
    )
    config.addinivalue_line(
        "markers",
        "llm_eval: LLM judge for chunking quality",
    )
