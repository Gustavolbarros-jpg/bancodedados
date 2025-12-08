import math
import re
import numpy as np

def cosine_similarity(v1, v2):
    """Calcula similaridade de cosseno entre dois vetores"""
    dot = sum(a*b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(b*b for b in v2))
    return dot / (norm1 * norm2)


def normalize_text(text):
    """
    Normaliza texto para melhor qualidade de busca
    - Converte para minúsculas
    - Remove pontuação excessiva
    - Remove espaços múltiplos
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_keywords(text):
    """
    Extrai palavras-chave relevantes (para boosting)
    Remove stop words comuns
    """
    stop_words = {
        'o', 'a', 'de', 'da', 'do', 'e', 'é', 'em', 'um', 'uma', 'os', 'as',
        'para', 'com', 'por', 'no', 'na', 'dos', 'das', 'ao', 'à',
        'the', 'is', 'are', 'in', 'of', 'and', 'to', 'a', 'an'
    }
    
    words = normalize_text(text).split()
    keywords = {w for w in words if len(w) > 2 and w not in stop_words}
    return keywords


class Index:
    """
    Sistema de indexação com melhorias de qualidade:
    - Threshold dinâmico
    - Boosting de keywords
    - Cache de vetores
    """
    
    def __init__(self, storage, threshold=0.45):
        self.storage = storage
        self.threshold = threshold
        self._vectors_cache = None
        self._data_cache = None

    def _load_vectors(self):
        """Pré-carrega vetores em memória (otimização)"""
        if self._vectors_cache is not None:
            return
        
        data = self.storage.load()
        self._data_cache = data
        self._vectors_cache = [item["embedding"] for item in data]
    
    def _calculate_dynamic_threshold(self, similarities):
        """
        Calcula threshold dinâmico baseado na distribuição de scores
        Usa: média - 0.5 * desvio padrão
        """
        if not similarities:
            return self.threshold
        
        scores = np.array(similarities)
        mean = np.mean(scores)
        std = np.std(scores)
        
        # Threshold dinâmico com limites
        dynamic = max(0.2, mean - 0.5 * std)
        return min(dynamic, 0.6)  # Cap em 0.6
    
    def _apply_boosting(self, query, text, base_score):
        """
        Aplica boosting baseado em palavras-chave compartilhadas
        Aumenta score em até 15% quando há overlap semântico
        """
        query_keywords = extract_keywords(query)
        text_keywords = extract_keywords(text)
        
        if not query_keywords or not text_keywords:
            return base_score
        
        # Calcula overlap
        overlap = len(query_keywords & text_keywords)
        total = len(query_keywords | text_keywords)
        
        if total == 0:
            return base_score
        
        # Boost proporcional (até +15%)
        boost = (overlap / total) * 0.15
        return min(1.0, base_score + boost)

    def search(self, query_emb, top_k=3, query_text=None, 
               use_dynamic_threshold=True, apply_boosting=True,
               min_relevance=0.0):
        """
        Busca vetorial avançada
        
        Args:
            query_emb: Embedding da query
            top_k: Número de resultados
            query_text: Texto original da query (para boosting)
            use_dynamic_threshold: Usa threshold dinâmico
            apply_boosting: Aplica boosting de keywords
            min_relevance: Score mínimo absoluto
        
        Returns:
            Lista de tuplas (score, text, metadata)
        """
        self._load_vectors()
        data = self._data_cache
        
        if not data:
            return []
        
        # Calcula similaridades
        similarities = []
        for item in data:
            score = cosine_similarity(query_emb, item["embedding"])
            similarities.append(score)
        
        # Define threshold
        threshold = self.threshold
        if use_dynamic_threshold:
            threshold = self._calculate_dynamic_threshold(similarities)
        
        # Coleta resultados
        results = []
        seen = set()
        
        for idx, item in enumerate(data):
            text = item["text"]
            score = similarities[idx]
            
            # Aplica threshold
            if score < threshold:
                continue
            
            # Aplica relevância mínima
            if score < min_relevance:
                continue
            
            # Remove duplicatas
            text_norm = normalize_text(text)
            if text_norm in seen:
                continue
            seen.add(text_norm)
            
            # Aplica boosting se ativado e query_text disponível
            original_score = score
            if apply_boosting and query_text:
                score = self._apply_boosting(query_text, text, score)
            
            # Prepara resultado
            result = {
                'score': score,
                'text': text,
                'original_score': original_score,
                'metadata': item.get('metadata', {})
            }
            
            results.append(result)
        
        # Ordena e retorna top-k
        results.sort(reverse=True, key=lambda x: x['score'])
        return results[:top_k]
    
    def invalidate_cache(self):
        """Invalida cache (após adicionar dados)"""
        self._vectors_cache = None
        self._data_cache = None