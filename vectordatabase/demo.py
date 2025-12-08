from vector_db import VectorDB

print("="*60)
print("🚀 VectorDB - Versão A+ (Evoluído)")
print("="*60)
print()

# Inicializa banco
db = VectorDB("database_evolved.json")

# ============================================
# TESTE 1: Adicionar documentos com metadados
# ============================================
print("📝 TESTE 1: Adicionando documentos com metadados")
print("-"*60)

documents = [
    ("Gatos são animais independentes e adoram explorar.", {"category": "animal", "type": "pet"}),
    ("Cachorros são leais e protetores.", {"category": "animal", "type": "pet"}),
    ("Python é usado em inteligência artificial.", {"category": "tech", "type": "language"}),
    ("Java é focado em orientação a objetos.", {"category": "tech", "type": "language"}),
    ("Cavalos são animais majestosos usados em esportes.", {"category": "animal", "type": "sport"}),
    ("JavaScript é essencial para desenvolvimento web.", {"category": "tech", "type": "language"}),
]

for text, meta in documents:
    db.add(text, metadata=meta)

# ============================================
# TESTE 2: Detecção de duplicatas
# ============================================
print("\n" + "="*60)
print("🔍 TESTE 2: Detecção inteligente de duplicatas")
print("-"*60)

duplicates = [
    "Gatos são animais muito independentes.",  # Similar ao primeiro
    "Python é usado para IA.",  # Similar ao terceiro
]

for dup in duplicates:
    print(f"Tentando adicionar: '{dup}'")
    db.add(dup)

# ============================================
# TESTE 3: Busca simples (modo compatível)
# ============================================
print("\n" + "="*60)
print("🔎 TESTE 3: Busca simples (compatível com versão A)")
print("-"*60)

query = "animais domésticos"
print(f"Query: '{query}'\n")

results = db.search(query, top_k=2, verbose=False)

for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.4f} | {result['text']}")
    print(f"   Metadata: {result['metadata']}\n")

# ============================================
# TESTE 4: Busca avançada com threshold dinâmico
# ============================================
print("\n" + "="*60)
print("🎯 TESTE 4: Busca com threshold dinâmico")
print("-"*60)

query = "programação moderna"
print(f"Query: '{query}'\n")

results = db.search(
    query, 
    top_k=3,
    use_dynamic_threshold=True,
    apply_boosting=True,
    verbose=False
)

for i, result in enumerate(results, 1):
    boost_diff = result['score'] - result['original_score']
    boost_info = f" (+{boost_diff:.4f} boost)" if boost_diff > 0 else ""
    
    print(f"{i}. Score: {result['score']:.4f}{boost_info}")
    print(f"   Texto: {result['text']}")
    print(f"   Metadata: {result['metadata']}\n")

# ============================================
# TESTE 5: Busca com filtro de relevância
# ============================================
print("\n" + "="*60)
print("⚡ TESTE 5: Busca com filtro de relevância mínima")
print("-"*60)

query = "pets e companheiros"
print(f"Query: '{query}'")
print(f"Relevância mínima: 0.35\n")

results = db.search(
    query,
    top_k=5,
    min_relevance=0.35,
    verbose=False
)

for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.4f} | {result['text']}")

# ============================================
# TESTE 6: Estatísticas do banco
# ============================================
print("\n" + "="*60)
db.print_stats()

# ============================================
# TESTE 7: Comparação com/sem boosting
# ============================================
print("="*60)
print("📊 TESTE 7: Comparação - Boosting ON vs OFF")
print("-"*60)

query = "linguagens de programação web"
print(f"Query: '{query}'\n")

print("🔴 SEM Boosting:")
results_no_boost = db.search(query, top_k=3, apply_boosting=False, verbose=False)
for i, r in enumerate(results_no_boost, 1):
    print(f"   {i}. Score: {r['score']:.4f} | {r['text'][:50]}...")

print("\n🟢 COM Boosting:")
results_with_boost = db.search(query, top_k=3, apply_boosting=True, verbose=False)
for i, r in enumerate(results_with_boost, 1):
    boost = r['score'] - r['original_score']
    print(f"   {i}. Score: {r['score']:.4f} (+{boost:.4f}) | {r['text'][:50]}...")

print("\n" + "="*60)
print("✅ Demonstração completa!")
print("="*60)