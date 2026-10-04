// ==== АДРЕС BACKEND (пока не используется, но пусть будет) ====
const API_URL = 'http://127.0.0.1:8000/predict';

// =====================================================
// 1. ОБРАБОТКА ФОРМЫ ВРАЧА
// =====================================================
const doctorForm = document.getElementById('doctorForm');
if (doctorForm) {
    doctorForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            role: 'doctor',
            sex: document.getElementById('sex').value,
            age: parseInt(document.getElementById('age').value),
            hemoglobin: parseFloat(document.getElementById('hemoglobin').value),
            mcv: parseFloat(document.getElementById('mcv').value) || null,
            ferritin: parseFloat(document.getElementById('ferritin').value) || null,
            stfr: parseFloat(document.getElementById('stfr').value) || null,
            tsat: parseFloat(document.getElementById('tsat').value) || null,
            b12: parseFloat(document.getElementById('b12').value) || null,
            crp: parseFloat(document.getElementById('crp').value) || null,
            folate: parseFloat(document.getElementById('folate').value) || null
        };

        await sendToBackend(data);
    });
}

// =====================================================
// 2. ОБРАБОТКА ФОРМЫ ПАЦИЕНТА
// =====================================================
const patientForm = document.getElementById('patientForm');
if (patientForm) {
    patientForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            role: 'patient',
            sex: document.getElementById('sex').value,
            age: parseInt(document.getElementById('age').value),
            hemoglobin: parseFloat(document.getElementById('hemoglobin').value),
            mcv: parseFloat(document.getElementById('mcv').value) || null,
            ferritin: parseFloat(document.getElementById('ferritin').value) || null,
            fatigue: document.getElementById('fatigue').checked,
            nails: document.getElementById('nails').checked,
            vegetarian: document.getElementById('vegetarian').checked
        };

        await sendToBackend(data);
    });
}

// =====================================================
// 3. ОТПРАВКА НА BACKEND (С ЗАГЛУШКОЙ)
// =====================================================
async function sendToBackend(data) {
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('hidden');
    resultDiv.innerHTML = '<p>Анализируем...</p>';

    // ============ ЗАГЛУШКА (пока нет backend) ============
    // Имитация задержки, как будто сервер отвечает
    await new Promise(resolve => setTimeout(resolve, 800));

    const fakeResult = data.role === 'doctor' ? {
        role: 'doctor',
        anemia: true,
        severity: 'moderate',
        top_diagnosis: 'iron_deficiency_anemia',
        probabilities: {
            iron_deficiency_anemia: 0.72,
            vitamin_B12_deficiency_anemia: 0.08,
            mixed_Fe_B12: 0.12,
            unexplained_anemia: 0.05,
            other: 0.03
        },
        explanation: [
            'Ферритин 8 нг/мл — ниже нормы',
            'sTfR 5.2 мг/л — повышен',
            'TSAT 12% — снижен'
        ],
        recommendations: [
            'Начать терапию препаратами железа',
            'Исключить кровопотерю (ФГДС, колоноскопия)',
            'Контроль ферритина через 4–6 недель'
        ],
        disclaimer: 'Требуется верификация врачом'
    } : {
        role: 'patient',
        anemia: true,
        message: 'У вас есть признаки анемии. Скорее всего, это нехватка железа.',
        what_to_do: [
            'Запишитесь к терапевту или гематологу',
            'Сдайте анализ на ферритин',
            'Не принимайте железо самостоятельно'
        ],
        urgent: false,
        confidence: 'medium',
        disclaimer: 'Сервис не заменяет консультацию врача'
    };

    renderResult(fakeResult, data.role);

    // ============ РЕАЛЬНЫЙ ЗАПРОС (раскомментируй, когда backend будет готов) ============
    /*
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Ошибка сервера');

        const result = await response.json();
        renderResult(result, data.role);
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
    */
}

// =====================================================
// 4. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА
// =====================================================
function renderResult(result, role) {
    const resultDiv = document.getElementById('result');

    if (role === 'doctor') {
        resultDiv.innerHTML = `
            <h2>Результат анализа</h2>
            <p><strong>Анемия:</strong> ${result.anemia ? 'Да' : 'Нет'}</p>
            <p><strong>Тяжесть:</strong> ${result.severity || '—'}</p>
            <p><strong>Топ-диагноз:</strong> ${result.top_diagnosis}</p>

            <h3>Вероятности:</h3>
            <ul>
                ${Object.entries(result.probabilities).map(([k, v]) =>
                    `<li>${k}: ${(v * 100).toFixed(1)}%</li>`
                ).join('')}
            </ul>

            <h3>Обоснование:</h3>
            <ul>
                ${result.explanation.map(e => `<li>${e}</li>`).join('')}
            </ul>

            <h3>Рекомендации:</h3>
            <ul>
                ${result.recommendations.map(r => `<li>${r}</li>`).join('')}
            </ul>

            <p class="disclaimer">${result.disclaimer || ''}</p>
        `;
    } else {
        resultDiv.innerHTML = `
            <h2>Результат</h2>
            <p>${result.message}</p>

            <h3>Что делать:</h3>
            <ul>
                ${result.what_to_do.map(w => `<li>${w}</li>`).join('')}
            </ul>

            <p class="disclaimer">${result.disclaimer}</p>
        `;
    }
}