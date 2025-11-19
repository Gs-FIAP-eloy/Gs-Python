# ELOY: Assistente Técnico Corporativo (Sistema Terminal)

## 1. Identificação e Visão Geral

| Atributo | Detalhe |
| :--- | :--- |
| **Nome do Projeto** | ELOY: Assistente Técnico Corporativo (Sistema Terminal) |
| **Integrantes** | Lucas Toledo (RM 563271), Leonardo Silva (RM 564929), Samuel Monteiro (RM 564391) |
| **Link do Vídeo** | [INSERIR LINK DO VÍDEO AQUI] |

### 1.1. Problema Abordado: A Ineficiência na Disseminação de Conhecimento

O principal desafio no ambiente corporativo, especialmente para novos membros, é a **dispersão e a dificuldade de acesso ao conhecimento interno**. Dúvidas operacionais e sobre políticas consomem o tempo de colaboradores sêniores, desviando o foco da inovação e da estratégia. O problema é a **baixa otimização do tempo** devido à dependência de consultas humanas para informações rotineiras.

### 1.2. Proposta de Solução: O Agente de IA ELOY

O **Agente de IA ELOY** é um sistema híbrido que integra um **Sistema de Gestão Interna** (para dados estruturados e dinâmicos) com um **Agente de Inteligência Artificial** (para interação e recuperação de conhecimento).

O sistema oferece uma interface de terminal para:
1.  **Consulta Imediata:** Funcionários podem interagir com a IA para obter respostas sobre a empresa, suas políticas e projetos.
2.  **Gestão de Dados:** Manutenção de informações cruciais sobre Relatórios, Equipe e Projetos, garantindo que a base de conhecimento da IA esteja sempre atualizada.

### 1.3. Diferencial Técnico e de Negócio: RAG com Contexto Dinâmico

O projeto se destaca pela sua arquitetura de **Geração Aumentada por Recuperação (RAG)**, que é implementada em dois níveis:

*   **RAG Estático:** O agente é treinado com uma base de conhecimento fixa (`RAG_CONTENT`) que define a persona, a história e o modelo de negócio da ELOY.
*   **RAG Dinâmico:** Antes de cada consulta, o sistema injeta o **estado atual do banco de dados JSON** (funcionários, projetos, relatórios) no *prompt* da IA. Isso permite que o agente ELOY responda a perguntas que exigem dados em tempo real, elevando a precisão e a utilidade do chatbot de um simples Q&A para um **assistente corporativo contextualizado**.

O **Modelo de Negócio é B2B (Business-to-Business)**: A ELOY vende a tecnologia do agente de IA, customizando-o e treinando-o com as diretrizes específicas de cada empresa cliente, transformando o código aqui apresentado em uma prova de conceito escalável.

---

## 2. Análise Detalhada do Código-Fonte (`app.py`)

O código foi meticulosamente estruturado em Python para demonstrar domínio sobre modularidade, persistência de dados, tratamento de exceções e validação de entrada, cumprindo integralmente os requisitos de programação.

### 2.1. Modularidade e Funções de Utilidade

O código é dividido em funções claras, cada uma com uma responsabilidade única, demonstrando o uso correto de **funções com passagem de parâmetros e retorno** (Requisito 5):

*   `limpar_tela()`: Utiliza o módulo `os` para garantir a compatibilidade de limpeza de tela entre sistemas Windows (`cls`) e Unix-like (`clear`).
*   `titulo(txt)`: Função simples para formatação visual da interface.
*   `forca_opcao(msg, lista_opcoes)`: **Função Crítica de Validação** (Requisito 2). Implementa um *loop* de repetição (`while`) que só é encerrado quando o usuário insere um valor numérico que corresponde a uma opção válida na lista, garantindo a integridade da navegação do menu.

### 2.2. Persistência de Dados e Robustez de I/O (Requisitos 3 e 6)

O sistema utiliza **dicionários como base de dados** (Requisito 6), persistindo-os em um arquivo JSON (`dados.json`). A implementação das funções de I/O foi projetada para ser **extremamente robusta**, demonstrando domínio sobre o **Tratamento de Exceções** (Requisito 3) em operações de arquivo:

| Função | Exceções Tratadas | Justificativa Técnica |
| :--- | :--- | :--- |
| `carregar_dados()` | `FileNotFoundError`, `json.JSONDecodeError`, `Exception` | **Domínio de I/O:** Garante que o sistema não falhe se o arquivo `dados.json` for excluído ou se for corrompido (ex: edição manual incorreta). Em ambos os casos, o sistema se recupera, notifica o usuário e reinicia com a estrutura de dados inicial, mantendo a integridade operacional. |
| `salvar_dados(dados)` | `IOError`, `Exception` | **Domínio de I/O:** Captura erros de escrita no disco (ex: falta de permissão ou espaço), impedindo que o programa trave e garantindo que o usuário seja notificado sobre a falha de persistência. |

### 2.3. Validação de Dados em Tempo Real (Requisito 2)

A função `adicionar_relatorio` implementa uma validação de formato de entrada crucial para dados estruturados, utilizando o módulo `datetime`:

```python
def adicionar_relatorio(dados):
    while True:
        data = input("🗓️ Data (DD/MM/AAAA): ").strip()
        try:
            # Tenta converter a string para um objeto datetime no formato DD/MM/AAAA
            datetime.datetime.strptime(data, "%d/%m/%Y")
            break # Sai do loop se a data for válida
        except ValueError:
            print("⚠️ Formato de data inválido. Use o formato DD/MM/AAAA.")
    # ... continua a função
```

**Domínio de Validação:** Este bloco de código demonstra a capacidade de **forçar o formato de entrada** de dados críticos. O `try...except ValueError` garante que apenas datas no formato `DD/MM/AAAA` sejam aceitas, prevenindo erros de lógica e garantindo a qualidade dos dados armazenados no sistema de gestão.

### 2.4. Estruturas de Programação (Requisitos 1, 4)

O código utiliza as estruturas de forma eficiente:
*   **Estrutura de Menu (Requisito 1):** Implementada de forma hierárquica (`menu_principal` -> submenus) com dicionários de ações, o que permite fácil expansão e manutenção.
*   **Decisão e Repetição (Requisito 4):**
    *   **Decisão:** Uso extensivo de `if/else` para lógica de CRUD (verificar se o item existe antes de remover/editar) e tratamento de exceções.
    *   **Repetição:** Uso de `while True` para *loops* de menu e chat, e `for` para iteração sobre listas (ex: listagem de funcionários e projetos).

---

## 3. Dicionário de Funções: Propósito e Funcionamento

Esta seção detalha o propósito e o funcionamento de cada função do `app.py`, demonstrando a modularidade e a clareza da arquitetura do sistema.

### 3.1. Funções de Utilidade e Menu

| Função | Propósito | Funcionamento Detalhado |
| :--- | :--- | :--- |
| `limpar_tela()` | Limpeza da Interface | Utiliza o módulo `os` para executar o comando de limpeza de tela apropriado (`cls` para Windows ou `clear` para Unix/Linux), garantindo uma interface de terminal limpa e organizada. |
| `titulo(txt)` | Formatação de Títulos | Imprime o texto fornecido entre linhas de separação (`=`), padronizando a exibição de títulos de menu e cabeçalhos. |
| `forca_opcao(msg, lista_opcoes)` | Validação de Entrada de Menu | Exibe as opções numeradas e utiliza um *loop* de repetição (`while`) para garantir que a entrada do usuário seja um número válido dentro do intervalo de opções disponíveis. Retorna a *string* da opção escolhida. |

### 3.2. Funções de Persistência de Dados (I/O)

| Função | Propósito | Funcionamento Detalhado |
| :--- | :--- | :--- |
| `carregar_dados()` | Carregar Dados e Inicializar Sistema | **1.** Verifica a existência do `dados.json`. Se não existir, cria o arquivo com a estrutura inicial. **2.** Se existir, tenta ler o JSON. **3.** Implementa tratamento de exceções para `FileNotFoundError` e `json.JSONDecodeError`, garantindo que o sistema se recupere de arquivos corrompidos ou ausentes, reiniciando com dados padrão. |
| `salvar_dados(dados)` | Salvar Dados no JSON | Escreve o dicionário de dados no arquivo `dados.json` com formatação (`indent=2`). Implementa tratamento de exceções (`IOError`) para garantir que falhas de escrita no disco (ex: permissão) sejam capturadas sem travar o programa. |

### 3.3. Funções do Agente de IA (ELOY)

| Função | Propósito | Funcionamento Detalhado |
| :--- | :--- | :--- |
| `gerar_contexto()` | Preparação do Contexto da IA | Carrega os dados atuais e constrói duas *strings*: o `system_prompt` (com o RAG estático e a persona) e o `contexto_dinamico` (com dados atualizados de projetos, equipe e relatórios). Retorna ambas para a função de chat. |
| `conversar_com_ia()` | Loop Principal de Chat | Gerencia a interação com o usuário e a comunicação com a API Groq. Constrói o *payload* da requisição (incluindo o RAG dinâmico), envia a requisição via `requests.post` e utiliza `try...except` para tratar erros de comunicação (`requests.exceptions.RequestException`) e erros da API. |

### 3.4. Funções de Gestão Interna (CRUD)

| Função | Propósito | Funcionamento Detalhado |
| :--- | :--- | :--- |
| `menu_relatorios()` | Menu de Relatórios | Orquestra as ações de CRUD para a entidade "Relatórios". |
| `adicionar_relatorio(dados)` | Adicionar Relatório | Solicita a data e o conteúdo. **Implementa validação de data** usando `datetime.strptime` para garantir o formato `DD/MM/AAAA` antes de salvar no dicionário `relatorios`. |
| `ver_relatorio(dados)` | Visualizar Relatório | Busca e exibe o conteúdo de um relatório pela data, utilizando `.get()` para retornar uma mensagem amigável se o relatório não for encontrado. |
| `editar_relatorio(dados)` | Editar Relatório | Permite a atualização do conteúdo de um relatório existente, buscando-o pela data. |
| `remover_relatorio(dados)` | Remover Relatório | Exclui uma entrada do dicionário `relatorios` pela data. |
| `listar_relatorios(dados)` | Listar Relatórios | Exibe todas as datas dos relatórios cadastrados. |
| `menu_equipe()` | Menu de Equipe | Orquestra as ações de CRUD para a entidade "Funcionários". |
| `ver_equipe(dados)` | Visualizar Equipe | Lista todos os funcionários e seus respectivos cargos. |
| `adicionar_membro(dados)` | Adicionar Membro | Adiciona um novo dicionário (membro) à lista de `funcionarios`. |
| `editar_cargo(dados)` | Editar Cargo | Busca um membro pelo nome (ignorando maiúsculas/minúsculas) e atualiza seu cargo. |
| `remover_membro(dados)` | Remover Membro | Remove um membro da lista de `funcionarios` por meio de uma list comprehension, garantindo a remoção correta. |
| `menu_projetos()` | Menu de Projetos | Orquestra as ações de CRUD para a entidade "Projetos". |
| `ver_projetos(dados)` | Visualizar Projetos | Lista todos os projetos ativos. |
| `adicionar_projeto(dados)` | Adicionar Projeto | Adiciona um novo projeto à lista, verificando se ele já existe. |
| `remover_projeto(dados)` | Remover Projeto | Remove um projeto da lista. |
| `menu_principal()` | Menu Principal | A função de controle que inicia o sistema e direciona o usuário para os submenus ou para o chat com a IA. |

## 4. O Modelo de Negócio B2B e a Aplicação Web

O projeto ELOY é a base para um produto **B2B (Business-to-Business)**, onde a tecnologia do agente de IA é licenciada e customizada para outras empresas.

### 4.1. Modelo de Negócio

A ELOY se posiciona como uma parceira estratégica, oferecendo:
*   **Customização:** Treinamento do agente de IA com a base de conhecimento interna (manuais, políticas, diretrizes) da empresa cliente.
*   **Proposta de Valor:** Redução da carga de trabalho de gestores, aceleração do *onboarding* de novos funcionários e garantia de uma fonte de conhecimento interno precisa e imediata.

### 4.2. Aplicação Web (Chatbot Backend)

O sistema terminal é a prova de conceito do *backend* de gestão e contexto. A aplicação mais ampla do Agente ELOY já está em produção como um chatbot web, servindo como a principal vitrine do produto B2B.

*   **Link para Teste:** O agente ELOY da nossa empresa pode ser acessado através do link configurado no menu principal do sistema terminal: `https://eloy-ai.vercel.app/welcome`.

Este projeto demonstra, portanto, a capacidade de desenvolver tanto a **lógica de *backend* robusta** (sistema terminal) quanto a **aplicação de *frontend* escalável** (versão web), validando a viabilidade técnica e comercial do modelo de negócio.
