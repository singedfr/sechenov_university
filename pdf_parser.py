import re
import io
import pdfplumber


PATTERNS = {
    "hemoglobin": [
        r"(?:гемоглобин|hgb|hb|haemoglobin|hemoglobin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "MCV": [
        r"\bmcv[^\d]{0,10}([\d]+[.,]?\d*)",
    ],
    "MCH": [
        r"\bmch[^\d]{0,10}([\d]+[.,]?\d*)",
    ],
    "MCHC": [
        r"\bmchc[^\d]{0,10}([\d]+[.,]?\d*)",
    ],
    "RDW": [
        r"\brdw[^\d]{0,10}([\d]+[.,]?\d*)",
    ],
    "hematocrit": [
        r"(?:гематокрит|hct)[^\d]{0,10}([\d]+[.,]?\d*)",
    ],
    "RBC": [
        r"(?:эритроциты|rbc)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "WBC": [
        r"(?:лейкоциты|wbc)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "platelets": [
        r"(?:тромбоциты|plt|platelets)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "reticulocytes": [
        r"(?:ретикулоциты|reticulocytes)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "ferritin": [
        r"(?:ферритин|ferritin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "serum_iron": [
        r"(?:железо\s+сыворот|сывороточное\s+железо|serum\s+iron)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "transferrin": [
        r"(?:трансферрин|transferrin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "TIBC": [
        r"(?:ожсс|tibc)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "UIBC": [
        r"(?:лжсс|uibc)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "TSAT": [
        r"(?:нтж|tsat|насыщение\s+трансферрина)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "sTfR": [
        r"(?:stfr|sTfR|рецептор\s+трансферрина)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "Ret_He": [
        r"(?:ret[-_ ]?he|ret-he)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "vitamin_B12": [
        r"(?:витамин\s*b12|b12|цианокобаламин)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "active_B12": [
        r"(?:голотранскобаламин|holotc|активный\s*b12)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "MMA": [
        r"(?:метилмалонов|mma)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "homocysteine": [
        r"(?:гомоцистеин|homocysteine)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "folate": [
        r"(?:фолат|фолиев|folate|folic\s+acid)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "vitamin_B6": [
        r"(?:витамин\s*b6|b6|пиридокс)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "copper": [
        r"(?:медь|copper)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "ceruloplasmin": [
        r"(?:церулоплазмин|ceruloplasmin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "CRP": [
        r"(?:срб|crp|c-реактивный)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "ESR": [
        r"(?:соэ|esr)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "creatinine": [
        r"(?:креатинин|creatinine)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "eGFR": [
        r"(?:скф|egfr|gfr)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "TSH": [
        r"(?:ттг|tsh)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "albumin": [
        r"(?:альбумин|albumin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "LDH": [
        r"(?:лдг|ldh)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "indirect_bilirubin": [
        r"(?:непрямой\s+билирубин|indirect\s+bilirubin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
    "haptoglobin": [
        r"(?:гаптоглобин|haptoglobin)[^\d]{0,15}([\d]+[.,]?\d*)",
    ],
}


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_analyte_value(raw: str) -> float | None:
    try:
        return float(raw.replace(",", "."))
    except (ValueError, AttributeError):
        return None


def extract_analytes(text: str) -> dict:
    text_lower = text.lower()
    result = {}

    for feature, patterns in PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text_lower, flags=re.IGNORECASE)
            if match:
                value = parse_analyte_value(match.group(1))
                if value is not None:
                    result[feature] = value
                    break

    return result


def parse_pdf(pdf_bytes: bytes) -> dict:
    try:
        text = extract_text_from_pdf(pdf_bytes)

        if not text.strip():
            return {
                "ok": False,
                "extracted": {},
                "not_found": list(PATTERNS.keys()),
                "raw_text_preview": "",
                "error": "Не удалось извлечь текст из PDF. Возможно, это сканированный документ.",
            }

        extracted = extract_analytes(text)
        not_found = [k for k in PATTERNS.keys() if k not in extracted]

        return {
            "ok": True,
            "extracted": extracted,
            "not_found": not_found,
            "raw_text_preview": text[:500],
            "error": None,
        }

    except Exception as e:
        return {
            "ok": False,
            "extracted": {},
            "not_found": list(PATTERNS.keys()),
            "raw_text_preview": "",
            "error": f"Ошибка парсинга PDF: {str(e)}",
        }