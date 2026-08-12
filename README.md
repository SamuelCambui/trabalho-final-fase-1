## Configuração

### 1. Clone o projeto

git clone <https://github.com/SamuelCambui/trabalho-final-fase-1.git>

cd tech-challenge-churn

### 2. Instale as dependências

pip install -r requirements.txt

### 3. Autentique o Kaggle

Acesse o https://www.kaggle.com/settings/api faça login e clique em API tokens e após clique em "Create Legacy API Key"

Baixe o json e coloque na pasta do projeto

### 4. Execute o setup

python scripts/setup.py


### 5. Para acessar a API FASTAPI
python -m uvicorn src.api.main:app --reload

Acesse o http://127.0.0.1:8000