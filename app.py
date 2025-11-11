import json
import os
import requests
from typing import List, Dict, Any

def forca_opcao(pergunta: str, opcoes_validas: List[str]) -> str:
    """
    Força o usuário a escolher uma opção válida de uma lista.
    
    Args:
        pergunta (str): A pergunta a ser exibida ao usuário.
        opcoes_validas (List[str]): Lista de strings com as opções válidas (case-insensitive).
        
    Retorna:
        str: A opção escolhida pelo usuário (em maiúsculas).
    """
    opcoes_validas_upper = [op.upper() for op in opcoes_validas]
    
    while True:
        resposta = input(f"{pergunta} ({'/'.join(opcoes_validas)}): ").strip().upper()
        if resposta in opcoes_validas_upper:
            return resposta
        else:
            print(f"Opção inválida. Por favor, escolha entre {', '.join(opcoes_validas)}.")

# URL da API real de empregos (Arbeitnow Job Board API)
API_URL = "https://www.arbeitnow.com/api/job-board-api"

def obter_tendencias_emprego() -> List[Dict[str, Any]]:
    """
    Questão 1: Acessando uma API de Tendências de Emprego
    
    Faz uma requisição HTTP para a API real da Arbeitnow para obter dados de empregos.
    
    Retorna:
        List[Dict[str, Any]]: Uma lista de dicionários, onde cada dicionário
                              representa uma vaga de emprego.
    """
    print("-> Questão 1: Obtendo tendências de emprego da API real...")
    
    try:
        # Faz a requisição para a API
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status() # Lança exceção para códigos de status HTTP ruins (4xx ou 5xx)
        
        data = response.json()
        
        # A API retorna um dicionário com a chave 'data' contendo a lista de vagas
        vagas = data.get("data", [])
        
        if not vagas:
            print("Aviso: A lista de vagas retornada pela API está vazia.")
            
        print(f"   {len(vagas)} vagas carregadas com sucesso.")
        
        # Adaptação dos dados para incluir campos necessários para as Questões 2 e 3
        # Como a API real não fornece "taxa de crescimento" ou "promising", 
        # vamos simular esses campos com base no título da vaga para fins de demonstração
        # e atender aos requisitos da Questão 3.
        
        profissoes_adaptadas = []
        for vaga in vagas:
            titulo = vaga.get("title", "")
            
            # Simulação de "taxa de crescimento" e "promissora"
            # Profissões relacionadas a tecnologia terão uma taxa de crescimento maior
            if any(keyword in titulo.lower() for keyword in ["developer", "engineer", "data", "ai", "cloud", "software"]):
                growth_rate = 0.25 + (len(titulo) % 10) / 100 # 0.25 a 0.34
                promising = True
            else:
                growth_rate = 0.05 + (len(titulo) % 10) / 100 # 0.05 a 0.14
                promising = False
                
            # Cria um dicionário que atende à estrutura esperada pelas outras funções
            profissao_adaptada = {
                "title": titulo,
                "company_name": vaga.get("company_name", "Não Informada"),
                "growth_rate": growth_rate,
                "description": vaga.get("description", "Sem descrição.").split("</p>")[0].replace("<p>", "").strip(), # Pega o primeiro parágrafo
                "promising": promising
            }
            profissoes_adaptadas.append(profissao_adaptada)
            
        return profissoes_adaptadas
        
    except requests.exceptions.RequestException as e:
        # Tratamento de Erros (Questão 5): Falha na requisição (conectividade, timeout, status code)
        print(f"Erro de Tratamento de Erros (Questão 5): Falha na requisição à API: {e}")
        print("Retornando lista vazia.")
        return []
    except json.JSONDecodeError:
        # Tratamento de Erros (Questão 5): Falha ao decodificar o JSON
        print("Erro de Tratamento de Erros (Questão 5): Falha ao decodificar o JSON da API.")
        return []
    except Exception as e:
        # Tratamento de Erros (Questão 5): Outros erros inesperados
        print(f"Erro de Tratamento de Erros (Questão 5): Ocorreu um erro inesperado: {e}")
        return []

def filtrar_profissoes(profissoes: List[Dict[str, Any]], termo_filtro: str) -> List[Dict[str, Any]]:
    """
    Questão 2: Filtrando Profissões
    
    Filtra a lista de profissões. O critério de filtragem inclui profissões 
    consideradas "promissoras" E que contenham o termo de filtro fornecido 
    pelo usuário no título.
    
    Args:
        profissoes (List[Dict[str, Any]]): Lista de dicionários de profissões.
        termo_filtro (str): Termo a ser buscado no título da profissão.
        
    Retorna:
        List[Dict[str, Any]]: Uma nova lista contendo as profissões filtradas.
    """
    print(f"-> Questão 2: Filtrando profissões por 'promissoras' e termo '{termo_filtro}'...")
    
    # Normaliza o termo de filtro para busca case-insensitive
    termo_filtro_lower = termo_filtro.lower()
    
    profissoes_filtradas = []
    for p in profissoes:
        # Tratamento de Erros (Questão 5): Garante que os campos existam
        is_promising = p.get("promising", False)
        title_lower = p.get("title", "").lower()
        
        # Critério 1: A profissão é considerada promissora
        # Critério 2: O título da profissão contém o termo de filtro do usuário
        matches_filter = termo_filtro_lower in title_lower
        
        # Apenas inclui se for promissora E contiver o termo
        if is_promising and matches_filter:
            profissoes_filtradas.append(p)
            
    print(f"   {len(profissoes_filtradas)} profissões filtradas encontradas.")
    return profissoes_filtradas

def calcular_crescimento_total(profissoes: List[Dict[str, Any]]) -> float:
    """
    Questão 3: Cálculo Recursivo de Crescimento
    
    Calcula a soma total das taxas de crescimento para todas as profissões
    passadas como argumento, utilizando uma função recursiva.
    
    Args:
        profissoes (List[Dict[str, Any]]): Lista de dicionários de profissões.
        
    Retorna:
        float: A soma total das taxas de crescimento.
    """
    print("-> Questão 3: Calculando crescimento total (recursivo)...")
    
    if not profissoes:
        return 0.0
    
    # Pega a taxa de crescimento do primeiro elemento
    # Tratamento de Erros (Questão 5): Usa .get() com valor padrão 0.0
    taxa_primeiro = profissoes[0].get("growth_rate", 0.0)
    
    # Chamada recursiva com o restante da lista
    soma_restante = calcular_crescimento_total(profissoes[1:])
    
    # Retorna a soma da taxa do primeiro com a soma do restante
    return taxa_primeiro + soma_restante

def exibir_profissoes(profissoes: List[Dict[str, Any]]):
    """
    Questão 4: Exibição de Dados
    
    Recebe uma lista de profissões e exibe no console os nomes e informações
    mais relevantes.
    
    Args:
        profissoes (List[Dict[str, Any]]): Lista de dicionários de profissões.
    """
    print("-> Questão 4: Exibindo profissões e informações relevantes...")
    
    if not profissoes:
        print("   Nenhuma profissão para exibir.")
        return
        
    print("\n--- Profissões Filtradas ---")
    # Utiliza um laço for para iterar sobre a lista de profissões (Requisito 4.1)
    for i, p in enumerate(profissoes):
        # Tratamento de Erros (Questão 5): Garante que os campos existam
        titulo = p.get("title", "Título Desconhecido")
        empresa = p.get("company_name", "Empresa Não Informada")
        crescimento = p.get("growth_rate", 0.0)
        descricao = p.get("description", "Sem descrição.")
        
        print(f"\n{i+1}. Profissão: {titulo}")
        print(f"   Empresa: {empresa}")
        print(f"   Taxa de Crescimento: {crescimento:.2f} (ou {crescimento*100:.0f}%)")
        print(f"   Descrição: {descricao}")
    print("----------------------------\n")

def programa_principal():
    """
    Questão 5: Programa Principal
    
    Orquestra a execução das funções para desenvolver o programa completo,
    agora em um loop que permite múltiplas consultas.
    """
    print("=====================================================")
    print("  Global Solution 2025_2 - Futuro do Trabalho (Python)")
    print("=====================================================")
    
    # 1. Obtenha as tendências de emprego UMA VEZ no início
    todas_profissoes = obter_tendencias_emprego()
    
    if not todas_profissoes:
        print("\nPrograma encerrado devido à falha na obtenção dos dados.")
        return
        
    while True:
        print("\n--- Nova Consulta ---")
        
        # 2. Pergunte ao usuário uma profissão (termo de filtro).
        termo_filtro = input("\nDigite um termo para filtrar as profissões (ex: 'Developer', 'Engineer', 'Data'): ").strip()
        
        # 3. Filtre as profissões e exiba os resultados.
        profissoes_filtradas = filtrar_profissoes(todas_profissoes, termo_filtro)
        
        if not profissoes_filtradas:
            print(f"\nNenhuma profissão promissora encontrada que contenha o termo '{termo_filtro}'.")
        else:
            exibir_profissoes(profissoes_filtradas)
            
            # 4. Calcule e exiba a soma total das taxas de crescimento das profissões filtradas.
            soma_crescimento = calcular_crescimento_total(profissoes_filtradas)
            
            print(f"Soma Total das Taxas de Crescimento das Profissões Filtradas: {soma_crescimento:.2f}")
            print(f"Isso representa um crescimento médio de {soma_crescimento / len(profissoes_filtradas) * 100:.2f}% por profissão filtrada.")
        
        # Pergunta se o usuário deseja continuar
        continuar = forca_opcao("Deseja realizar outra consulta?", ["S", "N"])
        
        if continuar == "N":
            break
            
    print("\n=====================================================")
    print("  Programa Principal Concluído. Obrigado por usar.")
    print("=====================================================")

if __name__ == "__main__":
    # Instala a biblioteca 'requests' se ainda não estiver instalada
    try:
        import requests
    except ImportError:
        print("A biblioteca 'requests' não está instalada. Instalando...")
        os.system("pip install requests")
        import requests
        
    programa_principal()