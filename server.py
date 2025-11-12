#!/usr/bin/env python3
import os, json, requests
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

# ================= Helpers =================
def listar_funcionarios(): return supabase.table("funcionarios").select("*").execute().data or []
def adicionar_funcionario(nome,cargo): supabase.table("funcionarios").insert({"nome":nome,"cargo":cargo}).execute()
def atualizar_funcionario(nome,cargo): supabase.table("funcionarios").update({"cargo":cargo}).eq("nome",nome).execute()
def remover_funcionario(nome): supabase.table("funcionarios").delete().eq("nome",nome).execute()
def listar_relatorios(): return supabase.table("relatorios").select("*").execute().data or []
def adicionar_relatorio(date,texto): supabase.table("relatorios").insert({"date":date,"texto":texto}).execute()
def atualizar_relatorio(date,texto): supabase.table("relatorios").update({"texto":texto}).eq("date",date).execute()
def remover_relatorio(date): supabase.table("relatorios").delete().eq("date",date).execute()
def info_empresa(): 
    res = supabase.table("empresa").select("*").execute()
    return res.data[0] if res.data else {"nome":"Eloy Soluções Corporativas","fundacao":"2025-11-09"}

SAUDACOES = ["oi","olá","ola","hey","hello","bom dia","boa tarde","boa noite"]
COMANDOS_RELATORIO = ["adicionar relatorio","ver relatorio","listar relatorio","editar relatorio","remover relatorio"]
COMANDOS_MEMBRO = ["adicionar membro","remover membro","editar membro","ver membro"]

# ================= Processamento de Mensagem =================
def processar_mensagem(msg, contexto=None):
    contexto = contexto or {}
    texto = msg.strip()
    low = texto.lower()

    # ===== sair =====
    if low == "sair":
        contexto.clear()
        return {"resposta":"Saindo do menu. Escolha um menu:\n- chat\n- relatorios\n- equipe",
                "action":None,"contexto": contexto}

    # ===== Menu principal =====
    if not contexto.get("menu"):
        if low in ["chat","relatorios","equipe"]:
            contexto["menu"] = low
            if low=="chat": return {"resposta":"💬 Entrou no menu Chat. Digite sua mensagem ou 'sair' para voltar.","action":"menu_chat","contexto": contexto}
            if low=="relatorios": return {"resposta":"📊 Entrou no menu Relatórios. Comandos: "+", ".join(COMANDOS_RELATORIO)+"\nDigite o comando ou 'sair' para voltar.","action":"menu_relatorios","contexto": contexto}
            if low=="equipe": return {"resposta":"👥 Entrou no menu Equipe. Comandos: "+", ".join(COMANDOS_MEMBRO)+"\nDigite o comando ou 'sair' para voltar.","action":"menu_equipe","contexto": contexto}
        elif low in SAUDACOES:
            return {"resposta":"👋 Olá! Escolha um menu:\n- chat\n- relatorios\n- equipe","action":None,"contexto": contexto}
        else:
            return {"resposta":"⚠️ Comando não reconhecido. Digite 'chat', 'relatorios' ou 'equipe'.","action":None,"contexto": contexto}

    # ===== Menu Chat =====
    if contexto.get("menu")=="chat":
        if GROQ_API_KEY:
            headers = {"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
            payload = {"model":MODEL,"messages":[{"role":"system","content":"Você é Eloy, assistente corporativo."},{"role":"user","content":texto}],"temperature":0.7}
            try:
                res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
                res.raise_for_status()
                data = res.json()
                resposta = data.get("choices",[{}])[0].get("message",{}).get("content","")
                return {"resposta":resposta,"action":None,"contexto": contexto}
            except Exception as e:
                return {"resposta":f"(Erro na IA: {e})","action":None,"contexto": contexto}
        else:
            return {"resposta":"Eloy (modo teste): "+texto,"action":None,"contexto": contexto}

    # ===== Menu Relatórios =====
    if contexto.get("menu")=="relatorios":
        if low in COMANDOS_RELATORIO:
            contexto["acao"] = low
            if low=="listar relatorio":
                rels = listar_relatorios()
                datas = [r["date"] for r in rels]
                # <CHANGE> Remove a ação após listar para permitir novos comandos
                del contexto["acao"]
                return {"resposta":"Lista de relatórios: "+(", ".join(datas) if datas else "Nenhum relatório"),
                        "action":None,"contexto": contexto}
            if low=="ver relatorio": return {"resposta":"Digite a data do relatório (DD/MM/AAAA):","action":"ver_relatorio","contexto": contexto}
            if low in ["adicionar relatorio","editar relatorio"]: return {"resposta":"Digite a data e o conteúdo separados por '|' (ex: 14/11/2025|Conteúdo).","action":low,"contexto": contexto}
            if low=="remover relatorio": return {"resposta":"Digite a data do relatório que deseja remover:","action":low,"contexto": contexto}
        if "acao" in contexto:
            acao = contexto["acao"]
            if acao in ["adicionar relatorio","editar relatorio"] and "|" in texto:
                date, conteudo = texto.split("|",1)
                if acao=="adicionar relatorio": adicionar_relatorio(date.strip(),conteudo.strip())
                else: atualizar_relatorio(date.strip(),conteudo.strip())
                # <CHANGE> Remove apenas a ação, mantém o menu
                del contexto["acao"]
                return {"resposta":f"✅ Relatório {date.strip()} {'adicionado' if acao=='adicionar relatorio' else 'atualizado'}.","action":None,"contexto": contexto}
            if acao=="ver_relatorio":
                date = texto.strip()
                rels = [r for r in listar_relatorios() if r["date"]==date]
                # <CHANGE> Remove apenas a ação, mantém o menu
                del contexto["acao"]
                return {"resposta": rels[0]["texto"] if rels else "⚠️ Relatório não encontrado.","action":None,"contexto": contexto}
            if acao=="remover relatorio":
                date = texto.strip()
                remover_relatorio(date)
                # <CHANGE> Remove apenas a ação, mantém o menu
                del contexto["acao"]
                return {"resposta":f"🗑️ Relatório {date} removido.","action":None,"contexto": contexto}

    # ===== Menu Equipe =====
    if contexto.get("menu")=="equipe":
        if low in COMANDOS_MEMBRO:
            contexto["acao"] = low
            if low in ["adicionar membro","editar membro"]: return {"resposta":"Digite nome e cargo separados por '|' (ex: Lucas Toledo|Desenvolvedor).","action":low,"contexto": contexto}
            if low=="remover membro": return {"resposta":"Digite o nome do membro a remover:","action":low,"contexto": contexto}
            if low=="ver membro":
                membros = listar_funcionarios()
                lista = "\n".join([f"{m['nome']} ({m['cargo']})" for m in membros])
                # <CHANGE> Remove a ação após listar para permitir novos comandos
                del contexto["acao"]
                return {"resposta":lista if lista else "Nenhum membro cadastrado.","action":None,"contexto": contexto}
        if "acao" in contexto:
            acao = contexto["acao"]
            if acao in ["adicionar membro","editar membro"] and "|" in texto:
                nome,cargo = texto.split("|",1)
                if acao=="adicionar membro": adicionar_funcionario(nome.strip(),cargo.strip())
                else: atualizar_funcionario(nome.strip(),cargo.strip())
                # <CHANGE> Remove apenas a ação, mantém o menu
                del contexto["acao"]
                return {"resposta":f"✅ Membro {nome.strip()} {'adicionado' if acao=='adicionar membro' else 'atualizado'}.","action":None,"contexto": contexto}
            if acao=="remover membro":
                nome = texto.strip()
                remover_funcionario(nome)
                # <CHANGE> Remove apenas a ação, mantém o menu
                del contexto["acao"]
                return {"resposta":f"🗑️ Membro {nome} removido.","action":None,"contexto": contexto}

    return {"resposta":"⚠️ Comando não reconhecido. Digite 'chat', 'relatorios' ou 'equipe'.","action":None,"contexto": contexto}

# ================= HTTP Handler =================
class EloyHandler(BaseHTTPRequestHandler):
    def _set_headers(self,status=200,content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type",content_type)
        self.send_header("Access-Control-Allow-Origin",os.getenv("CORS_ORIGIN","*"))
        self.send_header("Access-Control-Allow-Methods","GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

    def do_OPTIONS(self): self._set_headers()
    def _read_json(self):
        length=int(self.headers.get('Content-Length',0))
        if length==0: return {}
        raw=self.rfile.read(length).decode('utf-8')
        try: return json.loads(raw)
        except: return {}

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/equipe":
            self._set_headers()
            self.wfile.write(json.dumps({"empresa":info_empresa(),"funcionarios":listar_funcionarios()}).encode("utf-8"))
            return
        if path=="/api/relatorios":
            self._set_headers()
            rels = listar_relatorios()
            datas = [r["date"] for r in rels]
            self.wfile.write(json.dumps({"relatorios": datas}).encode("utf-8"))
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

    def do_POST(self):
        path=urlparse(self.path).path
        body=self._read_json()
        if path=="/api/chat":
            msg=body.get("mensagem","")
            contexto=body.get("contexto",{})
            result=processar_mensagem(msg,contexto)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({"error":"rota não encontrada"}).encode("utf-8"))

# ================= Run =================
def run(server_class=HTTPServer, handler_class=EloyHandler, port=PORT):
    server_address=('',port)
    httpd=server_class(server_address,handler_class)
    print(f"🌐 Eloy server listening at http://0.0.0.0:{port}")
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    httpd.server_close()

if __name__=='__main__': run()