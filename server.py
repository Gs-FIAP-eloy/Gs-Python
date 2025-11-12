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
def processar_com_groq(texto, contexto=None):
    texto = texto.strip()
    low = texto.lower()
    contexto = contexto or {"modo": "chat", "acao": None}

    # ================= Comandos compostos =================
    COMANDOS_RELATORIO = [
        "adicionar relatorio",
        "ver relatorio",
        "listar relatorio",
        "editar relatorio",
        "remover relatorio"
    ]
    COMANDOS_MEMBRO = [
        "adicionar membro",
        "ver membro",
        "editar membro",
        "remover membro"
    ]

    # ================= Ativação de módulos =================
    if low in ["relatorios", "relatorio"]:
        contexto["modo"] = "relatorio"
        contexto["acao"] = None
        return {
            "resposta": "Você está no módulo de relatórios. 📊 Opções: " + ", ".join(COMANDOS_RELATORIO),
            "acao": None,
            "contexto": contexto
        }

    if low in ["equipe", "membros", "funcionarios"]:
        contexto["modo"] = "membro"
        contexto["acao"] = None
        return {
            "resposta": "Você está no módulo de equipe. 👥 Opções: " + ", ".join(COMANDOS_MEMBRO),
            "acao": None,
            "contexto": contexto
        }

    # ================= Módulo Relatórios =================
    if contexto.get("modo") == "relatorio":
        if low in [c for c in COMANDOS_RELATORIO if " " not in c]:
            return {"resposta": "⚠️ Por favor, use o comando composto completo (por exemplo: 'adicionar relatorio').",
                    "acao": None, "contexto": contexto}

        if low == "adicionar relatorio":
            contexto["acao"] = "adicionar relatorio"
            return {"resposta": "Digite a data (DD/MM/AAAA) e o conteúdo separados por '|' (ex: 11/11/2025|Relatório aqui).",
                    "acao": None, "contexto": contexto}

        if low == "listar relatorio":
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta": "Lista de relatórios: " + ", ".join(datas),
                        "acao": None, "contexto": contexto}
            return {"resposta": "Lista de relatórios: Nenhum relatório cadastrado.",
                    "acao": None, "contexto": contexto}

        if low == "ver relatorio":
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                contexto["acao"] = "ver relatorio"
                return {"resposta": f"Relatórios disponíveis: {', '.join(datas)}\nDigite a data desejada (DD/MM/AAAA):",
                        "acao": None, "contexto": contexto}
            return {"resposta": "Nenhum relatório cadastrado.",
                    "acao": None, "contexto": contexto}

        if low == "editar relatorio":
            contexto["acao"] = "editar relatorio"
            return {"resposta": "Digite a data (DD/MM/AAAA) e o novo conteúdo separados por '|' (ex: 11/11/2025|Novo conteúdo).",
                    "acao": None, "contexto": contexto}

        if low == "remover relatorio":
            contexto["acao"] = "remover relatorio"
            return {"resposta": "Digite a data (DD/MM/AAAA) do relatório a remover:",
                    "acao": None, "contexto": contexto}

        # ========== Processar ações com dados ==========
        if "|" in texto and contexto.get("acao") in ["adicionar relatorio", "editar relatorio"]:
            date, conteudo = [p.strip() for p in texto.split("|", 1)]
            if len(date.split("/")) == 3:
                if contexto["acao"] == "adicionar relatorio":
                    adicionar_relatorio(date, conteudo)
                    return {"resposta": f"✅ Relatório {date} adicionado.",
                            "acao": None, "contexto": contexto}
                elif contexto["acao"] == "editar relatorio":
                    atualizar_relatorio(date, conteudo)
                    return {"resposta": f"✏️ Relatório {date} atualizado.",
                            "acao": None, "contexto": contexto}
        elif contexto.get("acao") in ["ver relatorio", "remover relatorio"]:
            date = texto.strip()
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if contexto["acao"] == "ver relatorio":
                if rels:
                    return {"resposta": f"📄 {date}: {rels[0]['texto']}", "acao": None, "contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta": f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}",
                            "acao": None, "contexto": contexto}
            elif contexto["acao"] == "remover relatorio":
                if rels:
                    remover_relatorio(date)
                    return {"resposta": f"🗑️ Relatório {date} removido.", "acao": None, "contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta": f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}",
                            "acao": None, "contexto": contexto}

    # ================= Módulo Membros =================
    if contexto.get("modo") == "membro":
        if low in [c for c in COMANDOS_MEMBRO if " " not in c]:
            return {"resposta": "⚠️ Por favor, use o comando composto completo (por exemplo: 'adicionar membro').",
                    "acao": None, "contexto": contexto}

        if low == "adicionar membro":
            contexto["acao"] = "adicionar membro"
            return {"resposta": "Digite o nome e cargo separados por '|' (ex: Lucas Toledo|Desenvolvedor).",
                    "acao": None, "contexto": contexto}

        if low == "editar membro":
            contexto["acao"] = "editar membro"
            return {"resposta": "Digite o nome e novo cargo separados por '|' (ex: Lucas Toledo|Coordenador).",
                    "acao": None, "contexto": contexto}

        if low == "remover membro":
            contexto["acao"] = "remover membro"
            return {"resposta": "Digite o nome do membro a remover:", "acao": None, "contexto": contexto}

        if low == "ver membro":
            funcionarios = listar_funcionarios()
            if funcionarios:
                lista = "\n".join([f"{f['nome']} ({f['cargo']})" for f in funcionarios])
                return {"resposta": f"👥 Funcionários:\n{lista}", "acao": None, "contexto": contexto}
            return {"resposta": "Nenhum membro cadastrado.", "acao": None, "contexto": contexto}

        # ========== Processar ações com dados ==========
        if "|" in texto and contexto.get("acao") in ["adicionar membro", "editar membro"]:
            nome, cargo = [p.strip() for p in texto.split("|", 1)]
            if contexto["acao"] == "adicionar membro":
                adicionar_funcionario(nome, cargo)
                return {"resposta": f"✅ Membro {nome} adicionado.", "acao": None, "contexto": contexto}
            elif contexto["acao"] == "editar membro":
                atualizar_funcionario(nome, cargo)
                return {"resposta": f"✏️ Cargo de {nome} atualizado para {cargo}.", "acao": None, "contexto": contexto}
        elif contexto.get("acao") == "remover membro":
            nome = texto.strip()
            funcionarios = [f for f in listar_funcionarios() if f["nome"].lower() != nome.lower()]
            if len(funcionarios) != len(listar_funcionarios()):
                remover_funcionario(nome)
                return {"resposta": f"🗑️ Membro {nome} removido.", "acao": None, "contexto": contexto}
            return {"resposta": "⚠️ Membro não encontrado.", "acao": None, "contexto": contexto}

    # ================= Chat normal =================
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL, "messages": [{"role":"system","content":"Você é Eloy, assistente corporativo."},{"role":"user","content":texto}], "temperature":0.7}
        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices",[{}])[0].get("message",{}).get("content","")
            return {"resposta": resposta, "acao": None, "contexto": contexto}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e})", "acao": None, "contexto": contexto}
    else:
        return {"resposta": "Eloy (modo teste): " + texto, "acao": None, "contexto": contexto}

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
            contexto = body.get("contexto", {"modo": "chat"})
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
