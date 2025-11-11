import requests
import time
import os
import re
import unicodedata
import threading
import queue
import json
import webbrowser
from difflib import SequenceMatcher

# 🔑 Chaves - ESCOLHA UMA API ABAIXO
GROQ_API_KEY = "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"

# 🔧 Selecione qual API usar
CURRENT_API = "groq"  # "groq"

# 🎯 Estados
STATE_STANDBY = "standby"
STATE_ON = "on"
STATE_SPEAKING = "speaking"
STATE_CONVERSING = "conversing"

# Controle global
current_state = STATE_STANDBY
should_stop_speaking = False
should_stop_verification = False
sentence_queue = queue.Queue()


# ========== FUNÇÕES DE IA - MÚLTIPLAS OPÇÕES ==========

def processar_com_groq_streaming(texto_usuario):
    """
    Usando streaming real da API Groq
    """
    url = "https://api.groq.com/openai/v1/chat/completions"

    modelo = "llama-3.3-70b-versatile"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "system",
                "content": "Você é Eloy, assistente de voz simpático e direto. Responda de forma curta, clara e natural."
            },
            {"role": "user", "content": texto_usuario}
        ],
        "temperature": 0.7,
        "max_tokens": 150,
        "top_p": 0.9,
        "stream": True  # Ativando streaming
    }

    try:
        print(f"[v0] Enviando requisição Groq com STREAMING...", flush=True)

        res = requests.post(url, headers=headers, json=payload, timeout=30, stream=True)

        if res.status_code != 200:
            print(f"[v0] Erro HTTP {res.status_code}: {res.text}", flush=True)
            res.raise_for_status()

        print("🤖 Eloy: ", end="", flush=True)

        buffer_sentenca = ""

        for linha in res.iter_lines():
            if not linha:
                continue

            linha_str = linha.decode('utf-8')

            # Skip do prefixo "data: "
            if linha_str.startswith('data: '):
                linha_str = linha_str[6:]

            # Skip se for [DONE]
            if linha_str == '[DONE]':
                if buffer_sentenca.strip():
                    sentenca_final = buffer_sentenca.strip()
                    print(sentenca_final, end=" ", flush=True)
                    sentence_queue.put(sentenca_final)
                break

            try:
                chunk = json.loads(linha_str)

                # Extrair conteúdo do delta
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    conteudo = delta.get("content", "")

                    if conteudo:
                        buffer_sentenca += conteudo
                        print(conteudo, end="", flush=True)

                        if buffer_sentenca.rstrip().endswith(('.', ',')):
                            sentenca = buffer_sentenca.strip()
                            # Enviar a sentença
                            sentence_queue.put(sentenca)
                            buffer_sentenca = ""


            except json.JSONDecodeError:
                continue

        print()  # Quebra de linha
        sentence_queue.put(None)  # Sinal de fim

    except requests.exceptions.Timeout:
        print("\n Erro Groq: Timeout - Requisição demorou muito")
        print("[v0] Tentando fallback...")
        sentence_queue.put("Desculpe, não consigo processar agora.")
        sentence_queue.put(None)
    except requests.exceptions.HTTPError as e:
        print(f"\n Erro Groq HTTP: {e}")
        print(f"[v0] Status: {res.status_code}")
        print(f"[v0] Response: {res.text}")
        sentence_queue.put("Desculpe, não consigo processar agora.")
        sentence_queue.put(None)
    except Exception as e:
        print(f"\n Erro Groq: {type(e).__name__}: {e}")
        sentence_queue.put("Desculpe, não consigo processar agora.")
        sentence_queue.put(None)


def processar_resposta_com_ia(texto_usuario):
    """
    Dispatcher com fallback automático entre APIs
    """
    if CURRENT_API == "groq":
        try:
            processar_com_groq_streaming(texto_usuario)
        except Exception as e:
            print(f"\n[v0] Groq falhou: {e}, tentando fallback...")


# ========== Função para menu e interações com o usuário ==========

def exibir_menu():
    """Exibe o menu de opções para o usuário"""
    print("\nMenu de opções:")
    print("1. Iniciar modo de conversação")
    print("2. Acessar site da Eloy")
    print("3. Desligar Eloy (entra em standby)")


def processar_entrada(entrada):
    """Processa a entrada do usuário e executa as ações correspondentes"""
    global current_state

    if entrada == "1":
        if current_state == STATE_CONVERSING:
            print("Já estamos em modo de conversação! Digite 'desligar' para sair.")
        else:
            current_state = STATE_CONVERSING
            iniciar_conversacao()
    elif entrada == "2":
        webbrowser.open("http://www.eloy.com.br")
    elif entrada == "3":
        print("Eloy entrou em standby. Pressione 'Enter' para reativar.")
        current_state = STATE_STANDBY
        input()  # A Eloy só volta a funcionar após pressionar Enter
        print("Eloy reativado.")
    else:
        print("Opção inválida! Tente novamente.")


def iniciar_conversacao():
    """Inicia o modo de conversação"""
    global current_state  # Declare a variável como global aqui
    print("\nModo de conversação iniciado! Para sair, diga qualquer despedida (ex: 'tchau', 'até logo').")

    despedidas = ["desligar", "tchau", "até logo", "adeus", "nos vemos", "falou", "até mais", "bye", "bye bye", "até a próxima"]

    while current_state == STATE_CONVERSING:
        pergunta = input("Você: ")
        
        # Verificar se a frase contém alguma despedida
        if any(despedida in pergunta.lower() for despedida in despedidas):
            print("\nEloy desligado. Até mais!")
            current_state = STATE_STANDBY  # Altera o estado global para standby
            input("Pressione 'Enter' para voltar ao menu de opções.")
            break
        
        processar_resposta_com_ia(pergunta)


# ========== MAIN ==========

if __name__ == "__main__":
    print("\nEloy - Assistente Virtual Interativo (Sem Áudio)")

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")
        processar_entrada(opcao)
