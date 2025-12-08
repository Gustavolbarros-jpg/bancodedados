"""
Storage especializado para imagens
Armazena embeddings e metadados de imagens
"""

import json
import os
from pathlib import Path

class ImageStorage:
    """
    Armazenamento de embeddings de imagens
    Similar ao Storage textual, mas adaptado para imagens
    """
    
    def __init__(self, filepath="image_database.json"):
        """
        Inicializa storage de imagens
        
        Args:
            filepath: Caminho do arquivo JSON
        """
        self.filepath = filepath
        self._cache = None
        self._cache_loaded = False
        
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([], f)
    
    def load(self):
        """Carrega dados (com cache)"""
        if self._cache_loaded:
            return self._cache
        
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
                self._cache_loaded = True
                return self._cache
        except FileNotFoundError:
            self._cache = []
            self._cache_loaded = True
            return []
    
    def save(self, data):
        """Salva dados e atualiza cache"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._cache = data
        self._cache_loaded = True
    
    def add(self, image_path, embedding, metadata=None):
        """
        Adiciona imagem ao banco
        
        Args:
            image_path: Caminho da imagem
            embedding: Vetor de embedding visual
            metadata: Metadados opcionais
                     Ex: {"type": "screenshot", "date": "2024-12-08", 
                          "description": "gráfico de vendas"}
        """
        data = self.load()
        
        # Converte caminho para relativo se possível
        try:
            path_obj = Path(image_path)
            relative_path = str(path_obj.relative_to(Path.cwd()))
        except ValueError:
            relative_path = image_path
        
        record = {
            "image_path": relative_path,
            "absolute_path": os.path.abspath(image_path),
            "filename": os.path.basename(image_path),
            "embedding": embedding if isinstance(embedding, list) else embedding.tolist()
        }
        
        if metadata:
            record["metadata"] = metadata
        
        data.append(record)
        self.save(data)
    
    def exists(self, image_path):
        """
        Verifica se imagem já foi indexada
        
        Args:
            image_path: Caminho da imagem
        
        Returns:
            bool: True se existe
        """
        data = self.load()
        abs_path = os.path.abspath(image_path)
        
        for item in data:
            if item.get("absolute_path") == abs_path:
                return True
        
        return False
    
    def clear_cache(self):
        """Força recarregamento"""
        self._cache_loaded = False
        self._cache = None
    
    def count(self):
        """Retorna número de imagens indexadas"""
        return len(self.load())
    
    def get_all_paths(self):
        """Retorna lista de todos os caminhos de imagens"""
        data = self.load()
        return [item["image_path"] for item in data]
    def delete(self, filename):
        """Remove um registro pelo nome do arquivo"""
        data = self.load()
        initial_count = len(data)
        
        # Filtra a lista removendo o item com aquele filename
        new_data = [item for item in data if item["filename"] != filename]
        
        if len(new_data) < initial_count:
            self.save(new_data)
            return True
        return False

    def update_metadata(self, filename, new_metadata):
        """Atualiza os metadados de uma imagem específica"""
        data = self.load()
        updated = False
        
        for item in data:
            if item["filename"] == filename:
                # Atualiza ou cria chaves de metadados
                if "metadata" not in item:
                    item["metadata"] = {}
                item["metadata"].update(new_metadata)
                updated = True
                break
        
        if updated:
            self.save(data)
            return True
        return False