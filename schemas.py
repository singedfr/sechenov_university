from pydantic import BaseModel
from typing import Optional, List


class PatientData(BaseModel):
    patient_id: str

    age_years: Optional[float] = None
    sex: Optional[str] = None

    hemoglobin: Optional[float] = None
    RBC: Optional[float] = None
    hematocrit: Optional[float] = None
    MCV: Optional[float] = None
    MCH: Optional[float] = None
    MCHC: Optional[float] = None
    RDW: Optional[float] = None
    platelets: Optional[float] = None
    WBC: Optional[float] = None
    reticulocytes: Optional[float] = None

    ferritin: Optional[float] = None
    serum_iron: Optional[float] = None
    transferrin: Optional[float] = None
    TIBC: Optional[float] = None
    UIBC: Optional[float] = None
    TSAT: Optional[float] = None
    sTfR: Optional[float] = None
    Ret_He: Optional[float] = None

    vitamin_B12: Optional[float] = None
    active_B12: Optional[float] = None
    MMA: Optional[float] = None
    homocysteine: Optional[float] = None
    folate: Optional[float] = None
    vitamin_B6: Optional[float] = None

    copper: Optional[float] = None
    ceruloplasmin: Optional[float] = None

    CRP: Optional[float] = None
    ESR: Optional[float] = None
    creatinine: Optional[float] = None
    eGFR: Optional[float] = None
    TSH: Optional[float] = None
    albumin: Optional[float] = None

    LDH: Optional[float] = None
    indirect_bilirubin: Optional[float] = None
    haptoglobin: Optional[float] = None


class FeatureImpact(BaseModel):
    feature: str
    value: Optional[float] = None
    impact: float


class ClassProbability(BaseModel):
    name: str
    probability: float


class PredictionResponse(BaseModel):
    patient_id: str
    anemia_present: bool
    anemia_confidence: float
    class_prediction: str
    class_probability: float
    top_3_classes: List[ClassProbability]
    top_3_features: List[FeatureImpact]
    recommendation_for_doctor: str
    recommendation_for_patient: str
    missing_features: List[str] = []
    data_completeness: float = 1.0