# Predição de Churn de Clientes Telco

Projeto do Tech Challenge — Fase 1 da FIAP Pós-Tech. A solução percorre análise exploratória, definição de métricas, treinamento e comparação de modelos, auditoria de fairness e disponibilização de inferência por uma API FastAPI.

## Problema de negócio

Uma operadora de telecomunicações quer identificar antecipadamente clientes com maior propensão ao cancelamento para priorizar ações de retenção. O modelo serve como apoio à decisão e não deve tomar decisões automáticas sobre clientes.

Como deixar de identificar um cliente que cancelará pode custar mais do que uma abordagem de retenção desnecessária, o **recall da classe churn** foi definido como critério principal de negócio. ROC-AUC, PR-AUC, F1 e MCC também foram acompanhados para evitar uma escolha baseada em uma única métrica.

## Entregas

- [Etapa 1 — EDA, métricas e baseline de Regressão Logística](notebooks/eda_churn_prediction.ipynb);
- [Etapa 1.1 — auditoria de fairness por gênero](notebooks/fairness_churn_prediction.ipynb);
- [Etapa 2 — Random Forest, MLP e comparação controlada](notebooks/modelagem_avaliacao_churn_prediction.ipynb);
- Etapa 3 — código modular em `src/`, testes Pytest, CI e API FastAPI;
- Etapa 4 — este README, [Model Card](docs/MODEL_CARD.md) e [roteiro do vídeo STAR](docs/VIDEO_STAR.md);
- documentação complementar do [ML Canvas](docs/MLCanvas.docx).

## Dataset e principais achados

Foi utilizado o dataset público **Telco Customer Churn**, com 7.043 clientes e 21 colunas na versão bruta. A variável-alvo é `Churn`, em que `Yes` representa cancelamento.

Os principais achados descritivos da EDA foram:

- 26,54% dos clientes apresentam churn, caracterizando desbalanceamento da classe positiva;
- clientes com churn têm, em média, 17,98 meses de permanência, contra 37,57 meses entre os demais;
- contratos mensais apresentam 42,71% de churn, contra 11,27% nos anuais e 2,83% nos contratos de dois anos;
- clientes com fibra óptica apresentam 41,89% de churn no recorte observado;
- a cobrança mensal média é maior entre clientes com churn: 74,44 contra 61,27.

Essas relações são descritivas e não demonstram causalidade.

## Metodologia

O protocolo usado na comparação final:

1. converte `TotalCharges` para número e imputa seus 11 valores ausentes com a mediana calculada somente no treino;
2. remove `customerID` e transforma `Churn` em alvo binário;
3. faz divisão estratificada de 80% para treino e 20% para teste, com `random_state=42`;
4. cria e seleciona 18 features, incluindo atributos de permanência, cobrança, contrato, internet e interações;
5. aplica `StandardScaler` dentro dos pipelines que precisam de normalização;
6. avalia Regressão Logística, Random Forest e MLP nos mesmos dados e em validação cruzada estratificada de cinco folds;
7. compara recall, precision, F1, ROC-AUC, PR-AUC, MCC e estabilidade entre folds;
8. registra experimentos com MLflow e persiste os artefatos finais em `notebooks/models/`.

## Resultados

### Validação cruzada

| Modelo | Recall médio | Desvio do recall | ROC-AUC médio |
|---|---:|---:|---:|
| Regressão Logística | **0,8870** | **0,0119** | 0,8246 |
| Random Forest | 0,7987 | 0,0153 | **0,8423** |
| MLP | 0,5552 | 0,0239 | 0,8235 |

### Conjunto de teste

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | MCC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regressão Logística | 0,6615 | 0,4323 | **0,8797** | 0,5797 | 0,8260 | 0,6242 | 0,4096 |
| Random Forest | 0,7502 | 0,5194 | 0,7888 | **0,6263** | **0,8432** | **0,6493** | **0,4726** |
| MLP | **0,7913** | **0,6198** | 0,5535 | 0,5847 | 0,8373 | 0,6444 | 0,4473 |

### Modelo escolhido

A **Regressão Logística** é o modelo campeão formal porque obteve o maior recall, critério definido a partir do problema de negócio. No teste, seu recall foi 0,8797, com IC 95% bootstrap de `[0,845; 0,912]`, contra 0,7888 da Random Forest, com IC de `[0,747; 0,828]`.

Essa decisão tem um custo claro: a precision da Regressão Logística é 0,4323, portanto ela gera mais falsos positivos. A **Random Forest é a alternativa operacional mais equilibrada**, pois vence em F1, ROC-AUC, PR-AUC e MCC. Antes de produção, a escolha deve ser refeita com custos reais de falso positivo e falso negativo, capacidade da campanha e ajuste de threshold.

A API usa o artefato `notebooks/models/champion_model.joblib`, uma `Pipeline` com `StandardScaler` e Regressão Logística. O threshold atual é 0,5.

## Fairness

O notebook de fairness auditou o modelo campeão por `gender`. As diferenças máximas observadas entre os grupos `Female` e `Male` foram:

| Métrica | Diferença máxima |
|---|---:|
| Accuracy | 0,0016 |
| Selection rate | 0,0169 |
| False positive rate | 0,0070 |
| False negative rate | 0,0083 |

Não foi observada diferença superior a 2 pontos percentuais nesse recorte. Isso não prova equidade geral: a auditoria cobre somente gênero, nesta amostra e neste threshold.

## Estrutura do projeto

```text
.
├── .github/workflows/              # testes, qualidade de dados/modelo e secrets scan
├── data/
│   ├── download_dataset.py
│   └── raw/                        # criado pelo setup; dados não versionados
├── docs/
│   ├── MODEL_CARD.md
│   ├── VIDEO_STAR.md
│   └── MLCanvas.docx
├── models/
│   └── comparison_results.csv      # tabela definitiva dos três modelos
├── notebooks/
│   ├── eda_churn_prediction.ipynb
│   ├── fairness_churn_prediction.ipynb
│   ├── modelagem_avaliacao_churn_prediction.ipynb
│   └── models/                     # campeão e alternativa usados na entrega
├── scripts/setup.py
├── src/
│   ├── api/                        # routers, schemas, services e interface web
│   └── train_model/                # pipeline modular de treinamento
├── tests/
├── pyproject.toml
└── uv.lock
```

O notebook antigo `notebook.ipynb` e o treinamento modular em `src/train_model/` permanecem como histórico de desenvolvimento. A fonte da comparação final e do artefato servido é a sequência de notebooks em `notebooks/`.

## Contribuições da equipe

A divisão abaixo foi conferida no histórico de commits e registra as principais frentes, sem excluir revisões cruzadas:

| Integrante | Principais contribuições |
|---|---|
| Samuel Cambui | EDA e baseline; auditoria de fairness; comparação final entre os três modelos; persistência dos modelos |
| Lucas Balduino | pipeline modular inicial; refatoração da API para o novo artefato; schemas e engenharia das 18 features |
| Leonardo Oliveira | configuração do ambiente com `pyproject.toml`/uv; setup; GitHub Actions; testes e interface web da API |
| Lincoln | ML Canvas; revisão e documentação dos notebooks; apoio à integração das entregas |
| Claudia Park | README final; Model Card; roteiro STAR; testes e revisão de consistência da Etapa 4 |

## Instalação

Pré-requisitos: Git, Python 3.13 e [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/SamuelCambui/trabalho-final-fase-1.git
cd trabalho-final-fase-1
python -m pip install uv
uv sync --dev
```

O `pyproject.toml` e o `uv.lock` são as fontes de dependências do projeto.

### Download do dataset

1. Nas [configurações de API do Kaggle](https://www.kaggle.com/settings/api), crie uma chave legada.
2. Salve o arquivo como `kaggle.json` na raiz do projeto.
3. Execute:

```bash
uv run python scripts/setup.py
```

O script baixa `blastchar/telco-customer-churn` e valida o CSV em `data/raw/`. O `kaggle.json` é ignorado pelo Git e nunca deve ser versionado.

Para a CI, o conteúdo completo do arquivo deve ser cadastrado no secret de repositório `KAGGLE_JSON`.

## Reprodução dos notebooks

Depois do setup, abra os notebooks a partir da pasta `notebooks/` e execute-os nesta ordem:

```bash
cd notebooks
uv run jupyter notebook
```

1. `eda_churn_prediction.ipynb`;
2. `modelagem_avaliacao_churn_prediction.ipynb`;
3. `fairness_churn_prediction.ipynb`.

O primeiro notebook gera os dados processados usados pelos demais. O notebook de modelagem registra execuções no MLflow e sobrescreve os artefatos em `notebooks/models/`.

## Execução da API

O modelo campeão necessário para a demonstração está versionado no repositório.

```bash
cp .env.example .env
uv run uvicorn src.api.main:app --reload
```

Acesse:

- interface web: <http://127.0.0.1:8000/>;
- Swagger: <http://127.0.0.1:8000/docs>;
- health check: <http://127.0.0.1:8000/health>.

Credenciais locais de demonstração: `admin/admin` ou `user/user`.

### Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| GET | `/` | não | Interface web da demonstração |
| GET | `/health` | não | Estado da API e do modelo |
| GET | `/model/info` | não | Tipo do classificador e threshold |
| POST | `/auth/login` | não | Autentica e grava o JWT em cookie HttpOnly |
| GET | `/auth/me` | cookie | Dados do usuário autenticado |
| POST | `/auth/logout` | não | Remove o cookie de autenticação |
| POST | `/predict` | cookie | Classe e probabilidade de churn |

### Exemplo com `curl`

O login grava o cookie em um arquivo local:

```bash
curl -c cookies.txt -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Use o cookie na predição:

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/predict \
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

Resposta observada com o artefato versionado:

```json
{
  "prediction": "Yes",
  "probability": 0.6411
}
```

## Testes e CI

Os testes independentes do dataset podem ser executados logo após a instalação:

```bash
uv run pytest -q tests/test_api.py tests/test_preprocessing.py tests/tests/test_train.py
```

Após baixar o dataset, execute a suíte completa:

```bash
uv run pytest -q
```

Os workflows do GitHub Actions validam API, dados, métricas do modelo, cobertura e exposição de segredos. Os jobs que usam o dataset dependem do secret `KAGGLE_JSON`.

## Limitações e uso responsável

- a base pública de uma única empresa pode não representar outras operadoras ou períodos;
- não há dimensão temporal adequada para validação fora do tempo ou medição histórica de drift;
- o threshold 0,5 não foi escolhido por uma função de custo nem pela capacidade real de uma campanha;
- as probabilidades ainda não foram calibradas;
- a fairness foi auditada somente por gênero, não por todas as combinações de subgrupos;
- o modelo não fornece explicações locais por predição;
- usuários fixos, senhas de demonstração e a chave JWT padrão não são adequados para produção.

Antes de qualquer uso real, são necessários dados recentes da operadora, definição de custos, escolha e validação do threshold, calibração, análise ampliada por subgrupos, monitoramento de drift e revisão humana das ações de retenção.

## Documentação da entrega

- [Model Card](docs/MODEL_CARD.md)
- [Roteiro e plano de gravação do vídeo STAR](docs/VIDEO_STAR.md)
- [ML Canvas](docs/MLCanvas.docx)
