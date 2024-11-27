import google.generativeai as genai

class GEMINI:
    def __init__(self):
        try:
            # Lê a chave de API do arquivo
            FILE = "KEY.txt"
            with open(FILE, "r") as f:
                GOOGLE_API_KEY = f.read().strip()

            # Configura a API com a chave
            genai.configure(api_key=GOOGLE_API_KEY)

            # Inicializa o modelo
            self.model = genai.GenerativeModel('gemini-1.5-flash')

        except Exception as e:
            raise ValueError("Erro ao configurar o modelo Gemini: " + str(e))

    def enviar(self, texto):
        try:
            # Chama a API para gerar conteúdo
            response = self.model.generate_content(texto)

            # Converte a resposta para o formato de dicionário
            response = response.to_dict()

            # Acessa o conteúdo desejado da resposta
            resposta = response['candidates'][0]['content']['parts'][0]['text']

            #convete os caracteres especiais para utf-8
            resposta = resposta.encode('utf-8').decode('utf-8')
            return resposta

        except Exception as e:
            raise ValueError("Erro ao processar a requisição com o modelo Gemini: " + str(e))

