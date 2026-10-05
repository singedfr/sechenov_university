from schemas import PatientData


DIAGNOSES = {
    "iron_deficiency_anemia": {
        "must_have": ["hemoglobin", "ferritin"],
        "helpful": ["CRP", "sTfR", "TSAT", "MCV"],
        "treatment": "Терапия препаратами железа per os (например, сульфат железа 100–200 мг элементарного Fe/сут).",
        "cause_search": [
            "ФГДС — исключить кровотечение из ЖКТ",
            "Колоноскопия — при возрасте 45+ или семейном анамнезе",
            "Гинекологический осмотр — у женщин (меноррагии)",
        ],
        "patient_text": "У вас железодефицитная анемия. Врач назначит препараты железа и обследование, чтобы найти причину дефицита.",
    },
    "B12_deficiency_anemia": {
        "must_have": ["hemoglobin", "vitamin_B12"],
        "helpful": ["active_B12", "MMA", "homocysteine", "MCV"],
        "treatment": "Заместительная терапия витамином B12 (цианокобаламин или гидроксокобаламин) в/м по схеме.",
        "cause_search": [
            "Исключить атрофический гастрит (антитела к париетальным клеткам, гастрин)",
            "Исключить целиакию (антитела к тканевой трансглутаминазе)",
            "Исключить паразитоз (Diphyllobothrium latum)",
        ],
        "patient_text": "У вас дефицит витамина B12. Врач назначит уколы B12.",
    },
    "folate_deficiency_anemia": {
        "must_have": ["hemoglobin", "folate"],
        "helpful": ["vitamin_B12", "homocysteine"],
        "treatment": "Фолиевая кислота 1–5 мг/сут per os.",
        "cause_search": [
            "Оценить диету, алкоголь, приём метотрексата/триметоприма",
            "Исключить мальабсорбцию (целиакия, ХВЗК)",
        ],
        "patient_text": "У вас дефицит фолиевой кислоты. Лечится таблетками.",
    },
    "B6_deficiency": {
        "must_have": ["vitamin_B6"],
        "helpful": ["homocysteine"],
        "treatment": "Пиридоксин (витамин B6) per os 50–100 мг/сут под контролем врача.",
        "cause_search": [
            "Оценить приём изониазида, пеницилламина, леводопы, гидралазина",
        ],
        "patient_text": "У вас дефицит витамина B6. Врач разберётся в причине и назначит лечение.",
    },
    "copper_deficiency": {
        "must_have": ["copper"],
        "helpful": ["ceruloplasmin"],
        "treatment": "Препараты меди per os (например, сульфат меди) — по назначению врача.",
        "cause_search": [
            "Исключить мальабсорбцию, бариатрические операции",
            "Оценить приём цинка (избыток блокирует усвоение меди)",
        ],
        "patient_text": "У вас дефицит меди — редкое состояние. Врач назначит лечение.",
    },
    "inflammation_anemia": {
        "must_have": ["hemoglobin", "CRP"],
        "helpful": ["ESR", "ferritin", "sTfR", "Ret_He"],
        "treatment": "Лечение основного воспалительного/инфекционного/онкологического заболевания.",
        "cause_search": [
            "Поиск источника воспаления (инфекции, аутоиммунные, опухоли)",
            "Исключить ХБП (креатинин, eGFR)",
        ],
        "patient_text": "У вас анемия, связанная с воспалением. Главное — пролечить основное заболевание.",
    },
    "mixed_deficiency": {
        "must_have": ["hemoglobin"],
        "helpful": ["ferritin", "vitamin_B12", "folate", "CRP", "sTfR", "MCV"],
        "treatment": "Комбинированная заместительная терапия — по назначению гематолога.",
        "cause_search": [
            "Полное обследование для выявления всех компонентов дефицита",
            "Консультация гематолога",
        ],
        "patient_text": "У вас сочетание нескольких дефицитов. Нужна консультация гематолога.",
    },
    "latent_deficiency": {
        "must_have": ["ferritin"],
        "helpful": ["vitamin_B12", "folate", "MCV"],
        "treatment": "Профилактическая коррекция выявленного дефицита — по назначению врача.",
        "cause_search": [
            "Уточнить, какой именно дефицит латентный",
        ],
        "patient_text": "У вас скрытый дефицит без анемии. Важно не пропустить — покажитесь врачу.",
    },
    "B12_deficiency_no_anemia": {
        "must_have": ["vitamin_B12"],
        "helpful": ["active_B12", "MMA", "homocysteine"],
        "treatment": "Заместительная терапия B12 — по назначению врача.",
        "cause_search": [
            "Исключить атрофический гастрит, целиакию, паразитоз",
        ],
        "patient_text": "У вас дефицит B12 без анемии. Важно начать лечение сейчас.",
    },
    "folate_deficiency_no_anemia": {
        "must_have": ["folate"],
        "helpful": ["vitamin_B12", "homocysteine"],
        "treatment": "Фолиевая кислота per os.",
        "cause_search": [
            "Оценить диету, алкоголь, лекарства",
        ],
        "patient_text": "У вас дефицит фолатов без анемии. Врач назначит лечение.",
    },
    "anemia_other": {
        "must_have": ["hemoglobin"],
        "helpful": ["LDH", "haptoglobin", "indirect_bilirubin", "creatinine", "eGFR", "TSH"],
        "treatment": "Тактика определяется после уточнения причины анемии.",
        "cause_search": [
            "Исключить гемолиз (ЛДГ, гаптоглобин, непрямой билирубин, ретикулоциты)",
            "Исключить ХБП (креатинин, eGFR)",
            "Исключить гипотиреоз (ТТЗ)",
            "Консультация гематолога",
        ],
        "patient_text": "У вас анемия неясного происхождения. Нужно дополнительное обследование у гематолога.",
    },
    "no_anemia_no_deficiency": {
        "must_have": [],
        "helpful": [],
        "treatment": "",
        "cause_search": [],
        "patient_text": "У вас всё хорошо — признаков анемии и дефицитов не обнаружено. Повторите контроль через 12 месяцев.",
    },
}


def _is_present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip() in ("", "-", "—", "н/д"):
        return False
    return True


def _check_presence(tests: list, data_dict: dict) -> tuple:
    present, missing = [], []
    for t in tests:
        if _is_present(data_dict.get(t)):
            present.append(t)
        else:
            missing.append(t)
    return present, missing


def _names_human(tests: list) -> str:
    friendly = {
        "hemoglobin": "гемоглобин",
        "ferritin": "ферритин",
        "MCV": "MCV",
        "MCH": "MCH",
        "TSAT": "насыщение трансферрина (TSAT)",
        "sTfR": "растворимый рецептор трансферрина (sTfR)",
        "CRP": "С-реактивный белок (СРБ)",
        "ESR": "СОЭ",
        "vitamin_B12": "витамин B12 (общий)",
        "active_B12": "активный B12 (голотранскобаламин)",
        "MMA": "метилмалоновая кислота",
        "homocysteine": "гомоцистеин",
        "folate": "фолаты",
        "vitamin_B6": "витамин B6",
        "copper": "медь сывороточная",
        "ceruloplasmin": "церулоплазмин",
        "creatinine": "креатинин",
        "eGFR": "расчётная СКФ (eGFR)",
        "TSH": "ТТГ",
        "LDH": "ЛДГ",
        "haptoglobin": "гаптоглобин",
        "indirect_bilirubin": "непрямой билирубин",
        "Ret_He": "Ret-He",
    }
    return ", ".join(friendly.get(t, t) for t in tests)


def generate_doctor_recommendation(class_name: str, data_dict: dict) -> str:
    cfg = DIAGNOSES.get(class_name)
    if not cfg:
        return "Рекомендована консультация гематолога."

    must = cfg["must_have"]
    helpful = cfg["helpful"]

    if class_name == "no_anemia_no_deficiency":
        return cfg["patient_text"].replace("Вас", "Пациента")

    parts = []

    must_present, must_missing = _check_presence(must, data_dict)

    if must_missing:
        parts.append(
            "⚠️ **Диагноз предварительный.** Для подтверждения необходимо сдать: "
            f"**{_names_human(must_missing)}**."
        )
        if must_present:
            parts.append(
                f"Уже сданы: {_names_human(must_present)} — учтено при расчёте."
            )
        return "\n\n".join(parts)

    helpful_present, helpful_missing = _check_presence(helpful, data_dict)

    parts.append(
        f"✅ **Диагноз подтверждён** ключевыми анализами: {_names_human(must_present)}."
    )

    if helpful_missing:
        parts.append(
            f"Для уточнения и исключения сочетанных состояний желательно сдать: "
            f"**{_names_human(helpful_missing)}**. "
            f"Это не блокирует начало терапии, но улучшит картину."
        )
    else:
        parts.append("Все дополнительные анализы сданы — картина полная.")

    if cfg["treatment"]:
        parts.append(f"**Лечение:** {cfg['treatment']}")

    if cfg["cause_search"]:
        cause_str = "\n".join(f"  • {c}" for c in cfg["cause_search"])
        parts.append(f"**Поиск причины (клинические действия):**\n{cause_str}")

    return "\n\n".join(parts)


def generate_patient_recommendation(class_name: str, data_dict: dict) -> str:
    cfg = DIAGNOSES.get(class_name)
    if not cfg:
        return "Пожалуйста, обратитесь к врачу для уточнения диагноза."

    base = cfg["patient_text"]

    must_missing = [
        t for t in cfg["must_have"]
        if not _is_present(data_dict.get(t))
    ]
    if must_missing and class_name != "no_anemia_no_deficiency":
        base += "\n\nПока диагноз предварительный — врач попросит сдать дополнительные анализы."

    return base


def generate_recommendations(class_name: str, anemia_present: bool, data: PatientData):
    data_dict = data.model_dump()
    return (
        generate_doctor_recommendation(class_name, data_dict),
        generate_patient_recommendation(class_name, data_dict),
    )