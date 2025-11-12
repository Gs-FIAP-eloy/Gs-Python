#!/usr/bin/env python3
# server.py — Eloy minimal REST API (Supabase + Groq)

import json
import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote
from supabase import create_client, Client

# ================= Config =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("ELOY_MODEL", "llama-3.3-70b-versatile")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PORT = int(os.getenv("PORT", "10000"))

# ================= Supabase helpers =================
def listar_funcionarios():
    res = supabase.table("funcionarios").select("*").execute()
    return res.data if res.data else []

def adicionar_funcionario(nome, cargo):
    supabase.table("funcionarios").insert({"nome": nome, "cargo": cargo}).execute()

def atualizar_funcionario(nome, cargo):
    supabase.table("funcionarios").update({"cargo": cargo}).eq("nome", nome).execute()

def remover_funcionario(nome):
    supabase.table("funcionarios").delete().eq("nome", nome).execute()

def listar_relatorios():
    res = supabase.table("relatorios").select("*").execute()
    return res.data if res.data else []

def adicionar_relatorio(date, texto):
    supabase.table("relatorios").insert({"date": date, "texto": texto}).execute()

def atualizar_relatorio(date, texto):
    supabase.table("relatorios").update({"texto": texto}).eq("date", date).execute()

def remover_relatorio(date):
    supabase.table("relatorios").delete().eq("date", date).execute()

def info_empresa():
    res = supabase.table("empresa").select("*").execute()
    return res.data[0] if res.data else {"nome": "Eloy Soluções Corporativas", "fundacao": "2025-11-09"}

# ================= IA / Processador de mensagens =================
SAUDACOES = ["oi","olá","ola","hey","hello","bom dia","boa tarde","boa noite"]

def processar_com_groq(texto):
    texto = texto.strip()
    low = texto.lower()

    # 1️⃣ Saudações curtas => menu principal
    if low in SAUDACOES:
        menu = (
            "👋 Olá! Aqui está o menu principal do Eloy:\n"
            "1 - Conversar com IA\n"
            "2 - Relatórios\n"
            "3 - Equipe\n"
            "4 - Site da Eloy\n"
            "5 - Sair / Desligar Eloy"
        )
        return {"resposta": menu, "action": "menu_principal"}

    # 2️⃣ Relatórios via formato data|conteúdo
    if '|' in texto:
        partes = texto.split('|',1)
        date, conteudo = partes[0].strip(), partes[1].strip()
        if len(date.split('/')) == 3:
            adicionar_relatorio(date, conteudo)
            return {"resposta": f"✅ Relatório de {date} adicionado com sucesso.\n📊 MENU DE RELATÓRIOS: 1 - Adicionar relatório 2 - Ver relatório por data 3 - Listar relatórios existentes 4 - Editar relatório 5 - Remover relatório 6 - Voltar", "action": "menu_relatorios"}

    # 3️⃣ Menu de relatórios
    if any(kw in low for kw in ["relatorio","relatório"]):
        return {"resposta":"📊 MENU DE RELATÓRIOS: 1 - Adicionar relatório 2 - Ver relatório por data 3 - Listar relatórios existentes 4 - Editar relatório 5 - Remover relatório 6 - Voltar","action":"menu_relatorios"}

    # 4️⃣ Menu de equipe
    if any(kw in low for kw in ["adicionar membro","membro","funcionario","funcionário","equipe"]):
        return {"resposta":"👥 MENU DA EQUIPE: 1 - Ver empresa 2 - Adicionar membro 3 - Remover membro 4 - Editar cargo 5 - Voltar","action":"menu_equipe"}

    # 5️⃣ Sair
    if any(kw in low for kw in ["tchau","sair","voltar","adeus"]):
        return {"resposta":"Encerrando conversa.","action":"sair"}

    # 6️⃣ IA normal
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        payload = {"model": MODEL,"messages":[{"role":"system","content":"Você é Eloy, assistente corporativo."},{"role":"user","content":texto}],"temperature":0.7}
        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices",[{}])[0].get("message",{}).get("content","")
            return {"resposta": resposta,"action":None}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e}).","action":None}
    else:
        return {"resposta": "Eloy (modo teste): " + texto,"action":None}

# ================= HTTP Handler =================
class EloyHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", os.getenv("CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
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

    # ================= GET =================
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/equipe":
            self._set_headers()
            self.wfile.write(json.dumps({
                "empresa": info_empresa(),
                "funcionarios": listar_funcionarios()
            }).encode("utf-8"))
            return

        if path == "/api/relatorios":
            self._set_headers()
            rels = listar_relatorios()
            datas = [r["date"] for r in rels]
            self.wfile.write(json.dumps({"relatorios": datas}).encode("utf-8"))
            return

        if path.startswith("/api/relatorios/"):
            date = unquote(path[len("/api/relatorios/"):])
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if rels:
                self._set_headers()
                self.wfile.write(json.dumps({"date": date, "conteudo": rels[0]["texto"]}).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Relatório não encontrado"}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    # ================= POST =================
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path == "/api/chat":
            msg = body.get("mensagem", "")
            result = processar_com_groq(msg)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/equipe":
            nome = body.get("nome")
            cargo = body.get("cargo", "")
            if not nome:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error":"nome obrigatório"}).encode("utf-8"))
                return
            adicionar_funcionario(nome, cargo)
            self._set_headers(201)
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if path == "/api/relatorios":
            date = body.get("date")
            texto = body.get("texto","")
            if not date or not texto:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error":"date e texto obrigatórios"}).encode("utf-8"))
                return
            adicionar_relatorio(date, texto)
            self._set_headers(201)
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    # ================= PUT =================
    def do_PUT(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path.startswith("/api/equipe/"):
            nome = unquote(path[len("/api/equipe/"):])
            novo_cargo = body.get("cargo", "")
            atualizar_funcionario(nome, novo_cargo)
            self._set_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if path.startswith("/api/relatorios/"):
            date = unquote(path[len("/api/relatorios/"):])
            texto = body.get("texto", "")
            atualizar_relatorio(date, texto)
            self._set_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    # ================= DELETE =================
    def do_DELETE(self):
        path = urlparse(self.path).path

        if path.startswith("/api/equipe/"):
            nome = unquote(path[len("/api/equipe/"):])
            remover_funcionario(nome)
            self._set_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if path.startswith("/api/relatorios/"):
            date = unquote(path[len("/api/relatorios/"):])
            remover_relatorio(date)
            self._set_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

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
