# Model Card - Predição de Churn Telco

## 1. Informações gerais

| Campo | Valor |
|---|---|
| Projeto | Tech Challenge - Fase 1 FIAP Pós-Tech |
| Versão do documento | 1.0 |
| Data | 20/08/2026 |
| Responsáveis | Equipe do Tech Challenge |
| Domínio | Telecomunicações / retenção de clientes |
| Tipo de tarefa | Classificação binária supervisionada |
| Saída | Probabilidade de churn e classe `Yes` ou `No` |
| Artefato servido | `models/model.joblib` |

## 2. Objetivo e uso pretendido

O modelo estima a probabilidade de cancelamento de um cliente de telecomunicações. O uso pretendido é apoiar a priorização de campanhas de retenção, permitindo que a área responsável avalie clientes com maior risco e escolha uma ação apropriada.

Usuários previstos:

- analistas de dados e Machine Learning;
- equipes de CRM e retenção;
- desenvolvedores responsáveis pela API de inferência.

O resultado não deve ser usado isoladamente para negar serviços, modificar preços, aplicar punições, realizar discriminação ou tomar decisões de alto impacto sem revisão humana.

## 3. Dados

O projeto usa o dataset público **Telco Customer Churn**, distribuído no Kaggle em `blastchar/telco-customer-churn`.

- volume bruto: 7.043 registros e 21 colunas;
- alvo: `Churn`, mapeado de `No`/`Yes` para 0/1;
- prevalência observada de churn: 26,54%;
- identificador `customerID`: removido do treinamento;
- `TotalCharges`: convertido para valor numérico;
- registros inválidos após a conversão: removidos pelo pipeline de treinamento;
- divisão: 70% treino e 30% teste, estratificada, com `random_state=42`.

As variáveis incluem dados demográficos básicos, serviços contratados, tipo de contrato, forma de pagamento, tempo de permanência e cobranças. A documentação original disponível no projeto não informa período de coleta, população amostrada ou cobertura geográfica.

## 4. Modelos e pré-processamento

Foram considerados:

- Regressão Logística como baseline;
- Random Forest com balanceamento de classes;
- MLPClassifier como rede neural simples.

O pipeline final aplica:

- imputação pela mediana e padronização para variáveis numéricas;
- imputação pela moda e one-hot encoding para variáveis categóricas;
- categorias desconhecidas ignoradas no encoder;
- validação cruzada de 5 folds;
- ROC-AUC como métrica primária de seleção.

Parâmetros selecionados na execução registrada:

| Modelo | Parâmetros selecionados |
|---|---|
| Random Forest | `n_estimators=300`, `max_depth=10`, `min_samples_split=10`, `class_weight=balanced` |
| MLP | `hidden_layer_sizes=(64, 32)`, `activation=tanh`, `alpha=0.001`, `max_iter=500`, `early_stopping=True` |

Todos os modelos usam semente fixa igual a 42 quando o estimador oferece esse parâmetro.

## 5. Avaliação

### 5.1 Validação cruzada do pipeline final

| Modelo | ROC-AUC médio | Desvio padrão |
|---|---:|---:|
| MLP | 0,8481 | 0,0150 |
| Random Forest | 0,8477 | 0,0147 |

### 5.2 Teste hold-out

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0,7502 | 0,5202 | **0,7790** | **0,6238** | **0,8326** |
| MLP | **0,7948** | **0,6397** | 0,5223 | 0,5751 | 0,8324 |

### 5.3 Baseline

O notebook registra ROC-AUC médio de 0,8456 para a Regressão Logística, com desvio padrão de 0,0139. Essa métrica foi produzida em uma execução anterior do notebook, enquanto a tabela final em `models/comparison_results.csv` contém apenas os modelos otimizados MLP e Random Forest. Como as três alternativas não estão registradas no mesmo relatório final, a comparação com o baseline deve ser interpretada como indicativa.

Para uma conclusão experimental mais forte, recomenda-se executar Regressão Logística, Random Forest e MLP no mesmo conjunto limpo, nos mesmos folds e com o mesmo protocolo de avaliação.

## 6. Escolha do modelo

O código atual seleciona automaticamente o modelo com maior ROC-AUC médio de validação cruzada. Por essa regra, a **MLP** é copiada para `models/model.joblib` e utilizada pela API.

A vantagem observada da MLP sobre a Random Forest é de aproximadamente 0,0004 em ROC-AUC médio, muito menor que o desvio padrão de ambos os modelos. Portanto, os resultados não demonstram uma superioridade prática clara da MLP.

Há também um trade-off de negócio importante:

- MLP: maior accuracy e precision no threshold 0,5, gerando menos abordagens indevidas;
- Random Forest: maior recall e F1 para churn, deixando de identificar menos clientes que cancelam.

Se o custo de um falso negativo for alto, a recomendação é testar a Random Forest como modelo operacional ou ajustar o threshold da MLP usando uma função de custo de negócio. A escolha deve ser revalidada antes de produção.

## 7. Limitações

- **Generalização:** uma base pública de uma única empresa pode não representar outras operadoras ou períodos.
- **Temporalidade:** não há coluna temporal adequada para validação fora do tempo ou monitoramento histórico de drift.
- **Desbalanceamento:** apenas 26,54% dos registros pertencem à classe positiva.
- **Comparação experimental:** o baseline não aparece no relatório final gerado pelo pipeline modular.
- **Threshold:** o corte de 0,5 é fixo e não foi otimizado por custo, capacidade da campanha ou calibração.
- **Probabilidade:** não há avaliação de calibração; o valor retornado não deve ser interpretado como probabilidade perfeitamente calibrada.
- **Explicabilidade:** o projeto ainda não fornece explicações por predição nem análise de importância estável das variáveis.
- **Ausência de dados:** o processo remove registros inválidos de `TotalCharges`, o que pode introduzir viés se a ausência não for aleatória.

## 8. Possíveis vieses e riscos

O dataset inclui `gender`, `SeniorCitizen`, `Partner` e `Dependents`. Mesmo quando úteis para previsão, esses atributos podem gerar diferenças de desempenho ou tratamento entre grupos. Além disso, variáveis de contrato, método de pagamento e serviços podem funcionar como proxies de condição socioeconômica.

Antes de uso real, devem ser comparados, por subgrupo:

- taxa de positivos prevista;
- recall e taxa de falsos negativos;
- precision e taxa de falsos positivos;
- calibração das probabilidades;
- impacto das ações de retenção resultantes.

Não há, no pipeline atual, evidência suficiente para afirmar equidade entre grupos.

## 9. Recomendações de monitoramento

Em produção, monitorar:

- qualidade, schema, faixas e categorias das entradas;
- taxa prevista e taxa real de churn;
- ROC-AUC, precision, recall, F1 e calibração após chegada dos rótulos;
- métricas separadas por subgrupos relevantes;
- drift das variáveis e das probabilidades previstas;
- latência, erros HTTP e indisponibilidade do modelo;
- volume e resultado das campanhas de retenção.

Definir alertas e uma frequência de retreinamento somente após observar a velocidade real de mudança dos dados e o tempo de chegada do churn confirmado.

## 10. Segurança e privacidade

- não registrar payloads com dados pessoais sem necessidade e base legal;
- aplicar minimização de dados, controle de acesso, criptografia e política de retenção;
- substituir usuários e senhas de demonstração por um provedor de identidade;
- substituir a chave JWT padrão por segredo forte e gerenciado fora do código;
- revisar permissões e trilhas de auditoria antes de disponibilizar a API.

## 11. Reprodução

```bash
python scripts/setup.py
python -m src.train_model.train
python -m pytest -q
python -m uvicorn src.api.main:app --reload
```

Os artefatos de dados e modelos não são versionados. A reprodução exige acesso ao dataset e execução do treinamento no ambiente de destino.

## 12. Próximos passos

1. incluir a Regressão Logística no relatório modular final;
2. definir custos de falso positivo e falso negativo com a área de negócio;
3. selecionar e validar o threshold com dados de validação separados;
4. avaliar calibração e métricas por subgrupo;
5. adicionar versionamento de dados, modelo e métricas;
6. validar o modelo com dados recentes da operadora antes de produção.
