import joblib
import numpy as np
import pandas as pd
from pathlib import Path


MODEL_DIR = Path(__file__).parent / "ml" / "random_forest"


class ModelLoader:
    """Загружает модель и вспомогательные файлы один раз при старте."""

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.medians = None
        self.loaded = False
        self.load_error = None

    def load(self):
        try:
            self.model = joblib.load(MODEL_DIR / "model.pkl")
            self.feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")
            self.medians = joblib.load(MODEL_DIR / "medians.pkl")
            self.loaded = True
            print(f"[ML] Модель загружена. Признаков: {len(self.feature_names)}")
        except Exception as e:
            self.loaded = False
            self.load_error = str(e)
            print(f"[ML] Ошибка загрузки модели: {e}")

    def predict(self, data_dict: dict) -> dict:
    """Предсказание с учётом пропусков и без нормализации регистра."""
    if not self.loaded:
        return {
            "ok": False,
            "error": f"Модель не загружена: {self.load_error}",
        }

    try:
        row = []
        missing = []

        for f in self.feature_names:
            val = data_dict.get(f, None)

            is_missing = False
            if val is None:
                is_missing = True
            else:
                try:
                    val = float(val)
                    if not np.isfinite(val):
                        is_missing = True
                except (TypeError, ValueError):
                    is_missing = True

            if is_missing:
                missing.append(f)
                val = self.medians.get(f, 0)

            row.append(val)

        total = len(self.feature_names)
        present = total - len(missing)
        completeness = present / total if total > 0 else 0.0

        X = pd.DataFrame([row], columns=self.feature_names)

        probs = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        top_idx = np.argsort(probs)[::-1][:3]

        top_3_classes = [
            {"name": str(classes[i]), "probability": float(probs[i])}
            for i in top_idx
        ]

        importances = self.model.feature_importances_
        top_feat_idx = np.argsort(importances)[::-1][:3]
        top_3_features = [
            {
                "feature": self.feature_names[i],
                "value": float(row[i]),
                "impact": float(importances[i]),
            }
            for i in top_feat_idx
        ]

        return {
            "ok": True,
            "class_prediction": str(classes[top_idx[0]]),
            "class_probability": float(probs[top_idx[0]]),
            "top_3_classes": top_3_classes,
            "top_3_features": top_3_features,
            "missing_features": missing,
            "data_completeness": completeness,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Ошибка предсказания: {str(e)}",
        }

loader = ModelLoader()
loader.load()