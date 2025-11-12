#!/usr/bin/env python3
import os
import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# ================= Config =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("ELOY_MODEL", "llama-3.3-70b-versatile")
PORT = int(os.getenv("PORT", "10000"))

# ================= System Prompt da Eloy =================
SYSTEM_PROMPT = """Você é Eloy, assistente inteligente da empresa Eloy Soluções Corporativas.

Informações sobre a Eloy:
- Nome da Empresa: Eloy Soluções Corporativas
- Data de Criação: 09/11/2025
- Equipe: Lucas Toledo, Samuel Monteiro, Leonardo Silva
- Especialidade: Soluções corporativas inovadoras

Você responde perguntas sobre a empresa, sua equipe, história e serviços com precisão e profissionalismo. 
Seja amigável, prestativo e sempre representa bem a marca Eloy."""

# ================= Chat com Grok =================
def chat_com_grok(mensagem_usuario: str) -> str:
    """Envia mensagem ao Grok e retorna a resposta"""
    if not XAI_API_KEY:
        return "❌ Erro: Chave de API Grok não configurada. Configure XAI_API_KEY nas variáveis de ambiente."
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensagem_usuario}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(GROK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        resposta = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not resposta:
            return "⚠️ Resposta vazia do Grok. Tente novamente."
        
        return resposta
    
    except requests.exceptions.Timeout:
        return "⏱️ Timeout ao conectar ao Grok. Tente novamente."
    except requests.exceptions.RequestException as e:
        return f"❌ Erro na requisição ao Grok: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"

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
        """Lê JSON do corpo da requisição"""
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        try:
            raw = self.rfile.read(length).decode('utf-8')
            return json.loads(raw)
        except:
            return {}
    
    def log_message(self, format, *args):
        """Silencia logs padrão do servidor"""
        pass
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == "/api/chat":
            body = self._read_json()
            mensagem = body.get("mensagem", "").strip()
            
            if not mensagem:
                self._set_headers(400)
                self.wfile.write(json.dumps({"erro": "Mensagem vazia"}).encode("utf-8"))
                return
            
            # Envia para Grok e retorna resposta
            resposta = chat_com_grok(mensagem)
            
            self._set_headers()
            self.wfile.write(json.dumps({
                "resposta": resposta,
                "status": "sucesso"
            }).encode("utf-8"))
            return
        
        # Health check endpoint
        if path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "online", "servico": "Eloy Chatbot"}).encode("utf-8"))
            return
        
        self._set_headers(404)
        self.wfile.write(json.dumps({"erro": "Rota não encontrada"}).encode("utf-8"))
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "online", "servico": "Eloy Chatbot"}).encode("utf-8"))
            return
        
        if path == "/":
            self._set_headers(200, "text/plain")
            self.wfile.write(b"Eloy Chatbot - Envie POST para /api/chat com {'mensagem': 'sua_mensagem'}")
            return
        
        self._set_headers(404)
        self.wfile.write(json.dumps({"erro": "Rota não encontrada"}).encode("utf-8"))

# ================= Run =================
def run(server_class=HTTPServer, handler_class=EloyHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"🌐 Eloy Chatbot listening at http://0.0.0.0:{port}")
    print(f"📝 POST /api/chat para enviar mensagens")
    print(f"💚 GET /health para verificar status")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Servidor encerrado")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run()
