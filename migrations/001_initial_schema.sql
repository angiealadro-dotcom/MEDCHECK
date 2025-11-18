-- Migración inicial para MedCheck Multi-Tenant
-- Compatible con Cloudflare D1 (SQLite)

-- Tabla de Organizaciones
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    institution_type VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    is_active BOOLEAN DEFAULT 1,
    plan VARCHAR(50) DEFAULT 'free',
    max_users INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_ends_at TIMESTAMP,
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#0d6efd'
);

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    is_super_admin BOOLEAN DEFAULT 0,
    organization_id INTEGER,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Tabla de Entradas de Checklist
CREATE TABLE IF NOT EXISTS checklist_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    area VARCHAR(100),
    turno VARCHAR(50),
    protocolo_etapa VARCHAR(200),
    item VARCHAR(500),
    cumple BOOLEAN,
    observaciones TEXT,
    usuario VARCHAR(255),
    metadatos TEXT,

    -- Los 10 Correctos
    paciente_correcto BOOLEAN DEFAULT 0,
    medicamento_correcto BOOLEAN DEFAULT 0,
    dosis_correcta BOOLEAN DEFAULT 0,
    via_correcta BOOLEAN DEFAULT 0,
    hora_correcta BOOLEAN DEFAULT 0,
    fecha_vencimiento_verificada BOOLEAN DEFAULT 0,
    educacion_paciente BOOLEAN DEFAULT 0,
    registro_correcto BOOLEAN DEFAULT 0,
    alergias_verificadas BOOLEAN DEFAULT 0,
    responsabilidad_personal BOOLEAN DEFAULT 0,

    -- Multi-tenancy
    organization_id INTEGER DEFAULT 1,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Tabla de Recordatorios
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Tabla de Suscripciones WebPush
CREATE TABLE IF NOT EXISTS webpush_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_users_org ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_checklist_org ON checklist_entries(organization_id);
CREATE INDEX IF NOT EXISTS idx_checklist_fecha ON checklist_entries(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_reminders_org ON reminders(organization_id);
CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_orgs_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_orgs_active ON organizations(is_active);

-- Índices compuestos para queries comunes
CREATE INDEX IF NOT EXISTS idx_checklist_org_fecha ON checklist_entries(organization_id, fecha_hora);
CREATE INDEX IF NOT EXISTS idx_users_org_active ON users(organization_id, is_active);
