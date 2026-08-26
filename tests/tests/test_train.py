"""Testes unitários do script principal de treinamento."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from src.train_model import train


def test_parse_args_padrao(monkeypatch):
    """Deve utilizar os valores padrão quando nenhum argumento for informado."""

    monkeypatch.setattr(
        "sys.argv",
        ["train.py"],
    )

    args = train.parse_args()

    assert args.dataset is None
    assert args.sem_otimizacao is False


def test_parse_args_com_dataset(monkeypatch):
    """Deve interpretar corretamente o caminho do dataset."""

    caminho_dataset = "data/raw/customer_churn.csv"

    monkeypatch.setattr(
        "sys.argv",
        [
            "train.py",
            "--dataset",
            caminho_dataset,
        ],
    )

    args = train.parse_args()

    assert args.dataset == Path(caminho_dataset)
    assert args.sem_otimizacao is False


def test_parse_args_sem_otimizacao(monkeypatch):
    """Deve ativar a flag para desativar a otimização."""

    monkeypatch.setattr(
        "sys.argv",
        [
            "train.py",
            "--sem-otimizacao",
        ],
    )

    args = train.parse_args()

    assert args.sem_otimizacao is True


@patch("src.train_model.train.evaluate_on_test")
@patch("src.train_model.train.save_model")
@patch("src.train_model.train.compare_models")
@patch("src.train_model.train.train_mlp")
@patch("src.train_model.train.train_rf")
@patch("src.train_model.train.split_data")
@patch("src.train_model.train.prepare_features_target")
@patch("src.train_model.train.load_data")
@patch("src.train_model.train.clean_data")
@patch("src.train_model.train.find_dataset_csv")
@patch("src.train_model.train.parse_args")
def test_main_fluxo_completo(
    mock_parse_args,
    mock_find_dataset,
    mock_clean_data,
    mock_load_data,
    mock_prepare_features,
    mock_split_data,
    mock_train_rf,
    mock_train_mlp,
    mock_compare_models,
    mock_save_model,
    mock_evaluate_on_test,
):
    """Deve executar corretamente todo o fluxo de treinamento."""

    dataset_path = Path("data/raw/customer_churn.csv")

    mock_parse_args.return_value = MagicMock(
        dataset=None,
        sem_otimizacao=False,
    )

    mock_find_dataset.return_value = dataset_path

    dataframe = pd.DataFrame(
        {
            "feature": [1, 2, 3, 4],
            "Churn": [0, 1, 0, 1],
        }
    )

    mock_clean_data.return_value = dataframe
    mock_load_data.return_value = dataframe

    x = pd.DataFrame(
        {
            "feature": [1, 2, 3, 4],
        }
    )

    y = pd.Series(
        [0, 1, 0, 1],
        name="Churn",
    )

    mock_prepare_features.return_value = (
        x,
        y,
    )

    x_train = x.iloc[:2]
    x_test = x.iloc[2:]

    y_train = y.iloc[:2]
    y_test = y.iloc[2:]

    mock_split_data.return_value = (
        x_train,
        x_test,
        y_train,
        y_test,
    )

    rf_model = MagicMock(name="RandomForestModel")
    mlp_model = MagicMock(name="MLPModel")

    mock_train_rf.return_value = rf_model
    mock_train_mlp.return_value = mlp_model

    resultados_cv = pd.DataFrame(
        {
            "Modelo": [
                "Random Forest",
                "MLP",
            ],
            "F1": [
                0.80,
                0.70,
            ],
        }
    )

    mock_compare_models.return_value = resultados_cv

    caminho_salvo = Path(
        "models/best_model.joblib"
    )

    mock_save_model.return_value = caminho_salvo

    train.main()

    mock_parse_args.assert_called_once()

    mock_find_dataset.assert_called_once_with(
        train.DATA_DIR
    )

    mock_load_data.assert_called_once_with(
        dataset_path
    )

    mock_clean_data.assert_called_once()

    mock_prepare_features.assert_called_once_with(
        dataframe
    )

    mock_split_data.assert_called_once_with(
        x,
        y,
    )

    mock_train_rf.assert_called_once_with(
        x_train,
        y_train,
        otimizar=True,
    )

    mock_train_mlp.assert_called_once_with(
        x_train,
        y_train,
        otimizar=True,
    )

    mock_compare_models.assert_called_once_with(
        {
            "Random Forest": rf_model,
            "MLP": mlp_model,
        },
        x_train,
        y_train,
    )

    mock_save_model.assert_called_once_with(
        rf_model,
        train.BEST_MODEL_PATH,
    )

    assert mock_evaluate_on_test.call_count == 2


@patch("src.train_model.train.evaluate_on_test")
@patch("src.train_model.train.save_model")
@patch("src.train_model.train.compare_models")
@patch("src.train_model.train.train_mlp")
@patch("src.train_model.train.train_rf")
@patch("src.train_model.train.split_data")
@patch("src.train_model.train.prepare_features_target")
@patch("src.train_model.train.load_data")
@patch("src.train_model.train.clean_data")
@patch("src.train_model.train.find_dataset_csv")
@patch("src.train_model.train.parse_args")
def test_main_sem_otimizacao(
    mock_parse_args,
    mock_find_dataset,
    mock_clean_data,
    mock_load_data,
    mock_prepare_features,
    mock_split_data,
    mock_train_rf,
    mock_train_mlp,
    mock_compare_models,
    mock_save_model,
    mock_evaluate_on_test,
):
    """Deve treinar os modelos sem otimização quando solicitado."""

    dataset_path = Path(
        "data/raw/customer_churn.csv"
    )

    mock_parse_args.return_value = MagicMock(
        dataset=None,
        sem_otimizacao=True,
    )

    mock_find_dataset.return_value = dataset_path

    dataframe = pd.DataFrame(
        {
            "feature": [1, 2],
            "Churn": [0, 1],
        }
    )

    mock_clean_data.return_value = dataframe
    mock_load_data.return_value = dataframe

    x = pd.DataFrame(
        {
            "feature": [1, 2],
        }
    )

    y = pd.Series(
        [0, 1],
        name="Churn",
    )

    mock_prepare_features.return_value = (
        x,
        y,
    )

    mock_split_data.return_value = (
        x,
        x,
        y,
        y,
    )

    rf_model = MagicMock()
    mlp_model = MagicMock()

    mock_train_rf.return_value = rf_model
    mock_train_mlp.return_value = mlp_model

    mock_compare_models.return_value = pd.DataFrame(
        {
            "Modelo": ["MLP"],
        }
    )

    train.main()

    mock_train_rf.assert_called_once_with(
        x,
        y,
        otimizar=False,
    )

    mock_train_mlp.assert_called_once_with(
        x,
        y,
        otimizar=False,
    )

    mock_save_model.assert_called_once_with(
        mlp_model,
        train.BEST_MODEL_PATH,
    )


@patch("src.train_model.train.evaluate_on_test")
@patch("src.train_model.train.save_model")
@patch("src.train_model.train.compare_models")
@patch("src.train_model.train.train_mlp")
@patch("src.train_model.train.train_rf")
@patch("src.train_model.train.split_data")
@patch("src.train_model.train.prepare_features_target")
@patch("src.train_model.train.load_data")
@patch("src.train_model.train.clean_data")
@patch("src.train_model.train.find_dataset_csv")
@patch("src.train_model.train.parse_args")
def test_main_utiliza_dataset_informado(
    mock_parse_args,
    mock_find_dataset,
    mock_clean_data,
    mock_load_data,
    mock_prepare_features,
    mock_split_data,
    mock_train_rf,
    mock_train_mlp,
    mock_compare_models,
    mock_save_model,
    mock_evaluate_on_test,
):
    """Deve utilizar o dataset informado e não buscar automaticamente."""

    dataset_informado = Path(
        "meu_dataset.csv"
    )

    mock_parse_args.return_value = MagicMock(
        dataset=dataset_informado,
        sem_otimizacao=False,
    )

    dataframe = pd.DataFrame(
        {
            "feature": [1, 2],
            "Churn": [0, 1],
        }
    )

    mock_clean_data.return_value = dataframe
    mock_load_data.return_value = dataframe

    x = pd.DataFrame({"feature": [1, 2]})

    y = pd.Series(
        [0, 1],
        name="Churn",
    )

    mock_prepare_features.return_value = (
        x,
        y,
    )

    mock_split_data.return_value = (
        x,
        x,
        y,
        y,
    )

    rf_model = MagicMock()
    mlp_model = MagicMock()

    mock_train_rf.return_value = rf_model
    mock_train_mlp.return_value = mlp_model

    mock_compare_models.return_value = pd.DataFrame(
        {
            "Modelo": ["Random Forest"],
        }
    )

    train.main()

    mock_find_dataset.assert_not_called()

    mock_load_data.assert_called_once_with(
        dataset_informado
    )