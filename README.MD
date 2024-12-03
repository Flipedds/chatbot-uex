CHATBOT com OpenWeather

Passos:
Criar Arquivo .env -> criar variável OPENWEATHER_API_KEY e adicionar chave disponível em: https://openweathermap.org/api
Instalar dependências -> Executar pip install -r requirements.txt
Executando no terminal -> python chatbot.py

Criando Executável

pyinstaller --onefile --windowed --icon=icone.ico --add-data "pt_core_news_sm;pt_core_news_sm" chatbot.py