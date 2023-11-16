import requests
import os
from dotenv import load_dotenv


def testar_api_openai(api_key, prompt):
    # URL do endpoint da OpenAI para o modelo GPT-3.5
    url = "https://api.openai.com/v1/engines/text-davinci-003/completions"


    # Cabeçalhos da requisição, incluindo a chave de API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Corpo da requisição contendo o prompt para o modelo
    data = {
        "prompt": prompt,
        "max_tokens": 100  # Ajuste conforme necessário
    }

    # Fazendo a requisição POST para a API da OpenAI
    response = requests.post(url, headers=headers, json=data)

    # Verificando o status da resposta
    if response.status_code == 200:
        # Extraindo e imprimindo a resposta do modelo
        resposta_modelo = response.json()["choices"][0]["text"]
        print("Resposta do modelo:", resposta_modelo)
    else:
        # Imprimindo informações em caso de erro
        print("Erro na requisição:")
        print(response.status_code)
        print(response.text)

# Substitua "SUA_CHAVE_DE_API" pela sua chave de API da OpenAI
load_dotenv()

# Retrieve the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Exemplo de prompt para testar a API
prompt_teste = "Escreva uma breve descrição de como a inteligência artificial está impactando o mundo."

# Chamando a função para testar a API
testar_api_openai(api_key, prompt_teste)



