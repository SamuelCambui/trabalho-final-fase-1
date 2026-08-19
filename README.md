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

### 6. Para realizar o treinamento do modelo em MLP e RandomForest

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
