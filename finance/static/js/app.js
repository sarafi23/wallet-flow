/**
 * WALLET FLOW - Main Application Logic
 * Toast notifications, theme management, and utilities
 */

// ============================================
// TOAST NOTIFICATIONS
// ============================================
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slide-in-right`;

        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        toast.style.cssText = `
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid ${colors[type]}40;
            border-left: 4px solid ${colors[type]};
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 12px;
            color: #f1f5f9;
            font-size: 14px;
            min-width: 300px;
            cursor: pointer;
        `;

        toast.innerHTML = `
            <span style="color: ${colors[type]}; font-size: 20px;">${icons[type]}</span>
            <span style="flex: 1;">${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px; padding: 0;">
                <i class="bi bi-x"></i>
            </button>
        `;

        this.container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, duration);

        // Click to dismiss
        toast.addEventListener('click', () => toast.remove());
    }

    success(message) { this.show(message, 'success'); }
    error(message) { this.show(message, 'error'); }
    warning(message) { this.show(message, 'warning'); }
    info(message) { this.show(message, 'info'); }
}

// Global toast instance
const toast = new ToastManager();

// ============================================
// THEME MANAGEMENT
// ============================================
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'dark';
        this.apply();
    }

    toggle() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.apply();
        localStorage.setItem('theme', this.theme);
    }

    apply() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }

    isDark() {
        return this.theme === 'dark';
    }
}

const themeManager = new ThemeManager();

// ============================================
// MODAL MANAGEMENT
// ============================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('animate-fade-in');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.animation = 'fadeIn 0.2s ease-out reverse';
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 200);
    }
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// Close modal on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal[style*="display: flex"]');
        modals.forEach(modal => closeModal(modal.id));
    }
});

// ============================================
// FORM VALIDATION
// ============================================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// ============================================
// NUMBER FORMATTING
// ============================================
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

// ============================================
// DATE FORMATTING
// ============================================
function formatDate(date, format = 'short') {
    const d = new Date(date);
    const options = {
        short: { month: 'short', day: 'numeric', year: 'numeric' },
        long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    return d.toLocaleDateString('es-ES', options[format]);
}

// ============================================
// LOADING STATES
// ============================================
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
        element.style.display = 'flex';
        element.style.justifyContent = 'center';
        element.style.alignItems = 'center';
        element.style.minHeight = '200px';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.minHeight = 'auto';
    }
}

// ============================================
// CONFETTI ANIMATION (for achievements)
// ============================================
function createConfetti() {
    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        confetti.style.animationDuration = Math.random() * 2 + 2 + 's';
        document.body.appendChild(confetti);

        setTimeout(() => confetti.remove(), 4000);
    }
}

// ============================================
// COPY TO CLIPBOARD
// ============================================
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        toast.success('Copiado al portapapeles');
    } catch (err) {
        toast.error('Error al copiar');
    }
}

// ============================================
// DEBOUNCE UTILITY
// ============================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// SMOOTH SCROLL
// ============================================
function smoothScroll(targetId) {
    const element = document.getElementById(targetId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ============================================
// INITIALIZE ON DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Add animation classes to elements
    const animateElements = document.querySelectorAll('[data-animate]');
    animateElements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
        el.classList.add('animate-fade-in-up');
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.classList.add('tooltip');
    });
});

// ============================================
// SPA NAVIGATION
// ============================================
function showSection(sectionId, element) {
    // Hide all sections
    document.querySelectorAll('.spa-section').forEach(el => el.classList.remove('active'));
    // Show target section
    const targetSection = document.getElementById('section-' + sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'transactions': 'Transacciones',
        'goals': 'Metas de Ahorro',
        'categories': 'Categorías',
        'profile': 'Mi Perfil',
        'reports': 'Reportes',
        'insights': 'Insights Financieros'
    };
    const titleEl = document.getElementById('page-title');
    if (titleEl && titles[sectionId]) {
        titleEl.textContent = titles[sectionId];
    }
}

// Export for use in other modules
window.WalletFlow = {
    toast,
    themeManager,
    openModal,
    closeModal,
    validateForm,
    formatCurrency,
    formatNumber,
    formatDate,
    showLoading,
    hideLoading,
    createConfetti,
    copyToClipboard,
    debounce,
    smoothScroll,
    showSection
};
