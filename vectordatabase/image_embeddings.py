"""
Image Embeddings usando CLIP (OpenAI)
Gera embeddings visuais e permite busca texto→imagem
"""

import torch
from PIL import Image
import open_clip
import numpy as np

class ImageEmbeddings:
    """
    Geração de embeddings para imagens usando CLIP
    Permite busca multimodal (texto ↔ imagem)
    """
    
    def __init__(self, model_name="ViT-B-32", pretrained="openai"):
        """
        Inicializa modelo CLIP
        
        Args:
            model_name: Arquitetura do CLIP (ViT-B-32 é bom custo-benefício)
            pretrained: Dataset de treinamento (openai é padrão)
        """
        print(f"[🖼️] Carregando modelo CLIP: {model_name}...")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, 
            pretrained=pretrained
        )
        
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Dimensão dos embeddings do CLIP ViT-B-32
        self.dimension = 512
        
        print(f"[✅] CLIP carregado | Device: {self.device} | Dimensão: {self.dimension}")
    
    def encode_image(self, image_path, normalize=True):
        """
        Gera embedding para uma imagem
        
        Args:
            image_path: Caminho para arquivo de imagem
            normalize: Normaliza vetor (recomendado)
        
        Returns:
            Numpy array com embedding
        """
        try:
            # Carrega e preprocessa imagem
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Gera embedding
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                
                if normalize:
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()[0]
        
        except Exception as e:
            print(f"[❌] Erro ao processar imagem {image_path}: {e}")
            return None
    
    def encode_text(self, text, normalize=True):
        """
        Gera embedding para texto (para busca texto→imagem)
        
        Args:
            text: Texto de busca
            normalize: Normaliza vetor
        
        Returns:
            Numpy array com embedding
        """
        try:
            # Tokeniza texto
            text_input = self.tokenizer([text]).to(self.device)
            
            # Gera embedding
            with torch.no_grad():
                text_features = self.model.encode_text(text_input)
                
                if normalize:
                    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features.cpu().numpy()[0]
        
        except Exception as e:
            print(f"[❌] Erro ao processar texto '{text}': {e}")
            return None
    
    def encode_batch_images(self, image_paths, normalize=True):
        """
        Processa múltiplas imagens de uma vez (mais eficiente)
        
        Args:
            image_paths: Lista de caminhos de imagens
            normalize: Normaliza vetores
        
        Returns:
            Lista de embeddings
        """
        embeddings = []
        
        for path in image_paths:
            emb = self.encode_image(path, normalize)
            if emb is not None:
                embeddings.append(emb)
        
        return embeddings
    
    def similarity(self, emb1, emb2):
        """
        Calcula similaridade de cosseno entre dois embeddings
        
        Args:
            emb1: Primeiro embedding
            emb2: Segundo embedding
        
        Returns:
            Score de similaridade (0-1)
        """
        return float(np.dot(emb1, emb2))
    
    def get_dimension(self):
        """Retorna dimensão dos embeddings"""
        return self.dimension