# Model Card — Predição de Churn Telco

## 1. Informações gerais

| Campo | Valor |
|---|---|
| Projeto | Tech Challenge — Fase 1 FIAP Pós-Tech |
| Versão do documento | 2.0 |
| Data | 26/08/2026 |
| Responsáveis | Equipe do Tech Challenge |
| Domínio | Telecomunicações / retenção de clientes |
| Tarefa | Classificação binária supervisionada |
| Saída | Probabilidade de churn e classe `Yes` ou `No` |
| Modelo campeão | Regressão Logística com `class_weight='balanced'` |
| Artefato servido | `notebooks/models/champion_model.joblib` |
| Threshold atual | 0,5 |

## 2. Objetivo e uso pretendido

O modelo estima o risco de cancelamento de um cliente de telecomunicações. O uso pretendido é apoiar a priorização de campanhas de retenção, permitindo que a área responsável avalie clientes com maior risco e escolha uma ação apropriada.

Usuários previstos:

- analistas de dados e Machine Learning;
- equipes de CRM e retenção;
- desenvolvedores responsáveis pela API de inferência.

O resultado não deve ser usado isoladamente para negar serviços, modificar preços, aplicar punições ou tomar decisões de alto impacto sem revisão humana.

## 3. Dados

O projeto usa o dataset público **Telco Customer Churn**, distribuído no Kaggle em `blastchar/telco-customer-churn`.

- volume bruto: 7.043 registros e 21 colunas;
- alvo: `Churn`, mapeado de `No`/`Yes` para 0/1;
- prevalência de churn: 26,54%;
- `customerID`: removido da modelagem;
- `TotalCharges`: convertido para número; 11 ausências foram imputadas com a mediana do treino (1398,12);
- divisão: 80% treino e 20% teste, estratificada, com `random_state=42`;
- amostras finais: 5.634 registros de treino e 1.409 de teste.

O projeto não dispõe de informações confiáveis sobre período de coleta, população amostrada ou cobertura geográfica. Não há variável temporal adequada para validação fora do tempo.

## 4. Features e pré-processamento

Após engenharia e seleção, os modelos recebem 18 features relacionadas a permanência, cobranças, contrato, internet, método de pagamento e interações entre esses fatores.

A Regressão Logística e a MLP usam `StandardScaler` dentro de uma `Pipeline`. O Random Forest recebe as mesmas 18 features e usa pesos balanceados. A comparação usa os mesmos conjuntos de treino/teste e os mesmos cinco folds estratificados.

Principais configurações finais:

| Modelo | Configuração |
|---|---|
| Regressão Logística | `C=0.001707`, `solver='saga'`, `class_weight='balanced'`, `max_iter=2000`, `random_state=42` |
| Random Forest | `n_estimators=198`, `max_depth=5`, `max_features='sqrt'`, `min_samples_leaf=7`, `min_samples_split=6`, `class_weight='balanced'`, `random_state=42` |
| MLP | uma camada de 16 neurônios, `alpha=1e-5`, `learning_rate_init=1e-4`, `early_stopping=True`, `random_state=42` |

## 5. Protocolo de avaliação

O recall da classe churn é a métrica prioritária porque o problema assume que um falso negativo custa mais que uma abordagem desnecessária. Para tornar o trade-off visível, também são avaliados precision, F1, ROC-AUC, PR-AUC, MCC, matriz de confusão e estabilidade em validação cruzada.

Essa prioridade é uma hipótese de negócio, não um custo confirmado. A equipe ainda não recebeu valores monetários nem uma capacidade máxima de campanha.

## 6. Resultados

### 6.1 Validação cruzada estratificada — cinco folds

| Modelo | Recall médio | Desvio do recall | ROC-AUC médio |
|---|---:|---:|---:|
| Regressão Logística | **0,8870** | **0,0119** | 0,8246 |
| Random Forest | 0,7987 | 0,0153 | **0,8423** |
| MLP | 0,5552 | 0,0239 | 0,8235 |

### 6.2 Teste hold-out

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | MCC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regressão Logística | 0,6615 | 0,4323 | **0,8797** | 0,5797 | 0,8260 | 0,6242 | 0,4096 |
| Random Forest | 0,7502 | 0,5194 | 0,7888 | **0,6263** | **0,8432** | **0,6493** | **0,4726** |
| MLP | **0,7913** | **0,6198** | 0,5535 | 0,5847 | 0,8373 | 0,6444 | 0,4473 |

### 6.3 Incerteza e comparação estatística

O recall da Regressão Logística teve IC 95% bootstrap de `[0,845; 0,912]`; o da Random Forest, `[0,747; 0,828]`; e o da MLP, `[0,504; 0,604]`. Os intervalos sustentam a vantagem de recall da Regressão Logística nesta amostra.

Os intervalos de ROC-AUC e PR-AUC dos três modelos se sobrepõem. Portanto, as pequenas diferenças nessas métricas não demonstram, sozinhas, superioridade estatística de separabilidade.

O teste de McNemar aplicado às classificações mede diferença de erros globais, não diferença específica de recall. Ele favorece a Random Forest sobre a Regressão Logística em acertos totais; não deve ser usado como prova da vantagem de recall do modelo linear.

## 7. Escolha do modelo

A **Regressão Logística** é o campeão formal porque maximiza o recall, critério definido para minimizar falsos negativos. Seu artefato é servido pela API.

A decisão é sensível ao objetivo:

- a Regressão Logística encontra mais clientes que efetivamente cancelam, mas sua precision de 0,4323 produz mais abordagens desnecessárias;
- a Random Forest oferece o melhor equilíbrio global, vencendo em F1, ROC-AUC, PR-AUC e MCC;
- a MLP tem maior accuracy e precision no threshold 0,5, mas o pior recall.

Sem custos reais de erros e capacidade da campanha, não é possível afirmar que o campeão formal é também a alternativa economicamente ótima. A Random Forest deve permanecer como candidata operacional.

## 8. Fairness

O modelo campeão foi auditado com `fairlearn` por `gender` no conjunto de teste.

| Métrica | Female | Male | Diferença máxima |
|---|---:|---:|---:|
| Accuracy | 0,6623 | 0,6607 | 0,0016 |
| Selection rate | 0,5488 | 0,5319 | 0,0169 |
| False positive rate | 0,4211 | 0,4140 | 0,0070 |
| False negative rate | 0,1244 | 0,1160 | 0,0083 |

Nenhuma diferença ultrapassou 2 pontos percentuais. Esse resultado vale somente para gênero, nesta amostra, com o threshold atual. Ele não comprova ausência de viés em outros atributos, interseções de grupos, períodos ou populações.

## 9. Limitações e riscos

- **Generalização:** uma base pública de uma única empresa pode não representar outras operadoras.
- **Temporalidade:** não há validação fora do tempo nem evidência sobre drift histórico.
- **Desbalanceamento:** somente 26,54% dos registros pertencem à classe positiva.
- **Threshold:** o corte 0,5 não foi escolhido por custo, orçamento ou capacidade operacional.
- **Calibração:** não há Brier score, curva de calibração ou calibração pós-treino; a saída não deve ser interpretada como probabilidade perfeitamente calibrada.
- **Fairness:** somente gênero foi auditado e não houve avaliação interseccional.
- **Explicabilidade:** a API ainda não fornece justificativas locais por predição.
- **Feature engineering:** a API reproduz 18 features manualmente e usa uma mediana fixa do treino; qualquer novo treinamento exige validação de compatibilidade.
- **Segurança:** contas fixas e chave JWT padrão servem somente para demonstração local.
- **Persistência:** artefatos `joblib`/pickle só devem ser carregados de origem confiável.

## 10. Monitoramento recomendado

Em uma implantação real, monitorar:

- schema, categorias e faixas das entradas;
- taxa prevista e taxa real de churn;
- precision, recall, F1, ROC-AUC, PR-AUC e calibração após chegada dos rótulos;
- métricas por subgrupos e interseções relevantes;
- drift das features e das probabilidades;
- latência, erros HTTP e indisponibilidade do modelo;
- volume, custo e resultado das campanhas de retenção.

Threshold, alertas e frequência de retreinamento devem ser definidos a partir dos custos e da velocidade real de mudança dos dados.

## 11. Segurança e privacidade

- coletar e armazenar somente dados necessários e com base legal;
- não registrar payloads pessoais sem necessidade;
- aplicar controle de acesso, criptografia, retenção e trilha de auditoria;
- substituir usuários fixos por um provedor de identidade;
- manter a chave JWT em um gerenciador de segredos;
- manter revisão humana sobre as ações de retenção.

## 12. Reprodução

```bash
python -m pip install uv
uv sync --dev
uv run python scripts/setup.py
cd notebooks
uv run jupyter notebook
```

Execute `eda_churn_prediction.ipynb`, `modelagem_avaliacao_churn_prediction.ipynb` e `fairness_churn_prediction.ipynb`, nessa ordem. Depois, a partir da raiz:

```bash
uv run pytest -q
uv run uvicorn src.api.main:app --reload
```

O download exige uma credencial Kaggle local. A API da entrega carrega `notebooks/models/champion_model.joblib`.

## 13. Próximos passos

1. definir custos de falso positivo e falso negativo e a capacidade da campanha;
2. selecionar o threshold em validação separada e confirmar o ganho em teste final intocado;
3. avaliar e, se necessário, calibrar probabilidades;
4. ampliar a auditoria de fairness e incluir análise interseccional;
5. eliminar duplicidades entre o fluxo modular e o fluxo final dos notebooks;
6. adicionar versionamento formal de dados e artefatos;
7. validar o modelo em dados recentes e representativos da operadora.
