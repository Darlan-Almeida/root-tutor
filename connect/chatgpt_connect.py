import requests
import os
from dotenv import load_dotenv


load_dotenv()


class ChatGPTConnect:

    def __init__(self, api_key=os.getenv("OPENAI_API_KEY")):
        self.api_key= api_key


    def response_message(self, prompt):
        # URL do endpoint da OpenAI para o modelo GPT-3.5
        url = "https://api.openai.com/v1/engines/text-davinci-003/completions"


        # Cabeçalhos da requisição, incluindo a chave de API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Corpo da requisição contendo o prompt para o modelo
        data = {
            "prompt": prompt,
            "max_tokens": 150 
        }

        # Fazendo a requisição POST para a API da OpenAI
        response = requests.post(url, headers=headers, json=data)

        # Verificando o status da resposta
        if response.status_code == 200:
            # Extraindo e imprimindo a resposta do modelo
            resposta_modelo = response.json()["choices"][0]["text"]
            return resposta_modelo
        else:
            # Imprimindo informações em caso de erro
            return "Erro na requisição:"




