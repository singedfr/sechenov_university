import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from preprocess import load_and_prepare
from sklearn.calibration import CalibratedClassifierCV


X, y, feature_names, medians = load_and_prepare("deficiency_anemia.csv")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

base_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_leaf=3,
    random_state=42,
    class_weight="balanced"
)

calibrated_model = CalibratedClassifierCV(
    estimator=base_model, 
    method='sigmoid', 
    cv=5
)

calibrated_model.fit(X_train, y_train)

y_pred_proba = calibrated_model.predict_proba(X_test)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy на тесте:", accuracy_score(y_test, y_pred))
print()
print("Classification report:")
print(classification_report(y_test, y_pred, zero_division=0))

joblib.dump(model, "random_forest/model.pkl")
joblib.dump(feature_names, "random_forest/feature_names.pkl")
joblib.dump(medians, "random_forest/medians.pkl")

print()
print("Сохранено:")
print("  model.pkl         — обученная модель")
print("  feature_names.pkl — список признаков")
print("  medians.pkl       — медианы для заполнения пропусков")