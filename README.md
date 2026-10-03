# Predição de Churn de Clientes Telco

Projeto do Tech Challenge — Fase 1 da FIAP Pós-Tech. A solução percorre análise exploratória, definição de métricas, treinamento e comparação de modelos, auditoria de fairness e disponibilização de inferência por uma API FastAPI.

## Vídeo de apresentação

[Assista ao vídeo STAR do projeto no YouTube](https://youtu.be/mdZhZsDLKgU).

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
├── grafana/
│   └── provisioning/              # configuração automática do Grafana
│       ├── dashboards/
│       │   ├── dashboard.yml
│       │   └── churn-api-overview.json
│       └── datasources/
│           └── datasource.yml     # conexão com o Prometheus
├── models/
│   └── comparison_results.csv      # tabela definitiva dos três modelos
├── notebooks/
│   ├── eda_churn_prediction.ipynb
│   ├── fairness_churn_prediction.ipynb
│   ├── modelagem_avaliacao_churn_prediction.ipynb
│   └── models/                     # campeão e alternativa usados na entrega
├── prometheus/
│   ├── prometheus.yml             # coleta de métricas
│   └── alerts.yml                 # regras de alerta
├── scripts/setup.py
├── src/
│   ├── api/                        # routers, schemas, services e interface web
│   └── train_model/                # pipeline modular de treinamento
├── tests/
├── .env.example                   # exemplo de configuração, sem segredos
├── Dockerfile
├── docker-compose.yml             # API + Prometheus + Grafana
├── pyproject.toml
└── poetry.lock
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

Pré-requisitos: Git, Python 3.13 e [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/SamuelCambui/trabalho-final-fase-1.git
cd trabalho-final-fase-1
python -m pip install poetry
poetry install --with notebooks
```

O `pyproject.toml` e o `poetry.lock` são as fontes de dependências do projeto.

### Download do dataset

1. Nas [configurações de API do Kaggle](https://www.kaggle.com/settings/api), crie uma chave legada.
2. Salve o arquivo como `kaggle.json` na raiz do projeto.
3. Execute:

```bash
poetry run python scripts/setup.py
```

O script baixa `blastchar/telco-customer-churn` e valida o CSV em `data/raw/`. O `kaggle.json` é ignorado pelo Git e nunca deve ser versionado.

Para a CI, o conteúdo completo do arquivo deve ser cadastrado no secret de repositório `KAGGLE_JSON`.

## Reprodução dos notebooks

Depois do setup, abra os notebooks a partir da pasta `notebooks/` e execute-os nesta ordem:

```bash
cd notebooks
poetry run jupyter notebook
```

1. `eda_churn_prediction.ipynb`;
2. `modelagem_avaliacao_churn_prediction.ipynb`;
3. `fairness_churn_prediction.ipynb`.

O primeiro notebook gera os dados processados usados pelos demais. O notebook de modelagem registra execuções no MLflow e sobrescreve os artefatos em `notebooks/models/`.

## Execução da API

O modelo campeão necessário para a demonstração está versionado no repositório.

```bash
cp .env.example .env
poetry run uvicorn src.api.main:app --reload
```

Acesse:

- interface web: <http://127.0.0.1:8000/>;
- Swagger: <http://127.0.0.1:8000/docs>;
- health check: <http://127.0.0.1:8000/health>.

Use o usuário e a senha definidos no seu `.env`.

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
  -d '{"username":"admin","password":"SUA_SENHA"}'
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

## Monitoramento com Prometheus e Grafana

O projeto disponibiliza uma stack com a API FastAPI, Prometheus para coleta
de métricas e Grafana para visualização. A API expõe as métricas em `/metrics`;
o Prometheus consulta esse endpoint a cada 15 segundos. O Grafana usa o
Prometheus como fonte de dados.

### Subir a stack

Pré-requisitos: Docker com Docker Compose, `pyproject.toml`, `poetry.lock` e
o modelo `notebooks/models/champion_model.joblib` disponível. O modelo é
montado no container da API como volume somente leitura.

Na raiz do projeto, crie o arquivo de configuração (PowerShell):

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie a chave gerada para `SECRET_KEY` no `.env` e preencha
`API_ADMIN_PASSWORD`, `API_USER_PASSWORD` e `GF_SECURITY_ADMIN_PASSWORD`.
Os usuários são configurados por `API_ADMIN_USERNAME`, `API_USER_USERNAME`
e `GF_SECURITY_ADMIN_USER`. Se já tiver um `.env`, edite-o sem sobrescrevê-lo.

Depois, execute:

```bash
docker compose up -d --build
docker compose ps
```

| Serviço | Endereço padrão | Uso |
|---|---|---|
| API | http://localhost:8000/docs | Autenticação e predições |
| Métricas | http://localhost:8000/metrics | Métricas expostas pela API |
| Prometheus | http://localhost:9090 | Consultas PromQL, targets e alertas |
| Grafana | http://localhost:3000 | Dashboard de monitoramento |

As portas externas podem ser alteradas no `.env` usando `API_PORT`,
`PROMETHEUS_PORT` e `GRAFANA_PORT`. Os endereços internos dos containers
permanecem `api:8000` e `prometheus:9090`.

### Dashboard e métricas

Faça login no Grafana com `GF_SECURITY_ADMIN_USER` e
`GF_SECURITY_ADMIN_PASSWORD`. A fonte de dados **Prometheus** e o dashboard
**Churn API - Visão Geral** são provisionados automaticamente pelos arquivos
em `grafana/provisioning/`. Abra o dashboard na área **Dashboards**.

| Métrica | Informação acompanhada |
|---|---|
| `http_requests_total` | Quantidade de requisições HTTP |
| `http_request_duration_seconds` | Distribuição da latência HTTP |
| `churn_predictions_total` | Predições por classe e usuário |
| `churn_prediction_latency_seconds` | Distribuição da latência das predições |
| `login_attempts_total` | Tentativas de login por status |
| `api_errors_total` | Erros por endpoint e tipo |
| `model_loaded` | Modelo carregado (`1`) ou indisponível (`0`) |
| `prediction_avg_confidence` | Média cumulativa das probabilidades de churn desde a inicialização da API |

Para alimentar os gráficos, realize logins e predições pela interface ou pelo
Swagger e aguarde as coletas. Painéis baseados em `rate` e percentis precisam
de várias amostras; podem ficar vazios logo após a inicialização.

No Prometheus, abra **Status → Targets** e confira se `churn-api` está **UP**.
Exemplos de consultas:

```promql
# Disponibilidade da coleta da API
up{job="churn-api"}

# Requisições por segundo
sum(rate(http_requests_total{job="churn-api"}[5m]))

# Estado do modelo
model_loaded{job="churn-api"}

# Latência p95 das predições, em segundos
histogram_quantile(0.95, sum by (le) (rate(churn_prediction_latency_seconds_bucket{job="churn-api"}[5m])))
```

### Alertas e operação

O arquivo `prometheus/alerts.yml` contém três regras, avaliadas a cada 15 segundos:

| Regra | Objetivo configurado | Tempo de persistência |
|---|---|---|
| `HighErrorRate` | Detectar proporção de erros 5xx acima de 5% | 2 minutos |
| `HighLatency` | Detectar latência HTTP p95 acima de 1 segundo | 5 minutos |
| `ModelNotLoaded` | Detectar `model_loaded == 0` | 1 minuto |

Consulte os estados das regras na área **Alerts** do Prometheus. A stack
atual não inclui Alertmanager nem envio automático de notificações.
As consultas de erro e latência existentes precisam de validação com as
séries e labels efetivamente expostas pela API antes de uso operacional.

Para consultar logs e parar os serviços:

```bash
docker compose logs --tail=100 api prometheus grafana
docker compose down
```

Os volumes `prometheus_data` e `grafana_data` mantêm os dados após
`docker compose down`. O comando `docker compose down -v` também remove
esses volumes e seus dados.

## Testes

Os testes independentes do dataset podem ser executados logo após a instalação:

```bash
poetry run pytest -q tests/test_api.py tests/test_preprocessing.py tests/test_train.py
```

Após baixar o dataset, execute a suíte completa:

```bash
poetry run pytest -q
```

Os jobs que usam o dataset dependem do secret `KAGGLE_JSON`.

## Quality Gates da Esteira CI/CD

Um Pull Request ou Push será considerado aprovado apenas se todos os
workflows obrigatórios forem concluídos com sucesso.

### Testes
- Todos os testes automatizados devem passar.
- Testes de API, pré-processamento e treinamento devem executar sem erros.

### Cobertura
- A cobertura mínima exigida pelo projeto é de 70%.
- Valores abaixo de 70% fazem o workflow falhar.

### Métricas do Modelo

O modelo deve atender aos seguintes valores mínimos:

| Métrica | Classe 0 | Classe 1 |
|---|---:|---:|
| Precision | 0.70 | 0.55 |
| Recall | 0.70 | 0.45 |
| F1-Score | 0.70 | 0.45 |

Além disso:

- Accuracy >= 0.65
- Macro Precision >= 0.65
- Macro Recall >= 0.60
- Macro F1 >= 0.60
- Weighted Precision >= 0.60
- Weighted Recall >= 0.60
- Weighted F1 >= 0.60

### Segurança
- O workflow verifica a exposição de segredos no código.
- Credenciais e tokens não devem ser versionados.
- Os dados dependentes do Kaggle são acessados por meio do secret `KAGGLE_JSON`.

Se qualquer Quality Gate obrigatório falhar, o workflow será marcado como
falho e a alteração não atenderá aos critérios de qualidade definidos
para o projeto.


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

## Dependências e configuração com Poetry

Use Python 3.13. Produção: `poetry install --only main`.
Desenvolvimento: `poetry install`. Notebooks: `poetry install --with notebooks`.
As dependências de visualização, fairness e análise estatística ficam no grupo
opcional `notebooks`; pytest, Ruff e httpx ficam em `dev`.

Antes de iniciar a API, copie `.env.example` para `.env` (no PowerShell:
`Copy-Item .env.example .env`). Preencha SECRET_KEY, API_ADMIN_PASSWORD,
API_USER_PASSWORD e GF_SECURITY_ADMIN_PASSWORD. Nunca versione o `.env`.
Variáveis exportadas no sistema têm prioridade. Caminhos relativos são
resolvidos a partir da raiz do projeto.

Após alterar dependências, execute `poetry lock` e `poetry check --lock`.
Versione `pyproject.toml` e `poetry.lock` juntos. O Docker exige esse lock.
O lock do projeto é `poetry.lock`; o antigo lock do uv foi removido.
