import requests
from config.settings import GROQ_API_KEY, MODEL

def enviar_mensagem_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    resposta = requests.post(url, headers=headers, json=body)
    if resposta.status_code == 200:
        return resposta.json()["choices"][0]["message"]["content"]
    else:
        return f"Erro na API Groq: {resposta.text}"
