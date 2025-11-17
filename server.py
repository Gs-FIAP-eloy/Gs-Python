#!/usr/bin/env python3
# server.py — Eloy minimal REST API (apenas chat via Groq)

import os
import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# ================= Config =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY" )
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("ELOY_MODEL", "llama-3.3-70b-versatile" )
PORT = int(os.getenv("PORT", "10000"))

# ================= IA / Processador de mensagens =================
SAUDACOES = ["oi", "olá", "ola", "hey", "hello", "bom dia", "boa tarde", "boa noite"]

# Conteúdo do RAG (Documento de Geração Aumentada por Recuperação - Eloy)
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

def processar_com_groq(texto, contexto=None):
    texto = texto.strip()
    low = texto.lower()
    contexto = contexto or {}

    # Saudações
    if low in SAUDACOES:
        return {
            "resposta": "👋 Olá! Eu sou Eloy, seu assistente corporativo. Podemos conversar normalmente.",
            "action": None,
            "contexto": contexto
        }

    # Chat normal
    if GROQ_API_KEY:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # O novo prompt de sistema incorpora o conteúdo do RAG e as diretrizes de personalidade
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
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.5
        }


        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"resposta": resposta, "action": None, "contexto": contexto}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e})", "action": None, "contexto": contexto}
    else:
        # Modo teste sem chave
        return {"resposta": "Eloy (modo teste): " + texto, "action": None, "contexto": contexto}

# ================= HTTP Handler =================
class EloyHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", os.getenv("CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode('utf-8')
        try:
            return json.loads(raw)
        except:
            return {}

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path == "/api/chat":
            msg = body.get("mensagem", "")
            contexto = body.get("contexto", {})
            result = processar_com_groq(msg, contexto)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "rota não encontrada"}).encode("utf-8"))

    def do_GET(self):
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "rota não encontrada"}).encode("utf-8"))

# ================= Run =================
def run(server_class=HTTPServer, handler_class=EloyHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class )
    print(f"🌐 Eloy server listening at http://0.0.0.0:{port}" )
    try:
        httpd.serve_forever( )
    except KeyboardInterrupt:
        pass
    httpd.server_close( )

if __name__ == '__main__':
    run()
