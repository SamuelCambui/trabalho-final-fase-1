# Vídeo STAR - roteiro de até 5 minutos

Este roteiro cobre os quatro pontos exigidos pelo método STAR e reserva tempo para demonstrar a API. Use linguagem natural; não é necessário ler cada frase literalmente.

## Preparação antes de gravar

1. Treine o modelo com `python -m src.train_model.train`.
2. Inicie a API com `python -m uvicorn src.api.main:app --reload`.
3. Deixe abertas quatro abas: README, notebook, Model Card e Swagger em <http://127.0.0.1:8000/docs>.
4. No Swagger, teste previamente `/health`, `/auth/login` e `/predict`.
5. Feche notificações, aumente o zoom do navegador e confirme que nenhum token ou segredo real aparece na tela.
6. Grave em 1080p e mantenha a duração total entre 4min30s e 5min.

## Cronograma visual

| Tempo | STAR | Tela sugerida |
|---|---|---|
| 0:00-0:40 | Situation | Título do README e achados da EDA |
| 0:40-1:10 | Task | Entregas e arquitetura do projeto |
| 1:10-3:20 | Action | Notebook, comparação de modelos e estrutura `src/` |
| 3:20-4:35 | Result | Swagger: health, login e predict |
| 4:35-4:55 | Result / fechamento | Model Card e próximos passos |

## Roteiro falado

### 0:00-0:40 - Situation

> Olá! Este é o Tech Challenge da Fase 1 da FIAP Pós-Tech. O problema de negócio é o churn em uma operadora de telecomunicações. A empresa precisa reconhecer antecipadamente clientes com maior risco de cancelamento para priorizar ações de retenção. Usamos o dataset público Telco Customer Churn, com 7.043 clientes e 21 colunas. Na análise exploratória, 26,54% dos clientes apresentaram churn. Também observamos maior churn entre contratos mensais, clientes de fibra óptica e clientes com menor tempo de permanência. Essas relações são descritivas e não significam causalidade.

### 0:40-1:10 - Task

> Nossa tarefa foi construir um pipeline completo e reprodutível: explorar e limpar os dados, definir métricas, criar uma Regressão Logística como baseline, treinar Random Forest e uma rede MLP, comparar os resultados, salvar um modelo final e disponibilizar a inferência em uma API FastAPI. Também organizamos o código em módulos, fixamos as sementes, adicionamos testes e documentamos limitações e possíveis vieses.

### 1:10-3:20 - Action

> Primeiro, convertemos TotalCharges para formato numérico, removemos o identificador customerID e tratamos os registros inválidos. Dividimos os dados de forma estratificada, com 70% para treino e 30% para teste e semente 42.
>
> O pré-processamento foi colocado dentro de um Pipeline do Scikit-Learn. Variáveis numéricas recebem imputação pela mediana e padronização. Variáveis categóricas recebem imputação pela moda e one-hot encoding. Isso ajuda a evitar vazamento de dados entre treino e validação.
>
> A métrica principal de seleção foi ROC-AUC, avaliada com validação cruzada de cinco folds. A MLP obteve ROC-AUC médio de 0,8481, e a Random Forest, 0,8477. Como a regra implementada escolhe o maior ROC-AUC médio, a MLP foi salva como modelo usado pela API.
>
> Porém, a diferença é muito pequena. No teste, a Random Forest teve recall de 0,779 para churn, contra 0,522 da MLP. A MLP teve maior accuracy e precision. Portanto, documentamos no Model Card que a escolha operacional depende do custo de negócio: se perder um cliente de alto risco for mais caro, a Random Forest ou um threshold ajustado podem ser melhores.
>
> Depois, refatoramos o treinamento e a inferência para a pasta src. A API possui schemas de entrada e saída, serviços separados e rotas de health, autenticação e predição. O acesso à predição usa token JWT para demonstração.

### 3:20-4:35 - Result e demonstração

Enquanto fala, execute os passos abaixo no Swagger.

1. Abra `GET /health`, clique em **Try it out** e **Execute**.

> Com o modelo treinado, o health check retorna status ok e confirma que o artefato foi carregado.

2. Abra `POST /auth/login`, use `admin` e `admin`, execute e copie somente o valor de `access_token`.

> O login retorna um token temporário. Ele protege o endpoint de predição na demonstração.

3. Clique em **Authorize**, cole o token, feche a janela e abra `POST /predict`.
4. Use o exemplo já preenchido pelo Swagger e clique em **Execute**.

> O endpoint recebe os dados de um cliente e retorna a classe prevista, Yes ou No, junto com a probabilidade estimada de churn. Assim, o modelo treinado pode ser consumido por outros sistemas por meio de uma interface REST documentada.

### 4:35-4:55 - Fechamento

> Como resultado, entregamos a análise exploratória, os pipelines de modelagem, a comparação dos modelos e uma API funcional. Também registramos limitações: a base é pública, o threshold ainda não foi otimizado por custo, as probabilidades não foram calibradas e atributos demográficos exigem avaliação de equidade. Antes de produção, validaríamos o modelo com dados recentes da operadora, métricas por subgrupo e monitoramento de drift. Obrigado!

## Payload de reserva para a demonstração

```json
{
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
}
```

## Plano de contingência

- Se o modelo não carregar, mostre o `/health` degradado, explique que o artefato não é versionado e interrompa a gravação para treinar antes de tentar novamente.
- Se o token expirar, gere outro em `/auth/login`.
- Se a demonstração ao vivo atrasar, mostre apenas `/health` e `/predict`; a explicação da arquitetura já cobre a autenticação.
- Se a gravação ultrapassar 5 minutos, corte detalhes dos hiperparâmetros, não as quatro partes do STAR.

## Checklist final

- [ ] duração máxima de 5 minutos;
- [ ] Situation, Task, Action e Result claramente identificáveis;
- [ ] API demonstrada com modelo carregado;
- [ ] nenhum segredo ou token real visível;
- [ ] áudio compreensível e tela legível;
- [ ] link do vídeo adicionado à entrega da FIAP e, se desejado, ao README.
