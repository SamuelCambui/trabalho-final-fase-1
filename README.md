# Predição de Churn de Clientes Telco

Projeto do Tech Challenge - Fase 1 da FIAP Pós-Tech. A solução percorre o ciclo de vida de um produto de Machine Learning: análise exploratória, treinamento e comparação de modelos, empacotamento do pipeline e disponibilização de inferência por uma API REST com FastAPI.

## Problema de negócio

Uma operadora de telecomunicações precisa identificar clientes com maior propensão ao cancelamento. O objetivo do modelo é apoiar ações preventivas de retenção, priorizando clientes de maior risco para contato ou ofertas direcionadas.

A saída deve ser usada como apoio à decisão, e não como decisão automática sobre clientes. O custo de deixar de identificar um cliente que realmente cancelará pode ser maior que o custo de abordar um cliente sem intenção de cancelar; por isso, recall da classe de churn também deve ser considerado junto com ROC-AUC.

## Entregas do projeto

- EDA e baseline de Regressão Logística no notebook;
- pipelines reprodutíveis de pré-processamento com Scikit-Learn;
- treinamento e comparação de Random Forest e MLPClassifier;
- seleção e persistência do modelo usado pela API;
- API FastAPI com health check, autenticação JWT e predição;
- testes automatizados com Pytest;
- [Model Card](docs/MODEL_CARD.md) com desempenho, limitações e riscos;
- [roteiro do vídeo STAR](docs/VIDEO_STAR.md) com duração máxima de 5 minutos.

## Dataset e principais achados

Foi utilizado o dataset público **Telco Customer Churn**, com 7.043 clientes e 21 colunas na versão bruta. A variável alvo é `Churn`, em que `Yes` representa cancelamento.

Principais achados da EDA registrada em `notebook.ipynb`:

- 26,54% dos clientes apresentam churn, indicando desbalanceamento moderado;
- clientes com churn têm, em média, 17,98 meses de permanência, contra 37,57 meses entre os que permanecem;
- contratos mensais apresentam 42,71% de churn, contra 11,27% nos contratos anuais e 2,83% nos contratos de dois anos;
- clientes com fibra óptica apresentam 41,89% de churn no recorte observado;
- a cobrança mensal média é maior entre clientes com churn: 74,44 contra 61,27.

Essas relações são descritivas e não demonstram causalidade.

## Metodologia

O fluxo de treinamento:

1. converte `TotalCharges` para número, remove `customerID` e descarta registros inválidos;
2. divide os dados em 70% para treino e 30% para teste, com estratificação e `random_state=42`;
3. imputa variáveis numéricas pela mediana e aplica `StandardScaler`;
4. imputa variáveis categóricas pela moda e aplica `OneHotEncoder`;
5. treina Random Forest e MLP, com busca de hiperparâmetros opcional;
6. compara os modelos com validação cruzada de 5 folds usando ROC-AUC;
7. salva o modelo de maior ROC-AUC médio em `models/model.joblib`.

Todo o pré-processamento fica dentro do `Pipeline` do Scikit-Learn, reduzindo risco de vazamento entre treino e validação.

## Resultados

### Validação cruzada do pipeline final

| Modelo | ROC-AUC médio | Desvio padrão |
|---|---:|---:|
| MLP | 0,8481 | 0,0150 |
| Random Forest | 0,8477 | 0,0147 |

### Conjunto de teste

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0,7502 | 0,5202 | **0,7790** | **0,6238** | **0,8326** |
| MLP | **0,7948** | **0,6397** | 0,5223 | 0,5751 | 0,8324 |

O pipeline atual escolhe a **MLP** porque ela obteve o maior ROC-AUC médio na validação cruzada, que é a regra implementada. Entretanto, a diferença de 0,0004 para Random Forest é muito menor que o desvio observado nos folds e não comprova superioridade prática. Para uma campanha cujo objetivo principal seja encontrar o maior número possível de clientes propensos ao churn, a Random Forest é uma candidata operacional forte por seu recall de 0,7790. A decisão final deve considerar o custo de falsos positivos e falsos negativos e pode exigir ajuste do threshold.

O notebook também registra o baseline de Regressão Logística com ROC-AUC médio de 0,8456. Como esse resultado foi produzido em uma execução anterior do notebook e não consta no relatório final gerado por `src/train_model`, ele deve ser tratado como referência histórica, não como uma comparação controlada definitiva. Consulte o [Model Card](docs/MODEL_CARD.md) para detalhes.

## Estrutura do projeto

```text
.
├── data/
│   ├── download_dataset.py
│   └── raw/                         # criado pelo setup; dados não versionados
├── docs/
│   ├── MODEL_CARD.md
│   └── VIDEO_STAR.md
├── models/
│   └── comparison_results.csv
├── scripts/
│   └── setup.py
├── src/
│   ├── api/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   └── train_model/
├── tests/
├── notebook.ipynb
├── pyproject.toml
└── requirements.txt
```

Os arquivos CSV brutos e os artefatos `.joblib` são ignorados pelo Git. Cada ambiente deve baixar os dados e treinar o modelo antes de iniciar a API.

## Pré-requisitos

- Python 3.13 recomendado (`.python-version` e `pyproject.toml`);
- Git;
- conta no Kaggle e um token de API para o setup automático.

## Instalação

```bash
git clone https://github.com/SamuelCambui/trabalho-final-fase-1.git
cd trabalho-final-fase-1

Crie um ambiente virtual Python:

py -3.13 -m venv .venv 

Ative o ambiente virtual.

No Linux/macOS:

source .venv/bin/activate

No Windows PowerShell:

.venv\Scripts\Activate.ps1

No Windows CMD:

.venv\Scripts\activate.bat

Após ativar o ambiente, atualize o pip:

python -m pip install --upgrade pip

Agora vamos baixar todas as dependencias

python -m pip install pyproject.toml

### Download do dataset

1. Acesse as [configurações de API do Kaggle](https://www.kaggle.com/settings/api).
2. Crie uma chave legada em **Create Legacy API Key**.
3. Salve o arquivo baixado como `kaggle.json` na raiz do projeto.
4. Execute:

```bash
python scripts/setup.py
```

O script configura a credencial local, baixa `blastchar/telco-customer-churn` e valida os dados em `data/raw/`. O arquivo `kaggle.json` é ignorado pelo Git e nunca deve ser versionado.

## Treinamento

Treinamento com GridSearchCV, usado para produzir a comparação registrada:

```bash
python -m src.train_model.train
```

Para uma execução mais rápida, sem busca de hiperparâmetros:

```bash
python -m src.train_model.train --sem-otimizacao
```

Também é possível informar o caminho do CSV:

```bash
python -m src.train_model.train --dataset data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

O treinamento gera:

- `models/rf_model.joblib`: Random Forest;
- `models/mlp_model.joblib`: MLP;
- `models/model.joblib`: modelo selecionado e carregado pela API;
- `models/comparison_results.csv`: resumo da validação cruzada.

## Configuração e execução da API

Copie o arquivo de ambiente e troque a chave em qualquer ambiente compartilhado:

```bash
cp .env.example .env
python -m uvicorn src.api.main:app --reload
```

A documentação interativa fica disponível em <http://127.0.0.1:8000/docs>.

Se `models/model.joblib` não existir, a API inicia em modo degradado: `/health` informa `model_loaded: false` e `/predict` não fica disponível para inferência.

### Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| GET | `/health` | não | Informa o estado da API e do modelo |
| GET | `/model/info` | não | Informa tipo do classificador e threshold |
| POST | `/auth/login` | não | Retorna um token JWT |
| GET | `/auth/me` | Bearer token | Retorna os dados do usuário autenticado |
| POST | `/predict` | Bearer token | Retorna classe e probabilidade de churn |

As credenciais `admin/admin` e `user/user` existem apenas para demonstração local.

### Exemplo de uso

Obtenha o token:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Use o valor de `access_token` retornado na predição:

```bash
curl -X POST http://127.0.0.1:8000/predict \
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

Exemplo de resposta:

```json
{
  "prediction": "Yes",
  "probability": 0.6871
}
```

## Testes

Execute a suíte com:

```bash
python -m pytest -q
```

Os testes cobrem a limpeza dos dados, o health check da API e a autenticação de demonstração.

## Limitações e uso responsável

- os dados representam uma única base pública e podem não refletir clientes atuais ou outras operadoras;
- o dataset não permite avaliar deriva temporal ou generalização geográfica;
- há desbalanceamento da classe positiva;
- o threshold fixo de 0,5 ainda não foi otimizado pelo custo de negócio;
- atributos demográficos e familiares podem introduzir tratamento desigual entre grupos;
- as credenciais de demonstração e a chave JWT padrão não são adequadas para produção.

Antes de uso real, recomenda-se validação com dados da operadora, análise de custo, calibração, avaliação por subgrupos, monitoramento de drift e revisão humana das ações de retenção.

## Documentação da entrega

- [Model Card](docs/MODEL_CARD.md)
- [Roteiro e plano de gravação do vídeo STAR](docs/VIDEO_STAR.md)
