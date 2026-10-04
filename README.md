# sechenov_university
# Anemia Screening Service

Backend-сервис на FastAPI для автоматизированной интерпретации лабораторных анализов пациентов. Определяет наличие анемии, проводит мультиклассовую дифференциальную диагностику дефицитных состояний и формирует рекомендации для врача и пациента.

Разработан в рамках кейса от Сеченовского Университета.

---

## Содержание

- [Что делает сервис](#что-делает-сервис)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Установка и запуск](#установка-и-запуск)
- [API](#api)
- [ML-модель](#ml-модель)
- [Признаки на входе](#признаки-на-входе)
- [Ограничения и допущения](#ограничения-и-допущения)

---

## Что делает сервис

1. Принимает JSON с лабораторными анализами пациента.
2. Определяет наличие анемии по критериям ВОЗ (Hb < 120 г/л у женщин, < 130 г/л у мужчин).
3. Проводит мультиклассовую классификацию по 12 категориям дефицитных состояний.
4. Возвращает структурированный ответ: диагноз, вероятности, топ-3 класса, топ-3 влияющих признака.
5. Формирует **две версии рекомендаций** — для врача (медицинским языком) и для пациента (простым языком).
6. Честно сообщает, каких анализов не хватает для уверенного диагноза.

---

## Стек технологий

| Слой | Технология |
|---|---|
| Язык | Python 3.14 |
| Web-фреймворк | FastAPI |
| ASGI-сервер | Uvicorn |
| Валидация данных | Pydantic v2 |
| ML | scikit-learn (RandomForestClassifier) |
| Сериализация моделей | joblib |
| Контроль версий | Git / GitHub |

---

## Структура проекта

```
anemia_service/
├── main.py                    # Точка входа, эндпоинты FastAPI
├── schemas.py                 # Pydantic-схемы входа и выхода
├── recommendations.py         # Тексты рекомендаций для врача/пациента
├── ml_loader.py               # Загрузка и вызов ML-модели
├── requirements.txt           # Зафиксированные версии зависимостей
├── ml/
│   ├── explore.py             # EDA датасета
│   ├── preprocess.py          # Препроцессинг данных
│   ├── train.py               # Обучение модели
│   ├── test_model.py          # Стресс-тесты модели
│   ├── deficiency_anemia.csv  # Обучающий датасет (840 пациентов, 48 колонок)
│   └── random_forest/
│       ├── model.pkl          # Обученная модель
│       ├── feature_names.pkl  # Порядок признаков
│       └── medians.pkl        # Медианы для заполнения пропусков
└── README.md
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/singedfr/sechenov_university.git
cd sechenov_university
```

### 2. Создать виртуальное окружение

**Windows (PowerShell):**
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустить сервер

```bash
uvicorn main:app --reload
```

Открыть в браузере: **http://127.0.0.1:8000/docs** — интерактивная документация Swagger UI.

---

## API

### `GET /` — проверка работоспособности

Возвращает:
```json
{"status": "ok", "message": "Anemia service is running", "model_loaded": true}
```

### `GET /health` — расширенная проверка

Возвращает состояние ML-модели, количество признаков и ошибки загрузки.

### `POST /predict` — основной эндпоинт

**Пример запроса:**

```json
{
  "patient_id": "P001",
  "age_years": 45,
  "sex": "female",
  "hemoglobin": 100,
  "MCV": 70,
  "MCH": 22,
  "RDW": 17,
  "ferritin": 8
}
```

**Пример ответа:**

```json
{
  "patient_id": "P001",
  "anemia_present": true,
  "anemia_confidence": 0.61,
  "class_prediction": "iron_deficiency_anemia",
  "class_probability": 0.61,
  "top_3_classes": [
    {"name": "iron_deficiency_anemia", "probability": 0.61},
    {"name": "mixed_deficiency", "probability": 0.18},
    {"name": "anemia_other", "probability": 0.10}
  ],
  "top_3_features": [
    {"feature": "hemoglobin", "value": 100.0, "impact": 0.08},
    {"feature": "MCV", "value": 70.0, "impact": 0.06},
    {"feature": "ferritin", "value": 8.0, "impact": 0.05}
  ],
  "missing_features": ["vitamin_b12", "folate", "homocysteine"],
  "data_completeness": 0.83,
  "recommendation_for_doctor": "Железодефицитная анемия. Подтвердить ферритином, TSAT. Исключить кровопотерю...",
  "recommendation_for_patient": "У вас железодефицитная анемия. Врач назначит препараты железа..."
}
```

---

## ML-модель

### Что за модель

**RandomForestClassifier** из библиотеки `scikit-learn`.

- **Алгоритм:** ансамбль решающих деревьев (200 деревьев).
- **Параметры:** `max_depth=15`, `min_samples_leaf=3`, `class_weight="balanced"`.
- **Задача:** мультиклассовая классификация по 12 категориям.
- **Датасет:** `deficiency_anemia.csv` — 840 пациентов, 48 признаков.
- **Train/Test split:** 80% / 20%, стратифицированный по классам.

**Почему RandomForest:**
- Хорошо работает на табличных данных.
- Устойчив к выбросам.
- Возвращает вероятности классов.
- Даёт `feature_importances_` для объяснения предсказаний.
- Не требует масштабирования признаков.

### Метрики

| Метрика | Значение |
|---|---|
| Accuracy (test) | `<ВСТАВЬ СВОЁ ЗНАЧЕНИЕ, например 0.86>` |
| Weighted F1-score | `<ВСТАВЬ СВОЁ ЗНАЧЕНИЕ>` |
| Macro F1-score | `<ВСТАВЬ СВОЁ ЗНАЧЕНИЕ>` |

**Как получить значения:** открой в `ml/` вывод `python train.py` — там `classification_report` показывает точность по каждому классу. Верхние строки — `accuracy` и `macro avg` / `weighted avg`.

**Классы (12):**
`no_anemia_no_deficiency`, `latent_deficiency`, `iron_deficiency_anemia`, `B12_deficiency_anemia`, `B12_deficiency_no_anemia`, `folate_deficiency_anemia`, `folate_deficiency_no_anemia`, `B6_deficiency`, `copper_deficiency`, `inflammation_anemia`, `mixed_deficiency`, `anemia_other`.

### Как использовать модель

**Загрузка и предсказание в Python:**

```python
import joblib
import pandas as pd

# 1. Загружаем артефакты
model = joblib.load("ml/random_forest/model.pkl")
feature_names = joblib.load("ml/random_forest/feature_names.pkl")
medians = joblib.load("ml/random_forest/medians.pkl")

# 2. Готовим данные пациента (словарь)
patient = {
    "age_years": 45, "sex": 1, "hemoglobin": 100,
    "MCV": 70, "MCH": 22, "ferritin": 8,
}

# 3. Собираем вектор признаков в порядке feature_names
row = [
    patient.get(f) if patient.get(f) is not None else medians.get(f, 0)
    for f in feature_names
]

# 4. Предсказание
X = pd.DataFrame([row], columns=feature_names)
probs = model.predict_proba(X)[0]
classes = model.classes_

# 5. Топ-3 класса
import numpy as np
top_idx = np.argsort(probs)[::-1][:3]
for i in top_idx:
    print(f"{classes[i]}: {probs[i]:.3f}")
```

**Через HTTP-запрос (для фронтенда):**

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"P001","sex":"female","hemoglobin":100,"MCV":70,"ferritin":8}'
```

---

## Признаки на входе

Модель принимает **37 признаков** (все поля, кроме `patient_id` и целевых). Они объединены в 8 групп.

### 1. Демография
| Признак | Описание | Единица |
|---|---|---|
| `age_years` | Возраст | годы |
| `sex` | Пол (`male` → 0, `female` → 1) | — |

### 2. Общий анализ крови
| Признак | Описание |
|---|---|
| `hemoglobin` | Гемоглобин, г/л |
| `MCV` | Средний объём эритроцита, фл |
| `MCH` | Среднее содержание Hb в эритроците, пг |
| `MCHC` | Средняя концентрация Hb, г/л |
| `RDW` | Ширина распределения эритроцитов, % |
| `hematocrit` | Гематокрит, % |
| `rbc` | Эритроциты |
| `platelets` | Тромбоциты |
| `wbc` | Лейкоциты |
| `reticulocytes` | Ретикулоциты |

### 3. Метаболизм железа
| Признак | Описание |
|---|---|
| `ferritin` | Ферритин, нг/мл |
| `serum_iron` | Сывороточное железо |
| `transferrin` | Трансферрин |
| `TIBC` | Общая железосвязывающая способность |
| `UIBC` | Латентная железосвязывающая способность |
| `TSAT` | Насыщение трансферрина, % |
| `sTfR` | Растворимый рецептор трансферрина |
| `Ret-He` | Содержание Hb в ретикулоцитах |

### 4. Витамины и метаболиты
| Признак | Описание |
|---|---|
| `vitamin_b12` | Общий витамин B12 |
| `HolotC` | Активный B12 (голотранскобаламин) |
| `MMA` | Метилмалоновая кислота |
| `homocysteine` | Гомоцистеин |
| `folate` | Фолиевая кислота |
| `vitamin_b6` | Пиридоксаль-5-фосфат (PLP) |

### 5. Микроэлементы
| Признак | Описание |
|---|---|
| `copper` | Сывороточная медь |
| `ceruloplasmin` | Церулоплазмин |

### 6. Воспаление и соматика
| Признак | Описание |
|---|---|
| `crp` | С-реактивный белок |
| `esr` | СОЭ |
| `creatinine` | Креатинин |
| `gfr` | рСКФ |
| `tsh` | ТТГ |
| `albumin` | Сывороточный альбумин |

### 7. Гемолиз
| Признак | Описание |
|---|---|
| `ldh` | ЛДГ |
| `indirect_bilirubin` | Непрямой билирубин |
| `haptoglobin` | Гаптоглобин |

**Все признаки необязательные.** Если поле не передано — оно учитывается в `missing_features`, а в модель уходит медиана (не влияет на ответ так сильно, как реальное значение).

**Имена чувствительны к регистру:** `MCV`, `MCH`, `MCHC`, `RDW`, `TSAT`, `TIBC`, `UIBC`, `sTfR`, `Ret-He`, `HolotC`, `MMA` — как в датасете.

---

## ⚠️ Важно: версии библиотек

**Файлы `.pkl` созданы определённой версией `scikit-learn`.** Если загрузить модель в окружении с другой версией — возможны ошибки несовместимости (`InconsistentVersionWarning`, `AttributeError`).

**Текущая версия при обучении:** `scikit-learn==1.9.1` *(проверь у себя — команда `pip show scikit-learn`)*.

**Что делать:**

1. **В `requirements.txt`** зафиксировать точные версии:
   ```
   fastapi==0.142.2
   uvicorn==0.54.0
   pydantic==2.13.5
   scikit-learn==1.9.1
   pandas==3.0.6
   numpy==2.5.3
   joblib==1.6.0
   ```

2. **При обновлении `scikit-learn`** — переобучить модель: `python ml/train.py`. Старый `model.pkl` при этом перезапишется.

3. **Проверка версии перед запуском:**
   ```bash
   python -c "import sklearn; print(sklearn.__version__)"
   ```

Если версия отличается от той, что в датасете обучения — переобучи модель. Это дешевле, чем ловить несовместимости в продакшене.

---

## Ограничения и допущения

- **Датасет частично синтетический** (840 пациентов) — реальная точность может отличаться.
- **Не является медицинским заключением.** Сервис — инструмент поддержки принятия решений для врача, а не замена врачу.
- **12 классов — высокая гранулярность.** Вероятности предсказаний редко превышают 0.6–0.7 из-за большого числа классов и малого объёма данных.
- **SHAP-объяснения пока не подключены.** Поле `top_3_features` использует глобальные `feature_importances_`, которые одинаковы для всех пациентов.
- **Модель не откалибрована** по вероятностям (нет `CalibratedClassifierCV`).

---

## Лицензия и авторы

Проект разработан в рамках хакатона. Авторы: команда: "Нейронные связи" в лице четырёх участников.