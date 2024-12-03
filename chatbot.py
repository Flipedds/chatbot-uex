import os
import random
import sys
import customtkinter as ctk
from dotenv import load_dotenv
import requests
import spacy
import spacy.cli
import spacy.cli.download

# Carregar modelo de linguagem português do spaCy
# Verifica se está rodando no ambiente PyInstaller
if getattr(sys, '_MEIPASS', False):
    model_path = os.path.join(sys._MEIPASS, 'pt_core_news_sm')
else:
    model_path = spacy.util.get_package_path("pt_core_news_sm")

# Carrega o modelo
nlp = spacy.load(model_path)

# Carregar variáveis de ambiente
load_dotenv()

# Respostas randômicas
respostas_randomicas_sem_cidade_tempo = [
    "Por favor, me diga a cidade para que eu possa verificar o clima.",
    "Não consegui identificar a cidade. Qual cidade você quer saber sobre o clima?",
    "Preciso que você me diga a cidade para verificar o clima!"
]

respostas_randomicas_saudacao = [
    "Olá! Em que posso ajudar?",
    "Oi! Como posso te ajudar hoje?",
    "Olá! Estou aqui para ajudar. O que você precisa?"
]

respostas_randomicas_despedida = [
    "Até mais! Se precisar de algo, estou aqui.",
    "Tchau! Volte sempre que precisar.",
    "Até logo! Espero que tenha um ótimo dia!"
]

respostas_randomicas_socorro = [
    "Claro! Estou aqui para ajudar. O que você precisa?",
    "Com certeza, pode contar comigo! O que posso fazer por você?",
    "Estou aqui para ajudar. Diga-me como posso ajudar você."
]

respostas_randomicas_padrao = [
    "Desculpe, não entendi. Poderia reformular a pergunta?",
    "Humm... não consegui entender. Pode tentar de outra forma?",
    "Não entendi bem. Pode explicar de outro jeito, por favor?"
]

respostas_randomicas_tempo = lambda city, temp, description : random.choice([
        f"O clima em {city} é de {temp}°C com tempo {description}.",
        f"Em {city}, a temperatura é de {temp}°C e o tempo está {description}.",
        f"{city} está com {temp}°C e {description}."
    ])

"""
A função extract_city identifica e retorna o nome de um local (cidade, país, etc.) 
mencionado em um texto processado por um modelo de Processamento de Linguagem Natural (NLP). 
Caso nenhum local seja encontrado, a função retorna None.
"""
def extract_city(doc):
        for ent in doc.ents:
            if ent.label_ == "LOC":
                return ent.text
        return None


def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=pt_br&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            return respostas_randomicas_tempo(city, temp, description)
        elif response.status_code == 404:
            return f"Desculpe, não encontrei informações sobre a cidade '{city}'."
        else:
            return "Houve um problema ao acessar os dados de clima. Tente novamente mais tarde."
    except Exception as e:
        return f"Erro ao acessar a API: {e}"

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Artemis")
        master.geometry("600x500")

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, """Olá! Eu sou a Artemis, sua assistente virtual. Como posso te ajudar hoje?\nPergunte sobre o clima de alguma cidade. Exemplo: como está o clima hoje em recife ? \n""")
        self.text_area.configure(state="disabled")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite sua pergunta aqui...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")

        response = self.get_bot_response(user_input)
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")

        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

    def get_bot_response(self, user_input):
        doc = nlp(user_input.lower())
        # Extrair tokens lematizados sem pontuações e palavras de parada
        tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_stop]

        if "clima" in tokens:
            city = extract_city(doc)
            if city:
                return get_weather(city)
            return random.choice(respostas_randomicas_sem_cidade_tempo)

        if any(greeting in tokens for greeting in ["olá", "oi"]):
            return random.choice(respostas_randomicas_saudacao)
        elif any(farewell in tokens for farewell in ["tchau", "adeus", "até logo"]):
            return random.choice(respostas_randomicas_despedida)
        elif "ajuda" in tokens or "socorro" in tokens:
            return random.choice(respostas_randomicas_socorro)
        else:
            return random.choice(respostas_randomicas_padrao)

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()