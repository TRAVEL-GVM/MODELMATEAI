import openai
from config import *

instruction_str = """\
    1. Interprete a pergunta e retorne apenas a resposta final em linguagem natural, com base nos dados sobre findings de risco de crédito e outros tipos de risco.
    2. Não mostre o código Pandas, apenas forneça a resposta com os detalhes solicitados.
    3. A resposta deve ser clara, direta e referir-se aos detalhes relacionados aos findings e medidas no DataFrame.
"""

context = """Objetivo: O papel principal deste agente é ajudar os usuários fornecendo informações 
    precisas sobre findings de risco identificados em auditorias e processos de validação de um banco. 
    O DataFrame contém dados como:
    - ID: Identificador único do finding.
    - Detetor: A entidade ou departamento que identificou o finding (ex: Auditor Externo).
    - Referência Documental: Documentos associados ao finding.
    - Sponsor: O departamento responsável por tratar o finding.
    - Âmbito do Modelo: O modelo relacionado ao finding, como IFRS9.
    - Natureza da Medida: O tipo de medida aplicada (ex: governança, deficiência de documentos).
    - Status: O status atual do finding (ex: Concluída, Em Validação).
    - Observações: Comentários sobre o progresso ou a resolução do finding.
    - Evidências de Implementação: Provas documentais de que as ações foram tomadas.
    - Datas de Criação e Modificação: Datas relevantes para o acompanhamento do finding.
"""


def ask_question_to_dataframe(query, dataframe):
    df_str = dataframe.to_string()

    # Cria o prompt para o modelo
    prompt = f"""
    Você é um assistente que trabalha com um DataFrame do pandas em Python.
    O DataFrame contém os seguintes dados:
    {df_str}

    Contexto: {context}

    Instruções: {instruction_str}

    Responda à seguinte pergunta com base no DataFrame: {query}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um especialista em gestão de risco e ou análise de dados."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10000,
        temperature=0
    )

    answer = response['choices'][0]['message']['content'].strip()
    return answer
