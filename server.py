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

    contexto = contexto or {"menu": "principal"}

    # ================= Menu Principal =================
    if contexto["menu"] == "principal":
        if low in SAUDACOES + ["menu","menu principal"]:
            menu = (
                "👋 Olá! Aqui está o menu principal do Eloy:\n"
                "1 - Conversar com IA\n"
                "2 - Relatórios\n"
                "3 - Equipe\n"
                "4 - Site da Eloy\n"
                "5 - Sair / Desligar Eloy"
            )
            contexto["menu"] = "principal"
            return {"resposta": menu, "action": "menu_principal", "contexto": contexto}
        elif low in ["1", "conversar"]:
            contexto["menu"] = "chat"
            return {"resposta": "Olá! Como posso ajudá-lo hoje? Você pode perguntar qualquer coisa ou digitar 'menu' para retornar.", "action": "chat", "contexto": contexto}
        elif low in ["2", "relatorios", "relatorio"]:
            contexto["menu"] = "relatorios"
            return {"resposta":"📊 MENU DE RELATÓRIOS:\n1 - Adicionar relatório\n2 - Ver relatório por data\n3 - Listar relatórios existentes\n4 - Editar relatório\n5 - Remover relatório\n6 - Voltar", "action":"menu_relatorios", "contexto": contexto}
        elif low in ["3","equipe","membros","funcionarios","funcionario"]:
            contexto["menu"] = "equipe"
            return {"resposta":"👥 MENU DA EQUIPE:\n1 - Ver empresa\n2 - Adicionar membro\n3 - Remover membro\n4 - Editar cargo\n5 - Voltar","action":"menu_equipe","contexto": contexto}
        elif low in ["4","site"]:
            return {"resposta":"Abrindo site da Eloy: http://www.eloy.com.br","action":"abrir_site","contexto": contexto}
        elif low in ["5","sair","desligar"]:
            return {"resposta":"Encerrando conversa.","action":"sair","contexto": contexto}
        else:
            # conversa normal
            pass

    # ================= Menu Relatórios =================
    elif contexto["menu"] == "relatorios":
        if low in ["1","adicionar","adicionar relatorio"]:
            return {"resposta":"Digite a data (DD/MM/AAAA) e o conteúdo do relatório separados por '|' (ex: 11/11/2025|Relatório aqui).", "action":"add_relatorio","contexto": contexto}
        elif low in ["2","ver","ver relatorio","ver relatório"]:
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":f"Relatórios disponíveis: {', '.join(datas)}\nDigite a data desejada (DD/MM/AAAA) para visualizar:", "action":"ver_relatorio","contexto": contexto}
            else:
                return {"resposta":"Nenhum relatório cadastrado.", "action":"menu_relatorios","contexto": contexto}
        elif low in ["3","listar","listar relatorios","listar relatórios"]:
            rels = listar_relatorios()
            if rels:
                datas = [r["date"] for r in rels]
                return {"resposta":"Lista de relatórios: " + ", ".join(datas), "action":"menu_relatorios","contexto": contexto}
            else:
                return {"resposta":"Lista de relatórios: Nenhum relatório cadastrado.", "action":"menu_relatorios","contexto": contexto}
        elif low in ["4","editar","editar relatorio","editar relatório"]:
            return {"resposta":"Digite a data (DD/MM/AAAA) do relatório que deseja editar e o novo conteúdo separados por '|' (ex: 11/11/2025|Novo conteúdo).", "action":"edit_relatorio","contexto": contexto}
        elif low in ["5","remover","remover relatorio"]:
            return {"resposta":"Digite a data (DD/MM/AAAA) do relatório que deseja remover:", "action":"remove_relatorio","contexto": contexto}
        elif low in ["6","voltar","menu"]:
            contexto["menu"] = "principal"
            return {"resposta":"Voltando ao menu principal.\nDigite 'menu' para ver as opções novamente.", "action":"menu_principal","contexto": contexto}
        elif "|" in texto:  # adição ou edição
            partes = texto.split("|",1)
            date, conteudo = partes[0].strip(), partes[1].strip()
            if len(date.split("/")) == 3:
                if contexto.get("action") == "add_relatorio":
                    adicionar_relatorio(date, conteudo)
                    return {"resposta":f"✅ Relatório de {date} adicionado com sucesso.\n📊 MENU DE RELATÓRIOS: 1 - Adicionar relatório 2 - Ver relatório por data 3 - Listar relatórios existentes 4 - Editar relatório 5 - Remover relatório 6 - Voltar","action":"menu_relatorios","contexto": contexto}
                elif contexto.get("action") == "edit_relatorio":
                    atualizar_relatorio(date, conteudo)
                    return {"resposta":f"✏️ Relatório de {date} atualizado com sucesso.","action":"menu_relatorios","contexto": contexto}
        elif contexto.get("action") in ["ver_relatorio","remove_relatorio"]:
            date = texto.strip()
            rels = [r for r in listar_relatorios() if r["date"] == date]
            if contexto.get("action") == "ver_relatorio":
                if rels:
                    return {"resposta":f"📄 {date}: {rels[0]['texto']}","action":"menu_relatorios","contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta":f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}","action":"menu_relatorios","contexto": contexto}
            elif contexto.get("action") == "remove_relatorio":
                if rels:
                    remover_relatorio(date)
                    return {"resposta":f"🗑️ Relatório de {date} removido.","action":"menu_relatorios","contexto": contexto}
                else:
                    datas = [r["date"] for r in listar_relatorios()]
                    return {"resposta":f"⚠️ Relatório não encontrado. Datas disponíveis: {', '.join(datas)}","action":"menu_relatorios","contexto": contexto}
        else:
            return {"resposta":"Opção inválida. Escolha um número ou palavra-chave do menu.","action":"menu_relatorios","contexto": contexto}

    # ================= Menu Equipe =================
    elif contexto["menu"] == "equipe":
        if low in ["1","ver empresa"]:
            empresa = info_empresa()
            funcionarios = listar_funcionarios()
            lista = "\n".join([f"{f['nome']} ({f['cargo']})" for f in funcionarios])
            resp = f"🏢 Empresa: {empresa['nome']}\n📅 Fundação: {empresa['fundacao']}\n👤 Funcionários:\n{lista if lista else 'Nenhum funcionário cadastrado.'}"
            return {"resposta":resp,"action":"menu_equipe","contexto": contexto}
        elif low in ["2","adicionar membro","adicionar funcionario"]:
            return {"resposta":"Digite o nome e cargo do membro separados por '|' (ex: Lucas Toledo|Desenvolvedor).","action":"add_membro","contexto": contexto}
        elif low in ["3","remover membro","remover funcionario"]:
            return {"resposta":"Digite o nome do membro a remover:","action":"remove_membro","contexto": contexto}
        elif low in ["4","editar cargo"]:
            return {"resposta":"Digite o nome do membro e novo cargo separados por '|' (ex: Lucas Toledo|Coordenador).","action":"edit_membro","contexto": contexto}
        elif low in ["5","voltar","menu"]:
            contexto["menu"] = "principal"
            return {"resposta":"Voltando ao menu principal.\nDigite 'menu' para ver as opções novamente.","action":"menu_principal","contexto": contexto}
        elif "|" in texto:
            partes = texto.split("|",1)
            nome, cargo = partes[0].strip(), partes[1].strip()
            if contexto.get("action") == "add_membro":
                adicionar_funcionario(nome, cargo)
                return {"resposta":f"✅ Membro {nome} adicionado com sucesso.","action":"menu_equipe","contexto": contexto}
            elif contexto.get("action") == "edit_membro":
                atualizar_funcionario(nome, cargo)
                return {"resposta":f"✏️ Cargo de {nome} atualizado para {cargo}.","action":"menu_equipe","contexto": contexto}
        elif contexto.get("action") in ["remove_membro"]:
            nome = texto.strip()
            funcionarios = [f for f in listar_funcionarios() if f["nome"].lower() != nome.lower()]
            if len(funcionarios) != len(listar_funcionarios()):
                remover_funcionario(nome)
                return {"resposta":f"🗑️ Membro {nome} removido.","action":"menu_equipe","contexto": contexto}
            else:
                return {"resposta":f"⚠️ Membro não encontrado.","action":"menu_equipe","contexto": contexto}
        else:
            return {"resposta":"Opção inválida. Escolha um número ou palavra-chave do menu.","action":"menu_equipe","contexto": contexto}

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
            contexto = body.get("contexto", {"menu": "principal"})
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
