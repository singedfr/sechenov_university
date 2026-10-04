// ==== АДРЕС BACKEND ====
const API_URL = "http://127.0.0.1:8000/predict";


// =====================================================
// 1. СБОР ДАННЫХ ИЗ ФОРМЫ
// =====================================================
function collectFormData(form) {
    const formData = new FormData(form);
    const payload = {};

    for (const [key, value] of formData.entries()) {
        // Пропускаем пустые значения и прочерки
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

        // Если это числовое значение — приводим к числу
        const num = parseFloat(value);
        payload[key] = isNaN(num) ? value : num;
    }

    return payload;
}


// =====================================================
// 2. ОТПРАВКА НА BACKEND
// =====================================================
async function sendToBackend(form, role) {
    const resultDiv = document.getElementById("result");
    const errorDiv  = document.getElementById("error");
    const loadingDiv = document.getElementById("loading");
    const submitBtn = document.getElementById("submitBtn");

    // Сброс состояния
    resultDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");
    resultDiv.innerHTML = "";
    errorDiv.innerHTML = "";

    // Показать загрузку
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
            // Backend вернул ошибку (422, 500 и т.д.)
            const msg = data.detail || `Ошибка сервера: ${response.status}`;
            throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
        }

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


// =====================================================
// 3. ОТРИСОВКА РЕЗУЛЬТАТА
// =====================================================
function renderResult(result, role) {
    const resultDiv = document.getElementById("result");
    resultDiv.classList.remove("hidden");

    if (role === "doctor") {
        resultDiv.innerHTML = renderDoctorResult(result);
    } else {
        resultDiv.innerHTML = renderPatientResult(result);
    }

    resultDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}


// --- Отображение для врача ---
function renderDoctorResult(r) {
    const anemia = r.anemia_present;
    const completeness = r.data_completeness ?? 1.0;
    const missing = r.missing_features || [];

    // Цвет плашки диагноза
    const diagnosisClass = anemia ? "diagnosis-anemia" : "diagnosis-normal";

    // Цвет полноты данных
    let completenessClass = "completeness-good";
    if (completeness < 0.5) completenessClass = "completeness-bad";
    else if (completeness < 0.8) completenessClass = "completeness-warn";

    // Топ-3 класса
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

    // Топ-3 признака
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

    // Пропущенные признаки
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


// --- Отображение для пациента ---
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


// =====================================================
// 4. ПРИВЯЗКА ФОРМ
// =====================================================
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


// =====================================================
// 5. КНОПКА "ЗАГРУЗИТЬ ПРИМЕР" (для формы врача)
// =====================================================
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