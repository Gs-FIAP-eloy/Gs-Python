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

def processar_com_groq(texto, contexto=None):
    texto = texto.strip()
    low = texto.lower()
    contexto = contexto or {"modo": "chat", "action": None}

    # ================= Contexto Relatorios =================
    if contexto.get("modo") == "relatorios":
        # Comandos prioritários
        if "adicionar" in low:
            contexto["action"] = "add_relatorio"
            return {"resposta":"Digite a data (DD/MM/AAAA) e o conteúdo do relatório separados por '|' (ex: 11/11/2025|Relatório aqui).", "contexto": contexto}
        elif "ver" in low:
            contexto["action"] = "ver_relatorio"
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":f"Relatórios disponíveis: {', '.join(datas)}\nDigite a data desejada (DD/MM/AAAA) para visualizar:", "contexto": contexto}
            else:
                return {"resposta":"Nenhum relatório cadastrado.", "contexto": contexto}
        elif "listar" in low:
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":"Lista de relatórios: " + ", ".join(datas), "contexto": contexto}
            else:
                return {"resposta":"Lista de relatórios: Nenhum relatório cadastrado.", "contexto": contexto}
        elif "editar" in low:
            contexto["action"] = "edit_relatorio"
            return {"resposta":"Digite a data (DD/MM/AAAA) do relatório que deseja editar e o novo conteúdo separados por '|' (ex: 11/11/2025|Novo conteúdo).", "contexto": contexto}
        elif "remover" in low:
            contexto["action"] = "remove_relatorio"
            return {"resposta":"Digite a data (DD/MM/AAAA) do relatório que deseja remover:", "contexto": contexto}
        elif "voltar" in low or "menu" in low:
            contexto["modo"] = "chat"
            contexto["action"] = None
            return {"resposta":"Voltando ao chat normal. Você pode perguntar sobre relatórios ou equipe quando quiser.", "contexto": contexto}
        # Processa inputs específicos de ação
        elif "|" in texto and contexto.get("action") in ["add_relatorio","edit_relatorio"]:
            partes = texto.split("|",1)
            date, conteudo = partes[0].strip(), partes[1].strip()
            if len(date.split("/")) == 3:
                if contexto.get("action") == "add_relatorio":
                    adicionar_relatorio(date, conteudo)
                    contexto["action"] = None
                    return {"resposta":f"✅ Relatório de {date} adicionado com sucesso.", "contexto": contexto}
                elif contexto.get("action") == "edit_relatorio":
                    atualizar_relatorio(date, conteudo)
                    contexto["action"] = None
                    return {"resposta":f"✏️ Relatório de {date} atualizado com sucesso.", "contexto": contexto}
        elif contexto.get("action") in ["ver_relatorio","remove_relatorio"]:
            date = texto.strip()
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if contexto.get("action") == "ver_relatorio":
                if rels:
                    contexto["action"] = None
                    return {"resposta":f"📄 {date}: {rels[0]['texto']}", "contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta":f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}", "contexto": contexto}
            elif contexto.get("action") == "remove_relatorio":
                if rels:
                    remover_relatorio(date)
                    contexto["action"] = None
                    return {"resposta":f"🗑️ Relatório de {date} removido.", "contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta":f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}", "contexto": contexto}
        else:
            return {"resposta":"Opção inválida. Digite: adicionar, ver, listar, editar, remover ou voltar.", "contexto": contexto}

    # ================= Contexto Equipe =================
    if contexto.get("modo") == "equipe":
        if "ver" in low:
            empresa = info_empresa()
            funcionarios = listar_funcionarios()
            lista = "\n".join([f"{f['nome']} ({f['cargo']})" for f in funcionarios])
            contexto["action"] = None
            return {"resposta":f"🏢 Empresa: {empresa['nome']}\n📅 Fundação: {empresa['fundacao']}\n👤 Funcionários:\n{lista if lista else 'Nenhum funcionário cadastrado.'}", "contexto": contexto}
        elif "adicionar" in low:
            contexto["action"] = "add_membro"
            return {"resposta":"Digite o nome e cargo do membro separados por '|' (ex: Lucas Toledo|Desenvolvedor).", "contexto": contexto}
        elif "remover" in low:
            contexto["action"] = "remove_membro"
            return {"resposta":"Digite o nome do membro a remover:", "contexto": contexto}
        elif "editar" in low:
            contexto["action"] = "edit_membro"
            return {"resposta":"Digite o nome do membro e novo cargo separados por '|' (ex: Lucas Toledo|Coordenador).", "contexto": contexto}
        elif "voltar" in low or "menu" in low:
            contexto["modo"] = "chat"
            contexto["action"] = None
            return {"resposta":"Voltando ao chat normal. Você pode perguntar sobre relatórios ou equipe quando quiser.", "contexto": contexto}
        # Processa inputs específicos de ação
        elif "|" in texto and contexto.get("action") in ["add_membro","edit_membro"]:
            partes = texto.split("|",1)
            nome, cargo = partes[0].strip(), partes[1].strip()
            if contexto.get("action") == "add_membro":
                adicionar_funcionario(nome, cargo)
                contexto["action"] = None
                return {"resposta":f"✅ Membro {nome} adicionado com sucesso.", "contexto": contexto}
            elif contexto.get("action") == "edit_membro":
                atualizar_funcionario(nome, cargo)
                contexto["action"] = None
                return {"resposta":f"✏️ Cargo de {nome} atualizado para {cargo}.", "contexto": contexto}
        elif contexto.get("action") == "remove_membro":
            nome = texto.strip()
            funcionarios = [f for f in listar_funcionarios() if f["nome"].lower() != nome.lower()]
            if len(funcionarios) != len(listar_funcionarios()):
                remover_funcionario(nome)
                contexto["action"] = None
                return {"resposta":f"🗑️ Membro {nome} removido.", "contexto": contexto}
            else:
                return {"resposta":f"⚠️ Membro não encontrado.", "contexto": contexto}
        else:
            return {"resposta":"Opção inválida. Digite: ver, adicionar, remover, editar ou voltar.", "contexto": contexto}

    # ================= Chat normal =================
    if low in SAUDACOES:
        return {"resposta":"👋 Olá! Posso conversar com você normalmente ou ajudá-lo com relatórios e equipe. Digite 'relatorios' ou 'equipe' para começar.", "contexto": contexto}
    elif "relatorios" in low:
        contexto["modo"] = "relatorios"
        return {"resposta":"Você está no módulo de relatórios. 📊 Opções de Relatórios: adicionar, ver, listar, editar, remover", "contexto": contexto}
    elif "equipe" in low:
        contexto["modo"] = "equipe"
        return {"resposta":"Você está no módulo de equipe. 👥 Opções: ver, adicionar, remover, editar", "contexto": contexto}

    # Fallback para IA
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        payload = {"model": MODEL,"messages":[{"role":"system","content":"Você é Eloy, assistente corporativo."},{"role":"user","content":texto}],"temperature":0.7}
        try:
            res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()
            resposta = data.get("choices",[{}])[0].get("message",{}).get("content","")
            return {"resposta": resposta,"contexto": contexto}
        except Exception as e:
            return {"resposta": f"(Erro ao consultar a IA: {e}).","contexto": contexto}
    else:
        return {"resposta": "Eloy (modo teste): " + texto,"contexto": contexto}

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
