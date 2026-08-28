# Vídeo STAR — roteiro de até 5 minutos

Este roteiro apresenta o trabalho pelo método STAR e demonstra a interface da API. Fale de forma natural; use o texto como guia, não como leitura obrigatória.

## Preparação antes de gravar

1. Na raiz do projeto, execute `uv sync --dev`.
2. Copie o ambiente com `cp .env.example .env`.
3. Inicie a API com `uv run uvicorn src.api.main:app --reload`.
4. Abra e teste previamente:
   - README no GitHub;
   - tabela final do notebook de modelagem;
   - interface em <http://127.0.0.1:8000/>;
   - Model Card.
5. Na interface, confirme login com `admin/admin` e faça uma predição completa.
6. Feche notificações e qualquer tela com `kaggle.json`, `.env`, token ou dado pessoal.
7. Grave em 1080p, com zoom legível, e mantenha a duração entre 4min30s e 4min55s.

O modelo campeão já está versionado em `notebooks/models/champion_model.joblib`; não é necessário treinar novamente antes da gravação.

## Cronograma visual

| Tempo | STAR | Tela sugerida |
|---|---|---|
| 0:00–0:35 | Situation | README: problema e achados da EDA |
| 0:35–1:00 | Task | README: entregas e estrutura |
| 1:00–2:55 | Action | Notebook: protocolo e tabela dos três modelos |
| 2:55–4:20 | Result | Interface: login, health/modelo e predição |
| 4:20–4:50 | Result / fechamento | Model Card: decisão, fairness e limitações |

## Roteiro falado

### 0:00–0:35 — Situation

> Olá! Este é o Tech Challenge da Fase 1 da FIAP Pós-Tech. Trabalhamos com churn em uma operadora de telecomunicações: o objetivo é reconhecer clientes com maior risco de cancelamento para apoiar ações de retenção. O dataset público tem 7.043 clientes e 21 colunas. Na EDA, 26,54% dos clientes apresentaram churn. Também observamos maior churn em contratos mensais, clientes de fibra óptica e clientes com menor permanência. São associações descritivas, não relações causais.

### 0:35–1:00 — Task

> A tarefa foi entregar o ciclo completo: explorar e preparar os dados, definir métricas de negócio, criar uma Regressão Logística como baseline, treinar Random Forest e MLP, comparar os três modelos no mesmo protocolo e publicar a inferência em uma API FastAPI. Também incluímos testes, integração contínua, auditoria de fairness e documentação do modelo.

### 1:00–2:55 — Action

> Primeiro, convertemos TotalCharges para número e imputamos 11 valores ausentes com a mediana calculada apenas no treino. Removemos o identificador do cliente e fizemos uma divisão estratificada de 80% para treino e 20% para teste, com semente 42.
>
> A engenharia e a seleção resultaram em 18 features. A validação cruzada usa cinco folds estratificados, e todos os modelos foram comparados nos mesmos dados. Como o custo assumido de não identificar um cliente que cancelará é alto, definimos recall de churn como métrica de negócio. Também acompanhamos precision, F1, ROC-AUC, PR-AUC e MCC.
>
> No teste, a Regressão Logística atingiu recall de 0,8797; a Random Forest, 0,7888; e a MLP, 0,5535. Por isso, a Regressão Logística foi declarada campeã formal e é o modelo servido pela API. Mas a decisão tem trade-off: sua precision é 0,4323, enquanto a Random Forest tem o melhor F1, ROC-AUC, PR-AUC e MCC. Sem custos monetários e capacidade real da campanha, não afirmamos que existe um único modelo economicamente ótimo.
>
> A auditoria de fairness por gênero encontrou diferenças inferiores a 2 pontos percentuais nas métricas avaliadas. Esse resultado vale apenas para esse atributo e essa amostra.
>
> Por fim, organizamos a aplicação em routers, schemas e services, reproduzimos as 18 features na inferência, adicionamos autenticação JWT por cookie, testes automatizados e workflows no GitHub Actions.

### 2:55–4:20 — Result e demonstração

Enquanto fala, use a interface em <http://127.0.0.1:8000/>.

1. Mostre que o status indica API online e modelo carregado.
2. Faça login com `admin/admin`.
3. Preencha ou mantenha o exemplo de cliente e clique para prever.
4. Mostre a classe e a probabilidade retornadas.

> A API carregou a Pipeline de Regressão Logística e confirmou o health check. Após o login, a aplicação envia os dados brutos do cliente, aplica a mesma engenharia das 18 features e retorna a classe prevista junto com a probabilidade estimada. Neste exemplo de reserva, o retorno esperado com o artefato atual é churn `Yes`, com probabilidade próxima de 0,6411.

Se preferir o Swagger, execute `POST /auth/login` com `admin/admin`. O navegador grava o cookie HttpOnly automaticamente; depois execute `POST /predict`. Não use o botão **Authorize**, pois a implementação atual autentica por cookie, e não pelo header Bearer.

### 4:20–4:50 — Fechamento

> Como resultado, entregamos três modelos comparados, auditoria de fairness e API funcional. A Regressão Logística alcançou recall de 0,8797, e a esteira aprovou 20 testes, com 72% de cobertura e cinco workflows concluídos. Permanecem como limitações o threshold fixo, a ausência de calibração e a fairness restrita a gênero. Antes de produção, validaríamos dados recentes e custos de negócio. Obrigado!

## Payload de reserva

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

Retorno verificado com o artefato atual:

```json
{
  "prediction": "Yes",
  "probability": 0.6411
}
```

## Plano de contingência

- Se a interface não abrir, mostre `/health` e faça a demonstração pelo Swagger.
- Se o login falhar, confirme que as credenciais são exatamente `admin/admin`.
- Se o modelo não carregar, reinicie a API a partir da raiz do repositório e confirme a existência de `notebooks/models/champion_model.joblib`.
- Se a predição retornar 401, refaça o login na mesma aba; o JWT fica em cookie HttpOnly.
- Se a gravação ultrapassar 5 minutos, corte detalhes de hiperparâmetros, preservando Situation, Task, Action e Result.
- Tenha uma gravação de reserva da demonstração funcionando para inserir na edição se a execução ao vivo falhar.

## Checklist final

- [ ] duração máxima de 5 minutos;
- [ ] Situation, Task, Action e Result claramente identificáveis;
- [ ] os três modelos e o critério de escolha foram explicados;
- [ ] trade-off entre Regressão Logística e Random Forest foi mencionado;
- [ ] API demonstrada com modelo carregado;
- [ ] nenhum segredo, token ou dado pessoal aparece;
- [ ] áudio compreensível e tela legível;
- [ ] vídeo assistido do início ao fim após a edição;
- [ ] link final adicionado à entrega e, se desejado, ao README.
