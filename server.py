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

COMANDOS_RELATORIO = ["adicionar relatorio", "ver relatorio", "listar relatorio", "editar relatorio", "remover relatorio"]
COMANDOS_MEMBRO = ["adicionar membro", "remover membro", "editar membro", "ver membro"]

def processar_com_groq(texto, contexto=None):
    texto = texto.strip()
    low = texto.lower()
    contexto = contexto or {}

    # ================= Saudações e instruções iniciais =================
    if low in SAUDACOES:
        return {
            "resposta":"👋 Olá! Posso conversar com você normalmente ou ajudá-lo com relatórios e equipe.\nDigite 'relatorios' para ver opções de relatórios ou 'equipe' para gerenciar membros.",
            "action": None,
            "contexto": contexto
        }

    # ================= Mostrar menus =================
    if low == "relatorios":
        return {"resposta":"Você está no módulo de relatórios. 📊 Opções: " + ", ".join(COMANDOS_RELATORIO),
                "action":"menu_relatorios","contexto": contexto}
    if low == "equipe":
        return {"resposta":"Você está no módulo de equipe. 👥 Opções: " + ", ".join(COMANDOS_MEMBRO),
                "action":"menu_equipe","contexto": contexto}

    # ================= Relatórios =================
    if low in COMANDOS_RELATORIO:
        contexto["modo"] = "relatorio"
        contexto["acao"] = low
        if low == "adicionar relatorio":
            return {"resposta":"Digite a data (DD/MM/AAAA) e o conteúdo separados por '|' (ex: 11/11/2025|Relatório aqui).",
                    "action":"add_relatorio","contexto": contexto}
        elif low == "ver relatorio":
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":f"Relatórios disponíveis: {', '.join(datas)}\nDigite a data desejada (DD/MM/AAAA) para visualizar:",
                        "action":"ver_relatorio","contexto": contexto}
            else:
                return {"resposta":"Nenhum relatório cadastrado.","action":None,"contexto": contexto}
        elif low == "listar relatorio":
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":"Lista de relatórios: " + ", ".join(datas),"action":None,"contexto": contexto}
            else:
                return {"resposta":"Lista de relatórios: Nenhum relatório cadastrado.","action":None,"contexto": contexto}
        elif low == "editar relatorio":
            return {"resposta":"Digite a data (DD/MM/AAAA) e o novo conteúdo separados por '|' (ex: 11/11/2025|Novo conteúdo).",
                    "action":"edit_relatorio","contexto": contexto}
        elif low == "remover relatorio":
            return {"resposta":"Digite a data (DD/MM/AAAA) do relatório que deseja remover:",
                    "action":"remove_relatorio","contexto": contexto}

    # ================= Membros =================
    if low in COMANDOS_MEMBRO:
        contexto["modo"] = "membro"
        contexto["acao"] = low
        if low == "adicionar membro":
            return {"resposta":"Digite o nome e cargo separados por '|' (ex: Lucas Toledo|Desenvolvedor).",
                    "action":"add_membro","contexto": contexto}
        elif low == "remover membro":
            return {"resposta":"Digite o nome do membro a remover:","action":"remove_membro","contexto": contexto}
        elif low == "editar membro":
            return {"resposta":"Digite o nome e novo cargo separados por '|' (ex: Lucas Toledo|Coordenador).",
                    "action":"edit_membro","contexto": contexto}
        elif low == "ver membro":
            funcionarios = listar_funcionarios()
            lista = "\n".join([f"{f['nome']} ({f['cargo']})" for f in funcionarios])
            resp = f"👥 Funcionários:\n{lista if lista else 'Nenhum funcionário cadastrado.'}"
            return {"resposta": resp,"action":None,"contexto": contexto}

    # ================= Mensagem de instrução para palavra isolada =================
    palavras = low.split()
    if len(palavras) == 1 and palavras[0] in ["adicionar","remover","editar","ver","listar"]:
        return {"resposta": f"⚠️ Por favor, use o comando composto completo (por exemplo: '{palavras[0]} relatorio' ou '{palavras[0]} membro').",
                "action": None,"contexto": contexto}

    # ================= Processar ações já em andamento =================
    if contexto.get("modo") == "relatorio":
        if contexto.get("acao") == "adicionar relatorio" and "|" in texto:
            date, conteudo = texto.split("|",1)
            adicionar_relatorio(date.strip(), conteudo.strip())
            return {"resposta":f"✅ Relatório de {date.strip()} adicionado com sucesso.","action":None,"contexto": contexto}
        elif contexto.get("acao") == "editar relatorio" and "|" in texto:
            date, conteudo = texto.split("|",1)
            atualizar_relatorio(date.strip(), conteudo.strip())
            return {"resposta":f"✏️ Relatório de {date.strip()} atualizado.","action":None,"contexto": contexto}
        elif contexto.get("acao") == "remove_relatorio":
            date = texto.strip()
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if rels:
                remover_relatorio(date)
                return {"resposta":f"🗑️ Relatório de {date} removido.","action":None,"contexto": contexto}
            else:
                datas = [r["date"] for r in listar_relatorios()]
                return {"resposta": f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}","action":None,"contexto": contexto}
        elif contexto.get("acao") == "ver relatorio":
            date = texto.strip()
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if rels:
                return {"resposta": f"📄 {date}: {rels[0]['texto']}","action":None,"contexto": contexto}
            else:
                datas = [r["date"] for r in listar_relatorios()]
                return {"resposta": f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}","action":None,"contexto": contexto}

    if contexto.get("modo") == "membro":
        if contexto.get("acao") == "add_membro" and "|" in texto:
            nome, cargo = texto.split("|",1)
            adicionar_funcionario(nome.strip(), cargo.strip())
            return {"resposta":f"✅ Membro {nome.strip()} adicionado com sucesso.","action":None,"contexto": contexto}
        elif contexto.get("acao") == "edit_membro" and "|" in texto:
            nome, cargo = texto.split("|",1)
            atualizar_funcionario(nome.strip(), cargo.strip())
            return {"resposta":f"✏️ Cargo de {nome.strip()} atualizado para {cargo.strip()}.","action":None,"contexto": contexto}
        elif contexto.get("acao") == "remove_membro":
            nome = texto.strip()
            funcionarios = [f for f in listar_funcionarios() if f["nome"].lower() != nome.lower()]
            if len(funcionarios) != len(listar_funcionarios()):
                remover_funcionario(nome)
                return {"resposta":f"🗑️ Membro {nome} removido.","action":None,"contexto": contexto}
            else:
                return {"resposta":f"⚠️ Membro não encontrado.","action":None,"contexto": contexto}

    # ================= Chat normal =================
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        payload = {"model": MODEL,"messages":[{"role":"system","content":"Você é Eloy, assistente corporativo."},{"role":"user","content":texto}],"temperature":0.7}
        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices",[{}])[0].get("message",{}).get("content","")
            return {"resposta": resposta,"action":None,"contexto": contexto}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e}).","action":None,"contexto": contexto}
    else:
        return {"resposta": "Eloy (modo teste): " + texto,"action":None,"contexto": contexto}

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
