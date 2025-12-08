from embeddings import Embeddings

emb = Embeddings()

texto = "Gustavo está criando um vector database do zero!"
vetor = emb.encode(texto)

print("TEXTO:", texto)
print("VETOR (dimensão:", len(vetor[0]), "):")
print(vetor)
