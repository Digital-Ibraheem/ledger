const API_BASE = 'http://127.0.0.1:8000/api';

// --- State ---
let expenses = [];

// --- DOM Elements ---
const navItems = document.querySelectorAll('.nav-item');
const viewSections = document.querySelectorAll('.view-section');

// Upload Elements
const dropZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn-trigger');
const loadingState = document.getElementById('upload-loading');
const resultState = document.getElementById('upload-result');

// Form Elements
const expenseForm = document.getElementById('expense-form');
const cancelBtn = document.getElementById('btn-cancel-expense');

// Table Elements
const expensesList = document.getElementById('expenses-list');
const dashRecentList = document.getElementById('dash-recent-list');
const filterCategory = document.getElementById('filter-category');
const filterDeductible = document.getElementById('filter-deductible');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupUpload();
    setupFilters();

    // Initially load expenses (even if backend returns empty [] for now)
    fetchExpenses();
});

// --- Actions Logic ---
async function clearAllExpenses() {
    if (!confirm("Are you sure you want to permanently delete all expenses?")) return;

    try {
        const res = await fetch(`${API_BASE}/expenses`, {
            method: 'DELETE'
        });

        if (res.ok) {
            expenses = [];
            renderExpenses();
            updateDashboardStats();
            showToast("All expenses cleared.");
        } else {
            showToast("Failed to clear expenses.");
        }
    } catch (e) {
        showToast("Error clearing expenses.");
    }
}

// --- Navigation Logic ---
function setupNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // UI Toggle
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // View Toggle
            const targetId = item.getAttribute('data-target');
            viewSections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetId) section.classList.add('active');
            });

            // View-specific reloads
            if (targetId === 'dashboard-view') updateDashboardStats();
        });
    });
}

// --- Upload Logic ---
function setupUpload() {
    // Trigger file dialog
    uploadBtn.addEventListener('click', () => fileInput.click());

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // File Input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Form Submit
    expenseForm.addEventListener('submit', handleExpenseSubmit);
    cancelBtn.addEventListener('click', resetUploadView);
}

async function handleFileUpload(file) {
    if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
        showToast("Invalid file. Please upload an image or PDF.");
        return;
    }

    // UI State: Loading
    dropZone.classList.add('hidden');
    resultState.classList.add('hidden');
    loadingState.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        // We will build cors logic on the backend later if needed, assume it works or we run same domain
        const response = await fetch(`${API_BASE}/expenses/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Upload failed");

        const data = await response.json();

        // Populate Form
        document.getElementById('form-merchant').value = data.merchant || '';
        document.getElementById('form-date').value = data.date || '';
        document.getElementById('form-amount').value = data.amount || '';
        document.getElementById('form-currency').value = data.currency || 'CAD';

        // Match category
        const catSelect = document.getElementById('form-category');
        const validCategories = Array.from(catSelect.options).map(opt => opt.value);
        if (validCategories.includes(data.suggested_category)) {
            catSelect.value = data.suggested_category;
        } else {
            catSelect.value = 'other';
        }

        document.getElementById('form-deductible').checked = !!data.is_deductible;
        document.getElementById('form-receipt-url').value = data.receipt_url || '';

        // UI State: Result
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');

        showToast("Receipt analyzed successfully!");

    } catch (error) {
        console.error("Upload error:", error);
        showToast("Failed to analyze receipt.");
        resetUploadView();
    }
}

async function handleExpenseSubmit(e) {
    e.preventDefault();
    // Simulate saving the expense to the backend
    // Since create_expense is stubbed, we'll fake it locally for the demo

    const newExpense = {
        id: Date.now(),
        merchant: document.getElementById('form-merchant').value,
        date: document.getElementById('form-date').value,
        amount: parseFloat(document.getElementById('form-amount').value),
        currency: document.getElementById('form-currency').value,
        category: document.getElementById('form-category').value,
        is_deductible: document.getElementById('form-deductible').checked,
        notes: document.getElementById('form-notes').value,
        receipt_url: document.getElementById('form-receipt-url').value
    };

    try {
        // Hit the actual backend 
        const response = await fetch(`${API_BASE}/expenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newExpense)
        });

        if (!response.ok) {
            throw new Error('Failed to create expense on backend');
        }

        const savedExpense = await response.json();

        // Add to local state (using the DB returned one so we have the real ID)
        expenses.unshift(savedExpense);

        showToast("Expense saved successfully!");
        resetUploadView();

        // Update views
        renderExpenses();
        updateDashboardStats();

        // Navigate back to Dashboard or stay based on preference
        document.querySelector('[data-target="dashboard-view"]').click();

    } catch (error) {
        showToast("Failed to save expense.");
    }
}

function resetUploadView() {
    fileInput.value = '';
    expenseForm.reset();
    loadingState.classList.add('hidden');
    resultState.classList.add('hidden');
    dropZone.classList.remove('hidden');
}


// --- Data Fetching & Rendering ---

async function fetchExpenses() {
    try {
        const res = await fetch(`${API_BASE}/expenses`);
        if (res.ok) {
            expenses = await res.json();
            // Removed fallback to demo data so it correctly shows empty when empty
        } else {
            console.error("Failed to load expenses list");
        }
        renderExpenses();
        updateDashboardStats();
    } catch (e) {
        console.warn("Backend not running or unreachable");
        renderExpenses();
        updateDashboardStats();
    }
}

function renderExpenses() {
    // Apply filters
    const catFilter = filterCategory.value;
    const dedFilter = filterDeductible.value;

    let filtered = expenses.filter(exp => {
        if (catFilter !== 'all' && exp.category !== catFilter) return false;
        if (dedFilter === 'true' && !exp.is_deductible) return false;
        if (dedFilter === 'false' && exp.is_deductible) return false;
        return true;
    });

    expensesList.innerHTML = '';

    if (filtered.length === 0) {
        expensesList.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 2rem;">No matching expenses found.</td></tr>`;
        return;
    }

    filtered.forEach(exp => {
        expensesList.innerHTML += createExpenseRow(exp);
    });
}

async function updateDashboardStats() {
    document.getElementById('dash-recent-list').innerHTML = '';

    // Fetch true dashboard stats from backend
    try {
        const res = await fetch(`${API_BASE}/dashboard/monthly`);
        if (res.ok) {
            const stats = await res.json();
            document.getElementById('dash-total-income').textContent = `$${stats.total_income.toFixed(2)}`;
            document.getElementById('dash-total-expenses').textContent = `$${stats.total_expenses.toFixed(2)}`;
            document.getElementById('dash-deductible').textContent = `$${stats.total_deductible.toFixed(2)}`;
        }
    } catch (e) {
        console.warn("Failed to fetch true dashboard stats, keeping UI fallback");
    }

    if (expenses.length === 0) {
        document.getElementById('dash-recent-empty').style.display = 'block';
        document.getElementById('dash-recent-table').classList.add('hidden');
        return;
    }

    document.getElementById('dash-recent-empty').style.display = 'none';
    document.getElementById('dash-recent-table').classList.remove('hidden');

    // Render top 5 recent from local state
    expenses.slice(0, 5).forEach(exp => {
        document.getElementById('dash-recent-list').innerHTML += createDashboardRow(exp);
    });
}

// --- Helpers ---

function setupFilters() {
    filterCategory.addEventListener('change', renderExpenses);
    filterDeductible.addEventListener('change', renderExpenses);

    const clearBtn = document.getElementById('btn-clear-expenses');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllExpenses);
    }
}

function createExpenseRow(exp) {
    const isDed = exp.is_deductible ? '<span class="deductible-badge"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Yes</span>' : '-';
    return `
        <tr>
            <td>${formatDate(exp.date)}</td>
            <td style="font-weight: 500;">${exp.merchant}</td>
            <td><span class="tag tag-${exp.category}">${exp.category}</span></td>
            <td>${isDed}</td>
            <td class="text-right" style="font-family: monospace; font-size:1rem;">$${exp.amount.toFixed(2)} ${exp.currency}</td>
        </tr>
    `;
}

function createDashboardRow(exp) {
    return `
        <tr>
            <td>${formatDate(exp.date)}</td>
            <td style="font-weight: 500;">${exp.merchant}</td>
            <td><span class="tag tag-${exp.category}">${exp.category}</span></td>
            <td class="text-right" style="font-weight:600;">$${exp.amount.toFixed(2)}</td>
        </tr>
    `;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.remove('hidden');

    // Tiny delay to ensure display:block applies before opacity transition
    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.classList.add('hidden'), 300);
    }, 3000);
}

// Just mock data so the UI isn't completely empty before the backend is fully wired
function populateDemoData() {
    expenses = [
        { id: 1, merchant: "Apple Store", date: "2026-03-01", amount: 1299.00, currency: "CAD", category: "business", is_deductible: true },
        { id: 2, merchant: "Starbucks", date: "2026-03-05", amount: 6.50, currency: "CAD", category: "personal", is_deductible: false },
        { id: 3, merchant: "Vercel Hosting", date: "2026-03-10", amount: 20.00, currency: "USD", category: "business", is_deductible: true },
        { id: 4, merchant: "Pharmacy", date: "2026-03-12", amount: 45.20, currency: "CAD", category: "medical", is_deductible: true }
    ];
}
