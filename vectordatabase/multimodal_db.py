"""
MultimodalDB - Busca vetorial para imagens
Permite buscar imagens usando texto e vice-versa
"""

import numpy as np
from image_embeddings import ImageEmbeddings
from image_storage import ImageStorage
import os
from pathlib import Path

def cosine_similarity(v1, v2):
    """Calcula similaridade de cosseno"""
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


class MultimodalDB:
    """
    Banco de dados multimodal para imagens
    
    Funcionalidades:
    - Indexar imagens de uma pasta
    - Buscar imagens por texto
    - Buscar imagens similares
    - Metadados customizáveis
    """
    
    def __init__(self, storage_path="image_database.json"):
        """
        Inicializa MultimodalDB
        
        Args:
            storage_path: Caminho do arquivo de dados
        """
        self.clip = ImageEmbeddings()
        self.storage = ImageStorage(storage_path)
        self._vectors_cache = None
        self._data_cache = None
        
        print(f"[✅] MultimodalDB inicializado")
        print(f"[💾] Arquivo: {storage_path}\n")
    
    def _load_vectors(self):
        """Pré-carrega vetores em memória"""
        if self._vectors_cache is not None:
            return
        
        data = self.storage.load()
        self._vectors_cache = [np.array(item["embedding"]) for item in data]
        self._data_cache = data
    
    def _invalidate_cache(self):
        """Invalida cache"""
        self._vectors_cache = None
        self._data_cache = None
    
    def add_image(self, image_path, metadata=None, skip_if_exists=True, verbose=True):
        """
        Adiciona imagem ao banco
        
        Args:
            image_path: Caminho da imagem
            metadata: Metadados opcionais
            skip_if_exists: Pula se já indexada
            verbose: Mostra mensagens
        
        Returns:
            bool: True se adicionada
        """
        # Verifica se já existe
        if skip_if_exists and self.storage.exists(image_path):
            if verbose:
                print(f"[⚠️] Já indexada: {os.path.basename(image_path)}")
            return False
        
        # Gera embedding
        embedding = self.clip.encode_image(image_path)
        
        if embedding is None:
            if verbose:
                print(f"[❌] Erro ao processar: {image_path}")
            return False
        
        # Adiciona ao storage
        self.storage.add(image_path, embedding, metadata)
        self._invalidate_cache()
        
        if verbose:
            meta_info = f" | {metadata}" if metadata else ""
            print(f"[✔] Indexada: {os.path.basename(image_path)}{meta_info}")
        
        return True
    
    def add_folder(self, folder_path, extensions=None, metadata=None, verbose=True):
        """
        Indexa todas as imagens de uma pasta
        
        Args:
            folder_path: Caminho da pasta
            extensions: Lista de extensões (padrão: jpg, jpeg, png, bmp, webp)
            metadata: Metadados para todas as imagens
            verbose: Mostra progresso
        
        Returns:
            Dict com estatísticas
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif']
        
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"[❌] Pasta não encontrada: {folder_path}")
            return {"added": 0, "skipped": 0, "errors": 0}
        
        # Coleta imagens
        image_files = []
        for ext in extensions:
            image_files.extend(folder.glob(f"*{ext}"))
            image_files.extend(folder.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"[⚠️] Nenhuma imagem encontrada em: {folder_path}")
            return {"added": 0, "skipped": 0, "errors": 0}
        
        if verbose:
            print(f"\n[📂] Indexando {len(image_files)} imagens de: {folder_path}")
            print("-" * 60)
        
        stats = {"added": 0, "skipped": 0, "errors": 0}
        
        for img_path in image_files:
            added = self.add_image(str(img_path), metadata, verbose=verbose)
            
            if added:
                stats["added"] += 1
            elif self.storage.exists(str(img_path)):
                stats["skipped"] += 1
            else:
                stats["errors"] += 1
        
        if verbose:
            print("-" * 60)
            print(f"[📊] Resumo: {stats['added']} adicionadas | "
                  f"{stats['skipped']} puladas | {stats['errors']} erros\n")
        
        return stats
    
    def search_by_text(self, query, top_k=5, min_score=0.0, verbose=True):
        """
        Busca imagens usando texto
        
        Args:
            query: Texto de busca (ex: "gráfico de vendas", "cachorro")
            top_k: Número de resultados
            min_score: Score mínimo
            verbose: Mostra informações
        
        Returns:
            Lista de resultados
        """
        self._load_vectors()
        
        if not self._vectors_cache:
            if verbose:
                print("[⚠️] Banco vazio. Adicione imagens primeiro.")
            return []
        
        # Gera embedding do texto
        text_embedding = self.clip.encode_text(query)
        
        if text_embedding is None:
            return []
        
        # Calcula similaridades
        results = []
        
        for vec, data in zip(self._vectors_cache, self._data_cache):
            score = cosine_similarity(text_embedding, vec)
            
            if score < min_score:
                continue
            
            results.append({
                "score": float(score),
                "image_path": data["image_path"],
                "filename": data["filename"],
                "metadata": data.get("metadata", {})
            })
        
        # Ordena e retorna top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def search_by_image(self, image_path, top_k=5, min_score=0.0, verbose=True):
        """
        Busca imagens similares
        
        Args:
            image_path: Caminho da imagem de referência
            top_k: Número de resultados
            min_score: Score mínimo
            verbose: Mostra informações
        
        Returns:
            Lista de resultados
        """
        self._load_vectors()
        
        if not self._vectors_cache:
            if verbose:
                print("[⚠️] Banco vazio.")
            return []
        
        # Gera embedding da imagem
        query_embedding = self.clip.encode_image(image_path)
        
        if query_embedding is None:
            return []
        
        # Calcula similaridades
        results = []
        query_abs = os.path.abspath(image_path)
        
        for vec, data in zip(self._vectors_cache, self._data_cache):
            # Pula a própria imagem
            if data.get("absolute_path") == query_abs:
                continue
            
            score = cosine_similarity(query_embedding, vec)
            
            if score < min_score:
                continue
            
            results.append({
                "score": float(score),
                "image_path": data["image_path"],
                "filename": data["filename"],
                "metadata": data.get("metadata", {})
            })
        
        # Ordena e retorna top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def stats(self):
        """Retorna estatísticas do banco"""
        return {
            "total_images": self.storage.count(),
            "embedding_dimension": self.clip.get_dimension(),
            "cache_active": self._vectors_cache is not None,
            "indexed_images": self.storage.get_all_paths()
        }
    
    def print_stats(self):
        """Mostra estatísticas formatadas"""
        stats = self.stats()
        
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS DO BANCO DE IMAGENS")
        print("="*60)
        print(f"Total de imagens: {stats['total_images']}")
        print(f"Dimensão dos vetores: {stats['embedding_dimension']}")
        print(f"Cache ativo: {'✅ Sim' if stats['cache_active'] else '❌ Não'}")
        print("="*60 + "\n")

    # =========================================================================
    #  NOVAS FUNÇÕES ADICIONADAS PARA MANIPULAÇÃO (UPDATE / DELETE)
    # =========================================================================

    def remove_image(self, filename):
        """Remove imagem do banco"""
        success = self.storage.delete(filename)
        if success:
            self._invalidate_cache()
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