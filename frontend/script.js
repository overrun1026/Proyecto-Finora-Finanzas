
"use strict";

/*
 * Finora — Frontend de finanzas personales
 * API: /api/v1
 * El proxy de Nginx dirige estas peticiones a FastAPI.
 */

const API = "/api/v1";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const state = {
    transactions: [],
    categories: [],
    budgets: [],
    goals: [],
    monthlyReport: [],
    categoryReport: [],
    monthlyChart: null,
    categoryChart: null,
    reportChart: null,
    dialogAction: null,
    busy: false,
};

const MONTHS = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

const CHART_COLORS = [
    "#a6e66b", "#6fcf97", "#e7ba62", "#81b8a1", "#c5df85",
    "#a0a88e", "#d1a875", "#7eaa67", "#d4d9b9", "#83c5a3"
];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function number(value) {
    const result = Number(value);
    return Number.isFinite(result) ? result : 0;
}

function money(value, currency = "COP") {
    return new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency,
        maximumFractionDigits: 2
    }).format(number(value));
}

function dateText(value) {
    if (!value) return "—";
    const parts = String(value).slice(0, 10).split("-");
    if (parts.length !== 3) return escapeHTML(value);
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

function todayISO() {
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
}

function currentYear() {
    return new Date().getFullYear();
}

function selectedYear(selector, fallback = currentYear()) {
    const element = $(selector);
    return element && element.value ? Number(element.value) : fallback;
}

function monthName(month) {
    return MONTHS[number(month) - 1] || "—";
}

function showNotice(message, isError = false) {
    const box = $("#notification");
    box.textContent = message;
    box.classList.remove("hidden", "error");
    if (isError) box.classList.add("error");

    window.clearTimeout(showNotice.timer);
    showNotice.timer = window.setTimeout(() => {
        box.classList.add("hidden");
    }, 6000);
}

function showConnection(online, message) {
    const status = $("#connection-status");
    const dot = $(".status-dot");

    if (status) status.textContent = message;
    if (dot) {
        dot.classList.toggle("online", online);
        dot.classList.toggle("offline", !online);
    }
}

async function api(path, options = {}) {
    const config = {
        method: options.method || "GET",
        headers: { ...(options.headers || {}) },
    };

    if (options.body !== undefined) {
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(options.body);
    }

    let response;

    try {
        response = await fetch(`${API}${path}`, config);
    } catch {
        showConnection(false, "API no disponible");
        throw new Error("No se pudo conectar con el backend. Comprueba que FastAPI esté ejecutándose.");
    }

    if (response.status === 204) return null;

    const contentType = response.headers.get("content-type") || "";
    let payload = null;

    if (contentType.includes("application/json")) {
        payload = await response.json();
    } else {
        const text = await response.text();
        payload = text ? { detail: text } : null;
    }

    if (!response.ok) {
        const detail = payload?.detail;
        let message;

        if (Array.isArray(detail)) {
            message = detail.map(item => {
                const location = Array.isArray(item.loc) ? item.loc.join(".") : "";
                return `${location ? `${location}: ` : ""}${item.msg || "Dato inválido"}`;
            }).join(" · ");
        } else {
            message = typeof detail === "string"
                ? detail
                : `La API respondió con el estado ${response.status}.`;
        }

        throw new Error(message);
    }

    showConnection(true, "API conectada");
    return payload;
}

function handleError(error) {
    console.error(error);
    showNotice(error.message || "Ocurrió un error inesperado.", true);
}

function setBusy(busy) {
    state.busy = busy;
    const submit = $("#dialog-submit");
    if (submit) {
        submit.disabled = busy;
        submit.textContent = busy ? "Guardando..." : "Guardar";
    }
}

function setPage(page) {
    const titles = {
        dashboard: "Dashboard",
        transactions: "Transacciones",
        budgets: "Presupuestos",
        savings: "Metas de ahorro",
        reports: "Informes",
        categories: "Categorías"
    };

    if (!titles[page]) page = "dashboard";

    $$(".page").forEach(element => {
        element.classList.toggle("active", element.id === `page-${page}`);
    });

    $$(".nav-item").forEach(element => {
        element.classList.toggle("active", element.dataset.page === page);
    });

    $("#page-title").textContent = titles[page];

    if (page === "dashboard") loadDashboard().catch(handleError);
    if (page === "transactions") loadTransactions().catch(handleError);
    if (page === "budgets") loadBudgets().catch(handleError);
    if (page === "savings") loadGoals().catch(handleError);
    if (page === "reports") loadReports().catch(handleError);
    if (page === "categories") loadCategories().catch(handleError);

    window.scrollTo({ top: 0, behavior: "smooth" });
}

function initYearSelects() {
    const year = currentYear();
    const options = [];

    for (let value = year + 2; value >= year - 8; value--) {
        options.push(`<option value="${value}">${value}</option>`);
    }

    ["#dashboard-year", "#budget-year", "#report-year"].forEach(selector => {
        const select = $(selector);
        if (select) {
            select.innerHTML = options.join("");
            select.value = String(year);
        }
    });

    const month = $("#budget-month");
    if (month) month.value = String(new Date().getMonth() + 1);
}

function initDate() {
    const element = $("#current-date");
    if (element) {
        element.textContent = new Intl.DateTimeFormat("es-CO", {
            dateStyle: "medium"
        }).format(new Date());
    }
}

function field(name, label, type = "text", options = {}) {
    const required = options.required ? "required" : "";
    const min = options.min !== undefined ? `min="${escapeHTML(options.min)}"` : "";
    const max = options.max !== undefined ? `max="${escapeHTML(options.max)}"` : "";
    const step = options.step !== undefined ? `step="${escapeHTML(options.step)}"` : "";
    const maxlength = options.maxlength ? `maxlength="${options.maxlength}"` : "";
    const placeholder = options.placeholder
        ? `placeholder="${escapeHTML(options.placeholder)}"` : "";
    const full = options.full ? "full-width" : "";

    let control;

    if (type === "select") {
        const choices = options.choices || [];
        control = `
            <select name="${escapeHTML(name)}" id="field-${escapeHTML(name)}" ${required}>
                ${choices.map(choice => `
                    <option value="${escapeHTML(choice.value)}">
                        ${escapeHTML(choice.label)}
                    </option>
                `).join("")}
            </select>`;
    } else if (type === "textarea") {
        control = `
            <textarea name="${escapeHTML(name)}" id="field-${escapeHTML(name)}"
                ${required} ${maxlength} ${placeholder}></textarea>`;
    } else {
        control = `
            <input type="${escapeHTML(type)}" name="${escapeHTML(name)}"
                id="field-${escapeHTML(name)}" ${required} ${min} ${max}
                ${step} ${maxlength} ${placeholder}>`;
    }

    return `
        <div class="dialog-field ${full}">
            <label for="field-${escapeHTML(name)}">${escapeHTML(label)}</label>
            ${control}
        </div>`;
}

function categoryChoices(kind = null, includeEmpty = true) {
    const list = state.categories.filter(category => {
        if (category.is_active === false) return false;
        if (!kind || kind === "both") return true;
        return category.kind === kind || category.kind === "both";
    });

    const choices = list.map(category => ({
        value: String(category.id),
        label: category.name
    }));

    if (includeEmpty) {
        choices.unshift({ value: "", label: "Sin categoría" });
    }

    return choices;
}

function populateSelect(selector, choices, placeholder) {
    const element = $(selector);
    if (!element) return;

    const previous = element.value;
    element.innerHTML = [
        `<option value="">${escapeHTML(placeholder)}</option>`,
        ...choices.map(item =>
            `<option value="${escapeHTML(item.value)}">${escapeHTML(item.label)}</option>`
        )
    ].join("");

    if ([...element.options].some(option => option.value === previous)) {
        element.value = previous;
    }
}

function openDialog(title, fields, submitAction, existing = {}) {
    const dialog = $("#app-dialog");
    const form = $("#dialog-form");

    $("#dialog-title").textContent = title;
    $("#dialog-fields").innerHTML = fields.join("");
    state.dialogAction = submitAction;

    for (const [name, value] of Object.entries(existing)) {
        const input = $(`[name="${CSS.escape(name)}"]`, form);
        if (input && value !== null && value !== undefined) {
            input.value = String(value);
        }
    }

    setBusy(false);

    if (typeof dialog.showModal === "function") {
        dialog.showModal();
    } else {
        showNotice("Este navegador no admite el formulario emergente.", true);
    }
}

function closeDialog() {
    const dialog = $("#app-dialog");
    if (dialog.open) dialog.close();
    state.dialogAction = null;
    setBusy(false);
}

function formDataObject(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function nullableNumber(value) {
    return value === "" || value === null || value === undefined
        ? null
        : Number(value);
}

function nullableText(value) {
    const cleaned = String(value ?? "").trim();
    return cleaned ? cleaned : null;
}

function amountValue(value) {
    const amount = Number(value);
    if (!Number.isFinite(amount) || amount <= 0) {
        throw new Error("El importe debe ser mayor que cero.");
    }
    return amount;
}

function categoryName(id) {
    if (id === null || id === undefined || id === "") return "Sin categoría";
    return state.categories.find(category => Number(category.id) === Number(id))?.name
        || "Categoría eliminada";
}

function actionButtons(type, id, extra = "") {
    return `
        <div class="table-actions">
            <button type="button" class="table-action"
                data-action="edit-${type}" data-id="${escapeHTML(id)}">Editar</button>
            ${extra}
            <button type="button" class="table-action danger"
                data-action="delete-${type}" data-id="${escapeHTML(id)}">Eliminar</button>
        </div>`;
}

function emptyState(message) {
    return `<p class="empty-state">${escapeHTML(message)}</p>`;
}

function transactionRows(items) {
    if (!items.length) return emptyState("No hay transacciones para mostrar.");

    return `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Descripción</th>
                    <th>Categoría</th>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Importe</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>
                            <span class="table-primary">${escapeHTML(item.description)}</span>
                            ${item.notes ? `<span class="table-secondary">${escapeHTML(item.notes)}</span>` : ""}
                        </td>
                        <td>${escapeHTML(categoryName(item.category_id))}</td>
                        <td>${dateText(item.transaction_date)}</td>
                        <td>
                            <span class="pill ${item.kind === "income" ? "pill-income" : "pill-expense"}">
                                ${item.kind === "income" ? "Ingreso" : "Gasto"}
                            </span>
                        </td>
                        <td class="${item.kind === "income" ? "amount-income" : "amount-expense"}">
                            ${item.kind === "income" ? "+" : "−"}${money(item.amount)}
                        </td>
                        <td>${actionButtons("transaction", item.id)}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>`;
}

async function loadCategories() {
    state.categories = await api("/categories");

    populateSelect(
        "#filter-category",
        state.categories.map(category => ({
            value: String(category.id),
            label: `${category.name}${category.is_active === false ? " (inactiva)" : ""}`
        })),
        "Todas"
    );

    renderCategories();
}

async function loadTransactions() {
    const params = new URLSearchParams();
    const kind = $("#filter-kind")?.value;
    const category = $("#filter-category")?.value;
    const dateFrom = $("#filter-from")?.value;
    const dateTo = $("#filter-to")?.value;
    const min = $("#filter-min")?.value;
    const max = $("#filter-max")?.value;

    if (kind) params.set("kind", kind);
    if (category) params.set("category_id", category);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    if (min !== "") params.set("min_amount", min);
    if (max !== "") params.set("max_amount", max);
    params.set("limit", "200");
    params.set("offset", "0");

    const query = params.toString();
    state.transactions = await api(`/transactions${query ? `?${query}` : ""}`);

    $("#transactions-table").innerHTML = transactionRows(state.transactions);
}

async function loadDashboard() {
    const [summary, transactions, monthly, categoryExpenses, budgets, goals] =
        await Promise.all([
            api("/finance/summary"),
            api("/transactions?limit=8&offset=0"),
            api(`/reports/monthly?year=${selectedYear("#dashboard-year")}`),
            api("/reports/expenses-by-category"),
            api(`/budgets?year=${currentYear()}&month=${new Date().getMonth() + 1}`),
            api("/savings-goals")
        ]);

    $("#total-income").textContent = money(summary.total_income, summary.currency || "COP");
    $("#total-expenses").textContent = money(summary.total_expenses, summary.currency || "COP");
    $("#total-balance").textContent = money(summary.balance, summary.currency || "COP");
    $("#transaction-count").textContent = new Intl.NumberFormat("es-CO")
        .format(number(summary.transaction_count));

    $("#recent-transactions").innerHTML = transactionRows(transactions);
    state.budgets = budgets;
    state.goals = goals;

    renderMonthlyChart(monthly, "monthly-chart", "dashboard");
    renderCategoryChart(categoryExpenses);
    renderDashboardBudgets(budgets);
    renderDashboardGoals(goals);
}

function chartDefaults() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#aab3a4",
                    usePointStyle: true,
                    pointStyle: "circle",
                    padding: 18,
                    font: { size: 11 }
                }
            },
            tooltip: {
                callbacks: {
                    label(context) {
                        return `${context.dataset.label || context.label}: ${money(context.raw)}`;
                    }
                }
            }
        }
    };
}

function renderMonthlyChart(rows, canvasId, mode = "dashboard") {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;

    const map = new Map(rows.map(row => [Number(row.month), row]));
    const labels = MONTHS;
    const income = labels.map((_, index) => number(map.get(index + 1)?.income));
    const expenses = labels.map((_, index) => number(map.get(index + 1)?.expenses));
    const balance = labels.map((_, index) => number(map.get(index + 1)?.balance));

    const datasets = [
        {
            label: "Ingresos",
            data: income,
            backgroundColor: "#a6e66b",
            borderRadius: 5
        },
        {
            label: "Gastos",
            data: expenses,
            backgroundColor: "#d87979",
            borderRadius: 5
        }
    ];

    if (mode === "reports") {
        datasets.push({
            type: "line",
            label: "Balance",
            data: balance,
            borderColor: "#e7ba62",
            backgroundColor: "#e7ba62",
            tension: 0.35,
            pointRadius: 3,
            yAxisID: "y"
        });
    }

    const previous = mode === "reports" ? state.reportChart : state.monthlyChart;
    if (previous) previous.destroy();

    const options = chartDefaults();
    options.scales = {
        x: {
            ticks: { color: "#929c8e", maxRotation: 0, autoSkip: true },
            grid: { color: "rgba(255,255,255,0.035)" },
            border: { display: false }
        },
        y: {
            beginAtZero: true,
            ticks: {
                color: "#929c8e",
                callback: value => new Intl.NumberFormat("es-CO", {
                    notation: "compact",
                    maximumFractionDigits: 1
                }).format(value)
            },
            grid: { color: "rgba(255,255,255,0.06)" },
            border: { display: false }
        }
    };

    const chart = new Chart(canvas, {
        type: "bar",
        data: { labels, datasets },
        options
    });

    if (mode === "reports") state.reportChart = chart;
    else state.monthlyChart = chart;
}

function renderCategoryChart(rows) {
    const canvas = $("#category-chart");
    if (!canvas || typeof Chart === "undefined") return;

    if (state.categoryChart) state.categoryChart.destroy();

    const filtered = rows.filter(row => number(row.total) > 0);
    const labels = filtered.map(row => row.category_name || "Sin categoría");
    const values = filtered.map(row => number(row.total));

    state.categoryChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: labels.length ? labels : ["Sin gastos registrados"],
            datasets: [{
                data: values.length ? values : [1],
                backgroundColor: values.length
                    ? values.map((_, index) => CHART_COLORS[index % CHART_COLORS.length])
                    : ["#30382b"],
                borderColor: "#191e18",
                borderWidth: 4,
                hoverOffset: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "72%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: context => `${context.label}: ${money(context.raw)}`
                    }
                }
            }
        }
    });

    $("#category-legend").innerHTML = filtered.length
        ? filtered.slice(0, 7).map((item, index) => `
            <div class="legend-item">
                <span class="legend-label">
                    <span class="legend-color" style="background:${CHART_COLORS[index % CHART_COLORS.length]}"></span>
                    <span class="legend-name">${escapeHTML(item.category_name || "Sin categoría")}</span>
                </span>
                <span class="legend-value">${money(item.total)}</span>
            </div>
        `).join("")
        : emptyState("Todavía no hay gastos por categoría.");
}

function renderDashboardBudgets(items) {
    const container = $("#dashboard-budgets");

    if (!items.length) {
        container.innerHTML = emptyState("No hay presupuestos para este mes.");
        return;
    }

    container.innerHTML = items.slice(0, 4).map(item => {
        const percent = number(item.percent_used);
        const safePercent = Math.max(0, Math.min(100, percent));
        const tone = percent >= 100 ? "danger" : percent >= 80 ? "warning" : "";

        return `
            <div class="budget-summary">
                <div class="data-card-top">
                    <strong>${escapeHTML(item.category_name)}</strong>
                    <span class="category-kind">${percent.toFixed(0)}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill ${tone}" style="width:${safePercent}%"></div>
                </div>
                <div class="progress-meta">
                    <span>Gastado ${money(item.spent)}</span>
                    <span>Límite ${money(item.amount_limit)}</span>
                </div>
            </div>
        `;
    }).join("");
}

function renderDashboardGoals(items) {
    const container = $("#dashboard-savings");

    if (!items.length) {
        container.innerHTML = emptyState("Crea una meta para comenzar a ahorrar.");
        return;
    }

    container.innerHTML = items.slice(0, 4).map(item => {
        const percent = Math.max(0, Math.min(100, number(item.percent_complete)));

        return `
            <div class="budget-summary">
                <div class="data-card-top">
                    <strong>${escapeHTML(item.name)}</strong>
                    <span class="category-kind">${percent.toFixed(0)}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:${percent}%"></div>
                </div>
                <div class="progress-meta">
                    <span>Ahorrado ${money(item.saved_amount)}</span>
                    <span>Meta ${money(item.target_amount)}</span>
                </div>
            </div>
        `;
    }).join("");
}

async function loadBudgets() {
    const year = selectedYear("#budget-year");
    const month = $("#budget-month")?.value;
    const params = new URLSearchParams();
    if (year) params.set("year", year);
    if (month) params.set("month", month);

    state.budgets = await api(`/budgets?${params.toString()}`);
    renderBudgets();
}

function renderBudgets() {
    const container = $("#budgets-list");
    const items = state.budgets;

    if (!items.length) {
        container.innerHTML = `<div class="panel">${emptyState("No hay presupuestos para este periodo.")}</div>`;
        return;
    }

    container.innerHTML = items.map(item => {
        const percent = number(item.percent_used);
        const safePercent = Math.max(0, Math.min(100, percent));
        const tone = percent >= 100 ? "danger" : percent >= 80 ? "warning" : "";

        return `
            <article class="data-card">
                <div class="data-card-top">
                    <div>
                        <h3>${escapeHTML(item.category_name)}</h3>
                        <p>${monthName(item.month)} ${item.year}</p>
                    </div>
                    <span class="pill ${percent >= 100 ? "pill-danger" : "pill-active"}">
                        ${percent.toFixed(1)}%
                    </span>
                </div>
                <div class="card-amount">${money(item.spent)}</div>
                <div class="card-subtitle">de ${money(item.amount_limit)} presupuestados</div>
                <div class="progress-track">
                    <div class="progress-fill ${tone}" style="width:${safePercent}%"></div>
                </div>
                <div class="progress-meta">
                    <span>Disponible</span>
                    <strong>${money(item.remaining)}</strong>
                </div>
                ${percent >= 100 ? `<p class="category-kind">Has alcanzado o superado este límite.</p>` : ""}
                <div class="card-actions">
                    <button class="button button-secondary" data-action="edit-budget" data-id="${item.id}">Editar límite</button>
                    <button class="button button-danger" data-action="delete-budget" data-id="${item.id}">Eliminar</button>
                </div>
            </article>
        `;
    }).join("");
}

async function loadGoals() {
    state.goals = await api("/savings-goals");
    renderGoals();
}

function renderGoals() {
    const container = $("#savings-list");

    if (!state.goals.length) {
        container.innerHTML = `<div class="panel">${emptyState("Aún no tienes metas de ahorro. Crea la primera.")}</div>`;
        return;
    }

    container.innerHTML = state.goals.map(goal => {
        const percent = number(goal.percent_complete);
        const safePercent = Math.max(0, Math.min(100, percent));

        return `
            <article class="data-card">
                <div class="data-card-top">
                    <div>
                        <h3>${escapeHTML(goal.name)}</h3>
                        <p>${goal.deadline ? `Fecha límite: ${dateText(goal.deadline)}` : "Sin fecha límite"}</p>
                    </div>
                    <span class="pill pill-active">${percent.toFixed(1)}%</span>
                </div>
                <div class="card-amount">${money(goal.saved_amount)}</div>
                <div class="card-subtitle">de ${money(goal.target_amount)} de objetivo</div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:${safePercent}%"></div>
                </div>
                <div class="progress-meta">
                    <span>Falta por ahorrar</span>
                    <strong>${money(goal.remaining_amount)}</strong>
                </div>
                ${goal.notes ? `<p>${escapeHTML(goal.notes)}</p>` : ""}
                <div class="card-actions">
                    <button class="button button-primary" data-action="contribute-goal" data-id="${goal.id}">＋ Registrar aporte</button>
                    <button class="button button-secondary" data-action="history-goal" data-id="${goal.id}">Historial</button>
                    <button class="button button-secondary" data-action="edit-goal" data-id="${goal.id}">Editar</button>
                    <button class="button button-danger" data-action="delete-goal" data-id="${goal.id}">Eliminar</button>
                </div>
            </article>
        `;
    }).join("");
}

async function loadReports() {
    const year = selectedYear("#report-year");

    const [monthly, categories] = await Promise.all([
        api(`/reports/monthly?year=${year}`),
        api("/reports/expenses-by-category")
    ]);

    state.monthlyReport = monthly;
    state.categoryReport = categories;

    const totalIncome = monthly.reduce((sum, row) => sum + number(row.income), 0);
    const totalExpenses = monthly.reduce((sum, row) => sum + number(row.expenses), 0);
    const totalBalance = monthly.reduce((sum, row) => sum + number(row.balance), 0);

    $("#report-income").textContent = money(totalIncome);
    $("#report-expenses").textContent = money(totalExpenses);
    $("#report-balance").textContent = money(totalBalance);

    renderMonthlyChart(monthly, "report-monthly-chart", "reports");
    renderCategoryReport(categories);
}

function renderCategoryReport(items) {
    const container = $("#report-category-table");

    if (!items.length) {
        container.innerHTML = emptyState("No hay gastos por categoría para mostrar.");
        return;
    }

    const total = items.reduce((sum, item) => sum + number(item.total), 0);

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr><th>Categoría</th><th>Total gastado</th><th>Porcentaje</th></tr>
            </thead>
            <tbody>
                ${items.map(item => {
                    const amount = number(item.total);
                    const percent = total > 0 ? amount / total * 100 : 0;

                    return `
                        <tr>
                            <td class="table-primary">${escapeHTML(item.category_name || "Sin categoría")}</td>
                            <td class="amount-expense">${money(amount)}</td>
                            <td>${percent.toFixed(1)}%</td>
                        </tr>
                    `;
                }).join("")}
                <tr>
                    <td class="table-primary">Total</td>
                    <td class="amount-expense">${money(total)}</td>
                    <td>100%</td>
                </tr>
            </tbody>
        </table>`;
}

function renderCategories() {
    const container = $("#categories-table");
    if (!container) return;

    if (!state.categories.length) {
        container.innerHTML = emptyState("No hay categorías. Crea una para organizar tus movimientos.");
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr><th>Nombre</th><th>Tipo</th><th>Estado</th><th>Acciones</th></tr>
            </thead>
            <tbody>
                ${state.categories.map(category => `
                    <tr>
                        <td class="table-primary">${escapeHTML(category.name)}</td>
                        <td>${escapeHTML({
                            income: "Ingresos",
                            expense: "Gastos",
                            both: "Ambos"
                        }[category.kind] || category.kind)}</td>
                        <td>
                            <span class="pill ${category.is_active ? "pill-active" : "pill-neutral"}">
                                ${category.is_active ? "Activa" : "Inactiva"}
                            </span>
                        </td>
                        <td>
                            <div class="table-actions">
                                <button class="table-action" data-action="edit-category" data-id="${category.id}">Editar</button>
                                <button class="table-action danger" data-action="delete-category" data-id="${category.id}">Eliminar</button>
                            </div>
                        </td>
                    </tr>
                `).join("")}
            </tbody>
        </table>`;
}

function openTransactionDialog(item = null) {
    const fields = [
        field("kind", "Tipo de movimiento", "select", {
            required: true,
            choices: [
                { value: "expense", label: "Gasto" },
                { value: "income", label: "Ingreso" }
            ]
        }),
        field("amount", "Importe (COP)", "number", {
            required: true, min: "0.01", step: "0.01", placeholder: "Ej. 150000"
        }),
        field("description", "Descripción", "text", {
            required: true, maxlength: 200, full: true, placeholder: "Ej. Compra de mercado"
        }),
        field("transaction_date", "Fecha", "date", { required: true }),
        field("category_id", "Categoría", "select", {
            choices: categoryChoices(item?.kind || "expense")
        }),
        field("notes", "Notas", "textarea", { maxlength: 2000, full: true })
    ];

    openDialog(item ? "Editar transacción" : "Nueva transacción", fields, async form => {
        const data = formDataObject(form);
        const kind = data.kind;
        const payload = {
            kind,
            amount: amountValue(data.amount),
            description: data.description.trim(),
            transaction_date: data.transaction_date || todayISO(),
            category_id: nullableNumber(data.category_id),
            notes: nullableText(data.notes)
        };

        if (item) {
            await api(`/transactions/${item.id}`, {
                method: "PATCH",
                body: payload
            });
        } else {
            await api("/transactions", {
                method: "POST",
                body: payload
            });
        }

        closeDialog();
        showNotice(item ? "Transacción actualizada." : "Transacción creada.");
        await refreshAfterMutation();
    }, item || {
        kind: "expense",
        transaction_date: todayISO(),
        category_id: ""
    });

    const kindSelect = $('#field-kind');
    const categorySelect = $('#field-category_id');

    kindSelect.addEventListener("change", () => {
        const current = categorySelect.value;
        categorySelect.innerHTML = categoryChoices(kindSelect.value).map(choice =>
            `<option value="${escapeHTML(choice.value)}">${escapeHTML(choice.label)}</option>`
        ).join("");

        if ([...categorySelect.options].some(option => option.value === current)) {
            categorySelect.value = current;
        }
    });
}

function openCategoryDialog(item = null) {
    const fields = [
        field("name", "Nombre", "text", {
            required: true, maxlength: 80, full: true, placeholder: "Ej. Alimentación"
        }),
        field("kind", "Tipo de categoría", "select", {
            required: true,
            choices: [
                { value: "both", label: "Ingresos y gastos" },
                { value: "income", label: "Solo ingresos" },
                { value: "expense", label: "Solo gastos" }
            ]
        }),
        field("is_active", "Estado", "select", {
            required: true,
            choices: [
                { value: "true", label: "Activa" },
                { value: "false", label: "Inactiva" }
            ]
        })
    ];

    openDialog(item ? "Editar categoría" : "Nueva categoría", fields, async form => {
        const data = formDataObject(form);
        const payload = {
            name: data.name.trim(),
            kind: data.kind,
            is_active: data.is_active === "true"
        };

        await api(item ? `/categories/${item.id}` : "/categories", {
            method: item ? "PATCH" : "POST",
            body: payload
        });

        closeDialog();
        showNotice(item ? "Categoría actualizada." : "Categoría creada.");
        await refreshAfterMutation();
    }, item || { kind: "both", is_active: "true" });
}

function openBudgetDialog(item = null) {
    const fields = [
        field("category_id", "Categoría de gasto", "select", {
            required: true,
            choices: categoryChoices("expense", false)
        }),
        field("amount_limit", "Límite mensual (COP)", "number", {
            required: true, min: "0.01", step: "0.01", placeholder: "Ej. 500000"
        }),
        field("year", "Año", "number", {
            required: true, min: 2000, max: 2200, step: 1
        }),
        field("month", "Mes", "select", {
            required: true,
            choices: MONTHS.map((name, index) => ({
                value: String(index + 1),
                label: name
            }))
        })
    ];

    openDialog(item ? "Editar presupuesto" : "Nuevo presupuesto", fields, async form => {
        const data = formDataObject(form);

        if (item) {
            await api(`/budgets/${item.id}`, {
                method: "PATCH",
                body: { amount_limit: amountValue(data.amount_limit) }
            });
        } else {
            await api("/budgets", {
                method: "POST",
                body: {
                    category_id: Number(data.category_id),
                    amount_limit: amountValue(data.amount_limit),
                    year: Number(data.year),
                    month: Number(data.month)
                }
            });
        }

        closeDialog();
        showNotice(item ? "Presupuesto actualizado." : "Presupuesto creado.");
        await refreshAfterMutation();
    }, item || {
        year: currentYear(),
        month: new Date().getMonth() + 1
    });
}

function openGoalDialog(item = null) {
    const fields = [
        field("name", "Nombre de la meta", "text", {
            required: true, maxlength: 120, full: true, placeholder: "Ej. Fondo de emergencia"
        }),
        field("target_amount", "Objetivo de ahorro (COP)", "number", {
            required: true, min: "0.01", step: "0.01"
        }),
        field("deadline", "Fecha límite", "date"),
        field("notes", "Notas", "textarea", { maxlength: 500, full: true })
    ];

    openDialog(item ? "Editar meta" : "Nueva meta de ahorro", fields, async form => {
        const data = formDataObject(form);
        const payload = {
            name: data.name.trim(),
            target_amount: amountValue(data.target_amount),
            deadline: data.deadline || null,
            notes: nullableText(data.notes)
        };

        await api(item ? `/savings-goals/${item.id}` : "/savings-goals", {
            method: item ? "PATCH" : "POST",
            body: payload
        });

        closeDialog();
        showNotice(item ? "Meta actualizada." : "Meta de ahorro creada.");
        await refreshAfterMutation();
    }, item || {});
}

function openContributionDialog(goalId) {
    const fields = [
        field("amount", "Importe del aporte (COP)", "number", {
            required: true, min: "0.01", step: "0.01"
        }),
        field("contribution_date", "Fecha del aporte", "date", { required: true }),
        field("note", "Nota", "textarea", { maxlength: 300, full: true })
    ];

    openDialog("Registrar aporte", fields, async form => {
        const data = formDataObject(form);

        await api(`/savings-goals/${goalId}/contributions`, {
            method: "POST",
            body: {
                amount: amountValue(data.amount),
                contribution_date: data.contribution_date || todayISO(),
                note: nullableText(data.note)
            }
        });

        closeDialog();
        showNotice("Aporte registrado correctamente.");
        await refreshAfterMutation();
    }, { contribution_date: todayISO() });
}

async function showContributionHistory(goalId) {
    const contributions = await api(`/savings-goals/${goalId}/contributions`);
    const goal = state.goals.find(item => Number(item.id) === Number(goalId));

    const rows = contributions.length ? `
        <table class="data-table">
            <thead><tr><th>Fecha</th><th>Nota</th><th>Importe</th></tr></thead>
            <tbody>
                ${contributions.map(item => `
                    <tr>
                        <td>${dateText(item.contribution_date)}</td>
                        <td>${escapeHTML(item.note || "—")}</td>
                        <td class="amount-income">${money(item.amount)}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    ` : emptyState("Esta meta todavía no tiene aportes.");

    openDialog(
        `Historial: ${goal?.name || "Meta de ahorro"}`,
        [`<div class="dialog-field full-width">${rows}</div>`],
        async () => closeDialog()
    );

    $("#dialog-submit").textContent = "Cerrar";
    $("#dialog-cancel").classList.add("hidden");
}

async function confirmDelete(message) {
    return window.confirm(message);
}

async function deleteItem(type, id) {
    const configs = {
        transaction: {
            path: `/transactions/${id}`,
            message: "¿Quieres eliminar esta transacción?"
        },
        category: {
            path: `/categories/${id}`,
            message: "¿Quieres eliminar esta categoría? El backend puede impedirlo si tiene movimientos asociados."
        },
        budget: {
            path: `/budgets/${id}`,
            message: "¿Quieres eliminar este presupuesto?"
        },
        goal: {
            path: `/savings-goals/${id}`,
            message: "¿Quieres eliminar esta meta de ahorro?"
        }
    };

    const config = configs[type];
    if (!config || !(await confirmDelete(config.message))) return;

    try {
        await api(config.path, { method: "DELETE" });
        showNotice("Registro eliminado.");
        await refreshAfterMutation();
    } catch (error) {
        handleError(error);
    }
}

async function refreshAfterMutation() {
    await loadCategories();

    const activePage = $(".page.active")?.id?.replace("page-", "") || "dashboard";

    if (activePage === "transactions") await loadTransactions();
    else if (activePage === "budgets") await loadBudgets();
    else if (activePage === "savings") await loadGoals();
    else if (activePage === "reports") await loadReports();

    await loadDashboard();
}

function findById(items, id) {
    return items.find(item => Number(item.id) === Number(id));
}

document.addEventListener("click", async event => {
    const pageButton = event.target.closest("[data-page]");
    if (pageButton) {
        event.preventDefault();
        setPage(pageButton.dataset.page);
        return;
    }

    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) return;

    const { action, id } = actionButton.dataset;

    try {
        if (action === "edit-transaction") {
            const item = findById(state.transactions, id) ||
                await api(`/transactions/${id}`);
            openTransactionDialog(item);
        } else if (action === "delete-transaction") {
            await deleteItem("transaction", id);
        } else if (action === "edit-category") {
            openCategoryDialog(findById(state.categories, id));
        } else if (action === "delete-category") {
            await deleteItem("category", id);
        } else if (action === "edit-budget") {
            openBudgetDialog(findById(state.budgets, id));
        } else if (action === "delete-budget") {
            await deleteItem("budget", id);
        } else if (action === "edit-goal") {
            openGoalDialog(findById(state.goals, id));
        } else if (action === "delete-goal") {
            await deleteItem("goal", id);
        } else if (action === "contribute-goal") {
            openContributionDialog(id);
        } else if (action === "history-goal") {
            await showContributionHistory(id);
        }
    } catch (error) {
        handleError(error);
    }
});

$("#quick-add").addEventListener("click", () => openTransactionDialog());
$("#add-transaction").addEventListener("click", () => openTransactionDialog());
$("#add-category").addEventListener("click", () => openCategoryDialog());
$("#add-budget").addEventListener("click", () => openBudgetDialog());
$("#add-goal").addEventListener("click", () => openGoalDialog());

$("#transaction-filters").addEventListener("submit", async event => {
    event.preventDefault();

    const from = $("#filter-from").value;
    const to = $("#filter-to").value;

    if (from && to && from > to) {
        showNotice("La fecha inicial no puede ser posterior a la fecha final.", true);
        return;
    }

    if ($("#filter-min").value && $("#filter-max").value &&
        Number($("#filter-min").value) > Number($("#filter-max").value)) {
        showNotice("El monto mínimo no puede superar el monto máximo.", true);
        return;
    }

    try {
        await loadTransactions();
    } catch (error) {
        handleError(error);
    }
});

$("#clear-filters").addEventListener("click", async () => {
    $("#transaction-filters").reset();
    try {
        await loadTransactions();
    } catch (error) {
        handleError(error);
    }
});

$("#apply-budget-filters").addEventListener("click", async () => {
    try {
        await loadBudgets();
    } catch (error) {
        handleError(error);
    }
});

$("#dashboard-year").addEventListener("change", () => {
    loadDashboard().catch(handleError);
});

$("#report-year").addEventListener("change", () => {
    loadReports().catch(handleError);
});

$("#dialog-close").addEventListener("click", closeDialog);
$("#dialog-cancel").addEventListener("click", closeDialog);

$("#app-dialog").addEventListener("click", event => {
    if (event.target === $("#app-dialog")) closeDialog();
});

$("#dialog-form").addEventListener("submit", async event => {
    event.preventDefault();

    if (state.busy || !state.dialogAction) return;

    if (!event.currentTarget.reportValidity()) return;

    setBusy(true);

    try {
        await state.dialogAction(event.currentTarget);
    } catch (error) {
        handleError(error);
    } finally {
        setBusy(false);
    }
});

async function initialize() {
    initDate();
    initYearSelects();

    try {
        await api("/health");
        showConnection(true, "API conectada");
        await loadCategories();
        await loadDashboard();
    } catch (error) {
        showConnection(false, "API no disponible");
        handleError(error);
    }
}

initialize();
