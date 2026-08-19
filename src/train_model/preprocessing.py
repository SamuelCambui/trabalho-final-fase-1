"""Carregamento, limpeza e preparação dos dados para treinamento."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.train_model.config import ID_COLUMN, RANDOM_STATE, TARGET_COLUMN, TEST_SIZE


def load_data(caminho: Path) -> pd.DataFrame:
    """
    Carrega o dataset Telco Customer Churn a partir de um arquivo CSV.

    Args:
        caminho: Caminho absoluto ou relativo do arquivo CSV.

    Returns:
        DataFrame com os dados brutos.
    """
    return pd.read_csv(caminho)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza mínima alinhada ao notebook de EDA.

    Converte ``TotalCharges`` para numérico, remove ``customerID`` e
    descarta linhas inválidas geradas na conversão.

    Args:
        df: DataFrame bruto.

    Returns:
        DataFrame limpo e pronto para separação de features e target.
    """
    dados = df.copy()
    dados["TotalCharges"] = pd.to_numeric(dados["TotalCharges"], errors="coerce")

    if ID_COLUMN in dados.columns:
        dados = dados.drop(columns=[ID_COLUMN])

    dados = dados.dropna().reset_index(drop=True)
    return dados


def prepare_features_target(
    df: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separa features e variável alvo, codificando churn como 0/1.

    Args:
        df: DataFrame já limpo.
        target_col: Nome da coluna alvo.

    Returns:
        Tupla ``(X, y)`` com features e target numérico.
    """
    if target_col not in df.columns:
        raise ValueError(f"Coluna alvo '{target_col}' não encontrada no dataset.")

    x = df.drop(columns=[target_col])
    y = df[target_col].map({"No": 0, "Yes": 1})

    if y.isna().any():
        valores_invalidos = df.loc[y.isna(), target_col].unique()
        raise ValueError(
            "Valores inválidos em Churn. Esperado 'Yes' ou 'No'. "
            f"Encontrado: {valores_invalidos}"
        )

    return x, y.astype(int)


def split_data(
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Divide os dados em treino e teste com estratificação.

    Args:
        x: Features.
        y: Target codificado.
        test_size: Proporção reservada ao conjunto de teste.
        random_state: Semente para reprodutibilidade.

    Returns:
        Tupla ``(X_train, X_test, y_train, y_test)``.
    """
    return train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def get_feature_groups(x: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Identifica colunas numéricas e categóricas do dataset.

    Args:
        x: DataFrame de features.

    Returns:
        Tupla ``(numeric_features, categorical_features)``.
    """
    numeric_features = x.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = x.select_dtypes(include=["object"]).columns.tolist()
    return numeric_features, categorical_features


def build_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    """
    Constrói o pré-processador com imputação, escala e one-hot encoding.

    O pré-processador deve ser usado dentro de um ``Pipeline`` do scikit-learn
    para evitar vazamento de informação entre treino e validação.

    Args:
        x: DataFrame de treino usado apenas para inferir tipos de coluna.

    Returns:
        ``ColumnTransformer`` configurado para o dataset Telco.
    """
    numeric_features, categorical_features = get_feature_groups(x)

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )
