# main.py
from chunking.strategies.strategy_i import SemanticChunkingStrategy  


def main():
    
    strategy = SemanticChunkingStrategy()

    text = """
    La inteligencia artificial está transformando la industria.
    Empresas como Google, OpenAI y Anthropic están impulsando el desarrollo
    de modelos de lenguaje cada vez más potentes.
    Estos modelos tienen aplicaciones en múltiples campos, desde la atención al cliente
    hasta la creación de contenido.
    Sin embargo, también plantean desafíos éticos y de privacidad que deben abordarse.
    La regulación y la supervisión serán clave para garantizar un uso responsable de esta tecnología.
    
    El futbol es el deporte más popular del mundo.
    Equipos como el Real Madrid, Barcelona y Manchester United tienen millones de seguidores.
    La Copa del Mundo es el evento deportivo más visto a nivel global.
    Jugadores como Lionel Messi, Cristiano Ronaldo y Neymar son íconos mundiales.
    """
    
    results = strategy.chunk(text)
    print(results)

if __name__ == "__main__":
    main()
