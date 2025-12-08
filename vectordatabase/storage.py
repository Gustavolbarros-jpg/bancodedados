import json
import os

class Storage:
    """
    Storage com cache em memória e suporte a metadados
    """
    def __init__(self, path="database.json"):
        self.path = path
        self._cache = None  # Cache em memória
        self._cache_loaded = False
        
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump([], f)

    def load(self):
        """Carrega dados (com cache)"""
        if self._cache_loaded:
            return self._cache
        
        with open(self.path, "r", encoding="utf-8") as f:
            self._cache = json.load(f)
            self._cache_loaded = True
            return self._cache

    def save(self, data):
        """Salva dados e atualiza cache"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self._cache = data
        self._cache_loaded = True

    def add(self, text, embedding, metadata=None):
        """
        Adiciona documento com metadados opcionais
        
        Args:
            text: Texto do documento
            embedding: Vetor de embedding
            metadata: Dict com metadados (ex: {"category": "tech", "source": "manual"})
        """
        data = self.load()
        
        record = {
            "text": text,
            "embedding": embedding
        }
        
        # Adiciona metadados se fornecidos
        if metadata:
            record["metadata"] = metadata
        
        data.append(record)
        self.save(data)
    
    def clear_cache(self):
        """Força recarregamento na próxima leitura"""
        self._cache_loaded = False
        self._cache = None
    
    def count(self):
        """Retorna número de documentos"""
        return len(self.load())
    

    # ... (código anterior da classe MultimodalDB)

    def remove_image(self, filename):
        """Remove imagem do banco"""
        success = self.storage.delete(filename)
        if success:
            self._invalidate_cache() # Importante: limpa memória antiga
            print(f"[🗑️] Imagem removida com sucesso: {filename}")
        else:
            print(f"[⚠️] Imagem não encontrada para remoção: {filename}")
        return success

    def update_image_info(self, filename, extra_metadata):
        """Atualiza informações (tags, descrição) da imagem"""
        success = self.storage.update_metadata(filename, extra_metadata)
        if success:
            self._invalidate_cache()
            print(f"[✏️] Metadados atualizados para: {filename}")
        else:
            print(f"[⚠️] Erro ao atualizar: {filename}")
        return success