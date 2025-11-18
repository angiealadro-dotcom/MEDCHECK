// Función para inicializar los gráficos de reportes
function initializeCharts(data) {
    const ctx = document.getElementById('cumplimientoChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '% Cumplimiento',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Función para formatear fechas
function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para manejar errores de forma consistente
function handleError(error) {
    console.error('Error:', error);
    alert('Ha ocurrido un error. Por favor, inténtelo nuevamente.');
}

// Función para validar formularios
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });

    // Intentar registrar SW y suscripción SIN pedir permiso automático
    try {
        registerPushIfAllowed(false);
    } catch (e) {
        console.warn('Push setup skipped:', e);
    }
});

// Utilidad para convertir base64 url a Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerPushIfAllowed(promptUser = false) {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;

    // Solo pedir permiso si viene desde una acción del usuario
    if (Notification.permission !== 'granted') {
        if (promptUser) {
            const perm = await Notification.requestPermission();
            if (perm !== 'granted') return;
        } else {
            // Aún sin permiso: no forzar prompt silencioso
            return;
        }
    }

    const reg = await navigator.serviceWorker.register('/static/sw.js');
    const existing = await reg.pushManager.getSubscription();

    // Obtener clave pública del servidor
    const resp = await fetch('/notifications/public-key', { credentials: 'same-origin' });
    if (!resp.ok) return;
    const { publicKey } = await resp.json();

    let subscription = existing;
    if (!subscription) {
        subscription = await reg.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicKey)
        });
    }

    // Enviar suscripción (nueva o existente) al backend para guardarla
    const payload = subscription && subscription.toJSON ? subscription.toJSON() : subscription;
    try {
        const resp = await fetch('/notifications/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            console.warn('No se pudo guardar la suscripción (posible no autenticado).');
        }
    } catch (e) {
        console.warn('Fallo al enviar suscripción:', e);
    }
}
