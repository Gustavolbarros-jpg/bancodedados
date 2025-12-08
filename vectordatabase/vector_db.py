import numpy as np
from embeddings import Embeddings
from storage import Storage
from index import Index, cosine_similarity, normalize_text

class VectorDB:
    """
    VectorDB Evoluído - Versão A+
    
    Melhorias:
    - Cache em memória
    - Normalização de texto
    - Threshold dinâmico
    - Boosting de keywords
    - Suporte a metadados
    - Estatísticas do banco
    """
    
    def __init__(self, storage_path="database.json"):
        """
        Inicializa VectorDB
        
        Args:
            storage_path: Caminho do arquivo de dados
        """
        self.emb = Embeddings()
        self.store = Storage(storage_path)
        self.index = Index(self.store)
        
        print(f"[✅] VectorDB inicializado")
        print(f"[💾] Arquivo: {storage_path}\n")

    def exists_similar(self, vector, threshold=0.85):
        """
        Verifica se já existe documento similar
        
        Args:
            vector: Embedding para verificar
            threshold: Limite de similaridade (0.85 = 85% similar)
        
        Returns:
            (exists, score, text): Tupla com resultado
        """
        data = self.store.load()

        for item in data:
            v = np.array(item["embedding"])
            q = np.array(vector)
            score = cosine_similarity(q, v)

            if score >= threshold:
                return True, score, item["text"]

        return False, None, None

    def add(self, text, metadata=None, check_duplicates=True, 
            duplicate_threshold=0.85, verbose=True):
        """
        Adiciona documento ao banco
        
        Args:
            text: Texto a adicionar
            metadata: Metadados opcionais (dict)
                     Ex: {"category": "tech", "source": "manual"}
            check_duplicates: Verifica duplicatas antes de adicionar
            duplicate_threshold: Limite para considerar duplicata
            verbose: Mostra mensagens de feedback
        
        Returns:
            bool: True se adicionado, False se duplicata
        """
        # Normaliza texto para melhor qualidade
        text_normalized = normalize_text(text)
        
        # Gera embedding
        emb = self.emb.encode(text)[0]

        # Verifica duplicatas
        if check_duplicates:
            exists, score, found_text = self.exists_similar(emb, duplicate_threshold)
            
            if exists:
                if verbose:
                    print(f"[⚠️] Documento NÃO adicionado: muito parecido com algo existente.")
                    print(f"      Similaridade: {score:.4f}")
                    print(f"      Já existe:    {found_text}")
                    print(f"      Novo texto:   {text}\n")
                return False

        # Adiciona ao storage (com metadados)
        self.store.add(text, emb, metadata)
        
        # Invalida cache do índice
        self.index.invalidate_cache()
        
        if verbose:
            meta_info = f" | Metadata: {metadata}" if metadata else ""
            print(f"[✔] Adicionado: {text}{meta_info}\n")
        
        return True

    def search(self, query, top_k=3, use_dynamic_threshold=True,
               apply_boosting=True, min_relevance=0.0, verbose=True):
        """
        Busca vetorial avançada
        
        Args:
            query: Texto de busca
            top_k: Número de resultados
            use_dynamic_threshold: Usa threshold dinâmico
            apply_boosting: Aplica boosting de keywords
            min_relevance: Score mínimo de relevância
            verbose: Mostra informações da busca
        
        Returns:
            Lista de dicts com resultados
        """
        # Gera embedding da query
        emb = self.emb.encode(query)[0]
        
        # Busca usando índice avançado
        results = self.index.search(
            query_emb=emb,
            top_k=top_k,
            query_text=query,
            use_dynamic_threshold=use_dynamic_threshold,
            apply_boosting=apply_boosting,
            min_relevance=min_relevance
        )
        
        if verbose and not results:
            print(f"[ℹ️] Nenhum resultado encontrado para: '{query}'")
        
        return results
    
    def stats(self):
        """
        Retorna estatísticas do banco
        
        Returns:
            Dict com informações do banco
        """
        count = self.store.count()
        
        stats = {
            "total_documents": count,
            "embedding_dimension": self.emb.get_dimension(),
            "model_name": self.emb.get_model_name(),
            "cache_active": self.index._vectors_cache is not None
        }
        
        return stats
    
    def print_stats(self):
        """Mostra estatísticas formatadas"""
        stats = self.stats()
        
        print("\n" + "="*50)
        print("📊 ESTATÍSTICAS DO BANCO")
        print("="*50)
        print(f"Total de documentos: {stats['total_documents']}")
        print(f"Dimensão dos vetores: {stats['embedding_dimension']}")
        print(f"Modelo: {stats['model_name']}")
        print(f"Cache ativo: {'✅ Sim' if stats['cache_active'] else '❌ Não'}")
        print("="*50 + "\n")