from sentence_transformers import SentenceTransformer

class Embeddings:
    """
    Geração de embeddings com modelo otimizado para busca semântica
    Usa: BAAI/bge-small-en-v1.5 (excelente para retrieval)
    """
    
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        """
        Inicializa modelo de embeddings
        
        Args:
            model_name: Nome do modelo (padrão: BAAI/bge-small-en-v1.5)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"[📦] Modelo carregado: {model_name}")
        print(f"[📏] Dimensão dos embeddings: {self.dimension}")

    def encode(self, text, normalize=True):
        """
        Gera embeddings para texto(s)
        
        Args:
            text: String ou lista de strings
            normalize: Normaliza vetores (recomendado para cosseno)
        
        Returns:
            Lista de vetores (mesmo se input for string única)
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(
            text, 
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )
        
        return embeddings.tolist()
    
    def get_dimension(self):
        """Retorna dimensão dos vetores"""
        return self.dimension
    
    def get_model_name(self):
        """Retorna nome do modelo atual"""
        return self.model_name