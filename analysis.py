import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv('(СУ)deficiency_anemia.csv', encoding='utf-8-sig')

print(f"Размер таблицы: {df.shape}")
print(df.head())

drop_cols = [
    'patient_id', 'anemia', 'iron_deficiency', 'B12_deficiency', 
    'folate_deficiency', 'B6_deficiency', 'copper_deficiency', 
    'inflammation_anemia', 'mixed_deficiency', 'deficiency_cause'
]
X = df.drop(columns=drop_cols + ['anemia_class'])
y = df['anemia_class']

for col in ['vitamin_B12', 'active_B12', 'MMA', 'homocysteine', 'folate', 'ferritin', 'sTfR', 'Ret_He']:
    if col in X.columns:
        X[f'{col}_missing'] = X[col].isnull().astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = CatBoostClassifier(
    iterations=500,
    learning_rate=0.05,
    depth=6,
    loss_function='MultiClass',
    eval_metric='Accuracy',
    random_seed=42,
    verbose=100,
    early_stopping_rounds=50
)

cat_features = ['sex']
model.fit(X_train, y_train, cat_features=cat_features, eval_set=(X_test, y_test))

preds = model.predict(X_test)
print("\n=== РЕЗУЛЬТАТЫ ===")
print(classification_report(y_test, preds))

model.save_model('catboost_anemia.cbm')
print("\nМодель сохранена в catboost_anemia.cbm")