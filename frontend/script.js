const API_BASE = "https://anemia-backend-z8ny.onrender.com";
const API_URL = `${API_BASE}/predict`;


function collectFormData(form) {
    const formData = new FormData(form);
    const payload = {};

    for (const [key, value] of formData.entries()) {
        if (
            value === "" ||
            value === null ||
            value === undefined ||
            value === "-" ||
            value === "—" ||
            value === "н/д"
        ) {
            continue;
        }

        const num = parseFloat(value);
        payload[key] = isNaN(num) ? value : num;
    }

    return payload;
}


async function sendToBackend(form, role) {
    const resultDiv = document.getElementById("result");
    const errorDiv  = document.getElementById("error");
    const loadingDiv = document.getElementById("loading");
    const submitBtn = document.getElementById("submitBtn");

    resultDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");
    resultDiv.innerHTML = "";
    errorDiv.innerHTML = "";

    loadingDiv.classList.remove("hidden");
    if (submitBtn) submitBtn.disabled = true;

    try {
        const payload = collectFormData(form);
        console.log("→ Отправляем:", payload);

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        console.log("← Ответ:", data);

        if (!response.ok) {
            const msg = data.detail || `Ошибка сервера: ${response.status}`;
            throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
        }

        window.lastResult = data;
        window.lastFormData = payload;
        renderResult(data, role);

    } catch (err) {
        console.error("Ошибка запроса:", err);

        let userMessage = err.message;
        if (err.name === "TypeError" && userMessage.includes("fetch")) {
            userMessage =
                "Не удаётся связаться с сервером. Проверьте, что backend запущен " +
                "на http://127.0.0.1:8000 и что CORS настроен в main.py.";
        }

        errorDiv.innerHTML = `<strong>Ошибка:</strong> ${userMessage}`;
        errorDiv.classList.remove("hidden");

    } finally {
        loadingDiv.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;
    }
}


function renderResult(result, role) {
    const resultDiv = document.getElementById("result");
    resultDiv.classList.remove("hidden");

    if (role === "doctor") {
        resultDiv.innerHTML = renderDoctorResult(result);
    } else {
        resultDiv.innerHTML = renderPatientResult(result);
    }

    resultDiv.scrollIntoView({ behavior: "smooth", block: "start" });
    const shareBlock = document.getElementById("shareBlock");
    if (shareBlock && role === "doctor") {
        shareBlock.classList.remove("hidden");
        document.getElementById("shareResult").classList.add("hidden");
    }
}


function renderDoctorResult(r) {
    const anemia = r.anemia_present;
    const completeness = r.data_completeness ?? 1.0;
    const missing = r.missing_features || [];

    const diagnosisClass = anemia ? "diagnosis-anemia" : "diagnosis-normal";

    let completenessClass = "completeness-good";
    if (completeness < 0.5) completenessClass = "completeness-bad";
    else if (completeness < 0.8) completenessClass = "completeness-warn";

    const topClassesHtml = (r.top_3_classes || [])
        .map(
            (c) => `
        <div class="prob-row">
            <div class="prob-label">${c.name}</div>
            <div class="prob-bar">
                <div class="prob-fill" style="width: ${(c.probability * 100).toFixed(1)}%"></div>
            </div>
            <div class="prob-value">${(c.probability * 100).toFixed(1)}%</div>
        </div>`
        )
        .join("");

    const topFeaturesHtml = (r.top_3_features || [])
        .map(
            (f) => `
        <tr>
            <td>${f.feature}</td>
            <td>${f.value ?? "—"}</td>
            <td>${(f.impact ?? 0).toFixed(4)}</td>
        </tr>`
        )
        .join("");

    const missingHtml = missing.length
        ? `<div class="missing-block">
                <h4>⚠️ Не хватает анализов для точного диагноза (${missing.length}):</h4>
                <p class="missing-list">${missing.join(", ")}</p>
           </div>`
        : `<p class="all-complete">✅ Все необходимые анализы предоставлены.</p>`;

    return `
        <h2>Результат анализа</h2>

        <div class="diagnosis-block ${diagnosisClass}">
            <div class="diagnosis-title">${anemia ? "🔴 Анемия выявлена" : "🟢 Анемия не выявлена"}</div>
            <div class="diagnosis-class">Диагноз: <strong>${r.class_prediction}</strong></div>
            <div class="diagnosis-prob">Уверенность модели: <strong>${(r.class_probability * 100).toFixed(1)}%</strong></div>
        </div>

        <div class="completeness-block ${completenessClass}">
            Полнота данных: <strong>${(completeness * 100).toFixed(0)}%</strong>
        </div>

        <h3>Дифференциальный ряд (топ-3)</h3>
        <div class="prob-list">${topClassesHtml}</div>

        <h3>Наиболее значимые признаки</h3>
        <table class="features-table">
            <thead>
                <tr><th>Признак</th><th>Значение</th><th>Вклад</th></tr>
            </thead>
            <tbody>${topFeaturesHtml}</tbody>
        </table>

        ${missingHtml}

        <h3>Рекомендации врачу</h3>
        <div class="recommendation">${r.recommendation_for_doctor || "—"}</div>

        <p class="disclaimer">Результаты требуют верификации врачом.</p>
    `;
}


function renderPatientResult(r) {
    const anemia = r.anemia_present;
    const statusIcon = anemia ? "🔴" : "🟢";
    const statusText = anemia ? "У вас есть признаки анемии" : "Признаков анемии не найдено";

    return `
        <h2>Ваш результат</h2>

        <div class="patient-summary">
            <div class="patient-status">${statusIcon} ${statusText}</div>
            <p>${r.recommendation_for_patient || ""}</p>
        </div>

        <h3>Что делать дальше</h3>
        <ol class="patient-actions">
            <li>Покажите этот отчёт вашему лечащему врачу (терапевту или гематологу).</li>
            <li>Не занимайтесь самолечением — препараты железа и витаминов назначает врач.</li>
            <li>При необходимости врач назначит дополнительные анализы.</li>
        </ol>

        <p class="disclaimer">
            Этот сервис не является медицинским заключением. Окончательный диагноз ставит врач.
        </p>
    `;
}


const doctorForm = document.getElementById("doctorForm");
if (doctorForm) {
    doctorForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        await sendToBackend(doctorForm, "doctor");
    });
}

const patientForm = document.getElementById("patientForm");
if (patientForm) {
    patientForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        await sendToBackend(patientForm, "patient");
    });
}


const loadExampleBtn = document.getElementById("loadExample");
if (loadExampleBtn) {
    loadExampleBtn.addEventListener("click", () => {
        const example = {
            patient_id: "P001",
            sex: "female",
            age_years: 45,
            hemoglobin: 100,
            MCV: 70,
            MCH: 22,
            RDW: 17,
            ferritin: 8,
            sTfR: 5.2,
            TSAT: 12,
            vitamin_B12: 350,
            CRP: 2.1,
            folate: 5.0,
        };

        for (const [id, value] of Object.entries(example)) {
            const field = document.getElementById(id);
            if (field) {
                field.value = value;
            }
        }
    });
}

const pdfFileInput = document.getElementById("pdfFile");
const uploadPdfBtn = document.getElementById("uploadPdfBtn");
const parsePdfBtn = document.getElementById("parsePdfBtn");
const pdfFileName = document.getElementById("pdfFileName");
const pdfStatus = document.getElementById("pdfStatus");

if (uploadPdfBtn) {
    uploadPdfBtn.addEventListener("click", () => {
        pdfFileInput.click();
    });

    pdfFileInput.addEventListener("change", () => {
        const file = pdfFileInput.files[0];
        if (file) {
            pdfFileName.textContent = file.name;
            parsePdfBtn.classList.remove("hidden");
            pdfStatus.classList.add("hidden");
        } else {
            pdfFileName.textContent = "Файл не выбран";
            parsePdfBtn.classList.add("hidden");
        }
    });

    parsePdfBtn.addEventListener("click", async () => {
        const file = pdfFileInput.files[0];
        if (!file) return;

        pdfStatus.className = "pdf-status";
        pdfStatus.textContent = "⏳ Распознаю PDF…";
        pdfStatus.classList.remove("hidden");
        parsePdfBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch(`${API_BASE}/parse-pdf`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Не удалось распознать PDF");
            }

            const extracted = data.extracted || {};
            const count = Object.keys(extracted).length;

            if (count === 0) {
                pdfStatus.className = "pdf-status error";
                pdfStatus.textContent =
                    "⚠️ Не удалось распознать ни одного показателя. " +
                    "Возможно, файл отсканирован или имеет нестандартный формат. " +
                    "Заполните форму вручную.";
                return;
            }

            // Заполняем форму найденными значениями
            for (const [name, value] of Object.entries(extracted)) {
                const field = document.getElementById(name);
                if (field) {
                    field.value = value;
                    // Подсветить зелёным — видно, что поле распознано
                    field.classList.add("field-autofilled");
                }
            }

            pdfStatus.className = "pdf-status success";
            pdfStatus.innerHTML =
                `✅ Распознано показателей: <strong>${count}</strong>.<br>` +
                `Проверьте значения в форме — при необходимости исправьте.<br>` +
                `<small>Не найдено: ${data.not_found.length} показателей — их можно заполнить вручную.</small>`;

        } catch (err) {
            pdfStatus.className = "pdf-status error";
            pdfStatus.textContent = `⚠️ Ошибка: ${err.message}`;
        } finally {
            parsePdfBtn.disabled = false;
        }
    });
}


const saveForPatientBtn = document.getElementById("saveForPatient");
if (saveForPatientBtn) {
    saveForPatientBtn.addEventListener("click", async () => {
        const shareResult = document.getElementById("shareResult");
        const result = window.lastResult;

        if (!result) {
            shareResult.innerHTML = "⚠️ Сначала выполните анализ.";
            shareResult.classList.remove("hidden");
            return;
        }

        saveForPatientBtn.disabled = true;
        shareResult.innerHTML = "⏳ Сохраняю…";
        shareResult.classList.remove("hidden");

        try {
            const payload = {
                patient_id: result.patient_id || "unknown",
                result: {
                    anemia_present: result.anemia_present,
                    class_prediction: result.class_prediction,
                    class_probability: result.class_probability,
                    recommendation_for_patient: result.recommendation_for_patient,
                    recommendation_for_doctor: result.recommendation_for_doctor,
                    top_3_classes: result.top_3_classes,
                    data_completeness: result.data_completeness,
                    missing_features: result.missing_features,
                    saved_at: new Date().toISOString(),
                },
            };

            const response = await fetch(`${API_BASE}/patients`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Не удалось сохранить");
            }

            // Показываем код
            shareResult.innerHTML = `
                <div class="patient-code-hint">Код для пациента:</div>
                <div class="patient-code">${data.patient_id}</div>
                <div class="patient-code-hint">
                    Пациент должен открыть страницу <strong>«Я пациент»</strong> и ввести этот код.
                </div>
            `;
        } catch (err) {
            shareResult.innerHTML = `⚠️ Ошибка: ${err.message}`;
        } finally {
            saveForPatientBtn.disabled = false;
        }
    });
}


const lookupBtn = document.getElementById("lookupBtn");
if (lookupBtn) {
    const codeInput = document.getElementById("codeInput");
    const codeError = document.getElementById("codeError");
    const patientResult = document.getElementById("patientResult");

    codeInput.addEventListener("input", () => {
        codeInput.value = codeInput.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
    });

    codeInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") lookupBtn.click();
    });

    lookupBtn.addEventListener("click", async () => {
        const code = codeInput.value.trim();
        codeError.classList.add("hidden");
        patientResult.classList.add("hidden");

        if (code.length < 4) {
            codeError.textContent = "Код должен содержать минимум 4 символа.";
            codeError.classList.remove("hidden");
            return;
        }

        lookupBtn.disabled = true;
        lookupBtn.textContent = "⏳ Ищу…";

        try {
            const response = await fetch(`${API_BASE}/patients/${code}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Результат не найден");
            }

            renderPatientView(data);
            patientResult.classList.remove("hidden");
            patientResult.scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            codeError.textContent = `⚠️ ${err.message}`;
            codeError.classList.remove("hidden");
        } finally {
            lookupBtn.disabled = false;
            lookupBtn.textContent = "🔍 Показать результат";
        }
    });
}


function renderPatientView(record) {
    const patientResult = document.getElementById("patientResult");
    const r = record.result;

    const anemia = r.anemia_present;
    const statusClass = anemia ? "anemia" : "normal";
    const statusIcon = anemia ? "🔴" : "🟢";
    const statusTitle = anemia
        ? "По результатам анализа выявлены признаки анемии"
        : "Признаков анемии не обнаружено";

    const diagNames = {
        "iron_deficiency_anemia": "Железодефицитная анемия",
        "B12_deficiency_anemia": "B12-дефицитная анемия",
        "folate_deficiency_anemia": "Фолиеводефицитная анемия",
        "B6_deficiency": "Дефицит витамина B6",
        "copper_deficiency": "Дефицит меди",
        "inflammation_anemia": "Анемия при воспалении",
        "mixed_deficiency": "Сочетанный дефицит",
        "anemia_other": "Анемия неясного генеза",
        "no_anemia_no_deficiency": "Отклонений не выявлено",
        "latent_deficiency": "Скрытый дефицит",
        "B12_deficiency_no_anemia": "Дефицит B12 без анемии",
        "folate_deficiency_no_anemia": "Дефицит фолатов без анемии",
    };
    const diagHuman = diagNames[r.class_prediction] || r.class_prediction;

    const date = new Date(record.created_at).toLocaleString("ru-RU", {
        day: "2-digit", month: "long", year: "numeric",
        hour: "2-digit", minute: "2-digit",
    });

    const steps = anemia
        ? [
            "Запишитесь на приём к терапевту или гематологу — покажите ему этот отчёт.",
            "Не принимайте препараты железа или витамины самостоятельно — дозировки назначает врач.",
            "Сдайте дополнительные анализы, которые порекомендует врач — так диагноз будет точнее.",
            "После начала лечения обязательно сдайте контрольные анализы.",
        ]
        : [
            "Признаков анемии не найдено — повторите контрольные анализы через 12 месяцев.",
            "Если вы чувствуете слабость, утомляемость или другие симптомы — расскажите об этом врачу.",
            "Поддерживайте разнообразное питание, богатое железом и витаминами группы B.",
        ];

    const stepsHtml = steps
        .map(
            (s, i) => `
        <li class="next-step">
            <span class="next-step-number">${i + 1}</span>
            <span class="next-step-text">${s}</span>
        </li>`
        )
        .join("");

    patientResult.innerHTML = `
        <div class="result-header">
            <span class="result-header-icon">📋</span>
            <h2 class="result-header-title">Ваш результат</h2>
            <div class="result-header-sub">Код: ${record.patient_id} · ${date}</div>
        </div>

        <div class="status-card ${statusClass}">
            <span class="status-card-icon">${statusIcon}</span>
            <div class="status-card-title">${statusTitle}</div>
            <div class="status-card-diag">
                Что показывают анализы: <strong>${diagHuman}</strong>
            </div>
        </div>

        <div class="simple-explanation">
            <div class="simple-explanation-title">Что это значит</div>
            <p>${r.recommendation_for_patient || "Обратитесь к врачу за подробной интерпретацией."}</p>
        </div>

        <div class="next-steps">
            <h3 class="next-steps-title">📌 Что делать дальше</h3>
            <ul class="next-steps-list">
                ${stepsHtml}
            </ul>
        </div>

        <div class="result-actions">
            <button type="button" class="btn btn-patient" onclick="window.print()">
                🖨️ Распечатать
            </button>
            <button type="button" class="btn btn-secondary" onclick="window.location.href='index.html'">
                🏠 На главную
            </button>
        </div>
    `;
}