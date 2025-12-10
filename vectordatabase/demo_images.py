"""
Demonstração do MultimodalDB
Busca de imagens usando texto e vice-versa
"""

from multimodal_db import MultimodalDB
import os

print("="*70)
print("🖼️  MultimodalDB - Sistema de Busca Visual")
print("="*70)
print()

# Inicializa banco
db = MultimodalDB("image_database.json")

# ============================================
# TESTE 1: Indexar pasta de imagens
# ============================================
print("📂 TESTE 1: Indexando pasta de imagens")
print("-"*70)
print("Instruções:")
print("1. Crie uma pasta chamada 'images' no diretório atual")
print("2. Adicione algumas imagens de teste (screenshots, fotos, etc.)")
print()

# Verifica se pasta existe
if os.path.exists("images"):
    stats = db.add_folder(
        "images",
        metadata={"source": "demo", "indexed_date": "2024-12-08"}
    )
else:
    print("[⚠️] Pasta 'images' não encontrada.")
    print("[ℹ️] Criando pasta de exemplo...")
    os.makedirs("images", exist_ok=True)
    print("[✅] Pasta criada! Adicione imagens e rode novamente.")
    print()

# ============================================
# TESTE 2: Estatísticas
# ============================================
db.print_stats()

# Verifica se há imagens indexadas
if db.storage.count() == 0:
    print("\n" + "="*70)
    print("⚠️  AVISO: Banco de imagens vazio!")
    print("="*70)
    print("\nPara testar o sistema:")
    print("1. Adicione imagens na pasta 'images/'")
    print("2. Execute novamente: python demo_images.py")
    print("\nExemplos de imagens que funcionam bem:")
    print("  • Capturas de tela")
    print("  • Fotos de animais")
    print("  • Gráficos e diagramas")
    print("  • Interfaces de software")
    print("  • Paisagens")
    print()
    exit(0)

# ============================================
# TESTE 3: Busca por texto
# ============================================
print("\n" + "="*70)
print("🔎 TESTE 3: Busca de imagens por texto")
print("-"*70)

queries = [
    "dog or cat",
    "chart or graph",
    "landscape or nature",
    "person or people",
    "computer or screen"
]

print("\nExemplos de queries que você pode testar:")
for i, q in enumerate(queries, 1):
    print(f"  {i}. {q}")

print("\n" + "-"*70)
print("Digite sua query (ou Enter para usar 'dog or cat'):")
user_query = input("Query: ").strip()

if not user_query:
    user_query = "dog or cat"

print(f"\n🔍 Buscando por: '{user_query}'")
print("-"*70)

results = db.search_by_text(user_query, top_k=5, min_score=0.15, verbose=False)

if results:
    print(f"\n✅ Encontrados {len(results)} resultados:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   Arquivo: {result['filename']}")
        print(f"   Caminho: {result['image_path']}")
        print(f"   Metadata: {result['metadata']}")
        print()
else:
    print("\n❌ Nenhum resultado encontrado.")
    print("Dicas:")
    print("  • Tente queries mais genéricas")
    print("  • Reduza o min_score")
    print("  • Adicione mais imagens variadas")

# ============================================
# TESTE 4: Busca por imagem similar
# ============================================
print("\n" + "="*70)
print("🖼️  TESTE 4: Busca de imagens similares")
print("-"*70)

indexed_images = db.storage.get_all_paths()

if len(indexed_images) > 0:
    reference_image = indexed_images[0]
    print(f"\nUsando como referência: {reference_image}")
    print(f"Buscando imagens similares...")
    print("-"*70)
    
    results = db.search_by_image(reference_image, top_k=3, min_score=0.3, verbose=False)
    
    if results:
        print(f"\n✅ Imagens similares encontradas:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Arquivo: {result['filename']}")
            print(f"   Caminho: {result['image_path']}")
            print()
    else:
        print("\n[ℹ️] Nenhuma imagem similar encontrada (ou banco tem apenas 1 imagem)")
else:
    print("\n[⚠️] Adicione mais imagens para testar busca por similaridade")

# ============================================
# TESTE 5: Múltiplas queries
# ============================================
print("\n" + "="*70)
print("🎯 TESTE 5: Teste rápido com múltiplas queries")
print("-"*70)

test_queries = [
    ("animal", 2),
    ("technology", 2),
    ("nature", 2),
]

for query, k in test_queries:
    results = db.search_by_text(query, top_k=k, min_score=0.15, verbose=False)
    
    if results:
        print(f"\n🔎 '{query}' → {len(results)} resultado(s)")
        for r in results:
            print(f"   • {r['filename']} (score: {r['score']:.4f})")
# ==============================================================================
# ⏬ COLOQUE ISTO NO FINAL (SUBSTITUA O TESTE 6 ATUAL) ⏬
# ==============================================================================

print("\n" + "="*70)
print("🛠️ TESTE 6: Manipulação Específica (Cenário Poste/Refri/Naruto)")
print("-" * 70)

# CORREÇÃO AQUI: Note o .jpeg no final
imgs_teste = ["poste.jpg", "refrigerante.jpeg", "naruto.jpeg"]
caminho_base = "images"

# 1. Tenta garantir que elas estão no banco
print("1️⃣  Verificando imagens de teste...")
for img in imgs_teste:
    caminho_completo = os.path.join(caminho_base, img)
    if os.path.exists(caminho_completo):
        db.add_image(caminho_completo, verbose=False)
    else:
        print(f"[❌] Faltou colocar o arquivo na pasta: {img}")

# 2. UPDATE: Atualiza o poste (que é .jpg mesmo)
print("\n2️⃣  Atualizando o Poste...")
db.update_image_info("poste.jpg", {
    "tipo": "infraestrutura", 
    "status": "verificado", 
    "obs": "poste de luz intacto"
})

# 3. DELETE: Remove Naruto e Refrigerante (agora com .jpeg)
print("\n3️⃣  Removendo o que não é desejado...")
db.remove_image("naruto.jpeg")       # <--- .jpeg aqui
db.remove_image("refrigerante.jpeg") # <--- .jpeg aqui

# 4. CONFERÊNCIA FINAL
print("\n4️⃣  Conferência:")
todas = db.storage.load()

# Verifica se o poste ficou
poste_no_banco = next((item for item in todas if item["filename"] == "poste.jpg"), None)
if poste_no_banco:
    print(f"✅ O Poste permaneceu com metadados: {poste_no_banco.get('metadata')}")

# Verifica se os outros sumiram
restos = [i for i in todas if i["filename"] in ["naruto.jpeg", "refrigerante.jpeg"]]
if not restos:
    print("✅ Naruto e Refrigerante foram eliminados com sucesso.")
else:
    print(f"❌ Ops, ainda sobraram: {[i['filename'] for i in restos]}")

print(f"\nTotal final de imagens no banco: {len(todas)}")

# ==============================================================================
# ⏫ FIM DO CÓDIGO ⏫
# ==============================================================================
print("\n" + "="*70)
print("✅ Demonstração concluída!")
print("="*70)

