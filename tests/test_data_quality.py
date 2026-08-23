"""Testes de qualidade do dataset."""

from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")


def test_dataset_exists():
    """Verifica se o dataset existe."""
    assert DATA_PATH.exists(), (
        f"Dataset não encontrado: {DATA_PATH}"
    )


def test_dataset_not_empty():
    """Verifica se o dataset não está vazio."""
    df = pd.read_csv(DATA_PATH)

    assert not df.empty


def test_expected_columns():
    """Verifica se as colunas esperadas existem."""
    df = pd.read_csv(DATA_PATH)

    expected_columns = {
        "customerID",
        "gender",
        "SeniorCitizen",
        "Partner",
        "Dependents",
        "tenure",
        "PhoneService",
        "MonthlyCharges",
        "TotalCharges",
        "Churn",
    }

    assert expected_columns.issubset(df.columns)


def test_target_exists():
    """Verifica se a variável alvo existe."""
    df = pd.read_csv(DATA_PATH)

    assert "Churn" in df.columns


def test_target_values():
    """Verifica os valores esperados da variável alvo."""
    df = pd.read_csv(DATA_PATH)

    assert set(df["Churn"].dropna().unique()).issubset(
        {"Yes", "No"}
    )


def test_no_excessive_missing_values():
    """Verifica valores ausentes excessivos."""
    df = pd.read_csv(DATA_PATH)

    missing_ratio = df.isnull().mean()

    assert missing_ratio.max() < 0.30