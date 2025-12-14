"""
MultimodalDB Interativo
Menu controlado pelo usuário para busca e indexação
"""
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, IntPrompt

from multimodal_db import MultimodalDB

# Inicializa console e banco
console = Console()
db = MultimodalDB("image_database.json")

def clear():
    """Limpa a tela (compatível com Linux/Docker)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def header():
    clear()
    console.print(Panel.fit(
        "[bold cyan]🤖 MultimodalDB Interactive CLI[/]\n"
        "[dim]Sistema de Busca Semântica com CLIP[/]",
        border_style="blue"
    ))

def display_results(query, results):
    """Exibe resultados bonitos"""
    if not results:
        console.print(f"\n[bold red]❌ Nada encontrado para: '{query}'[/]")
        return

    console.print(f"\n[bold green]✅ Resultados para: '{query}'[/]")
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Score", justify="right")
    table.add_column("Confiança Visual", width=20)
    table.add_column("Arquivo", style="cyan")
    table.add_column("Metadados")

    for i, res in enumerate(results, 1):
        score = res['score']
        
        # Lógica visual de confiança
        confidence_pct = min((score / 0.32) * 100, 100)
        bar_len = int(confidence_pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        # Cores dinâmicas
        color = "green" if i == 1 else "yellow" if i <= 3 else "white"
        if score < 0.23: color = "red" # Alerta para resultados fracos

        table.add_row(
            str(i),
            f"{score:.4f}",
            f"[{color}]{bar}[/]",
            res['filename'],
            str(res.get('metadata', ''))
        )

    console.print(table)

def menu_indexar():
    console.print("\n[bold yellow]📂 Indexar Imagens[/]")
    pasta = Prompt.ask("Nome da pasta", default="images")
    
    if not os.path.exists(pasta):
        console.print(f"[red]Erro: Pasta '{pasta}' não existe![/]")
        return

    stats = db.add_folder(pasta, verbose=True)
    console.print(f"[green]Concluído![/] Adicionadas: {stats['added']}")
    Prompt.ask("\n[dim]Pressione Enter para voltar...[/]")

def menu_busca_texto():
    # Exemplos de queries que funcionam bem
    sugestoes = [
        "dog", "cat", "forest", "technology", 
        "red car", "beach", "city", "python code"
    ]

    while True:
        console.print("\n[bold yellow]🔍 Busca por Texto[/]")
        
        # Mostra os exemplos formatados
        console.print(f"[dim]Sugestões: {', '.join(sugestoes)}[/]")

        query = Prompt.ask("Digite sua busca (ou '0' para voltar)")
        
        if query == '0': break
        
        # Filtro: min_score 0.15 ajuda a tirar resultados muito ruins
        results = db.search_by_text(query, top_k=5, min_score=0.15, verbose=False)
        display_results(query, results)

def menu_busca_imagem():
    console.print("\n[bold yellow]🖼️  Busca por Imagem Similar[/]")
    
    # Lista algumas imagens para ajudar o usuário
    imgs = db.storage.get_all_paths()[:10]
    if not imgs:
        console.print("[red]O banco está vazio![/]")
        return

    console.print("Exemplos disponíveis:")
    for img in imgs:
        console.print(f" - {os.path.basename(img)}")
    
    filename = Prompt.ask("\nDigite o nome do arquivo (ex: cachorro1.jpeg)")
    path = os.path.join("images", filename) # Assumindo pasta padrão

    if not os.path.exists(path):
        # Tenta achar no banco se o caminho for diferente
        full_path = next((i for i in imgs if filename in i), None)
        path = full_path if full_path else path

    if os.path.exists(path):
        # Mude de 0.25 para 0.85 ou 0.90 se quiser apenas MUITO parecidos
        results = db.search_by_image(path, top_k=5, min_score=0.85, verbose=False)
        display_results(filename, results)
    else:
        console.print("[red]Arquivo não encontrado![/]")
    
    Prompt.ask("\n[dim]Pressione Enter para voltar...[/]")

def main():
    while True:
        header()
        db.print_stats()
        
        console.print(Panel(
            "[1] 📂 Indexar Pasta\n"
            "[2] 🔍 Buscar por Texto\n"
            "[3] 🖼️  Buscar por Imagem\n"
            "[4] ❌ Sair",
            title="Menu Principal",
            border_style="green"
        ))

        opcao = IntPrompt.ask("Escolha uma opção", choices=["1", "2", "3", "4"])

        if opcao == 1:
            menu_indexar()
        elif opcao == 2:
            menu_busca_texto()
        elif opcao == 3:
            menu_busca_imagem()
        elif opcao == 4:
            console.print("[bold blue]Saindo... Até mais! 👋[/]")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrompido pelo usuário.[/]")