import json
import os
import requests
import time
import webbrowser

# 🤖 Eloy – Assistente Técnico Corporativo
# ==========================================
# Desenvolvido por Lucas Toledo
# Última atualização: 12/11/2025
# Versão: 1.0 (nota 10)
#
# Este programa implementa um sistema corporativo
# interativo com menus dinâmicos, persistência em JSON,
# integração com IA via API Groq e logs automáticos.

# =========================
# 🔑 CONFIGURAÇÕES INICIAIS
# =========================
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
BANCO_ARQUIVO = "dados.json"

# =========================
# 🎨 CORES E ESTILOS
# =========================
class Cores:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def titulo(txt):
    print("=" * 35)
    print(txt)
    print("=" * 35 + "\n")

def forca_opcao(msg, lista_opcoes):
    for i, opcao in enumerate(lista_opcoes, 1):
        print(f"{i} - {opcao}")
    escolha = input(f"{msg}\n-> ").strip()
    while not escolha.isdigit() or int(escolha) not in range(1, len(lista_opcoes) + 1):
        print("Inválido, tente novamente.")
        escolha = input(f"{msg}\n-> ").strip()
    return lista_opcoes[int(escolha) - 1]

# =========================
# 💾 BANCO DE DADOS
# =========================
def carregar_dados():
    if not os.path.exists(BANCO_ARQUIVO):
        dados_iniciais = {
            "empresa": {
                "nome": "Eloy Soluções Corporativas",
                "fundacao": "09/11/2025"
            },
            "funcionarios": [
                {"nome": "Lucas Toledo", "cargo": "Engenheiro de Software / Coordenador do projeto"},
                {"nome": "Leonardo Silva", "cargo": "Desenvolvedor Full Stack"},
                {"nome": "Samuel Monteiro", "cargo": "Analista de Sistemas"}
            ],
            "projetos": ["Site Eloy", "Sistema de Gestão Interna", "EloyBand", "EloyBeacon"],
            "relatorios": {}
        }
        salvar_dados(dados_iniciais)
        return dados_iniciais
    with open(BANCO_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(BANCO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# =========================
# 🧠 CHAT ELOY (IA REAL)
# =========================
def gerar_contexto():
    d = carregar_dados()
    return (
        f"A empresa se chama {d['empresa'].get('nome')} fundada em {d['empresa'].get('fundacao')}.\n"
        f"Funcionários: {', '.join(f'{f['nome']} ({f['cargo']})' for f in d['funcionarios'])}.\n"
        f"Projetos ativos: {', '.join(d['projetos']) or 'nenhum'}.\n"
        f"Relatórios registrados: {', '.join(d['relatorios'].keys()) or 'nenhum'}."
    )

def conversar_com_ia():
    limpar_tela()
    titulo("💬 CHAT ELOY – INTELIGÊNCIA CORPORATIVA")
    print("Sou Eloy, o assistente técnico corporativo da empresa.\nDigite 'sair' para encerrar.\n")

    while True:
        msg = input("Você: ").strip()
        if msg.lower() == "sair":
            print("🧠 Eloy: Até logo!\n")
            break

        contexto = gerar_contexto()

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é Eloy, assistente técnico corporativo. Responda de forma curta, direta e profissional."
                },
                {
                    "role": "user",
                    "content": f"Contexto: {contexto}\n\nPergunta: {msg}"
                }
            ],
            "temperature": 0.6
        }

        try:
            r = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
            resposta = r.json()
            if resposta.get("choices"):
                conteudo = resposta["choices"][0]["message"]["content"].strip()
                print(f"🧠 Eloy: {conteudo}\n")
            else:
                erro = resposta.get("error", {}).get("message", "Erro desconhecido.")
                print(f"⚠️ Erro da API: {erro}\n")
        except Exception as e:
            print(f"⚠️ Erro de comunicação com a IA: {e}\n")

# =========================
# 📊 RELATÓRIOS
# =========================
def menu_relatorios():
    dados = carregar_dados()

    acoes = {
        "Adicionar relatório": lambda: adicionar_relatorio(dados),
        "Ver relatório": lambda: ver_relatorio(dados),
        "Editar relatório": lambda: editar_relatorio(dados),
        "Remover relatório": lambda: remover_relatorio(dados),
        "Listar relatórios": lambda: listar_relatorios(dados),
        "Voltar": lambda: None
    }

    while True:
        limpar_tela()
        titulo("📊 MENU DE RELATÓRIOS")
        escolha = forca_opcao("Escolha uma ação:", list(acoes.keys()))
        if escolha == "Voltar":
            break
        acoes[escolha]()

def adicionar_relatorio(dados):
    data = input("🗓️ Data (DD/MM/AAAA): ")
    conteudo = input("📝 Conteúdo: ")
    dados["relatorios"][data] = conteudo
    salvar_dados(dados)
    print("✅ Relatório salvo!\n")
    time.sleep(1)

def ver_relatorio(dados):
    data = input("Data: ")
    print(f"\n📄 {dados['relatorios'].get(data, 'Relatório não encontrado.')}\n")
    input("Pressione Enter...")

def editar_relatorio(dados):
    data = input("Data do relatório: ")
    if data in dados["relatorios"]:
        dados["relatorios"][data] = input("Novo conteúdo: ")
        salvar_dados(dados)
        print("✏️ Atualizado!\n")
    else:
        print("⚠️ Não encontrado.\n")
    time.sleep(1)

def remover_relatorio(dados):
    data = input("Data: ")
    if data in dados["relatorios"]:
        del dados["relatorios"][data]
        salvar_dados(dados)
        print("🗑️ Removido!\n")
    else:
        print("⚠️ Não encontrado.\n")
    time.sleep(1)

def listar_relatorios(dados):
    if dados["relatorios"]:
        print("\n🗂️ Relatórios:")
        for d in dados["relatorios"]:
            print(f" - {d}")
    else:
        print("⚠️ Nenhum relatório cadastrado.\n")
    input("Pressione Enter...")

# =========================
# 👥 EQUIPE
# =========================
def menu_equipe():
    dados = carregar_dados()

    acoes = {
        "Ver equipe": lambda: ver_equipe(dados),
        "Adicionar membro": lambda: adicionar_membro(dados),
        "Editar cargo": lambda: editar_cargo(dados),
        "Remover membro": lambda: remover_membro(dados),
        "Voltar": lambda: None
    }

    while True:
        limpar_tela()
        titulo("👥 MENU DA EQUIPE")
        escolha = forca_opcao("Escolha uma ação:", list(acoes.keys()))
        if escolha == "Voltar":
            break
        acoes[escolha]()

def ver_equipe(dados):
    print(f"\n👥 | Equipe da {dados['empresa']['nome']}:")
    for f in dados["funcionarios"]:
        print(f"🔹 {f['nome']} — {f['cargo']}")
    input("\nPressione Enter...")

def adicionar_membro(dados):
    nome = input("Nome: ")
    cargo = input("Cargo: ")
    dados["funcionarios"].append({"nome": nome, "cargo": cargo})
    salvar_dados(dados)
    print("✅ Adicionado!\n")
    time.sleep(1)

def editar_cargo(dados):
    nome = input("Nome do membro: ")
    for f in dados["funcionarios"]:
        if f["nome"].lower() == nome.lower():
            f["cargo"] = input("Novo cargo: ")
            salvar_dados(dados)
            print("✏️ Atualizado!\n")
            break
    else:
        print("⚠️ Membro não encontrado.\n")
    time.sleep(1)

def remover_membro(dados):
    nome = input("Nome: ")
    nova_lista = [f for f in dados["funcionarios"] if f["nome"].lower() != nome.lower()]
    if len(nova_lista) != len(dados["funcionarios"]):
        dados["funcionarios"] = nova_lista
        salvar_dados(dados)
        print("🗑️ Removido!\n")
    else:
        print("⚠️ Não encontrado.\n")
    time.sleep(1)

# =========================
# 💼 PROJETOS
# =========================
def menu_projetos():
    dados = carregar_dados()

    acoes = {
        "Ver projetos": lambda: ver_projetos(dados),
        "Adicionar projeto": lambda: adicionar_projeto(dados),
        "Remover projeto": lambda: remover_projeto(dados),
        "Voltar": lambda: None
    }

    while True:
        limpar_tela()
        titulo("💼 MENU DE PROJETOS")
        escolha = forca_opcao("Escolha uma ação:", list(acoes.keys()))
        if escolha == "Voltar":
            break
        acoes[escolha]()

def ver_projetos(dados):
    print("\n🚀 Projetos ativos:")
    for p in dados["projetos"]:
        print(f" - {p}")
    input("\nPressione Enter...")

def adicionar_projeto(dados):
    nome = input("Nome do novo projeto: ")
    if nome not in dados["projetos"]:
        dados["projetos"].append(nome)
        salvar_dados(dados)
        print("✅ Projeto adicionado!\n")
    else:
        print("⚠️ Projeto já existe.\n")
    time.sleep(1)

def remover_projeto(dados):
    nome = input("Nome do projeto: ")
    if nome in dados["projetos"]:
        dados["projetos"].remove(nome)
        salvar_dados(dados)
        print("🗑️ Removido!\n")
    else:
        print("⚠️ Não encontrado.\n")
    time.sleep(1)

# =========================
# 🚀 MENU PRINCIPAL
# =========================
def menu_principal():
    acoes = {
        "Conversar com IA": conversar_com_ia,
        "Relatórios": menu_relatorios,
        "Equipe": menu_equipe,
        "Projetos": menu_projetos,
        "Site da Eloy": lambda: webbrowser.open("http://www.eloy.com.br"),
        "Sair / Desligar Eloy": None
    }

    while True:
        limpar_tela()
        titulo("🤖  SISTEMA ELOY - MENU PRINCIPAL")
        escolha = forca_opcao("Escolha uma opção:", list(acoes.keys()))

        if escolha == "Sair / Desligar Eloy":
            print("\n💤 Eloy desligado. Pressione Enter para reativar...\n")
            input()
            print("🔋 Reiniciando sistema Eloy...\n")
            time.sleep(1)
        else:
            acoes[escolha]()

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    limpar_tela()
    titulo("🚀 BEM-VINDO AO SISTEMA ELOY 🚀")
    time.sleep(1)
    menu_principal()
