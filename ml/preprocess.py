import pandas as pd
import numpy as np


def load_and_prepare(csv_path: str):

    df = pd.read_csv(csv_path)

    drop_cols = [
        "patient_id",
        "anemia", "iron_deficiency", "B12_deficiency", "folate_deficiency",
        "B6_deficiency", "copper_deficiency", "inflammation_anemia",
        "mixed_deficiency", "anemia_class", "deficiency_cause",
    ]
    drop_cols = [c for c in drop_cols if c in df.columns]

    y = df["anemia_class"].copy()

    X = df.drop(columns=drop_cols).copy()

    if "sex" in X.columns:
        X["sex"] = X["sex"].map({"male": 0, "female": 1})


    X = X.apply(pd.to_numeric, errors="coerce")

    feature_names = list(X.columns)

    medians = X.median(numeric_only=True).to_dict()

    X = X.fillna(medians)

    return X, y, feature_names, medians


if __name__ == "__main__":
    X, y, feature_names, medians = load_and_prepare("deficiency_anemia.csv")
    print("Признаки:", X.shape)
    print("Классы:", y.shape)
    print("Список признаков:", feature_names)
    print("Пропуски после обработки:", X.isnull().sum().sum())