import joblib
import pandas as pd
import numpy as np


model = joblib.load("model.pkl")
feature_names = joblib.load("feature_names.pkl")
medians = joblib.load("medians.pkl")


def predict_one(patient_dict: dict):
    """Предсказание для одного пациента."""
    row = []
    for f in feature_names:
        val = patient_dict.get(f, None)
        if val is None or pd.isna(val):
            val = medians.get(f, 0)
        row.append(val)

    X = pd.DataFrame([row], columns=feature_names)

    probs = model.predict_proba(X)[0]
    classes = model.classes_
    top_idx = np.argsort(probs)[::-1][:3]

    print("Предсказание:", classes[top_idx[0]])
    print("Вероятности:")
    for i in top_idx:
        print(f"  {classes[i]}: {probs[i]:.3f}")
    print()


print("Тест 1: ЖДА")
predict_one({
    "age_years": 45, "sex": 1, "hemoglobin": 100, "mcv": 70, "ferritin": 8,
})

print("Тест 2: Все пропуски")
predict_one({})

print("Тест 3: Странные значения")
predict_one({
    "age_years": 999, "hemoglobin": 9999, "ferritin": -50,
})

print("Тест 4: Только гемоглобин")
predict_one({"hemoglobin": 130})