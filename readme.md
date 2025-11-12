# 🤖 Eloy – Assistente Técnico Corporativo

> **Sistema interativo de linha de comando (CLI) com integração à inteligência artificial Groq, projetado para simular um ambiente digital corporativo.**
>
> Desenvolvido como projeto acadêmico por alunos da **FIAP**, o Eloy simula o ambiente da empresa **Eloy Soluções Corporativas**, oferecendo funcionalidades de controle interno, chat de suporte técnico e gerenciamento de dados empresariais.

---

## 🧩 Sumário

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Execução e Instalação](#-execução-e-instalação)
- [Configuração da API Groq](#-configuração-da-api-groq)
- [Banco de Dados Local (`dados.json`)](#-banco-de-dados-local-dadosjson)
- [Integrantes do Projeto](#-integrantes-do-projeto)
- [Melhorias Futuras](#-melhorias-futuras)
- [Licença](#-licença)

---

## 📘 Visão Geral

O **Eloy** é um sistema corporativo de linha de comando (CLI) que se destaca pela sua integração com uma **Inteligência Artificial real** fornecida pela Groq. O sistema foi concebido para ser uma ferramenta de **assistência técnica corporativa**, oferecendo uma interface textual limpa, menus dinâmicos e persistência de dados em formato JSON.

O assistente “Eloy” atua como um **consultor técnico**, fornecendo respostas curtas, diretas e profissionais. Sua capacidade de resposta é aprimorada pelo uso de **RAG (Retrieval Augmented Generation)**, onde o contexto é extraído dos dados locais da empresa armazenados no arquivo `dados.json`.

---

## ⚙️ Funcionalidades

O sistema Eloy é modularizado para gerenciar diferentes aspectos do ambiente corporativo:

### 🧠 Módulo de Inteligência Artificial

- **Chat Interativo:** Conversa direta com o assistente **Eloy** utilizando a **Groq API** (modelo `llama-3.3-70b-versatile`).
- **Respostas Contextuais:** Geração de respostas curtas, profissionais e contextuais, baseadas no banco de dados da empresa via RAG.

### 💾 Módulo de Dados e Persistência

- **Banco de Dados Dinâmico:** Armazenamento local e persistente de dados em **`dados.json`**.
- **Inicialização Automática:** Criação de uma estrutura inicial de dados caso o arquivo `dados.json` não seja encontrado.

### 📊 Módulo de Relatórios

- **Gerenciamento Completo:** Permite adicionar, editar, remover, listar e visualizar relatórios internos por data.
- **Interface Otimizada:** Navegação interativa através de menus numéricos.

### 👥 Módulo de Equipe

- **Controle de Membros:** Visualização, adição, edição de cargos e remoção de membros da equipe.

### 💼 Módulo de Projetos

- **Gestão de Projetos:** Facilita o gerenciamento de projetos ativos da empresa, com opções para adicionar e remover projetos.

### 🎨 Interface e Usabilidade

- **Estilização Profissional:** Uso de **cores ANSI** para uma interface de terminal visualmente agradável.
- **Robustez:** Sistema de entrada validada para prevenir erros de digitação e garantir a integridade da operação.

---

## 📚 Tecnologias Utilizadas

| Tecnologia | Descrição |
| :--- | :--- |
| **Python 3.10+** | Linguagem de programação principal. |
| **Groq API** | Serviço de IA de alta velocidade (compatível com OpenAI) para o assistente Eloy. |
| **JSON** | Formato de arquivo para persistência e armazenamento do banco de dados local (`dados.json`). |
| **Requests** | Biblioteca Python para realizar requisições HTTP (comunicação com a Groq API). |
| **Webbrowser** | Módulo Python para integração com o navegador padrão (acesso ao site da empresa). |
| **ANSI Colors** | Utilizado para estilização e melhoria da experiência visual no terminal. |

---

## 📂 Estrutura do Projeto

```
📁 Eloy/
│
├── eloy.py           # Código principal do sistema e lógica de negócios
├── dados.json        # Banco de dados local (persistência de dados)
├── README.md         # Documentação do projeto
└── requirements.txt  # Dependências do projeto (a ser adicionado)
```

---

## 🖥️ Execução e Instalação

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local:

1. **Instale o Python 3.10+** (ou versão superior).

2. **Clone o repositório** (ou baixe os arquivos):

   ```bash
   git clone https://github.com/seuusuario/eloy-assistente.git
   cd eloy-assistente
   ```

3. **Instale as dependências** (se houver um `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure a chave da API Groq** (veja a seção abaixo).

5. **Execute o programa:**

   ```bash
   python eloy.py
   ```

6. Interaja com o menu principal e explore as opções do assistente Eloy.

---

## 🧠 Configuração da API Groq

O Eloy utiliza a **Groq OpenAI-Compatible API** para se conectar a modelos de linguagem de última geração.

### 🔑 Obtenção e Configuração da Chave

1. Obtenha sua chave de API no [console.groq.com](https://console.groq.com).
2. Localize no código (`eloy.py` ou arquivo de configuração) a variável de chave da API:

   ```python
   GROQ_API_KEY = "SUA_CHAVE_AQUI"
   ```

3. Substitua o valor pelo seu token pessoal. **Recomenda-se o uso de variáveis de ambiente** para maior segurança.

### 📡 Detalhes da Integração

| Parâmetro | Valor |
| :--- | :--- |
| **Endpoint** | `https://api.groq.com/openai/v1/chat/completions` |
| **Modelo** | `llama-3.3-70b-versatile` |
| **Temperatura** | `0.6` (Configurado para respostas curtas e profissionais) |

---

## 💾 Banco de Dados Local (`dados.json`)

O arquivo `dados.json` é o coração da persistência de dados do sistema, armazenando todas as informações da empresa utilizadas pelo assistente Eloy (RAG).

### Exemplo de Estrutura Padrão

```json
{
  "empresa": {
    "nome": "Eloy Soluções Corporativas",
    "fundacao": "09/11/2025"
  },
  "funcionarios": [
    {
      "nome": "Lucas Toledo",
      "cargo": "Engenheiro de Software / Coordenador do projeto"
    },
    // ... outros funcionários
  ],
  "projetos": [
    "Site Eloy",
    "Sistema de Gestão Interna",
    // ... outros projetos
  ],
  "relatorios": {}
}
```

Este arquivo é criado e atualizado automaticamente pelo sistema conforme as ações do usuário.

---

## 🧑‍💻 Integrantes do Projeto

Este projeto foi desenvolvido pelos seguintes alunos da FIAP:

| Nome Completo | RA | Função no Projeto |
| :--- | :--- | :--- |
| **Lucas Toledo Cortonezi** | 563271 | Engenheiro de Software / Coordenador do Projeto |
| **Leonardo da Silva Pinto** | 564929 | Desenvolvedor Full Stack |
| **Samuel Enzo D. Monteiro** | 564391 | Analista de Sistemas |

---

## 🚀 Melhorias Futuras

A lista de melhorias futuras foi mantida para fins de documentação, mas não foi detalhada no conteúdo original. Para um README profissional, esta seção deve ser preenchida com itens específicos.

---

## 📄 Licença

Este projeto foi desenvolvido para fins **educacionais e acadêmicos**.

Todos os direitos reservados © 2025 – Eloy Soluções Corporativas.
