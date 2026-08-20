import pandas as pd

from src.train_model.preprocessing import clean_data, prepare_features_target


def test_clean_data_converts_total_charges_and_removes_invalid_rows() -> None:
    raw = pd.DataFrame(
        {
            "customerID": ["A", "B"],
            "TotalCharges": ["100.50", " "],
            "Churn": ["No", "Yes"],
        }
    )

    cleaned = clean_data(raw)

    assert "customerID" not in cleaned.columns
    assert len(cleaned) == 1
    assert cleaned.loc[0, "TotalCharges"] == 100.50


def test_prepare_features_target_maps_churn_to_binary() -> None:
    cleaned = pd.DataFrame(
        {
            "tenure": [1, 24],
            "MonthlyCharges": [80.0, 45.0],
            "Churn": ["Yes", "No"],
        }
    )

    features, target = prepare_features_target(cleaned)

    assert "Churn" not in features.columns
    assert target.tolist() == [1, 0]
