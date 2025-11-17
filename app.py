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
# Nota: A chave da API Groq foi mantida como a original do usuário, mas
# em um ambiente real, ela deveria ser carregada de uma variável de ambiente.
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
BANCO_ARQUIVO = "dados.json"

# Conteúdo do RAG (Documento de Geração Aumentada por Recuperação - Eloy )
RAG_CONTENT = """
## 1. Perfil da Empresa

| Atributo | Detalhe |
| :--- | :--- |
| **Nome da Empresa** | Eloy |
| **Natureza** | Empresa inovadora de Inteligência Artificial (IA) |
| **Foco Principal** | Implementar IA no dia a dia do mundo corporativo |
| **Modelo de Negócio** | B2B (Business-to-Business) |
| **Data de Fundação** | 09 de Novembro de 2025 |
| **Localização Sede** | FIAP da Paulista (Avenida Paulista, São Paulo) |
| **Propósito** | Facilitar operações simples e tirar dúvidas básicas sobre a empresa para funcionários e estagiários, sem a necessidade de consultar superiores. |
| **Proposta de Valor** | Disponibilizar um agente de IA personalizado e treinado com todas as informações da empresa cliente. |

## 2. Fundadores e Equipe Chave

A Eloy foi fundada por três profissionais com expertises complementares, cada um responsável por uma área estratégica da empresa:

| Fundador | Área de Responsabilidade | Contribuição Específica |
| :--- | :--- | :--- |
| **Lucas Toledo** | Python e Edge Computing | Responsável pelo desenvolvimento da IA (como o próprio agente Eloy) e pela infraestrutura de back-end. |
| **Leonardo Silva** | Desenvolvimento Front-End | Responsável pelo desenvolvimento do site oficial da empresa. |
| **Samuel Monteiro** | UI/UX, Prototipagem e Levantamento de Requisitos | Responsável pela experiência do usuário, design de interface e definição das necessidades do produto. |

## 3. O Agente de IA Eloy

O agente de IA da Eloy, que serve como um modelo de demonstração e o produto principal da empresa, possui as seguintes características e diretrizes de comunicação:

*   **Personalidade:** Séria e objetiva.
*   **Estilo de Resposta:** Tenta responder com apenas **duas linhas** na maioria das interações.
*   **Exceção:** Respostas longas são fornecidas somente quando o usuário as solicita explicitamente.
*   **Função Principal:** Facilitar operações simples e responder a dúvidas básicas sobre a empresa (normas, práticas, etc.).
*   **Treinamento:** É treinado com todas as informações da respectiva empresa cliente, assim como o modelo de demonstração é treinado com as informações da própria Eloy.

## 4. Tecnologia e Infraestrutura

O desenvolvimento da Eloy se apoia em tecnologias modernas e uma infraestrutura clara:

*   **Desenvolvimento da IA (Back-end/Edge):** Liderado por Lucas Toledo, utilizando a linguagem **Python** e focado em soluções de **Edge Computing** para processamento de dados e inferência de IA.
*   **Desenvolvimento Web (Front-end):** Liderado por Leonardo Silva.
    *   **Site Oficial:** `eloy-ai.vercel.app`
    *   **Plataforma de Hospedagem:** Vercel (indicando uma arquitetura moderna e escalável para o front-end).
*   **Design e Produto (UI/UX):** Liderado por Samuel Monteiro, garantindo que a interface e a experiência do usuário sejam intuitivas e atendam aos requisitos levantados.

## 5. Proposta de Valor e Casos de Uso (B2B)

A Eloy se posiciona como uma parceira estratégica para o mundo corporativo, oferecendo soluções de IA que se integram diretamente aos fluxos de trabalho internos.

### 5.1. Proposta de Valor

A principal proposta de valor da Eloy é a **personalização e o treinamento específico** do agente de IA. Ao treinar o agente com os dados internos da empresa cliente, a Eloy garante que a IA se torne um recurso de conhecimento interno, capaz de:

*   Reduzir a carga de trabalho dos gestores e superiores ao responder a perguntas rotineiras.
*   Acelerar a integração de novos colaboradores e estagiários.
*   Garantir a consistência e a precisão das informações internas.

### 5.2. Casos de Uso Típicos

O agente Eloy é ideal para:

1.  **Suporte a Funcionários:** Responder a dúvidas sobre políticas internas, RH, benefícios, procedimentos de TI e normas de segurança.
2.  **Onboarding de Estagiários:** Servir como um mentor imediato para tirar dúvidas sobre a cultura, práticas e ferramentas da empresa.
3.  **Facilitação de Operações:** Auxiliar na realização de tarefas simples, como preenchimento de formulários, localização de documentos ou agendamento de recursos.
4.  **Acesso Rápido ao Conhecimento:** Fornecer informações específicas de projetos ou departamentos, atuando como um repositório de conhecimento instantâneo.

## 6. Contato e Parceria

Para empresas que desejam implementar um agente Eloy treinado e personalizado para suas necessidades, o contato deve ser feito através dos canais de comunicação oficiais da empresa.

*   **Site:** [eloy-ai.vercel.app](https://eloy-ai.vercel.app )
*   **Parceria:** Entre em contato conosco pelos nossos meios de comunicação para ter uma Eloy treinada para sua empresa.

---

*Este documento RAG foi elaborado para fornecer uma base de conhecimento completa e estruturada sobre a empresa Eloy, seus fundadores, produto e proposta de valor, otimizando a performance de modelos de linguagem em tarefas de recuperação de informação.*
"""

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
    # O contexto dinâmico do banco de dados foi mantido
    contexto_dinamico = (
        f"A empresa se chama {d['empresa'].get('nome')} fundada em {d['empresa'].get('fundacao')}.\n"
        f"Funcionários: {', '.join(f'{f['nome']} ({f['cargo']})' for f in d['funcionarios'])}.\n"
        f"Projetos ativos: {', '.join(d['projetos']) or 'nenhum'}.\n"
        f"Relatórios registrados: {', '.join(d['relatorios'].keys()) or 'nenhum'}."
    )
    
    # O prompt de sistema agora inclui o RAG_CONTENT e as diretrizes de personalidade
    system_prompt = (
        "Você é Eloy, o agente de IA da empresa Eloy. Sua função é facilitar operações simples e "
        "responder a dúvidas básicas sobre a empresa para funcionários e estagiários. "
        "Sua personalidade é **séria e objetiva**. "
        "Seu estilo de resposta é tentar responder com apenas **duas linhas** na maioria das interações. "
        "Respostas longas são fornecidas somente se o usuário solicitar explicitamente. "
        "Use o conteúdo a seguir como sua base de conhecimento. Responda apenas com base neste contexto, "
        "a menos que seja uma saudação ou uma pergunta de propósito geral que não possa ser respondida pelo contexto. "
        "\n\n"
        "**Contexto da Empresa Eloy (RAG):**\n"
        f"{RAG_CONTENT}"
    )
    
    return system_prompt, contexto_dinamico

def conversar_com_ia():
    limpar_tela()
    titulo("💬 CHAT ELOY – INTELIGÊNCIA CORPORATIVA")
    print("Sou Eloy, o assistente técnico corporativo da empresa.\nDigite 'sair' para encerrar.\n")

    system_prompt, contexto_dinamico = gerar_contexto()

    while True:
        msg = input("Você: ").strip()
        if msg.lower() == "sair":
            print("🧠 Eloy: Até logo!\n")
            break

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # O prompt do usuário combina a pergunta com o contexto dinâmico do banco de dados
        user_content = f"Contexto Dinâmico (Banco de Dados): {contexto_dinamico}\n\nPergunta: {msg}"
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.5 # Ajustado para 0.5 para respostas mais factuais, como no código anterior
        }

        try:
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            r.raise_for_status() # Lança exceção para códigos de status HTTP ruins
            resposta = r.json()
            
            if resposta.get("choices"):
                conteudo = resposta["choices"][0]["message"]["content"].strip()
                print(f"🧠 Eloy: {conteudo}\n")
            else:
                # Trata erros da API Groq que não lançam exceção HTTP
                erro = resposta.get("error", {}).get("message", "Erro desconhecido na resposta da API.")
                print(f"⚠️ Erro da API: {erro}\n")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erro de comunicação com a IA (Requisição): {e}\n")
        except Exception as e:
            print(f"⚠️ Erro inesperado: {e}\n")

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
        "Site da Eloy": lambda: webbrowser.open("https://eloy-ai.vercel.app/welcome" ),
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
