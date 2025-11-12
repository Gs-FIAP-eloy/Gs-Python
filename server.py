#!/usr/bin/env python3
# server.py — Eloy minimal REST API (Supabase + Groq)

import json
import os
import requests
import unicodedata
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

# ================= Util =================
SAUDACOES = ["oi","ola","olá","hey","hello","bom dia","boa tarde","boa noite"]

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ascii','ignore').decode('ascii').lower().strip()

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
def processar_com_groq(texto):
    texto = texto.strip()
    low = normalizar(texto)

    # ---------- Menu Principal ----------
    if low in SAUDACOES + ["menu","menu inicial", "menu principal"]:
        menu = (
            "👋 Olá! Aqui está o menu principal do Eloy:\n"
            "1 - Conversar com IA\n"
            "2 - Relatórios\n"
            "3 - Equipe\n"
            "4 - Site da Eloy\n"
            "5 - Sair / Desligar Eloy"
        )
        return {"resposta": menu, "action": "menu_principal"}

    # ---------- Menu Principal Opções ----------
    if low in ["1","conversar","ia"]:
        return {"resposta":"Olá! Como posso ajudá-lo hoje? Você pode digitar uma pergunta ou comando.","action":"conversar_ia"}
    if low in ["2","relatorios","relatorio"]:
        return {"resposta":"📊 MENU DE RELATÓRIOS: 1 - Adicionar relatório 2 - Ver relatório por data 3 - Listar relatórios existentes 4 - Editar relatório 5 - Remover relatório 6 - Voltar","action":"menu_relatorios"}
    if low in ["3","equipe","membro","funcionario"]:
        return {"resposta":"👥 MENU DA EQUIPE: 1 - Ver empresa 2 - Adicionar membro 3 - Remover membro 4 - Editar cargo 5 - Voltar","action":"menu_equipe"}
    if low in ["4","site"]:
        return {"resposta":"🌐 Abrindo o site da Eloy...","action":"abrir_site"}
    if low in ["5","sair","desligar"]:
        return {"resposta":"Encerrando conversa.","action":"sair"}

    # ---------- Menu Relatórios ----------
    if '|' in low:  # Adição/edição de relatório
        partes = texto.split('|',1)
        date, conteudo = partes[0].strip(), partes[1].strip()
        if len(date.split('/')) == 3:
            adicionar_relatorio(date, conteudo)
            return {"resposta": f"✅ Relatório de {date} adicionado com sucesso.\n📊 MENU DE RELATÓRIOS: 1 - Adicionar relatório 2 - Ver relatório por data 3 - Listar relatórios existentes 4 - Editar relatório 5 - Remover relatório 6 - Voltar","action":"menu_relatorios"}

    if low in ["1","adicionar","adicionar relatorio"]:
        return {"resposta":"Digite a data (DD/MM/AAAA) e o conteúdo do relatório separados por '|' (ex: 11/11/2025|Relatório aqui).","action":"add_relatorio"}
    if low in ["2","ver","ver relatorio","ver relatorios"]:
        rels = listar_relatorios()
        datas = [r["date"] for r in rels]
        return {"resposta": f"Relatórios disponíveis: {', '.join(datas) if datas else 'Nenhum relatório cadastrado.'}","action":"ver_relatorio"}
    if low in ["3","listar","listar relatorios"]:
        rels = listar_relatorios()
        datas = [r["date"] for r in rels]
        return {"resposta": f"Lista de relatórios: {', '.join(datas) if datas else 'Nenhum relatório cadastrado.'}","action":"listar_relatorio"}
    if low in ["4","editar","editar relatorio"]:
        return {"resposta":"Digite a data do relatório a editar e o novo conteúdo separados por '|' (ex: 11/11/2025|Novo conteúdo).","action":"editar_relatorio"}
    if low in ["5","remover","remover relatorio"]:
        return {"resposta":"Digite a data do relatório a remover:","action":"remover_relatorio"}
    if low in ["6","voltar","voltar menu"]:
        return {"resposta":"🔙 Retornando ao menu principal...","action":"menu_principal"}

    # ---------- Menu Equipe ----------
    if low in ["1","ver empresa","empresa"]:
        info = info_empresa()
        return {"resposta": f"🏢 Empresa: {info['nome']}\n📅 Fundação: {info['fundacao']}", "action":"menu_equipe"}
    if low in ["2","adicionar membro","adicionar"]:
        return {"resposta":"Digite o nome e cargo do novo membro separados por '|' (ex: Lucas|Desenvolvedor).","action":"add_membro"}
    if low in ["3","remover membro","remover"]:
        return {"resposta":"Digite o nome do membro a remover:","action":"remover_membro"}
    if low in ["4","editar cargo","editar"]:
        return {"resposta":"Digite o nome do membro e o novo cargo separados por '|' (ex: Lucas|Coordenador).","action":"editar_membro"}
    if low in ["5","voltar","voltar menu"]:
        return {"resposta":"🔙 Retornando ao menu principal...","action":"menu_principal"}

    # ---------- Sair ----------
    if any(kw in low for kw in ["tchau","sair","voltar","adeus"]):
        return {"resposta":"Encerrando conversa.","action":"sair"}

    # ---------- IA Normal ----------
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
        self.send_header("Access-Control-Allow-Origin", os.getenv("CORS_ORIGIN","*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def _read_json(self):
        length = int(self.headers.get('Content-Length',0))
        if length == 0: return {}
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
            rels = [r for r in listar_relatorios() if r["date"]==date]
            if rels:
                self._set_headers()
                self.wfile.write(json.dumps({"date": date,"conteudo": rels[0]["texto"]}).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error":"Relatório não encontrado"}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    # ================= POST =================
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path == "/api/chat":
            msg = body.get("mensagem","")
            result = processar_com_groq(msg)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/equipe":
            nome = body.get("nome")
            cargo = body.get("cargo","")
            if not nome:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error":"nome obrigatório"}).encode("utf-8"))
                return
            adicionar_funcionario(nome,cargo)
            self._set_headers(201)
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
            return

        if path == "/api/relatorios":
            date = body.get("date")
            texto = body.get("texto","")
            if not date or not texto:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error":"date e texto obrigatórios"}).encode("utf-8"))
                return
            adicionar_relatorio(date,texto)
            self._set_headers(201)
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    # ================= PUT =================
    def do_PUT(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path.startswith("/api/equipe/"):
            nome = unquote(path[len("/api/equipe/"):])
            novo_cargo = body.get("cargo","")
            atualizar_funcionario(nome, novo_cargo)
            self._set_headers()
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
            return

        if path.startswith("/api/relatorios/"):
            date = unquote(path[len("/api/relatorios/"):])
            texto = body.get("texto","")
            atualizar_relatorio(date,texto)
            self._set_headers()
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
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
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
            return

        if path.startswith("/api/relatorios/"):
            date = unquote(path[len("/api/relatorios/"):])
            remover_relatorio(date)
            self._set_headers()
            self.wfile.write(json.dumps({"ok":True}).encode("utf-8"))
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
