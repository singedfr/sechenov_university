import pandas as pd

df = pd.read_csv("deficiency_anemia.csv")

print("Размер датасета:", df.shape)
print()

print("Первые 5 строк:")
print(df.head())
print()

print("Типы данных:")
print(df.dtypes)
print()

print("Пропуски по столбцам:")
print(df.isnull().sum())
print()

print("Распределение классов anemia_class:")
print(df["anemia_class"].value_counts())