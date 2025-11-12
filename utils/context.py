def gerar_contexto(banco):
    funcionarios = ", ".join(banco.get("funcionarios", []))
    projetos = ", ".join(banco.get("projetos", []))
    data = banco.get("data_fundacao", "desconhecida")

    return (
        f"A empresa Eloy foi fundada em {data}. "
        f"Os funcionários atuais são: {funcionarios}. "
        f"Os projetos ativos incluem: {projetos}. "
        f"Os relatórios existentes são: {', '.join(banco.get('relatorios', {}).keys()) or 'nenhum ainda'}."
    )
