# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: pruebas unitarias rápidas y aisladas")
    config.addinivalue_line(
        "markers",
        "integration: pruebas de integración que pueden tocar servicios externos",
    )
