-- MedCheck Schema for Cloudflare D1
-- Multi-tenant medical checklist system

-- Organizations (Tenants)
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT,
    institution_type TEXT,
    country TEXT,
    city TEXT,
    address TEXT,
    is_active INTEGER DEFAULT 1,
    plan TEXT DEFAULT 'free', -- free, pro, enterprise
    max_users INTEGER DEFAULT 5,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    trial_ends_at TEXT,
    logo_url TEXT,
    primary_color TEXT DEFAULT '#0d6efd'
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0,
    is_super_admin INTEGER DEFAULT 0,
    organization_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Checklist Entries
CREATE TABLE IF NOT EXISTS checklist_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT DEFAULT (datetime('now')),
    area TEXT,
    turno TEXT,
    protocolo_etapa TEXT,
    item TEXT,
    cumple INTEGER,
    observaciones TEXT,
    usuario TEXT,
    metadatos TEXT,
    -- Los 10 Correctos
    paciente_correcto INTEGER DEFAULT 0,
    medicamento_correcto INTEGER DEFAULT 0,
    dosis_correcta INTEGER DEFAULT 0,
    via_correcta INTEGER DEFAULT 0,
    hora_correcta INTEGER DEFAULT 0,
    fecha_vencimiento_verificada INTEGER DEFAULT 0,
    educacion_paciente INTEGER DEFAULT 0,
    registro_correcto INTEGER DEFAULT 0,
    alergias_verificadas INTEGER DEFAULT 0,
    responsabilidad_personal INTEGER DEFAULT 0,
    -- Multi-tenancy
    organization_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    scheduled_at TEXT NOT NULL,
    sent_at TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    organization_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- WebPush Subscriptions
CREATE TABLE IF NOT EXISTS webpush_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_org ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_checklist_org ON checklist_entries(organization_id);
CREATE INDEX IF NOT EXISTS idx_checklist_fecha ON checklist_entries(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_reminders_org ON reminders(organization_id);
CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_orgs_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_orgs_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_checklist_org_fecha ON checklist_entries(organization_id, fecha_hora);
CREATE INDEX IF NOT EXISTS idx_users_org_active ON users(organization_id, is_active);
