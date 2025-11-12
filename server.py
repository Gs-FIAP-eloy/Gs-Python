#!/usr/bin/env python3
# server.py — Eloy minimal REST API (Chat Bot)

import json
import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# ================= Config =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("ELOY_MODEL", "llama-3.3-70b-versatile")
PORT = int(os.getenv("PORT", "10000"))

# ================= IA / Processador de mensagens =================
SAUDACOES = ["oi", "olá", "ola", "hey", "hello", "bom dia", "boa tarde", "boa noite"]

def processar_com_groq(texto, contexto=None):
    texto = texto.strip()
    contexto = contexto or {}

    # Saudações
    if texto.lower() in SAUDACOES:
        return {"resposta": "👋 Olá! Sou Eloy, seu assistente corporativo. Vamos conversar!", "contexto": contexto}

    # Chat com IA
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Você é Eloy, assistente corporativo amigável e prestativo."},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.7
        }
        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"resposta": resposta, "contexto": contexto}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e})", "contexto": contexto}
    else:
        # Modo teste
        return {"resposta": "Eloy (modo teste): " + texto, "contexto": contexto}

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

# ================= Run =================
def run(server_class=HTTPServer, handler_class=EloyHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"🌐 Eloy server listening at http://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
