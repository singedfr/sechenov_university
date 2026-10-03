from schemas import PatientData


DOCTOR_TEXTS = {
    "no_anemia_no_deficiency":
        "Анемия и дефицитные состояния не выявлены. Плановый контроль через 12 мес.",
    "iron_deficiency_anemia":
        "Железодефицитная анемия. Подтвердить ферритином, TSAT. Исключить кровопотерю. Начать терапию препаратами железа.",
    "B12_deficiency_anemia":
        "B12-дефицитная анемия. Подтвердить HolotC, MMA, гомоцистеином. Заместительная терапия B12 в/м.",
    "mixed_deficiency":
        "Сочетанный дефицит. Полное дообследование. Консультация гематолога.",
    "inflammation_anemia":
        "Анемия воспаления. Оценить sTfR, Ret-He, СРБ. Лечение основного заболевания.",
}

PATIENT_TEXTS = {
    "no_anemia_no_deficiency":
        "У вас всё хорошо. Повторите анализы через год.",
    "iron_deficiency_anemia":
        "У вас железодефицитная анемия. Врач назначит препараты железа и обследование.",
    "B12_deficiency_anemia":
        "У вас дефицит витамина B12. Врач назначит уколы.",
    "mixed_deficiency":
        "У вас сочетание нескольких дефицитов. Нужна консультация гематолога.",
    "inflammation_anemia":
        "У вас анемия, связанная с воспалением. Главное — пролечить основное заболевание.",
}


def generate_recommendations(class_name: str, anemia_present: bool, data: PatientData):
    doc = DOCTOR_TEXTS.get(class_name, "Рекомендована консультация гематолога.")
    pat = PATIENT_TEXTS.get(class_name, "Обратитесь к врачу.")
    return doc, pat