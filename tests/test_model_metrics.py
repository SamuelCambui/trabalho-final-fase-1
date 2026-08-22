
"""Testes das métricas mínimas esperadas para o modelo."""

import numpy as np

from sklearn.metrics import classification_report

from src.train_model.config import BEST_MODEL_PATH
from src.train_model.model import load_model


# ============================================================
# THRESHOLDS MÍNIMOS
# ============================================================

MIN_PRECISION_CLASS_0 = 0.70
MIN_RECALL_CLASS_0 = 0.70
MIN_F1_CLASS_0 = 0.70

MIN_PRECISION_CLASS_1 = 0.55
MIN_RECALL_CLASS_1 = 0.45
MIN_F1_CLASS_1 = 0.45

MIN_ACCURACY = 0.65

MIN_MACRO_PRECISION = 0.65
MIN_MACRO_RECALL = 0.60
MIN_MACRO_F1 = 0.60

MIN_WEIGHTED_PRECISION = 0.60
MIN_WEIGHTED_RECALL = 0.60
MIN_WEIGHTED_F1 = 0.60


def test_model_metrics(
    X_test,
    y_test,
):
    """Valida se o modelo atende às métricas mínimas."""

    model = load_model(BEST_MODEL_PATH)

    predictions = model.predict(X_test)

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "precision_class_0":
            report["0"]["precision"],

        "recall_class_0":
            report["0"]["recall"],

        "f1_class_0":
            report["0"]["f1-score"],

        "precision_class_1":
            report["1"]["precision"],

        "recall_class_1":
            report["1"]["recall"],

        "f1_class_1":
            report["1"]["f1-score"],

        "accuracy":
            report["accuracy"],

        "macro_precision":
            report["macro avg"]["precision"],

        "macro_recall":
            report["macro avg"]["recall"],

        "macro_f1":
            report["macro avg"]["f1-score"],

        "weighted_precision":
            report["weighted avg"]["precision"],

        "weighted_recall":
            report["weighted avg"]["recall"],

        "weighted_f1":
            report["weighted avg"]["f1-score"],
    }

    minimums = {
        "precision_class_0":
            MIN_PRECISION_CLASS_0,

        "recall_class_0":
            MIN_RECALL_CLASS_0,

        "f1_class_0":
            MIN_F1_CLASS_0,

        "precision_class_1":
            MIN_PRECISION_CLASS_1,

        "recall_class_1":
            MIN_RECALL_CLASS_1,

        "f1_class_1":
            MIN_F1_CLASS_1,

        "accuracy":
            MIN_ACCURACY,

        "macro_precision":
            MIN_MACRO_PRECISION,

        "macro_recall":
            MIN_MACRO_RECALL,

        "macro_f1":
            MIN_MACRO_F1,

        "weighted_precision":
            MIN_WEIGHTED_PRECISION,

        "weighted_recall":
            MIN_WEIGHTED_RECALL,

        "weighted_f1":
            MIN_WEIGHTED_F1,
    }

    failures = []

    for metric, minimum in minimums.items():

        actual = metrics[metric]

        print(
            f"{metric}: "
            f"{actual:.4f} "
            f"(mínimo: {minimum:.4f})"
        )

        if actual < minimum:

            failures.append(
                f"{metric}: "
                f"{actual:.4f} < "
                f"{minimum:.4f}"
            )

    if failures:

        message = (
            "\nO modelo não atende aos "
            "limites mínimos:\n\n"
            + "\n".join(failures)
        )

        raise AssertionError(message)
