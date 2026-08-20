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

### 5. Configure o `.env`

Na raiz do projeto, copie o `.env.example` e ajuste se precisar:

cp .env.example .env

As variáveis usadas pela API de autenticação:

- `SECRET_KEY` — chave para assinar o JWT
- `ALGORITHM` — padrão `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` — tempo de expiração do token (padrão 30 min)

### 6. Treinamento do modelo (MLP e Random Forest)

Rode isso depois do setup, antes de subir a API:

#### 6.1 Treinar com otimização (GridSearch — mais lento, recomendado)

python -m src.train_model.train

#### 6.2 Treinar rapido sem grid search

python -m src.train_model.train --sem-otimizacao

#### 6.3 Saida esperada

```terminal
Dataset: caminho/data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
Amostras de treino: 4922 | teste: 2110
Distribuição de churn (treino):
Churn
0    0.734254
1    0.265746
Name: proportion, dtype: float64
Melhores parâmetros (RF): {'classifier__max_depth': 10, 'classifier__min_samples_split': 10, 'classifier__n_estimators': 300}
Melhor roc_auc (CV): 0.8477
Modelo RF salvo em: caminho/models/rf_model.joblib
Melhores parâmetros (MLP): {'classifier__activation': 'tanh', 'classifier__alpha': 0.001, 'classifier__hidden_layer_sizes': (64, 32)}
Melhor roc_auc (CV): 0.8481
Modelo MLP salvo em: caminho/models/mlp_model.joblib
Relatório de comparação salvo em: caminho/models/comparison_results.csv

Comparação (validação cruzada):
       Modelo  ROC-AUC Médio  Desvio Padrão
          MLP       0.848078       0.014987
Random Forest       0.847671       0.014741

Melhor modelo (CV): MLP
Melhor modelo salvo para API em: caminho/models/model.joblib

============================================================
Avaliação no teste: Random Forest
============================================================
  ACCURACY: 0.7502
 PRECISION: 0.5202
    RECALL: 0.7790
        F1: 0.6238
   ROC_AUC: 0.8326

Matriz de confusão:
[[1146  403]
 [ 124  437]]

Relatório de classificação:
              precision    recall  f1-score   support

           0       0.90      0.74      0.81      1549
           1       0.52      0.78      0.62       561

    accuracy                           0.75      2110
   macro avg       0.71      0.76      0.72      2110
weighted avg       0.80      0.75      0.76      2110


============================================================
Avaliação no teste: MLP
============================================================
  ACCURACY: 0.7948
 PRECISION: 0.6397
    RECALL: 0.5223
        F1: 0.5751
   ROC_AUC: 0.8324

Matriz de confusão:
[[1384  165]
 [ 268  293]]

Relatório de classificação:
              precision    recall  f1-score   support

           0       0.84      0.89      0.86      1549
           1       0.64      0.52      0.58       561

    accuracy                           0.79      2110
   macro avg       0.74      0.71      0.72      2110
weighted avg       0.79      0.79      0.79      2110
```

Arquivos gerados em `models/`:

- `rf_model.joblib` — Random Forest
- `mlp_model.joblib` — MLP
- `model.joblib` — melhor modelo (usado pela API)
- `comparison_results.csv` — comparação entre os dois

### 7. Subir a API FastAPI

python -m uvicorn src.api.main:app --reload

Docs interativas: http://127.0.0.1:8000/docs

A API carrega o `models/model.joblib` na inicialização. Se o arquivo não existir, o `/health` vai retornar `degraded` e o `/predict` responde 503.

### 8. Rotas disponíveis

| Método | Rota | Auth | O que faz |
|--------|------|------|-----------|
| GET | `/health` | não | Status da API e se o modelo carregou |
| GET | `/model/info` | não | Caminho, tipo do classificador e threshold |
| POST | `/auth/login` | não | Login — retorna JWT |
| GET | `/auth/me` | sim | Dados do usuário logado |
| POST | `/predict` | sim | Predição de churn |

Usuários de teste:

| login | senha | role |
|-------|-------|------|
| admin | admin | admin |
| user | user | user |

### 9. Fluxo de uso da API

Primeiro faz login e pega o token:

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Resposta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Com o token, chama o `/predict` passando no header:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 89.10,
    "TotalCharges": 1047.65
  }'
```

Resposta:

```json
{
  "prediction": "Yes",
  "probability": 0.6871
}
```

Para testar se o token está válido:

```bash
curl -X GET "http://127.0.0.1:8000/auth/me" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

No Swagger (`/docs`), clique em **Authorize**, cole o token e teste os endpoints protegidos por la.
