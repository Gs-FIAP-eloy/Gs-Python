import json
import requests
import os
import webbrowser
import time

# =========================
# 🔑 CONFIGURAÇÕES INICIAIS
# =========================

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
BANCO_ARQUIVO = "dados.json"

# =========================
# 🎨 CORES E ESTILOS TERMINAL
# =========================

class Cores:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    MAGENTA = "\033[95m"

def linha():
    print(Cores.GRAY + "─" * 50 + Cores.RESET)

def titulo(texto):
    linha()
    print(f"{Cores.CYAN}{Cores.BOLD}{texto.center(50)}{Cores.RESET}")
    linha()


# =========================
# ⚙️ FUNÇÕES DE BANCO DE DADOS
# =========================

def carregar_banco():
    if not os.path.exists(BANCO_ARQUIVO):
        banco = {
            "empresa": {
                "nome": "Eloy Soluções Corporativas",
                "fundacao": "09/11/2025"
            },
            "funcionarios": [
                {"nome": "Lucas Toledo", "cargo": "Engenheiro de Computação / Coordenador de Projeto"},
                {"nome": "Leonardo Silva", "cargo": "Desenvolvedor Full Stack"},
                {"nome": "Samuel Monteiro", "cargo": "Analista de Sistemas"}
            ],
            "projetos": ["Web", "Cálculo", "Edge"],
            "relatorios": {}
        }
        salvar_banco(banco)
    else:
        with open(BANCO_ARQUIVO, "r", encoding="utf-8") as f:
            banco = json.load(f)
    return banco


def salvar_banco(banco):
    with open(BANCO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=2, ensure_ascii=False)


# =========================
# 🤖 CHATBOT GROQ
# =========================

def conversar_com_ia():
    titulo("💬 MODO DE CONVERSAÇÃO - ELOY")
    print("Digite suas mensagens normalmente.")
    print("Diga 'tchau', 'sair' ou 'voltar' para encerrar.\n")

    while True:
        user = input(f"{Cores.BOLD}Você:{Cores.RESET} ").strip()
        if any(x in user.lower() for x in ["tchau", "sair", "voltar", "adeus", "até logo"]):
            print(f"{Cores.MAGENTA}🤖 Eloy: Até mais!{Cores.RESET}\n")
            break

        comandos = {
            "relatorio": menu_relatorios,
            "membro": menu_equipe,
        }

        for cmd, func in comandos.items():
            if cmd in user.lower():
                print(f"{Cores.MAGENTA}🤖 Eloy: Redirecionando para o menu de {cmd}...{Cores.RESET}\n")
                func()
                return

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Você é Eloy, um assistente corporativo profissional e direto."},
                {"role": "user", "content": user}
            ]
        }

        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            data = res.json()
            resposta = data["choices"][0]["message"]["content"]
            print(f"{Cores.MAGENTA}🤖 Eloy:{Cores.RESET} {resposta}\n")
        except Exception as e:
            print(f"{Cores.RED}⚠️ Erro na IA:{Cores.RESET} {e}\n")


# =========================
# 📊 MENU DE RELATÓRIOS
# =========================

def menu_relatorios():
    banco = carregar_banco()
    while True:
        titulo("📊 MENU DE RELATÓRIOS")
        print(f"{Cores.CYAN}1.{Cores.RESET} Adicionar relatório")
        print(f"{Cores.CYAN}2.{Cores.RESET} Ver relatório por data")
        print(f"{Cores.CYAN}3.{Cores.RESET} Listar relatórios existentes")
        print(f"{Cores.CYAN}4.{Cores.RESET} Editar relatório")
        print(f"{Cores.CYAN}5.{Cores.RESET} Remover relatório")
        print(f"{Cores.CYAN}6.{Cores.RESET} Voltar ao menu principal")
        linha()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            data = input("🗓️  Data (DD/MM/AAAA): ")
            texto = input("📝 Conteúdo: ")
            banco["relatorios"][data] = texto
            salvar_banco(banco)
            print(f"{Cores.GREEN}✅ Relatório de {data} adicionado com sucesso.{Cores.RESET}")

        elif opcao == "2":
            data = input("Digite a data: ")
            if data in banco["relatorios"]:
                print(f"\n📅 {Cores.BOLD}Relatório de {data}:{Cores.RESET}\n{banco['relatorios'][data]}")
            else:
                print(f"{Cores.RED}⚠️ Relatório não encontrado.{Cores.RESET}")
                if banco["relatorios"]:
                    print("Relatórios disponíveis:")
                    for d in banco["relatorios"].keys():
                        print(f"- {d}")

        elif opcao == "3":
            if banco["relatorios"]:
                print("\n🗂️ Relatórios existentes:")
                for data in banco["relatorios"].keys():
                    print(f" - {data}")
            else:
                print(f"{Cores.YELLOW}⚠️ Nenhum relatório cadastrado.{Cores.RESET}")

        elif opcao == "4":
            data = input("Data do relatório a editar: ")
            if data in banco["relatorios"]:
                novo = input("Novo conteúdo: ")
                banco["relatorios"][data] = novo
                salvar_banco(banco)
                print(f"{Cores.GREEN}✏️ Relatório atualizado com sucesso.{Cores.RESET}")
            else:
                print(f"{Cores.RED}⚠️ Relatório não encontrado.{Cores.RESET}")

        elif opcao == "5":
            data = input("Data do relatório a remover: ")
            if data in banco["relatorios"]:
                del banco["relatorios"][data]
                salvar_banco(banco)
                print(f"{Cores.GREEN}🗑️ Relatório removido com sucesso.{Cores.RESET}")
            else:
                print(f"{Cores.RED}⚠️ Relatório não encontrado.{Cores.RESET}")

        elif opcao == "6":
            print(f"{Cores.MAGENTA}🔙 Retornando ao menu principal...{Cores.RESET}\n")
            break
        else:
            print(f"{Cores.RED}⚠️ Opção inválida!{Cores.RESET}")


# =========================
# 👥 MENU DA EQUIPE
# =========================

def menu_equipe():
    banco = carregar_banco()
    while True:
        titulo("👥 MENU DA EQUIPE")
        print(f"{Cores.CYAN}1.{Cores.RESET} Ver informações da empresa")
        print(f"{Cores.CYAN}2.{Cores.RESET} Adicionar membro")
        print(f"{Cores.CYAN}3.{Cores.RESET} Remover membro")
        print(f"{Cores.CYAN}4.{Cores.RESET} Editar cargo de membro")
        print(f"{Cores.CYAN}5.{Cores.RESET} Voltar ao menu principal")
        linha()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print(f"\n🏢 Empresa: {Cores.BOLD}{banco['empresa']['nome']}{Cores.RESET}")
            print(f"📅 Fundação: {banco['empresa']['fundacao']}\n")
            print(f"{Cores.BOLD}👤 Funcionários:{Cores.RESET}")
            for f in banco["funcionarios"]:
                print(f" - {f['nome']} ({f['cargo']})")

        elif opcao == "2":
            nome = input("Nome do novo membro: ")
            cargo = input("Cargo do novo membro: ")
            banco["funcionarios"].append({"nome": nome, "cargo": cargo})
            salvar_banco(banco)
            print(f"{Cores.GREEN}✅ Membro adicionado com sucesso.{Cores.RESET}")

        elif opcao == "3":
            nome = input("Nome do membro a remover: ")
            funcionarios = [f for f in banco["funcionarios"] if f["nome"].lower() != nome.lower()]
            if len(funcionarios) != len(banco["funcionarios"]):
                banco["funcionarios"] = funcionarios
                salvar_banco(banco)
                print(f"{Cores.GREEN}🗑️ Membro removido com sucesso.{Cores.RESET}")
            else:
                print(f"{Cores.RED}⚠️ Membro não encontrado.{Cores.RESET}")

        elif opcao == "4":
            nome = input("Nome do membro a editar: ")
            for f in banco["funcionarios"]:
                if f["nome"].lower() == nome.lower():
                    novo_cargo = input(f"Novo cargo para {f['nome']}: ")
                    f["cargo"] = novo_cargo
                    salvar_banco(banco)
                    print(f"{Cores.GREEN}✏️ Cargo atualizado com sucesso.{Cores.RESET}")
                    break
            else:
                print(f"{Cores.RED}⚠️ Membro não encontrado.{Cores.RESET}")

        elif opcao == "5":
            print(f"{Cores.MAGENTA}🔙 Retornando ao menu principal...{Cores.RESET}\n")
            break
        else:
            print(f"{Cores.RED}⚠️ Opção inválida!{Cores.RESET}")


# =========================
# 🏠 MENU PRINCIPAL
# =========================

def menu_principal():
    while True:
        titulo("⚙️ ELOY - INTELIGÊNCIA CORPORATIVA INTEGRADA")
        print(f"{Cores.CYAN}1.{Cores.RESET} Conversar com IA")
        print(f"{Cores.CYAN}2.{Cores.RESET} Relatórios")
        print(f"{Cores.CYAN}3.{Cores.RESET} Equipe")
        print(f"{Cores.CYAN}4.{Cores.RESET} Site da Eloy")
        print(f"{Cores.CYAN}5.{Cores.RESET} Sair / Desligar Eloy")
        linha()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            conversar_com_ia()
        elif opcao == "2":
            menu_relatorios()
        elif opcao == "3":
            menu_equipe()
        elif opcao == "4":
            webbrowser.open("http://www.eloy.com.br")
        elif opcao == "5":
            print(f"\n{Cores.YELLOW}💤 Eloy desligado. Pressione Enter para reativar...{Cores.RESET}")
            input()
            print(f"{Cores.GREEN}🔋 Reiniciando sistema Eloy...{Cores.RESET}\n")
            time.sleep(1)
        else:
            print(f"{Cores.RED}⚠️ Opção inválida!{Cores.RESET}")


# =========================
# 🚀 EXECUÇÃO
# =========================

if __name__ == "__main__":
    titulo("🚀 INICIALIZANDO O SISTEMA ELOY")
    time.sleep(1)
    menu_principal()
